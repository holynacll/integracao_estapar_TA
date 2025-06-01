import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QIcon, QAction
from totalatacadot1.config import get_assets_path
from totalatacadot1.gui import MainWindow


class AppController(QObject):
    # Sinais para operações thread-safe
    request_show_gui = Signal()
    request_hide_gui = Signal()
    request_shutdown = Signal()
    
    actual_valor_updated = Signal(float)  # Sinal específico para actual_valor

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

        # Conecta os sinais aos slots
        self.request_show_gui.connect(self._show_gui)
        self.request_hide_gui.connect(self._hide_gui)
        self.request_shutdown.connect(self._shutdown)
        
        # Conecta sinal do valor atual do ultimo pedido no Oracle DB
        self.actual_valor_updated.connect(self.window.update_actual_valor)

        self.setup_tray_icon()

    def setup_tray_icon(self):
        """Configura o ícone na bandeja do sistema de forma thread-safe."""
        self.tray_icon = QSystemTrayIcon(self.app)
        icon = str(get_assets_path() / "icons" / "icon")
        self.tray_icon.setIcon(QIcon(icon))

        tray_menu = QMenu()

        # Ações do menu
        show_action = QAction("Mostrar", self.app)
        show_action.triggered.connect(self.show_gui)  # Emite sinal

        exit_action = QAction("Sair", self.app)
        exit_action.triggered.connect(self.shutdown)  # Emite sinal

        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    @Slot()
    def on_tray_icon_activated(self, reason):
        """Manipula ativações do ícone de forma thread-safe."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.window.isVisible():
                self.request_hide_gui.emit()
            else:
                self.request_show_gui.emit()
    
    @Slot()
    def emit_actual_valor_update(self, valor):
        """Interface pública para emitir atualização do actual_valor (thread-safe)."""
        self.actual_valor_updated.emit(valor)


    @Slot()
    def show_gui(self):
        """Interface pública para mostrar a janela (thread-safe)."""
        self.request_show_gui.emit()

    @Slot()
    def hide_gui(self):
        """Interface pública para esconder a janela (thread-safe)."""
        self.request_hide_gui.emit()

    @Slot()
    def shutdown(self):
        """Interface pública para encerrar o app (thread-safe)."""
        self.request_shutdown.emit()

    # Slots reais que executam as operações
    @Slot()
    def _show_gui(self):
        """Mostra a janela (deve rodar no thread principal)."""
        # self.window.showFullScreen()
        self.window.showMaximized()
        self.window.activateWindow()

    @Slot()
    def _hide_gui(self):
        """Esconde a janela (deve rodar no thread principal)."""
        self.window.hide()

    @Slot()
    def _shutdown(self):
        """Encerra o aplicativo (deve rodar no thread principal)."""
        self.app.quit()

    def is_gui_open(self) -> bool:
        """Verifica se a GUI está aberta."""
        return self.window.isVisible()

    def run_event_loop(self):
        """Executa o loop de eventos."""
        sys.exit(self.app.exec())
