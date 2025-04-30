# /Users/dev/Code/dedup/ui/main_window.py
from ui.favorites import FavoritesDialog
from ui.settings_dialog import SettingsDialog
from ui.window_utils import save_window_geometry, restore_window_geometry
from ui.geometry_manager import GeometryManager
from settings.state import app_state

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QMenuBar, QMenu, QInputDialog, QHBoxLayout, QSizePolicy, QLayout,
    QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from ui.drop_area import DropArea
from ui.merge_dialog import MergeDialog

class MainWindow(QMainWindow, GeometryManager):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dedup")

        # Restore window geometry
        self.restore_geometry(app_state.window_geometries, "main_window")

        # Menubar
        menu_bar = QMenuBar()
        menu_bar.setNativeMenuBar(True)
        fav_menu = QMenu("Favoris", self)
        fav_menu.addAction("Ouvrir Favoris", self.open_favorites_dialog)
        menu_bar.addMenu(fav_menu)

        settings_menu = menu_bar.addMenu("⚙️ Paramètres")
        settings_action = settings_menu.addAction("Ouvrir les paramètres")
        settings_action.triggered.connect(self.open_settings)

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

    def open_favorites_dialog(self):
        dlg = FavoritesDialog(self)
        dlg.exec()

    def open_merge_dialog(self):
        if not app_state.destination:
            QMessageBox.warning(
                self,
                "Aucun dossier de destination",
                "Veuillez sélectionner un dossier de destination d'abord."
            )
            return
        dlg = MergeDialog(self, dry_run=self.dry_run_checkbox.isChecked())
        dlg.exec()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        self.save_geometry(app_state.window_geometries, "main_window")
        app_state.save()
        super().closeEvent(event)