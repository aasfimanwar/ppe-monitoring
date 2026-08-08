from typing import List, Optional

from app.data.models import Camera, SourceType
from app.data.repository import CameraRepository
from app.cameras.onvif_discovery import DiscoveredDevice, discover_devices, resolve_stream_uri


class CameraRegistry:
    def __init__(self, camera_repo: CameraRepository):
        self.camera_repo = camera_repo

    def add_manual(
        self,
        camera_id: str,
        name: str,
        source_type: SourceType,
        source_uri: str,
        zone: str,
        credentials_ref: Optional[str] = None,
    ) -> Camera:
        """Register a camera by hand - webcam device index, RTSP URL, or HTTP URL."""
        camera = Camera(
            id=camera_id,
            name=name,
            source_type=source_type,
            source_uri=source_uri,
            zone=zone,
            credentials_ref=credentials_ref,
        )
        self.camera_repo.add(camera)
        return camera

    def discover_onvif(self, timeout_seconds: float = 4.0) -> List[DiscoveredDevice]:
        """Broadcast WS-Discovery and return whatever ONVIF devices respond.

        This only finds devices - it does not register them. A found device
        still needs a camera_id, name, zone, and credentials before it becomes
        a usable Camera; see add_onvif().

        An empty list is a normal, valid result on a network with no ONVIF
        devices - not an error.
        """
        return discover_devices(timeout_seconds=timeout_seconds)

    def add_onvif(
        self,
        camera_id: str,
        name: str,
        zone: str,
        device: DiscoveredDevice,
        username: str,
        password: str,
    ) -> Camera:
        """Resolve a discovered device's stream URI and register it as a Camera.

        The resolve_stream_uri() call this depends on is unverified without
        real ONVIF hardware - see onvif_discovery.py's docstring.
        """
        stream_uri = resolve_stream_uri(device, username, password)
        camera = Camera(
            id=camera_id, name=name, source_type=SourceType.ONVIF,
            source_uri=stream_uri, zone=zone, credentials_ref=username,
        )
        self.camera_repo.add(camera)
        return camera

    def get(self, camera_id: str) -> Optional[Camera]:
        return self.camera_repo.get(camera_id)

    def list_all(self) -> List[Camera]:
        return self.camera_repo.list_all()