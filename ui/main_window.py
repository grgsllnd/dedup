from ui.favorites import FavoritesDialog
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QMenuBar, QMenu, QInputDialog, QHBoxLayout, QSizePolicy, QLayout, QCheckBox
)
from PySide6.QtCore import Qt
from ui.drop_area import DropArea
from ui.merge_dialog import MergeDialog
from PySide6.QtGui import QGuiApplication
from settings.state import app_state

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dedup")
        if app_state.window_size:
            self.resize(*app_state.window_size)
            if app_state.window_pos:
                self.move(*app_state.window_pos)
        else:
            screen_geo = QGuiApplication.primaryScreen().availableGeometry()
            w = int(screen_geo.width() * 0.8)
            h = int(screen_geo.height() * 0.8)
            self.resize(w, h)
            app_state.window_size = (w, h)

        # Menubar
        menu_bar = QMenuBar()
        menu_bar.setNativeMenuBar(True)
        fav_menu = QMenu("Favoris", self)
        fav_menu.addAction("Ouvrir Favoris", self.open_favorites_dialog)
        menu_bar.addMenu(fav_menu)
        self.setMenuBar(menu_bar)

        # Top bar
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Dedup"))
        title_layout.addStretch()
        btn_fav = QPushButton()
        btn_fav.setFlat(True)
        btn_fav.setStyleSheet("font-size: 14px;")
        btn_fav.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        inner_layout = QHBoxLayout(btn_fav)
        inner_layout.setContentsMargins(4, 2, 4, 2)
        inner_layout.setSpacing(4)
        inner_layout.setSizeConstraint(QLayout.SetFixedSize)
        inner_layout.addWidget(QLabel("★", alignment=Qt.AlignCenter))
        inner_layout.addWidget(QLabel("Favoris"))
        btn_fav.clicked.connect(self.open_favorites_dialog)
        title_layout.addWidget(btn_fav)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)

        # Sources
        main_layout.addWidget(QLabel("📂 Dossiers source :"))
        self.source_drop_area = DropArea()
        self.source_drop_area.setMinimumHeight(150)
        self.source_drop_area.set_sources(app_state.sources)
        self.source_drop_area.on_change = self.on_sources_changed
        main_layout.addWidget(self.source_drop_area)

        btn_add = QPushButton("Ajouter un dossier source")
        btn_add.clicked.connect(self.select_source_folder)
        main_layout.addWidget(btn_add)

        btn_clear = QPushButton("Tout effacer")
        btn_clear.clicked.connect(self.source_drop_area.clear)
        main_layout.addWidget(btn_clear)

        # Destination
        main_layout.addWidget(QLabel("🎯 Dossier de destination :"))
        self.destination_label = QLabel(app_state.destination or "Aucun dossier sélectionné")
        main_layout.addWidget(self.destination_label)

        btn_dest = QPushButton("Sélectionner le dossier de destination")
        btn_dest.clicked.connect(self.select_destination_folder)
        main_layout.addWidget(btn_dest)

        # Dry-run mode
        self.dry_run_checkbox = QCheckBox("Mode Test (dry run) – n’effectue pas les déplacements")
        main_layout.addWidget(self.dry_run_checkbox)

        # Merge button
        btn_merge = QPushButton("Déplacer vers destination")
        btn_merge.clicked.connect(self.open_merge_dialog)
        main_layout.addWidget(btn_merge)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

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
        dlg = FavoritesDialog(self)
        dlg.exec()

    def open_merge_dialog(self):
        dlg = MergeDialog(self, dry_run=self.dry_run_checkbox.isChecked())
        dlg.exec()

    def closeEvent(self, event):
        pos = self.pos()
        app_state.window_pos = (pos.x(), pos.y())
        app_state.window_screen = self.windowHandle().screen().name()
        app_state.window_size = (self.width(), self.height())
        app_state.save()
        super().closeEvent(event)