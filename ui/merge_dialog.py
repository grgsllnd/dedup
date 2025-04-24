
import os
import json
import xxhash
import shutil
from datetime import datetime

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit
 
class MergeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Sources vers Destination")
        self.resize(400, 200)
 
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Fenêtre de fusion des sources vers la destination"))
        # Progress bar and log view
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)
        # Write list of destination files to JSON
        self.write_destination_list()
        # Process and move duplicate files from sources
        self.move_duplicates_to_found()
        # TODO: ajouter les contrôles et la logique de fusion ici

    def write_destination_list(self):
        from ui.main_window import app_state
        dest = app_state.destination
        if not dest:
            return
        # Build checksum mapping for destination files
        checksums = {}
        for root, _, filenames in os.walk(dest):
            for f in filenames:
                path = os.path.join(root, f)
                h = xxhash.xxh64_hexdigest(open(path, "rb").read())
                checksums.setdefault(h, []).append(path)
        with open("destination_files.json", "w", encoding="utf-8") as jf:
            json.dump(checksums, jf, indent=2)

    def move_duplicates_to_found(self):
        from ui.main_window import app_state
        # Prepare log file
        start = datetime.now()
        log_name = start.strftime("merge_%Y%m%d_%H%M%S.log")
        log_fp = open(log_name, "w", encoding="utf-8")

        # Build and load destination checksums map
        self.write_destination_list()
        try:
            with open("destination_files.json", "r", encoding="utf-8") as jf:
                dest_checksums = json.load(jf)
        except FileNotFoundError:
            self.log_view.append("Aucun fichier de destination indexé.")
            log_fp.write("No destination index.\n")
            log_fp.close()
            return

        # Count total files for progress
        total = 0
        for src in app_state.sources:
            if not src.get("active", True):
                continue
            for _, _, files in os.walk(src["path"]):
                total += len(files)
        processed = 0

        # Process each source
        for src in app_state.sources:
            if not src.get("active", True):
                continue
            base = src["path"]
            for root, _, files in os.walk(base, topdown=False):
                    # Skip any existing found_duplicates folders
                    if "found_duplicates" in os.path.relpath(root, base).split(os.sep):
                        continue
                    for name in files:
                        path = os.path.join(root, name)
                        # Compute hash
                        with open(path, "rb") as f:
                            h = xxhash.xxh64_hexdigest(f.read())
                        if h in dest_checksums:
                            # Duplicate found
                            rel_dir = os.path.relpath(root, base)
                            dup_dir = os.path.join(base, "found_duplicates", rel_dir)
                            os.makedirs(dup_dir, exist_ok=True)
                            target = os.path.join(dup_dir, name)
                            if not os.path.exists(target):
                                shutil.move(path, target)
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] Duplicate: {path} -> {target}"
                                self.log_view.append(msg)
                                log_fp.write(msg + "\n")
                        else:
                            # Unique file – move to destination, avoid overwrite
                            rel_dir = os.path.relpath(root, base)
                            dest_path = os.path.join(dest, rel_dir, name)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            if not os.path.exists(dest_path):
                                shutil.move(path, dest_path)
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] Moved: {path} -> {dest_path}"
                                self.log_view.append(msg)
                                log_fp.write(msg + "\n")
                            else:
                                msg = f"[{datetime.now().strftime('%H:%M:%S')}] Skipped (exists): {path}"
                                self.log_view.append(msg)
                                log_fp.write(msg + "\n")
                        processed += 1
                        # Update progress
                        pct = int(processed / total * 100) if total else 100
                        self.progress.setValue(pct)
                    # Remove empty directory if nothing left
                    if not os.listdir(root):
                        os.rmdir(root)

        self.log_view.append("Merge terminé.")
        log_fp.write("Merge completed.\n")
        log_fp.close()