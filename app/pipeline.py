import time

from app import config
from app.alerts.email_alert import EmailAlertSender
from app.cameras.capture import FrameCaptureService
from app.cameras.normalize import letterbox, letterbox_to_original_coords
from app.cameras.resilience import ResilientCapture
from app.data.models import Camera, Violation
from app.data.repository import CameraRepository, ViolationRepository, get_connection
from app.detection.engine import DetectionEngine
from app.evidence.hashing import hash_file
from app.evidence.snapshot import EVIDENCE_ROOT, save_snapshot

VIOLATION_COOLDOWN_SECONDS = 30


class DetectionPipeline:
    def __init__(self, camera: Camera):
        self.camera = camera

        self.conn = get_connection(config.DATABASE_PATH)
        self.camera_repo = CameraRepository(self.conn)
        self.violation_repo = ViolationRepository(self.conn)

        capture_service = FrameCaptureService(camera)
        capture_service.open()
        self.resilient_capture = ResilientCapture(capture_service, self.camera_repo)

        self.engine = DetectionEngine(config.MODEL_PATH, config.CONFIDENCE_THRESHOLD)

        self.alert_sender = None
        if config.GMAIL_ADDRESS and config.GMAIL_APP_PASSWORD and config.ALERT_RECIPIENTS:
            self.alert_sender = EmailAlertSender(
                config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD, config.ALERT_RECIPIENTS
            )
        else:
            print(f"[{camera.id}] Email alerts disabled - GMAIL_ADDRESS/"
                  f"GMAIL_APP_PASSWORD/ALERT_RECIPIENTS not all set (check .env)")

        self.last_alert_time = {}

    def run_once(self) -> int:
        frame = self.resilient_capture.read_frame()
        if frame is None:
            return 0

        normalized = letterbox(frame.image)
        detections = self.engine.get_violations(normalized)

        for detection in detections:
            self._handle_violation(frame, detection)

        return len(detections)

    def _handle_violation(self, frame, detection) -> None:
        cooldown_key = (frame.camera_id, frame.zone, detection.class_label)
        last_time = self.last_alert_time.get(cooldown_key)
        now = time.monotonic()

        if last_time is not None and (now - last_time) < VIOLATION_COOLDOWN_SECONDS:
            return

        self.last_alert_time[cooldown_key] = now

        original_height, original_width = frame.image.shape[:2]
        original_bbox = letterbox_to_original_coords(detection.bbox, original_width, original_height)

        relative_path = save_snapshot(
            frame.image, frame.camera_id, frame.zone, frame.timestamp,
            violation_class=detection.class_label, bbox=original_bbox, confidence=detection.confidence,
        )
        full_path = EVIDENCE_ROOT / relative_path
        snapshot_hash = hash_file(str(full_path))

        violation = Violation(
            camera_id=frame.camera_id,
            zone=frame.zone,
            violation_class=detection.class_label,
            confidence=detection.confidence,
            timestamp=frame.timestamp,
            snapshot_path=relative_path,
            snapshot_hash=snapshot_hash,
        )
        new_id = self.violation_repo.save(violation)
        violation.id = new_id
        print(f"[{frame.camera_id}] Violation #{new_id}: {detection.class_label} "
              f"({detection.confidence:.2f}) -> {relative_path}")

        if self.alert_sender is not None:
            self.alert_sender.send_violation_alert(violation)

    def run_forever(self, interval_seconds: float = config.CAPTURE_INTERVAL_SECONDS) -> None:
        print(f"[{self.camera.id}] Pipeline started. Press Ctrl+C to stop.")
        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"\n[{self.camera.id}] Stopping...")
        finally:
            self.resilient_capture.capture_service.release()
            self.conn.close()