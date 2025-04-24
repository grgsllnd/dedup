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