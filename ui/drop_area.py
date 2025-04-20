from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QMenuBar, QMenu, QInputDialog, QDialog, QListWidget, QTextEdit, QDialogButtonBox, QHBoxLayout, QCheckBox
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
        self.layout.setSpacing(4)
        self.paths = []

        self.on_change = None

        self.setAcceptDrops(True)
        self.setStyleSheet("padding: 4px;")

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

    def add_path(self, path, active=True):
        if any(p["path"] == path for p in self.paths):
            return
        entry = {"path": path, "active": active}
        self.paths.append(entry)

        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(2, 0, 2, 0)

        checkbox = QCheckBox()
        checkbox.setChecked(active)
        checkbox.stateChanged.connect(lambda state, p=path: self.update_active(p, state == Qt.Checked))
        layout.addWidget(checkbox)

        btn = QPushButton("🗑️")
        btn.setFixedWidth(30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("border: none;")

        label = QLabel(path)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(btn)
        layout.addWidget(label)
        layout.addStretch()

        self.layout.addWidget(item_widget)
        if self.on_change:
            self.on_change(self.paths)

        def remove():
            self.layout.removeWidget(item_widget)
            item_widget.deleteLater()
            self.paths = [p for p in self.paths if p["path"] != path]
            if self.on_change:
                self.on_change(self.paths)

        btn.clicked.connect(remove)

    def update_active(self, path, is_active):
        updated = False
        for item in self.paths:
            if item["path"] == path:
                if item["active"] != is_active:
                    item["active"] = is_active
                    updated = True
                break
        if updated and self.on_change:
            self.on_change(self.paths)

    def clear(self):
        while self.layout.count():
            child = self.layout.takeAt(0).widget()
            if child:
                child.deleteLater()
        self.paths.clear()

    def get_sources(self):
        return list(self.paths)