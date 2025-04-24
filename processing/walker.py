import os
from typing import Iterator

def iter_files(
    root: str,
    follow_symlinks: bool = False,
    skip_dirs: set[str] = (),
) -> Iterator[str]:
    """
    Yield all file paths under `root`, skipping any directory
    whose name is in `skip_dirs`. Does not follow symlinks by default.
    """
    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        # prune out skip_dirs in-place so os.walk won’t recurse into them
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            yield os.path.join(dirpath, fname)