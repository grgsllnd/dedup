# dedup/processing/orchestrator.py
import os
from processing.walker import iter_files
from processing.indexer import build_index, update_index_for
from processing.mover import move_unique, move_duplicate
from processing.logger import get_logger

def run_merge(sources, dest, dry_run=False, progress_callback=None, log_callback=None):
    """
    Merge files from `sources` into `dest`.  
    - dry_run: if True, only log actions, do not move.  
    - progress_callback(percent:int) called as files are processed.  
    - log_callback(msg:str) called for each action.
    """
    logger = get_logger("merge")
    # Build initial index of destination
    index = build_index(dest)

    # Count total files (skip found_duplicates)
    total = sum(
        1
        for src in sources
        for _ in iter_files(src, skip_dirs={"found_duplicates"})
    )
    processed = 0

    def do_progress(pct):
        if progress_callback:
            progress_callback(pct)

    def do_log(msg):
        logger.info(msg)
        if log_callback:
            log_callback(msg)

    # Process each source
    for src in sources:
        for path in iter_files(src, skip_dirs={"found_duplicates"}):
            size = os.path.getsize(path)

            # 1) size+light check
            from processing.hashing import light_hash, full_hash
            lh = light_hash(path)
            # determine unique vs potential dup
            if size not in index or lh not in index[size]:
                # unique by size/light
                rel = os.path.relpath(path, src)
                dest_path = os.path.join(dest, rel)
                if dry_run:
                    do_log(f"DRY RUN: would move {path} → {dest_path}")
                else:
                    if move_unique(path, dest, src, index):
                        update_index_for(dest_path, index)
            else:
                # may be duplicate
                fh = full_hash(path)
                if fh not in index[size][lh]:
                    rel = os.path.relpath(path, src)
                    dest_path = os.path.join(dest, rel)
                    if dry_run:
                        do_log(f"DRY RUN: would move {path} → {dest_path}")
                    else:
                        if move_unique(path, dest, src, index):
                            update_index_for(dest_path, index)
                else:
                    # true duplicate
                    if dry_run:
                        do_log(f"DRY RUN: would move duplicate {path}")
                    else:
                        move_duplicate(path, src)

            processed += 1
            pct = int(processed / total * 100) if total else 100
            do_progress(pct)

    do_log("Merge completed.")