from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from ui.drop_area import DropArea

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dedup")
        self.resize(700, 500)

        layout = QVBoxLayout()

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

        self.setLayout(layout)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier source")
        if folder:
            self.source_drop_area.add_path(folder)

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination")
        if folder:
            self.destination_label.setText(folder)
