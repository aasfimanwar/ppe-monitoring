from app.cameras.capture import FrameCaptureService
from app.data.models import Camera, SourceType
from app.evidence.snapshot import save_snapshot, EVIDENCE_ROOT
from app.evidence.hashing import hash_file

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)
capture_service = FrameCaptureService(camera)
capture_service.open()
frame = capture_service.read_frame()
capture_service.release()

if frame is not None:
    relative_path = save_snapshot(frame.image, frame.camera_id, frame.zone, frame.timestamp)
    print("Saved snapshot at relative path:", relative_path)

    full_path = EVIDENCE_ROOT / relative_path
    print("Full path on disk:", full_path)
    print("File actually exists:", full_path.exists())
    print("SHA-256 hash:", hash_file(str(full_path)))
else:
    print("Failed to capture a frame")