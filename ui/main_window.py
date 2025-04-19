from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog
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
        layout.addWidget(self.source_drop_area)

        source_btns = QHBoxLayout()

        btn_add_source = QPushButton("Ajouter un dossier source")
        btn_add_source.clicked.connect(self.select_source_folder)

        btn_remove_selected = QPushButton("Supprimer le dossier sélectionné")
        btn_remove_selected.clicked.connect(self.remove_selected_source)

        btn_clear_all = QPushButton("Tout effacer")
        btn_clear_all.clicked.connect(self.clear_all_sources)

        source_btns.addWidget(btn_add_source)
        source_btns.addWidget(btn_remove_selected)
        source_btns.addWidget(btn_clear_all)

        layout.addLayout(source_btns)

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
            self.source_drop_area.addItem(folder)

    def remove_selected_source(self):
        row = self.source_drop_area.currentRow()
        if row >= 0:
            self.source_drop_area.takeItem(row)

    def clear_all_sources(self):
        self.source_drop_area.clear()

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination")
        if folder:
            self.destination_label.setText(folder)