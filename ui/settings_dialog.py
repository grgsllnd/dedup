from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QDialogButtonBox, QLabel, QFileDialog, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from ui.geometry_manager import GeometryManager
from settings.state import app_state

class SettingsDialog(QDialog, GeometryManager):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Paramètres")

        # Restore geometry
        self.restore_geometry(app_state.window_geometries, "settings_dialog")

        # Scroll area setup
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QScrollArea.NoFrame)  # Remove border

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside the scroll content

        # Logs folder path
        self.logs_folder_label = QLabel("Dossier des logs :")
        self.logs_folder_input = QLineEdit(app_state.logs_folder or "~/dedup_logs")
        self.logs_folder_input.setPlaceholderText("Chemin du dossier des logs")
        self.logs_folder_input.setReadOnly(True)

        # Buttons for logs folder (inline with input)
        folder_buttons_layout = QHBoxLayout()
        self.choose_folder_btn = QPushButton("📂")
        self.choose_folder_btn.setToolTip("Choisir un dossier")
        self.reset_folder_btn = QPushButton("❌")
        self.reset_folder_btn.setToolTip("Réinitialiser au chemin par défaut")
        folder_buttons_layout.addWidget(self.logs_folder_input)
        folder_buttons_layout.addWidget(self.choose_folder_btn)
        folder_buttons_layout.addWidget(self.reset_folder_btn)

        # Add widgets to scroll layout
        scroll_layout.addWidget(self.logs_folder_label)
        scroll_layout.addLayout(folder_buttons_layout)

        # Dialog buttons
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        scroll_layout.addWidget(self.dialog_buttons)

        # Set scroll content and area
        scroll_area.setWidget(scroll_content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding around the main layout
        main_layout.addWidget(scroll_area)

        # Connect signals
        self.choose_folder_btn.clicked.connect(self.choose_folder)
        self.reset_folder_btn.clicked.connect(self.reset_folder)
        self.dialog_buttons.accepted.connect(self.save_settings)
        self.dialog_buttons.rejected.connect(self.reject)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier pour les logs")
        if folder:
            self.logs_folder_input.setText(folder)

    def reset_folder(self):
        self.logs_folder_input.setText("~/dedup_logs")

    def save_settings(self):
        app_state.logs_folder = self.logs_folder_input.text()
        app_state.save()
        self.accept()

    def closeEvent(self, event):
        self.save_geometry(app_state.window_geometries, "settings_dialog")
        app_state.save()
        super().closeEvent(event)