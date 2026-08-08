from dataclasses import dataclass
from typing import List

from ultralytics import YOLO

CONFIDENCE_THRESHOLD = 0.25  # confirmed production threshold (Section 7)

VIOLATION_CLASSES = {"NO-Hardhat", "NO-Mask", "Fall-Detected"}


@dataclass
class Detection:
    """One detected object in a frame - not yet a Violation. Becomes one only
    if class_label is in VIOLATION_CLASSES (see DetectionEngine.get_violations)."""
    class_label: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2) in pixel coordinates


class DetectionEngine:
    def __init__(self, model_path: str, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, image) -> List[Detection]:
        """Run inference on one normalized frame, returning every detection the
        model finds - including the 11 classes not currently treated as violations."""
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        detections: List[Detection] = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_label = self.model.names[class_id]
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(Detection(
                    class_label=class_label,
                    confidence=confidence,
                    bbox=(x1, y1, x2, y2),
                ))
        return detections

    def get_violations(self, image) -> List[Detection]:
        """Same as detect(), filtered to only the classes currently treated as
        violations (VIOLATION_CLASSES). This is what the rest of the pipeline
        (evidence capture, alerting) should actually call."""
        return [d for d in self.detect(image) if d.class_label in VIOLATION_CLASSES]