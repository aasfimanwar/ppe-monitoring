from app.data.repository import get_connection, CameraRepository
from app.data.models import SourceType
from app.cameras.registry import CameraRegistry

conn = get_connection("violations.db")
registry = CameraRegistry(CameraRepository(conn))

if registry.get("cam-yard-01") is None:
    registry.add_manual(
        camera_id="cam-yard-01",
        name="Yard Camera",
        source_type=SourceType.WEBCAM,
        source_uri="0",
        zone="yard",
    )

print("All cameras:", registry.list_all())
print("ONVIF discovery (placeholder):", registry.discover_onvif())

conn.close()