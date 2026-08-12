import sqlite3
import sys

from app import config


def migrate(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(violations)").fetchall()]
        if "escalated" in columns:
            print("Column 'escalated' already exists - nothing to do.")
            return

        conn.execute(
            "ALTER TABLE violations ADD COLUMN escalated INTEGER NOT NULL DEFAULT 0"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_violations_zone ON violations(zone)")
        conn.commit()
        print("Migration complete: 'escalated' column added, all existing rows default to 0.")
    finally:
        conn.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else config.DATABASE_PATH
    migrate(target)