from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QCheckBox

from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QDesktopServices

import os

class DropArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)

        self.container = QWidget()
        self.setWidget(self.container)

        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(4)

        self.paths = []
        self.on_change = None

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.add_path(path)

    def add_path(self, path, active=True):
        if any(p["path"] == path for p in self.paths):
            return

        entry = {"path": path, "active": active}
        self.paths.append(entry)

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        checkbox = QCheckBox()
        checkbox.setChecked(active)
        layout.addWidget(checkbox)

        btn = QPushButton("⊖")
        btn.setFixedSize(24, 24)
        btn.setFlat(True)
        btn.setToolTip("Supprimer")
        layout.addWidget(btn)
        # Open in Finder/Explorer button
        open_btn = QPushButton("📂")
        open_btn.setFixedSize(24, 24)
        open_btn.setFlat(True)
        open_btn.setToolTip("Ouvrir dans le gestionnaire de fichiers")
        layout.addWidget(open_btn)
        def on_open():
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        open_btn.clicked.connect(on_open)

        label = QLabel(path)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(label)

        layout.addStretch()
        self.layout.addWidget(widget)

        def on_toggled(checked):
            print(f"🔄 Checkbox toggled: {path} → {checked}")
            for item in self.paths:
                if item["path"] == path:
                    item["active"] = checked
                    break
            if self.on_change:
                self.on_change(self.get_sources())

        def on_remove():
            self.layout.removeWidget(widget)
            widget.deleteLater()
            self.paths = [p for p in self.paths if p["path"] != path]
            if self.on_change:
                self.on_change(self.get_sources())

        checkbox.toggled.connect(on_toggled)
        btn.clicked.connect(on_remove)

        if self.on_change:
            self.on_change(self.get_sources())

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.paths.clear()
        if self.on_change:
            self.on_change(self.get_sources())

    def get_sources(self):
        return list(self.paths)

    def set_sources(self, sources):
        self.clear()
        for item in sources:
            if isinstance(item, dict):
                self.add_path(item["path"], item.get("active", True))