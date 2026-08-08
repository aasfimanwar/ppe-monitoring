from app.cameras.capture import FrameCaptureService
from app.cameras.normalize import letterbox
from app.data.models import Camera, SourceType
from app.detection.engine import DetectionEngine

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)
capture_service = FrameCaptureService(camera)
capture_service.open()
frame = capture_service.read_frame()
capture_service.release()

if frame is not None:
    normalized = letterbox(frame.image)
    engine = DetectionEngine("models/ppe_best.pt")

    all_detections = engine.detect(normalized)
    print(f"All detections ({len(all_detections)}):")
    for d in all_detections:
        print(f"  {d.class_label} ({d.confidence:.2f})")

    violations = engine.get_violations(normalized)
    print(f"\nViolations only ({len(violations)}):")
    for v in violations:
        print(f"  {v.class_label} ({v.confidence:.2f})")
else:
    print("Failed to capture a frame")