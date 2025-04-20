
import os
import json
import xxhash
import shutil
 
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
 
class MergeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge Sources vers Destination")
        self.resize(400, 200)
 
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Fenêtre de fusion des sources vers la destination"))
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
        # Load destination checksums
        try:
            with open("destination_files.json", "r", encoding="utf-8") as jf:
                dest_checksums = json.load(jf)
        except FileNotFoundError:
            return

        # For each active source
        for src in app_state.sources:
            if not src.get("active", True):
                continue
            base = src["path"]
            for root, _, files in os.walk(base, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    # Compute hash
                    with open(path, "rb") as f:
                        h = xxhash.xxh64_hexdigest(f.read())
                    if h in dest_checksums:
                        # prepare target duplicate folder
                        rel_dir = os.path.relpath(root, base)
                        dup_dir = os.path.join(base, "found_duplicates", rel_dir)
                        os.makedirs(dup_dir, exist_ok=True)
                        target = os.path.join(dup_dir, name)
                        # only move if file doesn't already exist there
                        if not os.path.exists(target):
                            shutil.move(path, target)
                # Remove empty directory if nothing left
                if not os.listdir(root):
                    os.rmdir(root)