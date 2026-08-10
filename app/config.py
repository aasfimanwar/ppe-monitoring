from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_PATH = str(PROJECT_ROOT / "violations.db")
MODEL_PATH = str(PROJECT_ROOT / "models" / "ppe_best.pt")
EVIDENCE_ROOT = PROJECT_ROOT / "evidence"

CONFIDENCE_THRESHOLD = 0.25
SNAPSHOT_HASH_ALGORITHM = "sha256"

import os
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
ALERT_RECIPIENTS = [addr.strip() for addr in os.environ.get("ALERT_RECIPIENTS", "").split(",") if addr.strip()]

CAPTURE_INTERVAL_SECONDS = 1.0