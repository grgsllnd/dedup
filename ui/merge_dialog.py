import os
import json
import xxhash
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton, QCheckBox

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

    def write_destination_list(self):
        from settings.state import app_state
        dest = app_state.destination
        if not dest:
            return
        checksums = {}
        for root, _, filenames in os.walk(dest):
            for f in filenames:
                path = os.path.join(root, f)
                h = xxhash.xxh64_hexdigest(open(path, "rb").read())
                checksums.setdefault(h, []).append(path)
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(data_dir / "destination_files.json", "w", encoding="utf-8") as jf:
            json.dump(checksums, jf, indent=2)

    def move_duplicates_to_found(self):
        from settings.state import app_state
        dest = app_state.destination
        start = datetime.now()
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_name = start.strftime("merge_%Y%m%d_%H%M%S.log")
        log_fp = open(logs_dir / log_name, "w", encoding="utf-8")

        self.write_destination_list()
        try:
            with open(Path("data") / "destination_files.json", "r", encoding="utf-8") as jf:
                dest_checksums = json.load(jf)
        except FileNotFoundError:
            self.log_view.append("Aucun fichier de destination indexé.")
            log_fp.write("No destination index.\n")
            log_fp.close()
            return

        total = sum(
            len(files)
            for src in app_state.sources if src.get("active", True)
            for _, _, files in os.walk(src["path"])
        )
        processed = 0
        dry = self.debug_checkbox.isChecked()

        for src in app_state.sources:
            if not src.get("active", True):
                continue
            base = src["path"]
            for root, _, files in os.walk(base, topdown=False):
                if "found_duplicates" in os.path.relpath(root, base).split(os.sep):
                    continue
                for name in files:
                    path = os.path.join(root, name)
                    h = xxhash.xxh64_hexdigest(open(path, "rb").read())
                    if h in dest_checksums:
                        rel_dir = os.path.relpath(root, base)
                        dup_dir = os.path.join(base, "found_duplicates", rel_dir)
                        os.makedirs(dup_dir, exist_ok=True)
                        target = os.path.join(dup_dir, name)
                        if not os.path.exists(target):
                            if dry:
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] DRY RUN: would move {path} -> {target}"
                            else:
                                shutil.move(path, target)
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] Duplicate: {path} -> {target}"
                            self.log_view.append(msg)
                            log_fp.write(msg + "\n")
                    else:
                        rel_dir = os.path.relpath(root, base)
                        dest_path = os.path.join(dest, rel_dir, name)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        if not os.path.exists(dest_path):
                            if dry:
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] DRY RUN: would move {path} -> {dest_path}"
                            else:
                                shutil.move(path, dest_path)
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] Moved: {path} -> {dest_path}"
                            self.log_view.append(msg)
                            log_fp.write(msg + "\n")
                        else:
                            msg = f"[{datetime.now().strftime('%H:%M:%S')}] Skipped (exists): {path}"
                            self.log_view.append(msg)
                            log_fp.write(msg + "\n")
                    processed += 1
                    pct = int(processed / total * 100) if total else 100
                    self.progress.setValue(pct)
                if not os.listdir(root):
                    os.rmdir(root)

        self.log_view.append("Merge terminé.")
        log_fp.write("Merge completed.\n")
        log_fp.close()
    def sync_debug_mode(self, result):
        # Propagate the debug checkbox state back to the main window
        parent = self.parent()
        if parent and hasattr(parent, "dry_run_checkbox"):
            parent.dry_run_checkbox.setChecked(self.debug_checkbox.isChecked())