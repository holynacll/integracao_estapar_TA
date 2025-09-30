# src/totalatacadot1/gui/main_window.py
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon

from ..config import get_assets_path
from .main_widget import MainWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Total Atacado - Integração Estacionamento")
        icon_path = str(get_assets_path() / "icons" / "icon")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 1024, 768)

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowMinMaxButtonsHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

    @Slot(int)
    def update_actual_valor(self, valor: int):
        """Atualiza especificamente o actual_valor na interface."""
        self.main_widget.actual_valor.setValue(valor)
        print(f"Actual valor atualizado: {valor}")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
