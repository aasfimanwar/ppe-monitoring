from app.cameras.capture import FrameCaptureService
from app.data.models import Camera, SourceType

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)

service = FrameCaptureService(camera)

if service.open():
    print("Camera opened successfully")
    frame = service.read_frame()
    if frame:
        print(f"Got frame from {frame.camera_id} at {frame.timestamp}, shape={frame.image.shape}")
    else:
        print("Failed to read a frame")
else:
    print("Failed to open camera - is a webcam connected and not in use by another app?")

service.release()