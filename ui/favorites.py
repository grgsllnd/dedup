from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QTextEdit, QDialogButtonBox, QPushButton, QMessageBox, QInputDialog
)
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QGuiApplication
from ui.geometry_manager import GeometryManager
from settings.state import app_state

class FavoritesDialog(QDialog, GeometryManager):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("★ Favoris")

        # Restore geometry
        self.restore_geometry(app_state.window_geometries, "favorites_dialog")

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.info_view)

        box = QDialogButtonBox()
        self.btn_load = QPushButton("Charger")
        self.btn_delete = QPushButton("Supprimer")
        self.btn_save = QPushButton("Sauvegarder actuel")
        box.addButton(self.btn_load, QDialogButtonBox.AcceptRole)
        box.addButton(self.btn_delete, QDialogButtonBox.DestructiveRole)
        box.addButton(self.btn_save, QDialogButtonBox.ActionRole)
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
        labels = []
        if "last_used" in app_state.favorites:
            labels += ["📌 Dernier utilisé", "──────"]
        for name in app_state.favorites:
            if name != "last_used":
                labels.append(name)
        return labels

    def update_info(self, *_):
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

    def save_current_as_favorite(self, default_name=""):
        name, ok = QInputDialog.getText(self, "Nom du favori", "Entrer un nom :", text=default_name)
        if ok and name:
            app_state.favorites[name] = {
                "sources": app_state.sources,
                "destination": {"path": app_state.destination} if app_state.destination else None
            }
            app_state.save()

    def load_favorite(self, name):
        fav = app_state.favorites.get(name, {})
        if not fav:
            QMessageBox.warning(self, "Erreur", f"Le favori '{name}' est introuvable.")
            return
        app_state.sources = fav.get("sources", [])
        dest = fav.get("destination")
        app_state.destination = dest.get("path") if isinstance(dest, dict) else dest
        self.parent().source_drop_area.set_sources(app_state.sources)
        self.parent().destination_label.setText(app_state.destination or "Aucun dossier sélectionné")
        app_state.save()

    def handle_load(self):
        name = self.list_widget.currentItem().text()
        if name == "📌 Dernier utilisé":
            name = "last_used"
        self.load_favorite(name)
        self.accept()

    def handle_delete(self):
        name = self.list_widget.currentItem().text()
        if name == "📌 Dernier utilisé":
            name = "last_used"
        app_state.favorites.pop(name, None)
        app_state.save()
        self.accept()

    def handle_save(self):
        sel = self.list_widget.currentItem()
        default = ""
        if sel and sel.text() not in ("──────", ""):
            default = "last_used" if sel.text() == "📌 Dernier utilisé" else sel.text()
        self.save_current_as_favorite(default)
        self.list_widget.clear()
        for label in self._initial_labels():
            self.list_widget.addItem(label)

    def closeEvent(self, event):
        self.save_geometry(app_state.window_geometries, "favorites_dialog")
        app_state.save()
        super().closeEvent(event)
