from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt
import os

class DropArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        container = QWidget()
        self.setWidget(container)

        self.layout = QVBoxLayout(container)
        self.layout.setAlignment(Qt.AlignTop)
        self.paths = set()

        self.setAcceptDrops(True)
        self.setStyleSheet("border: 2px dashed #888; padding: 10px;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path) or os.path.isfile(path):
                self.add_path(path)

    def add_path(self, path):
        if path in self.paths:
            return
        self.paths.add(path)

        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(5, 2, 5, 2)

        label = QLabel(path)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        btn = QPushButton("🗑️")
        btn.setFixedWidth(30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("border: none;")

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(btn)

        self.layout.addWidget(item_widget)

        def remove():
            self.layout.removeWidget(item_widget)
            item_widget.deleteLater()
            self.paths.remove(path)

        btn.clicked.connect(remove)

    def clear(self):
        while self.layout.count():
            child = self.layout.takeAt(0).widget()
            if child:
                child.deleteLater()
        self.paths.clear()