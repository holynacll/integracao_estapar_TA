# gui.py
from datetime import datetime

from loguru import logger
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect, # Importar QGraphicsOpacityEffect
    QDoubleSpinBox,  # Para o campo de valor
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QPalette, QColor # Importar QColor

from totalatacadot1.enums import CommandType
from totalatacadot1.estapar_integration_service import EstaparIntegrationService
from totalatacadot1.custom_message_box import CustomMessageBox
from totalatacadot1.repository import get_last_pdv_pedido
from totalatacadot1.schemas import DiscountRequest

from .config import get_assets_path

# load_dotenv()

# Estapar API
IP = "10.7.39.10"
PORT = 3000


def is_dark_theme():
    """Verifica se o tema atual da aplicação Qt é considerado escuro."""
    try:
        # Tenta obter a paleta da aplicação. Pode falhar se QApplication não existir ainda.
        app_instance = QApplication.instance()
        if not app_instance:
             # Se a aplicação ainda não foi criada, tente usar a paleta padrão do estilo
             # Pode não ser 100% preciso antes da app rodar, mas é uma tentativa.
             # Ou podemos assumir um padrão (ex: light) se a app não existe.
             # Para simplificar, vamos assumir light se não houver app.instance()
            logger.warning("QApplication instance not found for theme detection. Assuming light theme.")
            return False

        palette = app_instance.palette()
        # Compara o brilho da cor de fundo da janela com um limiar
        # O valor 128 é um ponto médio comum (0=preto, 255=branco)
        window_color = palette.color(QPalette.ColorRole.Window)
        # Usar QColor para obter HSL lightness
        return QColor(window_color).lightnessF() < 0.5 # Usar lightnessF() que retorna 0.0 a 1.0
    except Exception as e:
        logger.error(f"Error detecting theme: {e}. Assuming light theme.")
        return False # Assume light theme em caso de erro

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Total Atacado")
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
    
    @Slot(float)
    def update_actual_valor(self, valor):
        """Atualiza especificamente o actual_valor na interface."""
        self.main_widget.actual_valor.setValue(valor)
        # self.actual_valor.setValue(valor)
        # self.valor_label.setText(f"Valor Atual: R$ {valor:.2f}")
        print(f"Actual valor atualizado: {valor}")

    def closeEvent(self, event):
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

        # Determina o tema ANTES de iniciar a UI para que os estilos base sejam aplicados
        self._dark_theme_active = is_dark_theme()
        logger.info(f"Theme detected: {'Dark' if self._dark_theme_active else 'Light'}")

        self.init_ui()
        self.apply_dynamic_styles() # Aplica os estilos após a criação dos widgets

    # Substitua seu método init_ui() por este:

    def init_ui(self):
        # --- Background Setup ---
        self.background_label = QLabel(self)
        pixmap = QPixmap(self.background_image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.background_label.setGraphicsEffect(self.opacity_effect)
        self.background_label.lower()

        # --- Layout Principal (fullscreen) ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- Container Central ---
        self.container = QWidget()
        self.container.setObjectName("formContainer")
        self.container.setFixedWidth(600)  # Largura fixa do formulário
        self.container.setMaximumHeight(700)  # Altura máxima para não ficar muito alto
        
        # Layout do container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(40, 30, 40, 30)
        container_layout.setSpacing(15)

        # --- Widgets (mesmo conteúdo, diferente organização) ---
        self.title = QLabel("Integração Estacionamento")
        self.title.setObjectName("Total Atacado - Integração Estacionamento")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 28, QFont.Weight.Bold))  # Menor para caber melhor

        self.operation_label = QLabel("Tipo de Operação:")
        self.operation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operation_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.operation_combo = QComboBox()
        self.operation_combo.addItem("Validação Automática", CommandType.VALIDATION)
        # self.operation_combo.addItem("Consulta", CommandType.CONSULT)
        self.operation_combo.addItem("Validação Manual", "MANUAL_VALIDATION")
        self.operation_combo.setFixedHeight(40)
        self.operation_combo.setFont(QFont("Arial", 12))
        self.operation_combo.currentTextChanged.connect(self.on_operation_changed)

        self.label = QLabel("Ticket do Cliente:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Escreva o código aqui")
        self.edit.setFixedHeight(40)
        self.edit.setFont(QFont("Arial", 12))
        self.edit.returnPressed.connect(self.trigger_button_click)
        
        self.automatic_fields_frame = QFrame()
        automatic_fields_layout = QVBoxLayout(self.automatic_fields_frame)
        automatic_fields_layout.setSpacing(15)
        automatic_fields_layout.setContentsMargins(0, 0, 0, 0)

        self.actual_valor_label = QLabel("Valor Total (R$):")
        self.actual_valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.actual_valor_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.actual_valor_label.setContentsMargins(0, 15, 0, 0)
        
        self.actual_valor = QDoubleSpinBox()
        self.actual_valor.setReadOnly(True)
        self.actual_valor.setRange(0.01, 999999.99)
        self.actual_valor.setDecimals(2)
        self.actual_valor.setPrefix("R$ ")
        self.actual_valor.setFixedHeight(40)
        self.actual_valor.setFont(QFont("Arial", 12))
        self.actual_valor.lineEdit().returnPressed.connect(self.trigger_button_click)
        
        automatic_fields_layout.addWidget(self.actual_valor_label)
        automatic_fields_layout.addWidget(self.actual_valor)

        # --- Campos manuais ---
        self.manual_fields_frame = QFrame()
        manual_fields_layout = QVBoxLayout(self.manual_fields_frame)
        manual_fields_layout.setSpacing(15)
        manual_fields_layout.setContentsMargins(0, 0, 0, 0)

        self.num_cupom = QLabel("Número do Cupom:")
        self.num_cupom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.num_cupom.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.num_cupom.setContentsMargins(0, 15, 0, 0)

        self.num_cupom_edit = QLineEdit()
        self.num_cupom_edit.setPlaceholderText("Digite o número do cupom")
        self.num_cupom_edit.setFixedHeight(40)
        self.num_cupom_edit.setFont(QFont("Arial", 12))
        self.num_cupom_edit.returnPressed.connect(self.trigger_button_click)

        self.valor_label = QLabel("Valor Total (R$):")
        self.valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valor_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.valor_label.setContentsMargins(0, 15, 0, 0)
        
        self.valor_edit = QDoubleSpinBox()
        self.valor_edit.setRange(0.01, 999999.99)
        self.valor_edit.setDecimals(2)
        self.valor_edit.setPrefix("R$ ")
        self.valor_edit.setFixedHeight(40)
        self.valor_edit.setFont(QFont("Arial", 12))
        self.valor_edit.lineEdit().returnPressed.connect(self.trigger_button_click)

        manual_fields_layout.addWidget(self.num_cupom)
        manual_fields_layout.addWidget(self.num_cupom_edit)
        manual_fields_layout.addWidget(self.valor_label)
        manual_fields_layout.addWidget(self.valor_edit)
        self.manual_fields_frame.hide()

        self.button = QPushButton("Processar")
        self.button.setFixedHeight(50)
        self.button.clicked.connect(self.process_ticket)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.button.pressed.connect(self.process_ticket)

        self.footer_label = QLabel(f"© {datetime.now().year} Total Atacado")
        self.footer_label.setObjectName("footerLabel")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setFont(QFont("Arial", 10, QFont.Weight.DemiBold))

        # --- Montagem do Container ---
        container_layout.addWidget(self.title)
        container_layout.addSpacing(20)
        container_layout.addWidget(self.operation_label)
        container_layout.addWidget(self.operation_combo)
        container_layout.addSpacing(15)
        container_layout.addWidget(self.label)
        container_layout.addWidget(self.edit)
        container_layout.addWidget(self.automatic_fields_frame)
        container_layout.addWidget(self.manual_fields_frame)
        container_layout.addSpacing(15)
        container_layout.addWidget(self.button)
        container_layout.addStretch()  # Empurra o footer para baixo
        container_layout.addWidget(self.footer_label)

        # --- Adicionar container ao layout principal ---
        main_layout.addWidget(self.container)

    # Adicione também estilos para o container no apply_dynamic_styles():
    def apply_dynamic_styles(self):
        """Aplica estilos aos widgets com base no tema detectado."""
        dark = self._dark_theme_active

        # Suas cores existentes...
        text_color = "#E0E0E0" if dark else "#222222"
        secondary_text = "#B0B0B0" if dark else "#555555"
        footer_text = "#909090" if dark else "#666666"
        input_bg = "#3C3C3C" if dark else "#FFFFFF"
        input_text = "#F0F0F0" if dark else "#111111"
        border_color = "#555555" if dark else "#BBBBBB"
        border_focus_color = "#4A9CFF"
        button_bg_start = "#4A9CFF" if dark else "#007BFF"
        button_bg_end = "#1B6CD3" if dark else "#0056b3"
        button_hover_start = "#5AAFFF" if dark else "#0056b3"
        button_hover_end = "#2C7CEF" if dark else "#003d80"
        button_text = "#FFFFFF"
        
        # Cores para campos readonly
        readonly_bg = "#2A2A2A" if dark else "#F5F5F5"
        readonly_text = "#808080" if dark else "#666666"
        readonly_border = "#444444" if dark else "#CCCCCC"
        
        # Cor do container
        container_bg = "rgba(40, 40, 40, 0.8)" if dark else "rgba(255, 255, 255, 0.9)"
        container_border = "rgba(100, 100, 100, 0.3)" if dark else "rgba(200, 200, 200, 0.5)"

        self.opacity_effect.setOpacity(0.4 if dark else 0.2)

        style_sheet = f"""
            QWidget#formContainer {{
                background-color: {container_bg};
                border: 1px solid {container_border};
                border-radius: 15px;
            }}

            QWidget {{
                color: {secondary_text};
            }}

            QLabel#titleLabel {{
                color: {text_color};
            }}

            QLabel#footerLabel {{
                color: {footer_text};
            }}

            QLineEdit {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {border_focus_color};
            }}
            QLineEdit:hover {{
                border: 1px solid {border_focus_color};
            }}

            QComboBox {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border: 1.5px solid {border_focus_color};
            }}
            QComboBox:hover {{
                border: 1px solid {border_focus_color};
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {border_color};
                selection-background-color: {border_focus_color};
                selection-color: {button_text};
            }}

            QDoubleSpinBox {{
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }}
            QDoubleSpinBox:focus {{
                border: 1.5px solid {border_focus_color};
            }}
            QDoubleSpinBox:hover {{
                border: 1px solid {border_focus_color};
            }}
            
            /* Estilo específico para QDoubleSpinBox readonly */
            QDoubleSpinBox:read-only {{
                background-color: {readonly_bg};
                color: {readonly_text};
                border: 1px solid {readonly_border};
            }}
            QDoubleSpinBox:read-only:hover {{
                border: 1px solid {readonly_border};
            }}
            QDoubleSpinBox:read-only:focus {{
                border: 1px solid {readonly_border};
            }}

            QPushButton {{
                font-size: 14px;
                font-weight: bold;
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 {button_bg_start},
                    stop:1 {button_bg_end}
                );
                color: {button_text};
                border-radius: 8px;
                padding: 12px;
                border: none;
                outline: none;
            }}

            QPushButton:hover {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 {button_hover_start},
                    stop:1 {button_hover_end}
                );
            }}

            QPushButton:pressed {{
                background-color: {button_hover_end};
            }}

            QPushButton:focus {{
                border: 1.5px solid {border_focus_color};
                padding: 10.5px;
            }}
        """
        self.setStyleSheet(style_sheet)
    
    @Slot()
    def on_operation_changed(self):
        """Mostra/oculta campos baseado na operação selecionada."""
        operation_type = self.operation_combo.currentData()
        
        if operation_type == "MANUAL_VALIDATION":
            self.manual_fields_frame.show()
            self.automatic_fields_frame.hide()
            # Ajustar o texto do label principal
            self.label.setText("Ticket do Cliente:")
        else:
            self.manual_fields_frame.hide()
            self.automatic_fields_frame.show()
            self.label.setText("Ticket do Cliente:")
        
        # Forçar o layout a se recalcular
        self.updateGeometry()

    def resizeEvent(self, event):
        """Redimensiona a imagem de fundo quando a janela for redimensionada."""
        # Move e redimensiona o label de fundo para cobrir todo o widget
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event) # Chama o método da classe pai

    def trigger_button_click(self):
        """Aciona o clique visual no botão."""
        self.button.animateClick()

    @Slot()
    def process_ticket(self):
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

            # Lógica específica para Validação Manual
            if operation_type == "MANUAL_VALIDATION":
                # Validar campos manuais
                num_cupom = self.num_cupom_edit.text().strip()
                valor_total = self.valor_edit.value()

                if not num_cupom or not valor_total:
                    error_box = CustomMessageBox(
                        "Erro",
                        "Por favor, preencha todos os campos obrigatórios para Validação Manual.",
                        self.error_icon_path,
                        self,
                    )
                    error_box.exec()
                    return
            
                if not num_cupom.isdigit():
                    error_box = CustomMessageBox(
                        "Erro",
                        "O número do cupom deve ser um número inteiro.",
                        self.error_icon_path,
                        self,
                    )
                    error_box.exec()
                    return

                logger.debug(f"Validação Manual - Número do Cupom: {num_cupom}, Valor: {valor_total}")

                # Criar requisição com dados manuais
                discount_request = DiscountRequest(
                    cmd_card_id=ticket_code,
                    cmd_term_id=int(num_cupom),  # Usando número do cupom como terminal
                    cmd_op_value=valor_total,
                    cmd_type=CommandType.VALIDATION,  # Pode ajustar conforme necessário
                )

            else:
                # Lógica original para Validação e Consulta automáticas
                logger.debug("Consultando último pedido PDV")
                pdv_pedido = get_last_pdv_pedido()

                if not pdv_pedido:
                    logger.error("Nenhum pedido PDV encontrado")
                    error_box = CustomMessageBox(
                        "Erro",
                        "Não foi possível encontrar o ticket do cliente.\nPor favor, verifique o código e tente novamente.\n",
                        self.error_icon_path,
                        self,
                    )
                    error_box.exec()
                    return

                logger.debug("Criando requisição")
                discount_request = DiscountRequest(
                    cmd_card_id=ticket_code,
                    cmd_term_id=pdv_pedido.num_ped_ecf, # Num cupom
                    cmd_op_value=pdv_pedido.vl_total,
                    cmd_type=operation_type,
                )

            # Validando se o ticket é válido
            try:
                discount_request.validate()  # 👈 Valida os campos
            except ValueError as e:
                logger.error(f"Erro de validação: {e}")
                error_box = CustomMessageBox(
                    "Erro de Validação",
                    f"Dados inválidos:\n{str(e)}",
                    self.error_icon_path,
                    self,
                )
                error_box.exec()
                return  # Interrompe o processamento

            logger.debug("Criando instancia do servico de integração com a estapar")
            service = EstaparIntegrationService(IP, PORT)

            logger.debug("Enviando requisição para API")
            result = service.create_discount(discount_request)
            logger.debug(f"Resposta da API: {result}")
            
            if result.success:
                if operation_type == "MANUAL_VALIDATION":
                    success_title = "Validação Manual Realizada"
                elif operation_type == CommandType.CONSULT:
                    success_title = "Consulta Realizada"
                else:
                    success_title = "Validação Realizada"
                    
                msg = f"Operação realizada com sucesso!\nAPI Estapar: {result.message}"

                logger.success(msg)
                success_box = CustomMessageBox(
                    success_title,
                    msg,
                    self.success_icon_path,
                    self,
                )
                success_box.exec()
                # MINIMIZAR COM DELAY DE 2 SEGUNDO
                QTimer.singleShot(2000, self.window().showMinimized)
                
                # Limpar campos após sucesso
                if operation_type in [CommandType.VALIDATION, "MANUAL_VALIDATION"]:
                    self.edit.clear()
                    if operation_type == "MANUAL_VALIDATION":
                        self.num_cupom_edit.clear()
                        # self.valor_edit.setValue(0.01)
            else:
                logger.error(f"Erro na API: {result.message}")
                error_box = CustomMessageBox(
                    "Erro",
                    f"Operação não realizada!\nAPI Estapar: {result.message}",
                    self.error_icon_path,
                    self,
                )
                error_box.exec()

        except Exception as e:
            logger.critical(f"Erro inesperado: {str(e)}")
            import traceback
            traceback.print_exc() # Imprime o stack trace completo no console/log

            error_box = CustomMessageBox(
                "Erro Crítico",
                f"Ocorreu um erro inesperado:\n{str(e)}\n\nVerifique os logs para mais detalhes.",
                self.error_icon_path,
                self,
            )
            error_box.exec()


# # Bloco principal para execução (se este for o script principal)
# if __name__ == "__main__":
#     # Configuração básica do logger (opcional, mas útil)
#     log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
#     logger.add("app.log", rotation="10 MB", level="DEBUG", format=log_format) # Log em arquivo
#     logger.add(sys.stderr, level="INFO", format=log_format) # Log no console

#     logger.info("Iniciando aplicação...")
#     app = QApplication(sys.argv)

#     # Tentar definir um estilo base que pode ajudar na integração com o tema do SO
#     # app.setStyle("Fusion") # Fusion geralmente funciona bem em diferentes plataformas

#     main_window = MainWindow()
#     main_window.show()
#     logger.info("Aplicação iniciada.")
#     sys.exit(app.exec())