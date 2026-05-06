import os
import platform
import sys
from pathlib import Path
from threading import Thread
from time import sleep

from loguru import logger

from totalatacadot1.config import settings
from totalatacadot1.controllers.app_controller import AppController
from totalatacadot1.database import init_db
from totalatacadot1.models import PCPEDCECF
from totalatacadot1.notification import Notification
from totalatacadot1.repository import (
    create_pdv_control_item,
    get_last_notification_not_sent,
    get_last_pdv_pedido,
    get_pdv_control_item_by_num_ped_ecf_and_today,
)

if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"


def logger_init_setup():
    logger.remove()  # Remove o handler padrão para evitar duplicação
    log_dir = Path.home() / "logs"
    log_dir.mkdir(exist_ok=True)  # Garante que o diretório exista

    log_file = log_dir / "app.log"
    logger.add(log_file, rotation="1 day", retention="7 days")
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
    logger.info("Iniciando o aplicativo...")


def db_init_setup():
    db_on = False
    try:
        init_db()
        db_on = True
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
    return db_on


def listen_new_pdv_item(
    controller: AppController, is_active_db: bool, last_cupom: list
):
    if not is_active_db:
        logger.warning(
            "Banco de dados desativado. Não será possível verificar novos itens do PDV."
        )
        return

    last_pdv_pedido: PCPEDCECF | None = get_last_pdv_pedido()
    if last_pdv_pedido is None:
        logger.info("Nenhum pedido encontrado - SKIPPING.")
        return

    logger.info(
        f"Último pedido PDV: num_ped_ecf={last_pdv_pedido.num_ped_ecf}, vl_total={last_pdv_pedido.vl_total}"
    )
    controller.emit_actual_valor_update(last_pdv_pedido.vl_total)

    if not settings.use_internal_control:
        if last_pdv_pedido.num_ped_ecf != last_cupom[0]:
            last_cupom[0] = last_pdv_pedido.num_ped_ecf
            logger.info(
                f"Novo pedido detectado (sem controle interno): num_ped_ecf={last_pdv_pedido.num_ped_ecf}"
            )
            controller.show_gui()
        return

    pdv_control_item = get_pdv_control_item_by_num_ped_ecf_and_today(
        last_pdv_pedido.num_ped_ecf
    )
    if pdv_control_item is None:
        pdv_control_item = create_pdv_control_item(
            last_pdv_pedido.num_ped_ecf,
            last_pdv_pedido.num_cupom,
            last_pdv_pedido.data,
        )
        logger.info(
            f"Criando novo item de controle PDV: num_ped_ecf={pdv_control_item.num_ped_ecf}"
            " - Lançamento do desconto liberado."
        )
        controller.show_gui()
    else:
        logger.info(
            f"Item de controle PDV encontrado: num_ped_ecf={pdv_control_item.num_ped_ecf} - SKIPPING."
        )


def listen_notification_not_sent():
    try:
        last_notification_not_sent = get_last_notification_not_sent()
        if last_notification_not_sent is not None:
            logger.info(
                f"Encontrada notificação não enviada: {last_notification_not_sent.id}"
            )
            notification_item = Notification(**last_notification_not_sent.data)
            notification_item.notify_discount()
        else:
            logger.info("Nenhuma notificação não enviada encontrada - SKIPPING.")
    except Exception as e:
        logger.error(f"Erro ao processar notificação: {e}")


def background_task(controller: AppController, is_active_db: bool):
    logger.info("Iniciando thread de background...")
    controller.show_gui()
    last_cupom = [None]
    while True:
        sleep(5)
        listen_notification_not_sent()
        listen_new_pdv_item(controller, is_active_db, last_cupom)


def print_inital_configuration():
    logger.info("Configurações iniciais:")
    logger.info(f"IP da API Estapar: {settings.estapar_ip}")
    logger.info(f"Porta da API Estapar: {settings.estapar_port}")
    logger.info(f"Usuário do banco de dados Oracle: {settings.oracle_user}")
    logger.info(f"Senha do banco de dados Oracle: {settings.oracle_password}")
    logger.info(f"Host do banco de dados Oracle: {settings.oracle_host}")
    logger.info(f"Porta do banco de dados Oracle: {settings.oracle_port}")
    logger.info(f"URL de notificação: {settings.url_notification}")
    logger.info(f"Controle interno ativo: {settings.use_internal_control}")
    logger.info(f"Caminho da raiz do projeto: {settings.project_root}")
    logger.info(f"Caminho dos assets: {settings.assets_path}")
    logger.info(f"Caminho das imagens: {settings.images_path}")
    logger.info(f"Caminho do Instant Client: {settings.orcl_instant_client_path}")
    logger.info(
        f"Caminho do Instant Client zipado: {settings.orcl_instant_client_path_zipped}"
    )


def main():
    logger_init_setup()
    print_inital_configuration()
    is_db_active = db_init_setup()
    controller = AppController()

    # Criar e iniciar a thread que executa a lógica em segundo plano
    thread = Thread(
        target=background_task, args=(controller, is_db_active), daemon=True
    )
    thread.start()

    # Iniciar o loop de eventos do Qt
    controller.run_event_loop()


if __name__ == "__main__":
    main()
