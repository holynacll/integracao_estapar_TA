# src/totalatacadot1/gui/main_widget.py
from datetime import datetime

from loguru import logger
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QSpinBox,
)
from PySide6.QtGui import QFont, QPixmap

from ..enums import CommandType
from ..config import get_assets_path
from .styles import get_stylesheet
from .theme import is_dark_theme

class MainWidget(QWidget):
    # Sinal emitido com os dados do formulário quando o botão de processar é clicado
    process_request = Signal(dict)

    def __init__(self):
        super().__init__()
        self.background_image_path = str(
            get_assets_path() / "images" / "background-2.jpg"
        )
        self.success_icon_path = str(get_assets_path() / "images" / "checked.png")
        self.error_icon_path = str(get_assets_path() / "images" / "warning.png")

        self._dark_theme_active = is_dark_theme()
        logger.info(f"Theme detected: {'Dark' if self._dark_theme_active else 'Light'}")

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # --- Background Setup ---
        self.background_label = QLabel(self)
        pixmap = QPixmap(self.background_image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.background_label.setGraphicsEffect(self.opacity_effect)
        self.background_label.lower()

        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Container Central ---
        self.container = QWidget()
        self.container.setObjectName("formContainer")
        self.container.setFixedWidth(600)
        self.container.setMaximumHeight(600)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(40, 30, 40, 30)
        container_layout.setSpacing(10)

        # --- Widgets ---
        self.operation_label = QLabel("Tipo de Operação:")
        self.operation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.operation_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.operation_combo = QComboBox()
        self.operation_combo.addItem("Validação Automática", CommandType.VALIDATION)
        self.operation_combo.addItem("Validação Manual", "MANUAL_VALIDATION")
        self.operation_combo.setFixedHeight(40)
        self.operation_combo.setFont(QFont("Arial", 10))
        self.operation_combo.currentTextChanged.connect(self.on_operation_changed)

        self.label = QLabel("Ticket do Cliente:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Escreva o código aqui")
        self.edit.setFixedHeight(40)
        self.edit.setFont(QFont("Arial", 10))
        self.edit.returnPressed.connect(self._on_edit_return_pressed)

        # --- Campos Automáticos ---
        self.automatic_fields_frame = QFrame()
        automatic_fields_layout = QVBoxLayout(self.automatic_fields_frame)
        automatic_fields_layout.setSpacing(10)
        automatic_fields_layout.setContentsMargins(0, 0, 0, 0)

        self.actual_valor_label = QLabel("Valor Total (R$):")
        self.actual_valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.actual_valor_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.actual_valor_label.setContentsMargins(0, 10, 0, 0)

        self.actual_valor = QSpinBox()
        self.actual_valor.setReadOnly(True)
        self.actual_valor.setRange(0, 99999999)
        self.actual_valor.setPrefix("R$ ")
        self.actual_valor.setFixedHeight(40)
        self.actual_valor.setFont(QFont("Arial", 10))
        self.actual_valor.lineEdit().returnPressed.connect(self.trigger_button_click)

        automatic_fields_layout.addWidget(self.actual_valor_label)
        automatic_fields_layout.addWidget(self.actual_valor)

        # --- Campos Manuais ---
        self.manual_fields_frame = QFrame()
        manual_fields_layout = QVBoxLayout(self.manual_fields_frame)
        manual_fields_layout.setSpacing(10)
        manual_fields_layout.setContentsMargins(0, 0, 0, 0)

        self.num_cupom = QLabel("Número do Cupom:")
        self.num_cupom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.num_cupom.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.num_cupom.setContentsMargins(0, 10, 0, 0)

        self.num_cupom_edit = QLineEdit()
        self.num_cupom_edit.setPlaceholderText("Digite o número do cupom")
        self.num_cupom_edit.setFixedHeight(40)
        self.num_cupom_edit.setFont(QFont("Arial", 10))
        self.num_cupom_edit.returnPressed.connect(lambda: self.valor_edit.setFocus())

        self.valor_label = QLabel("Valor Total (R$):")
        self.valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valor_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.valor_label.setContentsMargins(0, 15, 0, 0)

        self.valor_edit = QSpinBox()
        self.valor_edit.setRange(0, 99999999)
        self.valor_edit.setPrefix("R$ ")
        self.valor_edit.setFixedHeight(40)
        self.valor_edit.setFont(QFont("Arial", 10))
        self.valor_edit.lineEdit().returnPressed.connect(self.trigger_button_click)

        manual_fields_layout.addWidget(self.num_cupom)
        manual_fields_layout.addWidget(self.num_cupom_edit)
        manual_fields_layout.addWidget(self.valor_label)
        manual_fields_layout.addWidget(self.valor_edit)
        self.manual_fields_frame.hide()

        self.button = QPushButton("Processar")
        self.button.setFixedHeight(50)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.button.clicked.connect(self.on_process_clicked)

        self.footer_label = QLabel(f"© {datetime.now().year} Total Atacado")
        self.footer_label.setObjectName("footerLabel")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setFont(QFont("Arial", 8, QFont.Weight.DemiBold))

        # --- Montagem do Container ---
        container_layout.addWidget(self.operation_label)
        container_layout.addWidget(self.operation_combo)
        container_layout.addSpacing(10)
        container_layout.addWidget(self.label)
        container_layout.addWidget(self.edit)
        container_layout.addWidget(self.automatic_fields_frame)
        container_layout.addWidget(self.manual_fields_frame)
        container_layout.addSpacing(10)
        container_layout.addWidget(self.button)
        container_layout.addWidget(self.footer_label)

        main_layout.addWidget(self.container)

    def apply_styles(self):
        """Aplica estilos dinâmicos ao widget."""
        self.opacity_effect.setOpacity(0.4 if self._dark_theme_active else 0.2)
        self.setStyleSheet(get_stylesheet(self._dark_theme_active))

    @Slot()
    def on_operation_changed(self):
        """Alterna a visibilidade dos campos com base na operação selecionada."""
        if self._is_manual_validation():
            self.manual_fields_frame.show()
            self.automatic_fields_frame.hide()
        else:
            self.manual_fields_frame.hide()
            self.automatic_fields_frame.show()
        self.updateGeometry()

    def _is_manual_validation(self):
        return self.operation_combo.currentData() == "MANUAL_VALIDATION"

    def _on_edit_return_pressed(self):
        if self._is_manual_validation():
            self.num_cupom_edit.setFocus()
        else:
            self.trigger_button_click()

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def trigger_button_click(self):
        self.button.animateClick()

    @Slot()
    def on_process_clicked(self):
        """Coleta os dados do formulário e emite um sinal para o controlador."""
        form_data = {
            "ticket_code": self.edit.text().strip(),
            "operation_type": self.operation_combo.currentData(),
            "num_cupom": self.num_cupom_edit.text().strip(),
            "valor_total": self.valor_edit.value(),
            "parent_widget": self
        }
        self.process_request.emit(form_data)

    def clear_inputs(self, all_fields=False):
        """Limpa os campos de entrada."""
        self.edit.clear()
        if all_fields:
            self.num_cupom_edit.clear()
            self.valor_edit.setValue(0)