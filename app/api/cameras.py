from dataclasses import asdict

from flask import Blueprint, jsonify

from app import config
from app.data.repository import CameraRepository, get_connection

cameras_bp = Blueprint("cameras", __name__, url_prefix="/api/cameras")


def _get_camera_repo() -> CameraRepository:
    conn = get_connection(config.DATABASE_PATH)
    return CameraRepository(conn)


@cameras_bp.route("", methods=["GET"])
def list_cameras():
    """All registered cameras, with their current status and last_seen_at."""
    repo = _get_camera_repo()
    cameras = repo.list_all()
    return jsonify([_serialize_camera(c) for c in cameras])


@cameras_bp.route("/<camera_id>", methods=["GET"])
def get_camera(camera_id):
    """One specific camera by id."""
    repo = _get_camera_repo()
    camera = repo.get(camera_id)
    if camera is None:
        return jsonify({"error": "camera not found"}), 404
    return jsonify(_serialize_camera(camera))


def _serialize_camera(camera) -> dict:
    """Converts a Camera dataclass to JSON-safe data - source_type and status
    are enums (SourceType, CameraStatus), which jsonify cannot serialize
    directly, so .value pulls out the plain string each one wraps."""
    data = asdict(camera)
    data["source_type"] = camera.source_type.value
    data["status"] = camera.status.value
    return data