import cv2
import numpy as np

MODEL_INPUT_SIZE = 640  # confirmed from ppe_best.pt train_args (imgsz=640)
PAD_COLOR = (114, 114, 114)  # standard YOLO letterbox grey


def letterbox(image: np.ndarray, target_size: int = MODEL_INPUT_SIZE) -> np.ndarray:
    """Resize `image` to fit inside a target_size x target_size square, padded to fill it."""
    original_height, original_width = image.shape[:2]

    scale = min(target_size / original_width, target_size / original_height)
    new_width = round(original_width * scale)
    new_height = round(original_height * scale)

    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    canvas = np.full((target_size, target_size, 3), PAD_COLOR, dtype=np.uint8)
    pad_x = (target_size - new_width) // 2
    pad_y = (target_size - new_height) // 2
    canvas[pad_y:pad_y + new_height, pad_x:pad_x + new_width] = resized

    return canvas


def letterbox_to_original_coords(
    bbox: tuple, original_width: int, original_height: int, target_size: int = MODEL_INPUT_SIZE
) -> tuple:
    """Converts a bounding box (x1, y1, x2, y2) from letterboxed coordinates back
    to the original image's coordinate space, undoing letterbox()'s scale and padding.

    Recomputes the same scale/pad values letterbox() used, from the original
    dimensions - deterministic, so no need to have stored them separately.
    """
    x1, y1, x2, y2 = bbox

    scale = min(target_size / original_width, target_size / original_height)
    new_width = round(original_width * scale)
    new_height = round(original_height * scale)
    pad_x = (target_size - new_width) // 2
    pad_y = (target_size - new_height) // 2

    orig_x1 = (x1 - pad_x) / scale
    orig_y1 = (y1 - pad_y) / scale
    orig_x2 = (x2 - pad_x) / scale
    orig_y2 = (y2 - pad_y) / scale
    return (orig_x1, orig_y1, orig_x2, orig_y2)