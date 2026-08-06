from repository import get_connection, CameraRepository, ViolationRepository
from models import Camera, Violation, SourceType

conn = get_connection("violations.db")
camera_repo = CameraRepository(conn)
violation_repo = ViolationRepository(conn)

# Add a camera (skip if it already exists from a previous run)
if camera_repo.get("cam-gate-01") is None:
    camera_repo.add(Camera(
        id="cam-gate-01", name="Front Gate", source_type=SourceType.RTSP,
        source_uri="rtsp://10.0.0.5/stream", zone="gate",
    ))

print("Cameras:", camera_repo.list_all())

# Save a violation against that camera
new_id = violation_repo.save(Violation(
    camera_id="cam-gate-01", zone="gate", violation_class="NO-Hardhat",
    snapshot_path="cam-gate-01/2026-07-26/1721990400.jpg", snapshot_hash="abc123",
))
print("Saved violation with id:", new_id)

print("All violations:", violation_repo.get_all())
print("Violations for cam-gate-01:", violation_repo.get_by_camera("cam-gate-01"))

conn.close()