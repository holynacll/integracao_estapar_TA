import os
import sys
from threading import Thread
from pathlib import Path

from loguru import logger

from time import sleep
from totalatacadot1.dml_tables import create_tables
from totalatacadot1.controller_gui import AppController
from totalatacadot1.models import PCPEDCECF, PCPEDCECFItem
from totalatacadot1.repository import (
    create_pdv_control_item,
    get_last_pdv_pedido,
    get_pdv_control_item_by_num_ped_ecf,
)

# os.environ["QT_QPA_PLATFORM"] = "xcb"
# os.environ["QT_QPA_PLATFORM"] = "windows"  # or "direct2d"


def background_task(controller: AppController):
    while True:
        sleep(5)

        if controller.is_gui_open():
            logger.info("A GUI já está aberta. Aguardando liberação...")
            continue
        last_pdv_pedido: PCPEDCECF = get_last_pdv_pedido()
        if last_pdv_pedido is None:
            continue

        pdv_control_item = get_pdv_control_item_by_num_ped_ecf(
            last_pdv_pedido.num_ped_ecf
        )
        if pdv_control_item is None:
            pdv_control_item: PCPEDCECFItem = create_pdv_control_item(
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

    logger.info("Log funcionando!")
    logger.info("TESTEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE = Iniciando o aplicativo...")

    create_tables()
    controller = AppController()

    # Inicialmente esconder a janela principal, mas manter o ícone na bandeja
    controller.hide_gui()

    # Criar e iniciar a thread que executa a lógica em segundo plano
    thread = Thread(target=background_task, args=(controller,), daemon=True)
    thread.start()

    # Iniciar o loop de eventos do Qt
    controller.run_event_loop()


if __name__ == "__main__":
    main()
