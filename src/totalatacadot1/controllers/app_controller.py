import sys
import socket
import traceback
from loguru import logger
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QAction

from ..config import get_assets_path, IP, PORT
from ..gui.main_window import MainWindow
from ..components.custom_message_box import CustomMessageBox
from ..notification import Notification
from ..repository import get_last_pdv_pedido
from ..schemas import DiscountRequest
from ..enums import CommandType
from ..services.estapar_integration_service import EstaparIntegrationService


class AppController(QObject):
    request_show_gui = Signal()
    request_hide_gui = Signal()
    request_shutdown = Signal()
    actual_valor_updated = Signal(float)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

        # Conexões de sinais e slots
        self.request_show_gui.connect(self._show_gui)
        self.request_hide_gui.connect(self._hide_gui)
        self.request_shutdown.connect(self._shutdown)
        self.actual_valor_updated.connect(self.window.update_actual_valor)
        
        # Conecta o sinal de processamento do widget ao handler do controlador
        self.window.main_widget.process_request.connect(self.handle_process_request)

        self.setup_tray_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self.app)
        icon_path = str(get_assets_path() / "icons" / "icon.ico")
        self.tray_icon.setIcon(QIcon(icon_path))

        tray_menu = QMenu()
        show_action = QAction("Mostrar", self.app)
        show_action.triggered.connect(self.show_gui)
        exit_action = QAction("Sair", self.app)
        exit_action.triggered.connect(self.shutdown)
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    @Slot(dict) # type: ignore
    def handle_process_request(self, form_data: dict) -> None:
        """Lida com a lógica de negócio de processar o ticket."""
        hostname = socket.gethostname()
        ticket_code = form_data["ticket_code"]
        operation_type = form_data["operation_type"]
        parent_widget = form_data["parent_widget"]
        
        error_icon_path = str(get_assets_path() / "images" / "warning.png")
        success_icon_path = str(get_assets_path() / "images" / "checked.png")

        try:
            logger.debug("Iniciando processamento de ticket")
            if not ticket_code:
                logger.warning("Ticket vazio recebido")
                CustomMessageBox("Erro", "Código inválido!\nPor favor, verifique o código e tente novamente.", error_icon_path, parent_widget).exec()
                return

            pdv_pedido = None
            if operation_type != "MANUAL_VALIDATION":
                logger.debug("Consultando último pedido PDV")
                pdv_pedido = get_last_pdv_pedido()

            if operation_type == "MANUAL_VALIDATION":
                num_cupom = form_data["num_cupom"]
                valor_total = form_data["valor_total"]

                if not num_cupom or not valor_total:
                    CustomMessageBox("Erro", "Por favor, preencha todos os campos obrigatórios para Validação Manual.", error_icon_path, parent_widget).exec()
                    return
                if not num_cupom.isdigit():
                    CustomMessageBox("Erro", "O número do cupom deve ser um número inteiro.", error_icon_path, parent_widget).exec()
                    return

                logger.debug(f"Validação Manual - Cupom: {num_cupom}, Valor: {valor_total}")
                discount_request = DiscountRequest(
                    cmd_card_id=ticket_code,
                    cmd_term_id=int(num_cupom),
                    cmd_op_value=valor_total,
                    cmd_type=CommandType.VALIDATION,
                )
                notification_data = Notification(
                    ticket_code=ticket_code,
                    operation_type=operation_type,
                    num_caixa=None,
                    hostname=hostname,
                    num_cupom=int(num_cupom),
                    vl_total=valor_total
                )
            else:
                if not pdv_pedido:
                    logger.error("Nenhum pedido PDV encontrado")
                    CustomMessageBox("Erro", "Não foi possível encontrar um pedido PDV válido.\nPor favor, contate a administração.", error_icon_path, parent_widget).exec()
                    return
                
                logger.debug("Criando requisição automática")
                discount_request = DiscountRequest(
                    cmd_card_id=ticket_code,
                    cmd_term_id=pdv_pedido.num_ped_ecf,
                    cmd_op_value=pdv_pedido.vl_total,
                    cmd_type=operation_type,
                )
                notification_data = Notification(
                    ticket_code=ticket_code,
                    operation_type="AUTOMATIC_VALIDATION",
                    num_caixa=pdv_pedido.num_caixa,
                    hostname=hostname,
                    num_ped_ecf=str(pdv_pedido.num_ped_ecf),
                    vl_total=float(pdv_pedido.vl_total)
                )

            discount_request.validate()
            
            logger.debug("Enviando requisição para API Estapar")
            service = EstaparIntegrationService(IP, PORT)
            result = service.create_discount(discount_request)
            logger.debug(f"Resposta da API: {result}")


            # print("MOCKANDO resultado do desconto lançado!")
            # result.message = "MENSAGEM DE SUCESSO MOCKADA"
            # result.success = True

            notification_data.success = result.success
            notification_data.message = result.message
            notification_data.notify_discount()

            if result.success:
                success_title = "Operação Realizada com Sucesso"
                if operation_type == "MANUAL_VALIDATION":
                    success_title = "Validação Manual Realizada"
                
                msg = f"API Estapar: {result.message}"
                logger.success(msg)
                CustomMessageBox(success_title, msg, success_icon_path, parent_widget).exec()
                
                QTimer.singleShot(1500, self.window.showMinimized)
                self.window.main_widget.clear_inputs(all_fields=operation_type == "MANUAL_VALIDATION")
            else:
                logger.error(f"Erro na API: {result.message}")
                CustomMessageBox("Erro", f"Operação não realizada!\nAPI Estapar: {result.message}", error_icon_path, parent_widget).exec()

        except ValueError as e:
            logger.error(f"Erro de validação: {e}")
            CustomMessageBox("Erro de Validação", f"Dados inválidos:\n{str(e)}", error_icon_path, parent_widget).exec()
        except Exception as e:
            logger.critical(f"Erro inesperado: {str(e)}")
            traceback.print_exc()
            CustomMessageBox("Erro Crítico", "Ocorreu um erro inesperado, verifique os logs.", error_icon_path, parent_widget).exec()
            # Notificação de erro crítico
            notification = Notification(
                ticket_code=ticket_code if 'ticket_code' in locals() else 'N/A',
                operation_type=operation_type if 'operation_type' in locals() else 'UNKNOWN',
                vl_total=0.0,
                success=False, message=f"Erro inesperado: {str(e)}"
            )
            notification.notify_discount()

    @Slot() # type: ignore
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_gui() if not self.window.isVisible() else self.hide_gui()

    @Slot(float) # type: ignore
    def emit_actual_valor_update(self, valor: float):
        self.actual_valor_updated.emit(valor)

    @Slot()
    def show_gui(self):
        self.request_show_gui.emit()

    @Slot()
    def hide_gui(self):
        self.request_hide_gui.emit()

    @Slot()
    def shutdown(self):
        self.request_shutdown.emit()

    @Slot()
    def _show_gui(self):
        self.window.showMaximized()
        self.window.activateWindow()

    @Slot()
    def _hide_gui(self):
        self.window.hide()

    @Slot()
    def _shutdown(self):
        self.app.quit()

    def is_gui_open(self) -> bool:
        return self.window.isVisible()

    def run_event_loop(self):
        sys.exit(self.app.exec())
