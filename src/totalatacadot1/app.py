import sys
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Slot
from PySide6.QtWidgets import (
    QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QMainWindow, QLineEdit, QMessageBox
)
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Total Atacado T1")
        # add icon ico file here
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(100, 100, 600, 400)

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.label = QLabel("Código do Ticket:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Escreva o código do ticket aqui")
        self.edit.setFixedHeight(40)
        self.edit.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #888;
                border-radius: 8px;
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

            QLineEdit:disabled {
                background-color: #E0E0E0;
                color: #888;
            }
        """)


        self.button = QPushButton("Salvar")
        self.button.setFixedHeight(40)
        self.button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #007BFF;
                color: white;
                border-radius: 8px;
                padding: 10px;
                border: none;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #003d80;
            }
        """)

        # Conectar botão às funções
        self.button.clicked.connect(self.save_code)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.setLayout(layout)

    @Slot()
    def animate_border(self, widget, color):
        """Cria animação suave para mudar a borda do campo"""
        animation = QPropertyAnimation(widget, b"styleSheet")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        animation.setStartValue(widget.styleSheet())
        animation.setEndValue(f"""
            font-size: 14px;
            padding: 5px;
            border: 2px solid {color};
            border-radius: 8px;
        """)
        animation.start()

    @Slot()
    def animate_error(self):
        """Anima o campo de entrada para indicar erro"""
        animation = QPropertyAnimation(self.edit, b"styleSheet")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        animation.setStartValue(self.edit.styleSheet())
        animation.setEndValue("""
            font-size: 14px;
            padding: 5px;
            border: 2px solid red;
            border-radius: 8px;
            background-color: #FFDDDD;
        """)
        animation.start()

    @Slot()
    def save_code(self):
        """Verifica o código e exibe mensagem de sucesso ou erro"""
        code = self.edit.text().strip()

        if code == "some_value":
            QMessageBox.information(self, "Sucesso", "Código salvo com sucesso! 🎉")
            self.edit.clear()
            self.animate_border(self.edit, "#888")  # Volta a cor original
        else:
            QMessageBox.warning(self, "Erro", "Código inválido! ❌")
            self.animate_error()  # Anima erro no campo


def main():
    app = QApplication(sys.argv)

    # Aplicar tema do qt-material
    # apply_stylesheet(app, theme='light_blue.xml')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
