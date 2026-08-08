from app.cameras.capture import FrameCaptureService
from app.cameras.normalize import letterbox
from app.data.models import Camera, SourceType

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)

service = FrameCaptureService(camera)
if service.open():
    frame = service.read_frame()
    if frame:
        print("Original shape:", frame.image.shape)
        normalized = letterbox(frame.image)
        print("Normalized shape:", normalized.shape)
service.release()