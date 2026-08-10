from flask import Flask, jsonify

from app.api.cameras import cameras_bp
from app.api.violations import violations_bp
from app.dashboard.routes import dashboard_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(violations_bp)
    app.register_blueprint(cameras_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/api/health")
    def health():
        """Confirms the API process itself is running - NOT that detection is
        active. Camera monitoring status is a separate concern, readable from
        cameras.status/last_seen_at via /api/cameras."""
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)