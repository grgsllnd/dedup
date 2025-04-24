import os
import hashlib
import xxhash
import blake3

def light_hash(path: str, chunk_size: int = 16 * 1024) -> str:
    with open(path, "rb") as f:
        data = f.read(chunk_size)
    return xxhash.xxh3_64(data).hexdigest()

def full_hash(path: str, block_size: int = 1 * 1024 * 1024) -> str:
    h = blake3.blake3()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            h.update(chunk)
    return h.hexdigest()