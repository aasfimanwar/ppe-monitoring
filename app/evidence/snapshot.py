from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

EVIDENCE_ROOT = Path(__file__).resolve().parents[2] / "evidence"

BOX_COLOR = (0, 0, 255)  # red, BGR order (OpenCV convention)


def build_snapshot_path(camera_id: str, timestamp: str, violation_class: str) -> str:
    """Build the camera_id/date/timestamp_class.jpg relative path."""
    dt = datetime.fromisoformat(timestamp)
    date_str = dt.strftime("%Y-%m-%d")
    epoch_str = str(int(dt.timestamp()))
    safe_class = violation_class.replace(" ", "-")
    return f"{camera_id}/{date_str}/{epoch_str}_{safe_class}.jpg"


def _draw_bbox(image: np.ndarray, bbox: tuple, label: str, confidence: float) -> np.ndarray:
    """Draws the detected bounding box and a class/confidence label directly on image."""
    height, width = image.shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = max(0, min(int(round(x1)), width - 1))
    y1 = max(0, min(int(round(y1)), height - 1))
    x2 = max(0, min(int(round(x2)), width - 1))
    y2 = max(0, min(int(round(y2)), height - 1))

    cv2.rectangle(image, (x1, y1), (x2, y2), BOX_COLOR, 2)

    label_text = f"{label} {confidence:.0%}"
    label_y = max(y1 - 8, 14)
    cv2.putText(image, label_text, (x1, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BOX_COLOR, 2, cv2.LINE_AA)
    return image


def _draw_overlay(image: np.ndarray, camera_id: str, zone: str, timestamp: str) -> np.ndarray:
    """Draws a readable camera/timestamp label at the bottom of the image."""
    text = f"{camera_id} ({zone}) - {timestamp}"
    position = (10, image.shape[0] - 10)

    cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return image


def save_snapshot(
    image: np.ndarray, camera_id: str, zone: str, timestamp: str,
    violation_class: str, bbox: tuple, confidence: float,
) -> str:
    """Draws the bounding box and overlay, saves the image under evidence/, and
    returns the relative path to store in violations.snapshot_path."""
    relative_path = build_snapshot_path(camera_id, timestamp, violation_class)
    full_path = EVIDENCE_ROOT / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    annotated = image.copy()
    _draw_bbox(annotated, bbox, violation_class, confidence)
    _draw_overlay(annotated, camera_id, zone, timestamp)
    cv2.imwrite(str(full_path), annotated)

    return relative_path