import hashlib
from pathlib import Path


def hash_file(file_path: str) -> str:
    """Compute the SHA-256 hash of a file on disk, returned as a hex string."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_bytes(data: bytes) -> str:
    """Compute the SHA-256 hash of raw bytes already in memory, returned as a hex string."""
    return hashlib.sha256(data).hexdigest()