import os
import json
import xxhash
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton, QCheckBox

from processing.orchestrator import run_merge

class MergeDialog(QDialog):
    def __init__(self, parent=None, dry_run=False):
        super().__init__(parent)
        self.dry_run = dry_run
        self.setWindowTitle("Merge Sources vers Destination")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Fenêtre de fusion des sources vers la destination"))

        # Progress bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Log view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        # Debug mode checkbox
        self.debug_checkbox = QCheckBox("Mode Debug (dry run) – n’effectue pas les déplacements")
        self.debug_checkbox.setChecked(dry_run)
        layout.addWidget(self.debug_checkbox)

        # Start button
        self.start_btn = QPushButton("Démarrer")
        layout.addWidget(self.start_btn)
        self.start_btn.clicked.connect(self.move_duplicates_to_found)
        # Sync debug mode back to main window when dialog closes
        self.finished.connect(self.sync_debug_mode)

    def move_duplicates_to_found(self):
        from settings.state import app_state
        sources = [s["path"] for s in app_state.sources if s.get("active", True)]
        dest = app_state.destination
        dry = self.debug_checkbox.isChecked()

        # reset UI
        self.log_view.clear()
        self.progress.setValue(0)

        run_merge(
            sources,
            dest,
            dry_run=dry,
            progress_callback=lambda pct: self.progress.setValue(pct),
            log_callback=lambda msg: self.log_view.append(msg)
        )
    def sync_debug_mode(self, result):
        # Propagate the debug checkbox state back to the main window
        parent = self.parent()
        if parent and hasattr(parent, "dry_run_checkbox"):
            parent.dry_run_checkbox.setChecked(self.debug_checkbox.isChecked())