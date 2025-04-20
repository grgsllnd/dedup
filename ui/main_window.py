from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMenuBar, QMenu, QInputDialog, QDialog, QListWidget, QTextEdit, QDialogButtonBox, QHBoxLayout, QListWidgetItem
from PySide6.QtCore import Qt
from ui.drop_area import DropArea
import json
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dedup")
        
        self.menu_bar = QMenuBar()
        self.menu_bar.setNativeMenuBar(True)
        self.menu_bar.addAction("Favoris", self.open_favorites_dialog)

        self.resize(700, 500)

        self.favorites = {}
        # Insert top row layout with title and Favoris button
        top_row = QHBoxLayout()
        title_label = QLabel("Dedup")
        btn_open_favorites = QPushButton("★ Favoris")
        btn_open_favorites.clicked.connect(self.open_favorites_dialog)
        top_row.addWidget(title_label)
        top_row.addStretch()
        top_row.addWidget(btn_open_favorites)

        layout = QVBoxLayout()
        layout.addLayout(top_row)

        self.settings_path = Path("dedup.settings")
        self.sources = set()
        self.destination = None
        self.destination_active = False

        # --- Sources Section ---
        layout.addWidget(QLabel("📂 Dossiers source :"))
        self.source_drop_area = DropArea()
        self.source_drop_area.setMinimumHeight(150)
        layout.addWidget(self.source_drop_area)

        btn_add_source = QPushButton("Ajouter un dossier source")
        btn_add_source.clicked.connect(self.select_source_folder)
        layout.addWidget(btn_add_source)

        btn_clear_sources = QPushButton("Tout effacer")
        btn_clear_sources.clicked.connect(self.source_drop_area.clear)
        layout.addWidget(btn_clear_sources)

        # --- Destination Section ---
        layout.addWidget(QLabel("🎯 Dossier de destination :"))
        self.destination_label = QLabel("Aucun dossier sélectionné")
        layout.addWidget(self.destination_label)

        btn_select_dest = QPushButton("Sélectionner le dossier de destination")
        btn_select_dest.clicked.connect(self.select_destination_folder)
        layout.addWidget(btn_select_dest)
        
        # Removed redundant Favoris button from vertical layout

        self.load_settings()
        self.update_settings_file()

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setMenuBar(self.menu_bar)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier source")
        if folder:
            self.source_drop_area.add_path(folder)
            self.sources = list(self.source_drop_area.sources)
            self.update_settings_file()

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination")
        if folder:
            self.destination = folder
            self.destination_label.setText(folder)
            self.update_settings_file()

    def load_settings(self):
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorites = data.get("favorites", {})
                    last = self.favorites.get("last_used", {})
                    self.sources = [item.get("path") for item in last.get("sources", []) if "path" in item]
                    dest = last.get("destination")
                    self.destination = dest.get("path") if dest and "path" in dest else None
                    self.destination_active = dest.get("active", False) if dest else False
                    for path in self.sources:
                        self.source_drop_area.add_path(path)
                    if self.destination:
                        self.destination_label.setText(self.destination)
                    
            except Exception as e:
                print(f"Erreur chargement settings: {e}")

    def open_favorites_dialog(self):
        if not self.favorites:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Favoris")
        dialog.resize(500, 300)

        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        info_view = QTextEdit()
        info_view.setReadOnly(True)

        layout.addWidget(list_widget)
        layout.addWidget(info_view)

        button_box = QDialogButtonBox()
        btn_load = QPushButton("Charger")
        btn_delete = QPushButton("Supprimer")
        btn_save_current = QPushButton("Sauvegarder actuel")
        button_box.addButton(btn_load, QDialogButtonBox.AcceptRole)
        button_box.addButton(btn_delete, QDialogButtonBox.DestructiveRole)
        button_box.addButton(btn_save_current, QDialogButtonBox.ActionRole)

        layout.addWidget(button_box)

        if "last_used" in self.favorites:
            item = QListWidgetItem("📌 Dernier utilisé")
            list_widget.addItem(item)

            separator = QListWidgetItem("──────")
            list_widget.addItem(separator)

        for name in self.favorites:
            if name != "last_used":
                item = QListWidgetItem(name)
                list_widget.addItem(item)

        def update_info():
            selected = list_widget.currentItem()
            if not selected:
                info_view.clear()
                return
            name = selected.text()
            if name in ("──────", ""):
                info_view.clear()
                return
            if name == "📌 Dernier utilisé":
                name = "last_used"
            fav = self.favorites.get(name, {})

            txt = f"[{name}]\n\nDestination:\n{fav.get('destination')}\n\nSources:\n"
            txt += "\n".join(item["path"] if isinstance(item, dict) else item for item in fav.get("sources", []))
            info_view.setPlainText(txt)

        list_widget.currentItemChanged.connect(lambda: update_info())

        def handle_load():
            selected = list_widget.currentItem()
            name = selected.text()
            if name == "📌 Dernier utilisé":
                name = "last_used"
            if name == "──────":
                return
            if selected:
                self.load_favorite(name)
                dialog.accept()

        def handle_delete():
            selected = list_widget.currentItem()
            name = selected.text()
            if name == "📌 Dernier utilisé":
                name = "last_used"
            if name == "──────":
                return
            if selected:
                self.favorites.pop(name, None)
                self.update_settings_file()

        def handle_save():
            self.save_current_as_favorite()

        btn_load.clicked.connect(handle_load)
        btn_delete.clicked.connect(handle_delete)
        btn_save_current.clicked.connect(handle_save)

        dialog.exec()

    def load_favorite(self, name):
        fav = self.favorites.get(name, {})
        self.sources = fav.get("sources", [])
        self.destination = fav.get("destination", None)
        self.destination_active = self.destination.get("active", False) if isinstance(self.destination, dict) else False
        dest_path = self.destination.get("path") if isinstance(self.destination, dict) else self.destination
        self.source_drop_area.clear()
        for path in self.sources:
            self.source_drop_area.add_path(path)
        self.destination_label.setText(dest_path or "Aucun dossier sélectionné")
        self.update_settings_file()

    def save_current_as_favorite(self):
        name, ok = QInputDialog.getText(self, "Nom du favori", "Entrer un nom :")
        if ok and name:
            self.favorites[name] = {
                "sources": self.sources,
                "destination": {"path": self.destination, "active": self.destination_active} if self.destination else None
            }
            self.update_settings_file()

    def update_settings_file(self):
        self.favorites["last_used"] = {
            "sources": [{"path": p} for p in self.sources],
            "destination": {"path": self.destination, "active": self.destination_active} if self.destination else None,
        }
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump({"favorites": self.favorites}, f, indent=2)