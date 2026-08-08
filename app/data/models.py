from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SourceType(str, Enum):
    """Camera source types supported by the camera abstraction layer."""
    WEBCAM = "webcam"
    RTSP = "rtsp"
    HTTP = "http"
    ONVIF = "onvif"


class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class Role(str, Enum):
    """All three operational roles share equal evidence-viewing access."""
    SITE_MANAGER = "site_manager"
    SITE_SUPERVISOR = "site_supervisor"
    SAFETY_OFFICER = "safety_officer"
    ADMIN = "admin"


def _utc_now_iso() -> str:
    """Server-side timestamp helper (NFR8) - never trust a camera's own clock."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Camera:
    id: str                                  # stable camera_id, e.g. "cam-gate-01"
    name: str
    source_type: SourceType
    source_uri: str                          # device index, rtsp://, http://, or ONVIF-resolved URI
    zone: str
    credentials_ref: Optional[str] = None    # reference/secret name, never a plaintext password
    status: CameraStatus = CameraStatus.UNKNOWN
    created_at: str = field(default_factory=_utc_now_iso)
    last_seen_at: Optional[str] = None       # updated by the resilience layer's health check

    @staticmethod
    def from_row(row: tuple) -> "Camera":
        return Camera(
            id=row[0], name=row[1], source_type=SourceType(row[2]), source_uri=row[3],
            zone=row[4], credentials_ref=row[5], status=CameraStatus(row[6]),
            created_at=row[7], last_seen_at=row[8],
        )


@dataclass
class Violation:
    camera_id: str                           # frame-camera tagging (FR9 / Section 6.2)
    zone: str
    violation_class: str                     # e.g. NO-Hardhat, NO-Mask, Fall-Detected
    snapshot_path: str                       # confirmed convention: camera_id/date/timestamp.jpg
    snapshot_hash: str                       # confirmed default: SHA-256 hex digest (NFR7)
    id: Optional[int] = None                 # set once persisted (AUTOINCREMENT)
    confidence: Optional[float] = None
    timestamp: str = field(default_factory=_utc_now_iso)   # server-side (NFR8)
    resolved: bool = False                   # FR6 - permissions model still pending validation
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    created_at: str = field(default_factory=_utc_now_iso)

    @staticmethod
    def from_row(row: tuple) -> "Violation":
        return Violation(
            id=row[0], camera_id=row[1], zone=row[2], violation_class=row[3], confidence=row[4],
            timestamp=row[5], snapshot_path=row[6], snapshot_hash=row[7],
            resolved=bool(row[8]), resolved_by=row[9], resolved_at=row[10], created_at=row[11],
        )


@dataclass
class User:
    id: str
    name: str
    role: Role
    email: Optional[str] = None

    @staticmethod
    def from_row(row: tuple) -> "User":
        return User(id=row[0], name=row[1], role=Role(row[2]), email=row[3])