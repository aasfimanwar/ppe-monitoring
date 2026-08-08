from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import cv2
import numpy as np

from app.data.models import Camera, SourceType


@dataclass
class Frame:
    """A single captured frame, tagged with the camera it came from."""
    camera_id: str
    zone: str
    timestamp: str        # server-side (NFR8) - set the instant the frame is read
    image: np.ndarray


class FrameCaptureService:
    def __init__(self, camera: Camera):
        self.camera = camera
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> bool:
        """Open the underlying video source. Returns True on success."""
        source = (
            int(self.camera.source_uri)
            if self.camera.source_type == SourceType.WEBCAM
            else self.camera.source_uri
        )
        self._cap = cv2.VideoCapture(source)
        return self._cap.isOpened()

    def read_frame(self) -> Optional[Frame]:
        """Read one frame, tagged with this camera's id/zone and a server-side timestamp."""
        if self._cap is None or not self._cap.isOpened():
            return None
        success, image = self._cap.read()
        if not success:
            return None
        return Frame(
            camera_id=self.camera.id,
            zone=self.camera.zone,
            timestamp=datetime.now(timezone.utc).isoformat(),
            image=image,
        )

    def release(self) -> None:
        """Release the underlying video source."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None