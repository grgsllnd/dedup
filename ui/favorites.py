from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QTextEdit, QDialogButtonBox, QPushButton
)
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QGuiApplication

class FavoritesDialog(QDialog):
    def __init__(self, parent=None):
        from settings.state import app_state
        super().__init__(parent)
        self.setWindowTitle("Favoris")
        if app_state.fav_window_geometry:
            ba = QByteArray.fromBase64(app_state.fav_window_geometry.encode("utf-8"))
            self.restoreGeometry(ba)
        else:
            screen_geo = QGuiApplication.primaryScreen().availableGeometry()
            w = int(screen_geo.width() * 0.8)
            h = int(screen_geo.height() * 0.8)
            x0 = screen_geo.x() + (screen_geo.width() - w) // 2
            y0 = screen_geo.y() + (screen_geo.height() - h) // 2
            self.setGeometry(x0, y0, w, h)
            app_state.fav_window_geometry = self.saveGeometry().toBase64().data().decode("utf-8")
            app_state.save()

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.info_view)

        box = QDialogButtonBox()
        self.btn_load   = QPushButton("Charger")
        self.btn_delete = QPushButton("Supprimer")
        self.btn_save   = QPushButton("Sauvegarder actuel")
        box.addButton(self.btn_load,   QDialogButtonBox.AcceptRole)
        box.addButton(self.btn_delete, QDialogButtonBox.DestructiveRole)
        box.addButton(self.btn_save,   QDialogButtonBox.ActionRole)
        layout.addWidget(box)

        for label in self._initial_labels():
            self.list_widget.addItem(label)

        self.list_widget.currentItemChanged.connect(self.update_info)
        self.btn_load.clicked.connect(self.handle_load)
        self.btn_delete.clicked.connect(self.handle_delete)
        self.btn_save.clicked.connect(self.handle_save)
        self.finished.connect(self.save_geometry)

        self.update_info()

    def _initial_labels(self):
        from settings.state import app_state
        labels = []
        if "last_used" in app_state.favorites:
            labels += ["📌 Dernier utilisé", "──────"]
        for name in app_state.favorites:
            if name != "last_used":
                labels.append(name)
        return labels

    def update_info(self, *_):
        from settings.state import app_state
        item = self.list_widget.currentItem()
        if not item or item.text() in ("──────", ""):
            self.info_view.clear()
            return
        name = item.text()
        if name == "📌 Dernier utilisé":
            name = "last_used"
        fav = app_state.favorites.get(name, {})
        dest = fav.get("destination") or {}
        dest_path = dest.get("path", "")
        txt = f"[{name}]\n\nDestination:\n{dest_path}\n\nSources:\n"
        for s in fav.get("sources", []):
            if isinstance(s, dict):
                p, a = s.get("path", ""), s.get("active", True)
            else:
                p, a = s, True
            txt += f"{'✓' if a else '✗'} {p}\n"
        self.info_view.setPlainText(txt)

    def handle_load(self):
        from settings.state import app_state
        name = self.list_widget.currentItem().text()
        if name == "📌 Dernier utilisé":
            name = "last_used"
        self.parent().load_favorite(name)
        self.accept()

    def handle_delete(self):
        from settings.state import app_state
        name = self.list_widget.currentItem().text()
        if name == "📌 Dernier utilisé":
            name = "last_used"
        app_state.favorites.pop(name, None)
        app_state.save()
        self.accept()

    def handle_save(self):
        from settings.state import app_state
        sel = self.list_widget.currentItem()
        default = ""
        if sel and sel.text() not in ("──────", ""):
            default = "last_used" if sel.text() == "📌 Dernier utilisé" else sel.text()
        self.parent().save_current_as_favorite(default)
        self.list_widget.clear()
        for label in self._initial_labels():
            self.list_widget.addItem(label)

    def save_geometry(self):
        from settings.state import app_state
        ba = self.saveGeometry().toBase64().data().decode("utf-8")
        app_state.fav_window_geometry = ba
        app_state.save()
