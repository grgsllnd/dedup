import os
import shutil
from typing import List
from .hashing import light_hash, full_hash
from .logger import get_logger

log = get_logger("mover")

def move_unique(
    src: str,
    dest_root: str,
    rel_root: str,
    idx,
) -> None:
    rel = os.path.relpath(src, rel_root)
    dst = os.path.join(dest_root, rel)
    if os.path.exists(dst):
        log.warning(f"Skip path collision, exists: {dst}")
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    log.info(f"Moved unique: {src} → {dst}")
    from .indexer import update_index_for
    update_index_for(dst, idx)

def move_duplicate(
    src: str,
    rel_root: str,
) -> None:
    rel = os.path.relpath(src, rel_root)
    dup_root = os.path.join(rel_root, "found_duplicates", os.path.dirname(rel))
    os.makedirs(dup_root, exist_ok=True)
    dst = os.path.join(dup_root, os.path.basename(src))
    if os.path.exists(dst):
        log.warning(f"Duplicate folder collision: {dst}")
        return
    shutil.move(src, dst)
    log.info(f"Moved duplicate: {src} → {dst}")