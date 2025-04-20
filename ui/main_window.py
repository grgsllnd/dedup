from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QMenuBar, QInputDialog, QDialog, QListWidget, QTextEdit,
    QDialogButtonBox, QHBoxLayout, QListWidgetItem
)
from PySide6.QtCore import Qt
from ui.drop_area import DropArea
from PySide6.QtGui import QGuiApplication
import json
from pathlib import Path

class AppState:
    def __init__(self):
        self.sources = []
        self.destination = None
        self.favorites = {}
        self.settings_path = Path("dedup.settings")
        self.window_size = None

    def load(self):
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorites = data.get("favorites", {})
                    last = self.favorites.get("last_used", {})
                    self.sources = list(last.get("sources", []))
                    dest = last.get("destination")
                    self.destination = dest.get("path") if isinstance(dest, dict) else dest
                    window = data.get("window", {})
                    if isinstance(window, dict) and "width" in window and "height" in window:
                        self.window_size = (window["width"], window["height"])
            except Exception as e:
                print("Erreur lors du chargement des paramètres :", e)

    def save(self):
        self.favorites["last_used"] = {
            "sources": self.sources,
            "destination": {"path": self.destination} if self.destination else None
        }
        data = {
            "favorites": self.favorites,
            "window": {
                "width": self.window_size[0],
                "height": self.window_size[1]
            } if self.window_size else {}
        }
        print("💾 Sauvegarde dans dedup.settings :", self.sources, "window_size:", self.window_size)
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

app_state = AppState()
app_state.load()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dedup")
        if app_state.window_size:
            self.resize(app_state.window_size[0], app_state.window_size[1])
        else:
            screen_geo = QGuiApplication.primaryScreen().availableGeometry()
            w = int(screen_geo.width() * 0.8)
            h = int(screen_geo.height() * 0.8)
            self.resize(w, h)
            app_state.window_size = (w, h)

        # Menubar
        menu_bar = QMenuBar()
        menu_bar.setNativeMenuBar(True)
        menu_bar.addAction("Favoris", self.open_favorites_dialog)
        self.setMenuBar(menu_bar)

        # Top bar
        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("Dedup"))
        title_row.addStretch()
        btn_fav = QPushButton("★ Favoris")
        btn_fav.clicked.connect(self.open_favorites_dialog)
        title_row.addWidget(btn_fav)

        layout = QVBoxLayout()
        layout.addLayout(title_row)

        # Sources
        layout.addWidget(QLabel("📂 Dossiers source :"))
        self.source_drop_area = DropArea()
        self.source_drop_area.setMinimumHeight(150)
        self.source_drop_area.set_sources(app_state.sources)
        self.source_drop_area.on_change = self.on_sources_changed
        layout.addWidget(self.source_drop_area)

        btn_add = QPushButton("Ajouter un dossier source")
        btn_add.clicked.connect(self.select_source_folder)
        layout.addWidget(btn_add)

        btn_clear = QPushButton("Tout effacer")
        btn_clear.clicked.connect(self.source_drop_area.clear)
        layout.addWidget(btn_clear)

        # Destination
        layout.addWidget(QLabel("🎯 Dossier de destination :"))
        self.destination_label = QLabel(app_state.destination or "Aucun dossier sélectionné")
        layout.addWidget(self.destination_label)

        btn_select = QPushButton("Sélectionner le dossier de destination")
        btn_select.clicked.connect(self.select_destination_folder)
        layout.addWidget(btn_select)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier source")
        if folder:
            self.source_drop_area.add_path(folder)

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination")
        if folder:
            app_state.destination = folder
            self.destination_label.setText(folder)
            app_state.save()

    def on_sources_changed(self, sources):
        app_state.sources = [dict(p) for p in sources]
        app_state.save()

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
        app_state.sources = fav.get("sources", [])
        dest = fav.get("destination")
        app_state.destination = dest.get("path") if isinstance(dest, dict) else dest
        self.source_drop_area.set_sources(app_state.sources)
        self.destination_label.setText(app_state.destination or "Aucun dossier sélectionné")
        app_state.save()

    def open_favorites_dialog(self):
        if not app_state.favorites:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Favoris")
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        info_view = QTextEdit()
        info_view.setReadOnly(True)

        layout.addWidget(list_widget)
        layout.addWidget(info_view)

        button_box = QDialogButtonBox()
        btn_load = QPushButton("Charger")
        btn_delete = QPushButton("Supprimer")
        btn_save = QPushButton("Sauvegarder actuel")
        button_box.addButton(btn_load, QDialogButtonBox.AcceptRole)
        button_box.addButton(btn_delete, QDialogButtonBox.DestructiveRole)
        button_box.addButton(btn_save, QDialogButtonBox.ActionRole)
        layout.addWidget(button_box)

        if "last_used" in app_state.favorites:
            list_widget.addItem("📌 Dernier utilisé")
            list_widget.addItem("──────")

        for name in app_state.favorites:
            if name != "last_used":
                list_widget.addItem(name)

        def update_info():
            item = list_widget.currentItem()
            if not item:
                info_view.clear()
                return
            name = item.text()
            if name in ("──────", ""):
                info_view.clear()
                return
            if name == "📌 Dernier utilisé":
                name = "last_used"
            fav = app_state.favorites.get(name, {})
            dest = fav.get("destination")
            if isinstance(dest, dict):
                dest_path = dest.get("path", "")
            else:
                dest_path = dest or ""
            txt = f"[{name}]\n\nDestination:\n{dest_path}\n\nSources:\n"
            for s in fav.get("sources", []):
                # Determine path and active flag
                if isinstance(s, dict):
                    path = s.get("path", "")
                    active = s.get("active", True)
                else:
                    path = s
                    active = True
                mark = "✓" if active else "✗"
                txt += f"{mark} {path}\n"
            info_view.setPlainText(txt)

        list_widget.currentItemChanged.connect(update_info)

        def handle_load():
            name = list_widget.currentItem().text()
            if name == "📌 Dernier utilisé":
                name = "last_used"
            self.load_favorite(name)
            dialog.accept()

        def handle_delete():
            name = list_widget.currentItem().text()
            if name == "📌 Dernier utilisé":
                name = "last_used"
            app_state.favorites.pop(name, None)
            app_state.save()
            dialog.accept()

        def handle_save():
            selected = list_widget.currentItem()
            default_name = ""
            if selected:
                label = selected.text()
                if label not in ("──────", ""):
                    default_name = "last_used" if label == "📌 Dernier utilisé" else label
            self.save_current_as_favorite(default_name)

        btn_load.clicked.connect(handle_load)
        btn_delete.clicked.connect(handle_delete)
        btn_save.clicked.connect(handle_save)

        dialog.exec()

    def closeEvent(self, event):
        size = self.size()
        app_state.window_size = (size.width(), size.height())
        app_state.save()
        super().closeEvent(event)