# src/totalatacadot1/gui/styles.py

def get_stylesheet(dark: bool) -> str:
    """Gera a folha de estilo para a aplicação com base no tema."""
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

    readonly_bg = "#2A2A2A" if dark else "#F5F5F5"
    readonly_text = "#808080" if dark else "#666666"
    readonly_border = "#444444" if dark else "#CCCCCC"

    container_bg = "rgba(40, 40, 40, 0.8)" if dark else "rgba(255, 255, 255, 0.9)"
    container_border = "rgba(100, 100, 100, 0.3)" if dark else "rgba(200, 200, 200, 0.5)"

    return f"""
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

        QLineEdit, QComboBox, QSpinBox {{
            background-color: {input_bg};
            color: {input_text};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1.5px solid {border_focus_color};
        }}

        QLineEdit:hover, QComboBox:hover, QSpinBox:hover {{
            border: 1px solid {border_focus_color};
        }}

        QComboBox QAbstractItemView {{
            background-color: {input_bg};
            color: {input_text};
            border: 1px solid {border_color};
            selection-background-color: {border_focus_color};
            selection-color: {button_text};
        }}

        QSpinBox {{
            padding: 8px;
        }}

        QSpinBox:read-only {{
            background-color: {readonly_bg};
            color: {readonly_text};
            border: 1px solid {readonly_border};
        }}

        QSpinBox:read-only:hover, QSpinBox:read-only:focus {{
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
