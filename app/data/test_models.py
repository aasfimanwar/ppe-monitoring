from models import Camera, Violation, User, SourceType, CameraStatus, Role

c = Camera(id="cam-gate-01", name="Front Gate", source_type=SourceType.RTSP,
           source_uri="rtsp://10.0.0.5/stream", zone="gate")
print(c)

v = Violation(camera_id="cam-gate-01", zone="gate", violation_class="NO-Hardhat",
              snapshot_path="cam-gate-01/2026-07-26/1721990400.jpg", snapshot_hash="abc123")
print(v)

u = User(id="aad-obj-1", name="Test Manager", role=Role.SITE_MANAGER)
print(u)