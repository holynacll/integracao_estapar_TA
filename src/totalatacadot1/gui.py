import os
import sys
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtWidgets import (
    QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QMainWindow, QLineEdit, QMessageBox, QSpacerItem, QSizePolicy, QFrame, QGraphicsOpacityEffect
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QBrush
from qt_material import apply_stylesheet
from dotenv import load_dotenv

from totalatacadot1.controller_integration_service import DiscountCreationDto, create_discount
from totalatacadot1.custom_message_box import CustomMessageBox
from totalatacadot1.integration_service import IntegrationService
from totalatacadot1.models import PDV
from totalatacadot1.repository import get_last_pdv_pedido
from totalatacadot1.utils import resolve_date_to_timestamp

from .config import get_assets_path

load_dotenv()

IP = os.environ.get("IP")
PORT = int(os.environ.get("PORT"))
os.environ["QT_QPA_PLATFORM"] = "xcb"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Total Atacado")
        icon_path = str(get_assets_path() / "icons" / "icon")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 1024, 768)

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
    
    def closeEvent(self, event):
        # Override the close event to hide the window instead of closing it
        event.ignore()
        self.hide()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.background_image_path = str(get_assets_path() / "images" / "background-2.jpg")
        self.success_icon_path = str(get_assets_path() / "images" / "checked.png")
        self.error_icon_path = str(get_assets_path() / "images" / "warning.png")
        self.pdv_pedido: PDV = get_last_pdv_pedido()
        self.init_ui()
        

    def init_ui(self):        
        # Carrega a imagem original
        pixmap = QPixmap(self.background_image_path)

        # Criando um novo pixmap com transparência
        transparent_pixmap = QPixmap(pixmap.size())
        transparent_pixmap.fill(Qt.GlobalColor.transparent)

        # Aplicando a opacidade na imagem
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(0.2)  # Ajuste a opacidade aqui (1.0 = sem transparência, 0.0 = totalmente transparente)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        # Criar um QLabel para o fundo
        self.background_label = QLabel(self)
        self.background_label.setPixmap(transparent_pixmap)
        self.background_label.setScaledContents(True)  # Faz a imagem se expandir
        self.background_label.resize(self.size())  # Ajusta ao tamanho da tela

        # Criando layout principal (widgets ficarão sobre o frame)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title = QLabel("Integração Estacionamento")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #222;")

        # Input Label        
        self.label = QLabel("Ticket do Cliente:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label.setStyleSheet("""color: #444;""")

        # Input Field
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Escreva o código aqui")
        self.edit.setFixedHeight(50)
        self.edit.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border: 2px solid #bbb;
                border-radius: 10px;
                background-color: white;
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

        self.button = QPushButton("Validar")
        self.button.setFixedHeight(50)
        self.button.clicked.connect(self.validate_ticket)
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
            }
            
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0056b3, stop:1 #003d80);
            }
            
            QPushButton:pressed {
                background-color: #003d80;
            }
        """)
        
        # Input Label        
        self.footer_label = QLabel("@ 2025 Total Atacado")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setFont(QFont("Arial", 14, QFont.Weight.DemiBold))
        self.footer_label.setStyleSheet("""color: #444;""")

        # layout = QVBoxLayout(self.frame)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title)
        # Adiciona um espaço para empurrar os elementos para baixo
        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.edit)
        main_layout.addWidget(self.button)
        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(self.footer_label)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """ Redimensiona a imagem de fundo quando a janela for redimensionada """
        self.background_label.resize(self.size())

    @Slot()
    def validate_ticket(self):
        """Verifica o ticket para validação e exibe mensagem de sucesso ou erro"""
        ticket_code = self.edit.text().strip()

        if not ticket_code:
            # Exibe uma caixa de mensagem personalizada para erro
            error_box = CustomMessageBox(
                "Erro", 
                "Código inválido!\nPor favor, verifique o código e tente novamente.\n", 
                self.error_icon_path, 
                self
            )
            error_box.exec()
            return

        # # Instância do serviço
        service = IntegrationService(IP, PORT)

        # Criar uma requisição de exemplo
        request = DiscountCreationDto(
            card_barcode=ticket_code,
            terminal_id=self.pdv_pedido.num_caixa,
            num_cupom=self.pdv_pedido.num_cupom,
            discount_datetime=resolve_date_to_timestamp(self.pdv_pedido.data, self.pdv_pedido.hora_cupom),
            purchase_value=int(self.pdv_pedido.vl_total * 100),
            fiscal_document="04558054000173",  # CNPJ válido
        )

        # # Chamar a função para criar desconto
        result = create_discount(request, service)

        # Exibir o resultado
        print(f"Success: {result.Success}, Message: {result.Message}")

        if ticket_code == "some_value":
            # Exibe uma caixa de mensagem personalizada para sucesso
            success_box = CustomMessageBox(
                "Sucesso", 
                "Código validado com sucesso!\n", 
                self.success_icon_path, 
                self
            )
            success_box.exec()
            self.edit.clear()
        else:
            # Exibe uma caixa de mensagem personalizada para erro
            error_box = CustomMessageBox(
                "Erro", 
                "Código inválido!\nPor favor, verifique o código e tente novamente.\n", 
                self.error_icon_path, 
                self
            )
            error_box.exec()
