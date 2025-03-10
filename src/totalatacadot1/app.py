from threading import Thread
from time import sleep
from totalatacadot1.dml_tables import create_tables
from totalatacadot1.controller import AppController
from totalatacadot1.models import PDV, PDVItem
from totalatacadot1.repository import create_pdv_control_item, get_last_pdv_pedido, get_pdv_control_item_by_num_ped_ecf


def background_task(controller: AppController):
    while True:
        sleep(10)

        if controller.is_gui_open():
            print("A GUI já está aberta. Aguardando liberação...")
            continue

        last_pdv_pedido: PDV = get_last_pdv_pedido()
        if last_pdv_pedido is None:
            continue

        pdv_control_item = get_pdv_control_item_by_num_ped_ecf(last_pdv_pedido.num_ped_ecf)
        if pdv_control_item is None:
            pdv_control_item: PDVItem = create_pdv_control_item(last_pdv_pedido.num_ped_ecf)
            controller.show_gui(pdv_control_item.num_ped_ecf)


def main():
    create_tables()
    controller = AppController()

    # Criar e iniciar a thread que executa a lógica em segundo plano
    thread = Thread(target=background_task, args=(controller,), daemon=True)
    thread.start()

    # Iniciar o loop de eventos do Qt
    controller.run_event_loop()

        
if __name__ == "__main__":
    main()
