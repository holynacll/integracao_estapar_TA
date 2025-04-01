from datetime import datetime
import os
import sys

from loguru import logger
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QLineEdit,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QBrush
from qt_material import apply_stylesheet
# from dotenv import load_dotenv

from totalatacadot1.enums import CommandType
from totalatacadot1.estapar_integration_service import EstaparIntegrationService
from totalatacadot1.custom_message_box import CustomMessageBox
from totalatacadot1.estapar_integration_service import EstaparIntegrationService
from totalatacadot1.models import PCPEDCECF
from totalatacadot1.repository import get_last_pdv_pedido
from totalatacadot1.schemas import DiscountRequest
from totalatacadot1.utils import resolve_date_to_timestamp

from .config import get_assets_path

# load_dotenv()

# Estapar API
IP="10.7.39.10"
PORT=3000
IP="127.0.0.1"
PORT=33535

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Total Atacado")
        icon_path = str(get_assets_path() / "icons" / "icon")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 1024, 768)
        
        # Configura as flags da janela para remover o botão de minimizar
        self.setWindowFlags(
            Qt.WindowType.Window |  # Tipo básico de janela
            Qt.WindowType.WindowCloseButtonHint |  # Garante o botão de fechar
            Qt.WindowType.WindowMaximizeButtonHint |  # Botão de maximizar/redimensionar
            Qt.WindowType.CustomizeWindowHint  # Permite personalização
        )

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        # Override the close event to hide the window instead of closing it
        event.ignore()
        self.hide()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.background_image_path = str(
            get_assets_path() / "images" / "background-2.jpg"
        )
        self.success_icon_path = str(get_assets_path() / "images" / "checked.png")
        self.error_icon_path = str(get_assets_path() / "images" / "warning.png")
        self.init_ui()

    def init_ui(self):
        # Carrega a imagem original
        pixmap = QPixmap(self.background_image_path)

        # Criando um novo pixmap com transparência
        transparent_pixmap = QPixmap(pixmap.size())
        transparent_pixmap.fill(Qt.GlobalColor.transparent)

        # Aplicando a opacidade na imagem
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(
            0.2
        )  # Ajuste a opacidade aqui (1.0 = sem transparência, 0.0 = totalmente transparente)
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
        
        # Adicionando o ComboBox para seleção do tipo de operação
        self.operation_label = QLabel("Tipo de Operação:")
        self.operation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operation_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.operation_label.setStyleSheet("""color: #444;""")

        self.operation_combo = QComboBox()
        self.operation_combo.addItem("Consulta", CommandType.CONSULT)
        self.operation_combo.addItem("Validação", CommandType.VALIDATION)
        self.operation_combo.setFixedHeight(50)
        self.operation_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 10px;
                border: 2px solid #bbb;
                border-radius: 10px;
                background-color: white;
            }

            QComboBox:focus {
                border: 2px solid #007BFF;
                background-color: #F0F8FF;
                outline: none;
            }

            QComboBox:hover {
                border: 2px solid #0056b3;
            }
        """)

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
        self.button.clicked.connect(self.process_ticket)
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
        main_layout.addSpacerItem(
            QSpacerItem(
                20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )
        
        main_layout.addWidget(self.operation_label)
        main_layout.addWidget(self.operation_combo)
        main_layout.addSpacerItem(
            QSpacerItem(
                20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.edit)
        main_layout.addWidget(self.button)
        main_layout.addSpacerItem(
            QSpacerItem(
                20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )
        main_layout.addWidget(self.footer_label)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """Redimensiona a imagem de fundo quando a janela for redimensionada"""
        self.background_label.resize(self.size())

    @Slot()
    def process_ticket(self):
        """Processa o ticket conforme a operação selecionada (consulta ou validação)"""
        try:
            logger.debug("Iniciando processamento de ticket")
            ticket_code = self.edit.text().strip()
            operation_type = self.operation_combo.currentData()
            logger.debug(f"Ticket recebido: {ticket_code}")
            logger.debug(f"Tipo de operação: {operation_type}")

            if not ticket_code:
                logger.warning("Ticket vazio recebido")
                error_box = CustomMessageBox(
                    "Erro",
                    "Código inválido!\nPor favor, verifique o código e tente novamente.\n",
                    self.error_icon_path,
                    self,
                )
                error_box.exec()
                return

            logger.debug("Consultando último pedido PDV")
            pdv_pedido = get_last_pdv_pedido()
            
            if not pdv_pedido:
                logger.error("Nenhum pedido PDV encontrado")
                error_box = CustomMessageBox(
                    "Erro",
                    "Não foi possível encontrar o ticket do cliente.\nPor favor, verifique o código e tente novamente.\n",
                    self.error_icon_path,
                    self
                )
                error_box.exec()
                return

            logger.debug("Criando requisição")
            discount_request = DiscountRequest(
                cmd_card_id=ticket_code,
                cmd_term_id=pdv_pedido.num_caixa,
                cmd_op_value=int(pdv_pedido.vl_total*100),
                cmd_type=operation_type,
            )
            
            logger.debug("Criando instancia do servico de integração com a estapar")
            service = EstaparIntegrationService(IP, PORT)

            logger.debug("Enviando requisição para API")
            result = service.create_discount(discount_request)
            logger.debug(f"Resposta da API: {result}")
            if result.success:
                success_title = "Validação Realizada"
                msg = f"Operação realizada com sucesso!\nEstapar API response: {result.message}"
                if result.data:
                    msg += f"\n\nDetalhes da resposta: {result.data}"
                logger.success(msg)
                success_box = CustomMessageBox(
                    success_title,
                    msg,
                    self.success_icon_path,
                    self,
                )
                success_box.exec()
                if operation_type == CommandType.VALIDATION:
                    self.edit.clear()
            else:
                logger.error(f"Erro na API: {result.message}")
                error_box = CustomMessageBox(
                    "Erro",
                    f"Operação não realizada!\nEstapar API response: {result.message}",
                    self.error_icon_path,
                    self,
                )
                error_box.exec()

        except Exception as e:
            logger.critical(f"Erro inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_box = CustomMessageBox(
                "Erro Crítico",
                f"Ocorreu um erro inesperado:\n{str(e)}\n\nVerifique os logs para mais detalhes.",
                self.error_icon_path,
                self,
            )
            error_box.exec()
