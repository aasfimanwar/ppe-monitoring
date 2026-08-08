import sqlite3
from typing import List, Optional

from app.data.models import Camera, CameraStatus, Violation


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class CameraRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, camera: Camera) -> None:
        self.conn.execute(
            """
            INSERT INTO cameras (id, name, source_type, source_uri, zone,
                                  credentials_ref, status, created_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (camera.id, camera.name, camera.source_type.value, camera.source_uri,
             camera.zone, camera.credentials_ref, camera.status.value,
             camera.created_at, camera.last_seen_at),
        )
        self.conn.commit()

    def get(self, camera_id: str) -> Optional[Camera]:
        row = self.conn.execute("SELECT * FROM cameras WHERE id = ?", (camera_id,)).fetchone()
        return Camera.from_row(row) if row else None

    def list_all(self) -> List[Camera]:
        rows = self.conn.execute("SELECT * FROM cameras").fetchall()
        return [Camera.from_row(row) for row in rows]

    def update_status(self, camera_id: str, status: CameraStatus, last_seen_at: str) -> None:
        self.conn.execute(
            "UPDATE cameras SET status = ?, last_seen_at = ? WHERE id = ?",
            (status.value, last_seen_at, camera_id),
        )
        self.conn.commit()


class ViolationRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, violation: Violation) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO violations (camera_id, zone, class, confidence, timestamp,
                                     snapshot_path, snapshot_hash, resolved,
                                     resolved_by, resolved_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (violation.camera_id, violation.zone, violation.violation_class,
             violation.confidence, violation.timestamp, violation.snapshot_path,
             violation.snapshot_hash, int(violation.resolved), violation.resolved_by,
             violation.resolved_at, violation.created_at),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self) -> List[Violation]:
        rows = self.conn.execute("SELECT * FROM violations ORDER BY timestamp DESC").fetchall()
        return [Violation.from_row(row) for row in rows]

    def get_by_camera(self, camera_id: str) -> List[Violation]:
        rows = self.conn.execute(
            "SELECT * FROM violations WHERE camera_id = ? ORDER BY timestamp DESC", (camera_id,)
        ).fetchall()
        return [Violation.from_row(row) for row in rows]

    def mark_resolved(self, violation_id: int, resolved_by: str, resolved_at: str) -> None:
        self.conn.execute(
            "UPDATE violations SET resolved = 1, resolved_by = ?, resolved_at = ? WHERE id = ?",
            (resolved_by, resolved_at, violation_id),
        )
        self.conn.commit()