import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon, QAction
from totalatacadot1.config import get_assets_path
from totalatacadot1.gui import MainWindow


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        
        # Configurar o ícone da bandeja do sistema
        self.setup_tray_icon()
        
    def setup_tray_icon(self):
        """Configura o ícone na bandeja do sistema."""
        # Criar o ícone da bandeja
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Definir o ícone (substitua pelo caminho do seu ícone)
        # Se você não tiver um ícone, pode usar um dos ícones padrão do sistema
        icon = str(get_assets_path() / "icons" / "icon")
        self.tray_icon.setIcon(QIcon(icon))
        # QIcon.fromTheme("application-x-executable")
        
        # Criar menu de contexto para o ícone da bandeja
        tray_menu = QMenu()
        
        # Adicionar ações ao menu
        show_action = QAction("Mostrar", self.app)
        show_action.triggered.connect(self.show_gui)
        
        exit_action = QAction("Sair", self.app)
        exit_action.triggered.connect(self.app.quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(exit_action)
        
        # Definir o menu de contexto para o ícone da bandeja
        self.tray_icon.setContextMenu(tray_menu)
        
        # Mostrar o ícone na bandeja
        self.tray_icon.show()
        
        # Opcional: conectar o clique no ícone para mostrar a janela
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
    
    def on_tray_icon_activated(self, reason):
        """Manipula a ativação do ícone da bandeja."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Clique simples no ícone
            if self.window.isVisible():
                self.hide_gui()
            else:
                self.show_gui()

    def hide_gui(self):
        """Esconde a janela GUI."""
        self.window.hide()

    def show_gui(self):
        """Show the hidden GUI window."""
        self.window.show()
        self.window.activateWindow()  # Traz a janela para frente

    def is_gui_open(self) -> bool:
        """Verifica se a GUI está aberta (visível)."""
        return self.window.isVisible()
    
    def run_event_loop(self):
        """Executa o loop de eventos da aplicação Qt."""
        sys.exit(self.app.exec())
