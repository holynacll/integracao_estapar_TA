import sys
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtWidgets import (
    QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QMainWindow, QLineEdit, QMessageBox, QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtGui import QIcon, QFont
from qt_material import apply_stylesheet

from .config import get_assets_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Total Atacado")
        # add icon ico file here
        icon_path = str(get_assets_path() / "images" / "logo.jpeg")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 1024, 768)

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Criando um frame para aplicar o background
        self.frame = QFrame(self)
        self.frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        background_image_path = str(get_assets_path() / "images" / "background.png")
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-image: url({background_image_path}); 
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
                background-attachment: fixed;
                background-color: #f5f5f5;
            }}
        """)
        
        # Title
        self.title = QLabel("Integração Estapar")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.title.setFrameShadow(QLabel.Shadow.Plain)
        self.title.setStyleSheet("""
            color: #222;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        """)
        
        self.label = QLabel("Código do Ticket:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label.setStyleSheet("""
             color: #444;
        """)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Escreva o código do ticket aqui")
        self.edit.setFixedHeight(45)
        self.edit.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border: 2px solid #bbb;
                border-radius: 10px;
                background-color: white;
                box-shadow: 2 2 5px rgba(0, 0, 0, 0.1);
            }

            QLineEdit:focus {
                border: 2px solid #007BFF;
                background-color: #F0F8FF;
                outline: none;
            }

            QLineEdit:hover {
                border: 2px solid #0056b3;
            }
        """)


        self.button = QPushButton("Registrar")
        self.button.setFixedHeight(50)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #007BFF, stop:1 #0056b3);
                color: white;
                border-radius: 12px;
                padding: 12px;
                border: none;
                box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.2);
            }
            
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0056b3, stop:1 #003d80);
            }
            
            QPushButton:pressed {
                background-color: #003d80;
                transform: scale(0.98);
            }
        """)

        # Conectar botão às funções
        self.button.clicked.connect(self.save_code)

        layout = QVBoxLayout(self.frame)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)
        # Adiciona um espaço para empurrar os elementos para baixo
        layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

    @Slot()
    def save_code(self):
        """Verifica o código e exibe mensagem de sucesso ou erro"""
        code = self.edit.text().strip()

        if code == "some_value":
            QMessageBox.information(self, "Sucesso", "Código salvo com sucesso! ✅")
            self.edit.clear()
        else:
            QMessageBox.warning(self, "Erro", "Código inválido! ❌")


def main():
    app = QApplication(sys.argv)

    # Aplicar tema do qt-material
    # apply_stylesheet(app, theme='dark_medical.xml')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
