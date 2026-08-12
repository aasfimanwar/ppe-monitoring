from ultralytics import YOLO

from app import config
from app.cameras.capture import FrameCaptureService
from app.cameras.normalize import letterbox
from app.data.models import Camera, SourceType

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)
capture_service = FrameCaptureService(camera)
capture_service.open()
frame = capture_service.read_frame()
capture_service.release()

if frame is None:
    print("Failed to capture a frame")
else:
    normalized = letterbox(frame.image)
    model = YOLO(config.MODEL_PATH)

    print("Frame shape:", frame.image.shape)
    print("\nAll detections at confidence >= 0.05 (no class filtering):")
    results = model(normalized, conf=0.05, verbose=False)
    found_anything = False
    for result in results:
        for box in result.boxes:
            found_anything = True
            class_id = int(box.cls[0])
            class_label = model.names[class_id]
            confidence = float(box.conf[0])
            print(f"  {class_label}: {confidence:.3f}")

    if not found_anything:
        print("  (nothing detected at all, even at 0.05 confidence)")