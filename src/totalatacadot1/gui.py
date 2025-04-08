# gui.py
from datetime import datetime

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
    QGraphicsOpacityEffect, # Importar QGraphicsOpacityEffect
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QBrush, QPalette, QColor # Importar QColor
# from qt_material import apply_stylesheet # Manter comentado por enquanto
# from dotenv import load_dotenv

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

    def init_ui(self):
        # --- Background Setup ---
        self.background_label = QLabel(self)
        pixmap = QPixmap(self.background_image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        # Cria o efeito de opacidade (será configurado em apply_dynamic_styles)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.background_label.setGraphicsEffect(self.opacity_effect)
        # Garante que o label de fundo fique atrás dos outros widgets
        self.background_label.lower()

        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50) # Adiciona margens
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Widgets ---
        self.title = QLabel("Integração Estacionamento")
        self.title.setObjectName("titleLabel") # Definir nome para estilo específico se necessário
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 36, QFont.Weight.Bold))

        self.operation_label = QLabel("Tipo de Operação:")
        self.operation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operation_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        self.operation_combo = QComboBox()
        self.operation_combo.addItem("Validação", CommandType.VALIDATION)
        self.operation_combo.addItem("Consulta", CommandType.CONSULT)
        self.operation_combo.setFixedHeight(50)
        self.operation_combo.setFont(QFont("Arial", 14)) # Definir fonte base

        self.label = QLabel("Ticket do Cliente:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Escreva o código aqui")
        self.edit.setFixedHeight(50)
        self.edit.setFont(QFont("Arial", 14)) # Definir fonte base

        self.button = QPushButton("Processar")
        self.button.setFixedHeight(50)
        self.button.clicked.connect(self.process_ticket)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setFont(QFont("Arial", 14, QFont.Weight.Bold)) # Definir fonte base

        self.footer_label = QLabel(f"© {datetime.now().year} Total Atacado")
        self.footer_label.setObjectName("footerLabel")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setFont(QFont("Arial", 12, QFont.Weight.DemiBold))

        # --- Adicionando Widgets ao Layout ---
        main_layout.addWidget(self.title)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(self.operation_label)
        main_layout.addWidget(self.operation_combo)
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)) # Espaço menor
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.edit)
        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)) # Espaço menor
        main_layout.addWidget(self.button)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(self.footer_label)

        # Não precisa mais de self.setLayout(main_layout), pois foi passado no construtor do QVBoxLayout

    def apply_dynamic_styles(self):
        """Aplica estilos aos widgets com base no tema detectado."""
        dark = self._dark_theme_active

        # --- Definição das Cores ---
        text_color = "#E0E0E0" if dark else "#222222" # Texto principal (claro no escuro, escuro no claro)
        secondary_text = "#B0B0B0" if dark else "#555555" # Texto secundário/labels
        footer_text = "#909090" if dark else "#666666" # Texto do rodapé
        background_color = "#2E2E2E" if dark else "#F0F0F0" # Cor de fundo geral do widget (se necessário)
        input_bg = "#3C3C3C" if dark else "#FFFFFF"
        input_text = "#F0F0F0" if dark else "#111111"
        border_color = "#555555" if dark else "#BBBBBB"
        border_focus_color = "#4A9CFF" # Azul vibrante para foco (funciona em ambos)
        button_bg_start = "#4A9CFF" if dark else "#007BFF" # Gradiente do botão
        button_bg_end = "#1B6CD3" if dark else "#0056b3"
        button_hover_start = "#5AAFFF" if dark else "#0056b3" # Hover um pouco mais claro/diferente
        button_hover_end = "#2C7CEF" if dark else "#003d80"
        button_text = "#FFFFFF" # Texto do botão sempre branco

        # Aplica a cor de fundo ao widget principal
        # self.setStyleSheet(f"QWidget {{ background-color: {background_color}; }}")
        # Ou, para manter a imagem de fundo, ajustamos apenas a opacidade dela:
        self.opacity_effect.setOpacity(0.3 if dark else 0.15) # Ajuste a opacidade conforme necessário

        # --- Estilos CSS ---
        # Nota: Usar f-strings dentro de stylesheets pode ser confuso com as chaves {}.
        # É mais seguro formatar as cores antes.
        style_sheet = f"""
            QWidget {{
                /* background-color: {background_color}; Sem isso para ver a imagem */
                color: {secondary_text}; /* Cor de texto padrão para labels */
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
                /* background-color: ligeiramente diferente no foco? opcional */
            }}
            QLineEdit:hover {{
                 border: 1px solid {border_focus_color}; /* Ou uma cor de hover específica */
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
            QComboBox::drop-down {{ /* Estilizar a seta */
                border: none;
                background-color: transparent;
                /* subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px; */
            }}
            QComboBox::down-arrow {{
                 /* Idealmente usar um ícone SVG aqui que possa ter a cor trocada */
                 /* image: url(:/icons/down_arrow_{'dark' if dark else 'light'}.svg); */
                 /* Se não tiver ícone, a seta padrão do sistema será usada */
            }}
            QComboBox QAbstractItemView {{ /* Estilo do dropdown menu */
                background-color: {input_bg};
                color: {input_text};
                border: 1px solid {border_color};
                selection-background-color: {border_focus_color};
                selection-color: {button_text}; /* Texto do item selecionado */
            }}

            QPushButton {{
                font-size: 14px; /* Reduzido para consistência */
                font-weight: bold;
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0, /* Gradiente Horizontal */
                    stop:0 {button_bg_start},
                    stop:1 {button_bg_end}
                );
                color: {button_text};
                border-radius: 8px;
                padding: 12px;
                border: none;
                outline: none; /* Remove outline pontilhado no foco */
            }}

            QPushButton:hover {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 {button_hover_start},
                    stop:1 {button_hover_end}
                );
            }}

            QPushButton:pressed {{
                background-color: {button_hover_end}; /* Cor sólida ao pressionar */
            }}

            QPushButton:focus {{ /* Adiciona um indicador de foco sutil */
                 border: 1.5px solid {border_focus_color};
                 /* Padding precisa ser ajustado para compensar a borda */
                 padding: 10.5px;
            }}

        """
        self.setStyleSheet(style_sheet)

    def resizeEvent(self, event):
        """Redimensiona a imagem de fundo quando a janela for redimensionada."""
        # Move e redimensiona o label de fundo para cobrir todo o widget
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event) # Chama o método da classe pai

    @Slot()
    def process_ticket(self):
        # ... (seu código de processamento de ticket permanece o mesmo) ...
        try:
            logger.debug("Iniciando processamento de ticket")
            ticket_code = self.edit.text().strip()
            operation_type = self.operation_combo.currentData()
            logger.debug(f"Ticket recebido: {ticket_code}")
            logger.debug(f"Tipo de operação: {operation_type}")

            if not ticket_code:
                logger.warning("Ticket vazio recebido")
                # Usar CustomMessageBox (assumindo que ele também respeita o tema ou é neutro)
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
                    self,
                )
                error_box.exec()
                return

            logger.debug("Criando requisição")
            discount_request = DiscountRequest(
                cmd_card_id=ticket_code,
                cmd_term_id=pdv_pedido.num_caixa,
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
                success_title = "Consulta Realizada" if operation_type == CommandType.CONSULT else "Validação Realizada"
                msg = f"Operação realizada com sucesso!\nAPI Estapar: {result.message}"
                # if result.data:
                #     try:
                #         # Chama o __str__ da instância DiscountResponse para obter os detalhes formatados
                #         details_str = str(result.data) 
                        
                #         # Adiciona os detalhes formatados à mensagem principal (se não for vazio)
                #         if details_str: 
                #             msg += f"\n\n{details_str}" 
                            
                #     except Exception as e:
                #         logger.warning(f"Erro ao formatar detalhes da resposta via __str__: {e}")

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