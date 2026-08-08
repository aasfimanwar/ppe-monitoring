import time
from datetime import datetime, timezone
from typing import Optional

from app.cameras.capture import Frame, FrameCaptureService
from app.data.models import CameraStatus
from app.data.repository import CameraRepository

RETRY_DELAY_SECONDS = 2.0
MAX_RETRIES = 5


class ResilientCapture:
    def __init__(
        self,
        capture_service: FrameCaptureService,
        camera_repo: CameraRepository,
        retry_delay_seconds: float = RETRY_DELAY_SECONDS,
        max_retries: int = MAX_RETRIES,
    ):
        self.capture_service = capture_service
        self.camera_repo = camera_repo
        self.retry_delay_seconds = retry_delay_seconds
        self.max_retries = max_retries

    def read_frame(self) -> Optional[Frame]:
        """Read one frame, retrying on failure with a fixed delay between attempts.

        On success: marks the camera ONLINE.
        On exhausting all retries: marks the camera ERROR and returns None.
        """
        for attempt in range(1, self.max_retries + 1):
            frame = self.capture_service.read_frame()
            if frame is not None:
                self._update_status(CameraStatus.ONLINE)
                return frame

            print(f"[{self.capture_service.camera.id}] read failed "
                  f"(attempt {attempt}/{self.max_retries}) - reconnecting")
            self.capture_service.release()
            time.sleep(self.retry_delay_seconds)
            self.capture_service.open()

        self._update_status(CameraStatus.ERROR)
        return None

    def _update_status(self, status: CameraStatus) -> None:
        self.camera_repo.update_status(
            camera_id=self.capture_service.camera.id,
            status=status,
            last_seen_at=datetime.now(timezone.utc).isoformat(),
        )