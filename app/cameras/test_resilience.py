from app.cameras.capture import FrameCaptureService
from app.cameras.resilience import ResilientCapture
from app.data.models import Camera, SourceType
from app.data.repository import get_connection, CameraRepository

conn = get_connection("violations.db")
camera_repo = CameraRepository(conn)

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)
capture_service = FrameCaptureService(camera)
capture_service.open()

resilient = ResilientCapture(capture_service, camera_repo)
frame = resilient.read_frame()
print("Frame received:", frame is not None)
print("Camera status after read:", camera_repo.get("cam-yard-01").status)

capture_service.release()
conn.close()