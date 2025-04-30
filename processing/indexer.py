from collections import defaultdict
from typing import Dict, List
from .hashing import light_hash, full_hash
from .walker import iter_files
import os

Index = Dict[int, Dict[str, Dict[str, List[str]]]]

def build_index(dest_root: str) -> Index:
    idx: Index = {}
    for path in iter_files(dest_root, skip_dirs={"found_duplicates"}):
        size = os.path.getsize(path)
        lh = light_hash(path)
        fh = full_hash(path)
        idx.setdefault(size, {})\
           .setdefault(lh, {})\
           .setdefault(fh, [])\
           .append(path)
    return idx

def update_index_for(path: str, idx: Index) -> None:
    size = os.path.getsize(path)
    lh = light_hash(path)
    fh = full_hash(path)
    idx.setdefault(size, {})\
       .setdefault(lh, {})\
       .setdefault(fh, [])\
       .append(path)


# Remove a file from the index (if present), cleaning up empty dicts.
def remove_from_index(path: str, idx: Index) -> None:
    try:
        size = os.path.getsize(path)
        lh = light_hash(path)
        fh = full_hash(path)
        paths = idx.get(size, {}).get(lh, {}).get(fh, [])
        if path in paths:
            paths.remove(path)
            if not paths:
                del idx[size][lh][fh]
                if not idx[size][lh]:
                    del idx[size][lh]
                    if not idx[size]:
                        del idx[size]
    except FileNotFoundError:
        pass