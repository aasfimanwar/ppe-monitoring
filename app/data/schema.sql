PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cameras (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    source_type     TEXT NOT NULL CHECK (source_type IN ('webcam', 'rtsp', 'http', 'onvif')),
    source_uri      TEXT NOT NULL,
    zone            TEXT NOT NULL,
    credentials_ref TEXT,
    status          TEXT NOT NULL DEFAULT 'unknown'
                        CHECK (status IN ('online', 'offline', 'error', 'unknown')),
    created_at      TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
    last_seen_at    TEXT
);

CREATE TABLE IF NOT EXISTS violations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id       TEXT NOT NULL REFERENCES cameras(id),
    zone            TEXT NOT NULL,
    class           TEXT NOT NULL,
    confidence      REAL,
    timestamp       TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now')),
    snapshot_path   TEXT NOT NULL,
    snapshot_hash   TEXT NOT NULL,
    resolved        INTEGER NOT NULL DEFAULT 0 CHECK (resolved IN (0, 1)),
    resolved_by     TEXT,
    resolved_at     TEXT,
    created_at      TEXT NOT NULL DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_violations_camera    ON violations(camera_id);
CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp);
CREATE INDEX IF NOT EXISTS idx_violations_resolved  ON violations(resolved);

-- All three roles share equal evidence-viewing access (Section 6.4) - this table exists for
-- identity/audit purposes (who resolved what), not to gate who can VIEW a violation's evidence.
CREATE TABLE IF NOT EXISTS users (
    id      TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    role    TEXT NOT NULL CHECK (role IN ('site_manager', 'site_supervisor', 'safety_officer', 'admin')),
    email   TEXT
);