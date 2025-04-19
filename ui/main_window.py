from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from ui.drop_area import DropArea

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dedup")
        self.resize(600, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Glissez un dossier ou des fichiers ci-dessous :"))
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)

        self.setLayout(layout)