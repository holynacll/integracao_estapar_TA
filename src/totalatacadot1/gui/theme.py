# src/totalatacadot1/gui/theme.py
from loguru import logger
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPalette, QColor

def is_dark_theme():
    """Verifica se o tema atual da aplicação Qt é considerado escuro."""
    try:
        app_instance = QApplication.instance()
        if not app_instance:
            logger.warning("QApplication instance not found for theme detection. Assuming light theme.")
            return False

        # Create a temporary widget to get the palette if QApplication doesn't have one directly
        temp_widget = QWidget()
        window_color = temp_widget.palette().color(QPalette.ColorRole.Window)
        return QColor(window_color).lightnessF() < 0.5
    except Exception as e:
        logger.error(f"Error detecting theme: {e}. Assuming light theme.")
        return False
