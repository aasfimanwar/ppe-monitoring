from dataclasses import dataclass
from typing import List

from ultralytics import YOLO

CONFIDENCE_THRESHOLD = 0.25

VIOLATION_CLASSES = {"NO-Hardhat", "NO-Mask", "Fall-Detected", "NO-Safety Vest"}


@dataclass
class Detection:
    class_label: str
    confidence: float
    bbox: tuple


class DetectionEngine:
    def __init__(self, model_path: str, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, image) -> List[Detection]:
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
        return [d for d in self.detect(image) if d.class_label in VIOLATION_CLASSES]