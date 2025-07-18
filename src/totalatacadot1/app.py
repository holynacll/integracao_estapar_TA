import os
import platform
import sys
from threading import Thread
from pathlib import Path

from loguru import logger

from time import sleep
from totalatacadot1.controller_gui import AppController
from totalatacadot1.database import init_db
from totalatacadot1.models import PCPEDCECF, ControlPDV
from totalatacadot1.repository import (
    create_pdv_control_item,
    get_last_pdv_pedido,
    get_pdv_control_item_by_num_ped_ecf,
)

if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"


def background_task(controller: AppController):
    while True:
        sleep(5)

        # if controller.is_gui_open():
        #     logger.info("A GUI já está aberta. Aguardando liberação...")
        #     continue
        last_pdv_pedido: PCPEDCECF | None = get_last_pdv_pedido()
        if last_pdv_pedido is None:
            continue

        controller.emit_actual_valor_update(last_pdv_pedido.vl_total)

        pdv_control_item = get_pdv_control_item_by_num_ped_ecf(
            last_pdv_pedido.num_ped_ecf
        )
        if pdv_control_item is None:
            pdv_control_item = create_pdv_control_item(
                last_pdv_pedido.num_ped_ecf
            )
            """Solicita a validação do ticket."""
            controller.show_gui()


def main():
    log_dir = Path.home() / "logs"
    log_dir.mkdir(exist_ok=True)  # Garante que o diretório exista

    log_file = log_dir / "app.log"
    logger.add(log_file, rotation="1 day", retention="7 days")
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
    logger.info("Iniciando o aplicativo...")

    # init db
    db_on = False
    try:
        init_db()
        db_on = True
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")

    controller = AppController()

    # Inicialmente esconder a janela principal, mas manter o ícone na bandeja
    if db_on:
        controller.hide_gui()

        # Criar e iniciar a thread que executa a lógica em segundo plano
        thread = Thread(target=background_task, args=(controller,), daemon=True)
        thread.start()
    else:
        controller.show_gui()


    # Iniciar o loop de eventos do Qt
    controller.run_event_loop()


if __name__ == "__main__":
    main()
