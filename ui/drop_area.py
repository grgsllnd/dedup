from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Qt
import os
from logic.folder_walker import list_files_recursive

class DropArea(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("border: 2px dashed #888; padding: 10px;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path):
                for file in list_files_recursive(path):
                    self.addItem(file)
            elif os.path.isfile(path):
                self.addItem(path)