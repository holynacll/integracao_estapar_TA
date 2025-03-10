import sys
from PySide6.QtWidgets import QApplication

from totalatacadot1.gui import MainWindow


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

    def show_gui(self, num_ped_ecf: int):
        """Show the hidden GUI window."""
        print(f'Exibindo GUI para o ticket {num_ped_ecf}')
        self.window.show()

    def is_gui_open(self) -> bool:
        """Verifica se a GUI está aberta (visível)."""
        return self.window.isVisible()
    
    def run_event_loop(self):
        """Executa o loop de eventos da aplicação Qt."""
        sys.exit(self.app.exec())
