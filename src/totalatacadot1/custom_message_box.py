from PySide6.QtWidgets import QLabel, QVBoxLayout, QDialog, QPushButton
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt


class CustomMessageBox(QDialog):
    def __init__(self, title, message, icon_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Define o tamanho fixo da janela
        # self.setFixedSize(500, 275)

        # Layout da caixa de mensagem
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Espaçamento entre os widgets
        layout.setContentsMargins(20, 20, 20, 20)  # Margens internas

        # Adiciona um ícone personalizado
        icon_label = QLabel(self)
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Adiciona a mensagem
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        layout.addWidget(message_label)

        # Adiciona um botão de OK
        ok_button = QPushButton("OK", self)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        # Define o estilo da janela
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
        """)

        self.setLayout(layout)
