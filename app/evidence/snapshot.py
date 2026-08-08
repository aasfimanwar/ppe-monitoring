from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

# Anchored to this file's location, not the current working directory - the
# same robust pattern used by SCHEMA_PATH in app/data/init_db.py.
EVIDENCE_ROOT = Path(__file__).resolve().parents[2] / "evidence"


def build_snapshot_path(camera_id: str, timestamp: str) -> str:
    """Build the confirmed camera_id/date/timestamp.jpg relative path."""
    dt = datetime.fromisoformat(timestamp)
    date_str = dt.strftime("%Y-%m-%d")
    epoch_str = str(int(dt.timestamp()))
    return f"{camera_id}/{date_str}/{epoch_str}.jpg"


def _draw_overlay(image: np.ndarray, camera_id: str, zone: str, timestamp: str) -> np.ndarray:
    """Return a copy of image with a readable camera/timestamp label burned into it."""
    annotated = image.copy()
    text = f"{camera_id} ({zone}) - {timestamp}"
    position = (10, annotated.shape[0] - 10)  # bottom-left, 10px margin

    # Black outline first, then white text on top - keeps the text readable
    # regardless of what's behind it in the image.
    cv2.putText(annotated, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(annotated, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return annotated


def save_snapshot(image: np.ndarray, camera_id: str, zone: str, timestamp: str) -> str:
    """Draw the overlay, save the image under evidence/, and return the
    relative path to store in violations.snapshot_path."""
    relative_path = build_snapshot_path(camera_id, timestamp)
    full_path = EVIDENCE_ROOT / relative_path

    full_path.parent.mkdir(parents=True, exist_ok=True)

    annotated = _draw_overlay(image, camera_id, zone, timestamp)
    cv2.imwrite(str(full_path), annotated)

    return relative_path