from dataclasses import asdict
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_from_directory

from app import config
from app.data.repository import ViolationRepository, get_connection

violations_bp = Blueprint("violations", __name__, url_prefix="/api/violations")


def _get_violation_repo() -> ViolationRepository:
    """A fresh connection per request - simple and safe for SQLite under
    Flask's development server. Revisit if this becomes a real bottleneck."""
    conn = get_connection(config.DATABASE_PATH)
    return ViolationRepository(conn)


@violations_bp.route("", methods=["GET"])
def list_violations():
    """All violations, newest first."""
    repo = _get_violation_repo()
    violations = repo.get_all()
    return jsonify([asdict(v) for v in violations])


@violations_bp.route("/camera/<camera_id>", methods=["GET"])
def list_violations_for_camera(camera_id):
    """Violations for one specific camera, newest first."""
    repo = _get_violation_repo()
    violations = repo.get_by_camera(camera_id)
    return jsonify([asdict(v) for v in violations])


@violations_bp.route("/<int:violation_id>/evidence", methods=["GET"])
def get_evidence_photo(violation_id):
    """Serves the actual evidence photo file for one violation - the
    photo/timestamp/camera proof confirmed viewable by all three roles."""
    repo = _get_violation_repo()
    violation = next((v for v in repo.get_all() if v.id == violation_id), None)
    if violation is None:
        return jsonify({"error": "violation not found"}), 404

    directory = config.EVIDENCE_ROOT / violation.snapshot_path
    return send_from_directory(str(directory.parent), directory.name)


@violations_bp.route("/<int:violation_id>/resolve", methods=["PATCH"])
def resolve_violation(violation_id):
    """Marks one violation resolved. Expects a JSON body: {"resolved_by": "<name>"}.

    No identity/permission verification is performed here - see the module
    docstring's Permissions note. resolved_by is trusted as given.
    """
    repo = _get_violation_repo()
    violation = next((v for v in repo.get_all() if v.id == violation_id), None)
    if violation is None:
        return jsonify({"error": "violation not found"}), 404

    body = request.get_json(silent=True) or {}
    resolved_by = body.get("resolved_by")
    if not resolved_by:
        return jsonify({"error": "resolved_by is required in the request body"}), 400

    resolved_at = datetime.now(timezone.utc).isoformat()
    repo.mark_resolved(violation_id, resolved_by, resolved_at)

    updated = next((v for v in repo.get_all() if v.id == violation_id), None)
    return jsonify(asdict(updated))