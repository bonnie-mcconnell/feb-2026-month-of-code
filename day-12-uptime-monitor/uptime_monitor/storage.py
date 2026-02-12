import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import CheckResult


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_parent_dir()
        self._init_db()

    def _ensure_parent_dir(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL
                        CHECK(status IN ('UP','DEGRADED','DOWN')),
                    response_time REAL,
                    error TEXT
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_checks_url_timestamp
                ON checks (url, timestamp DESC);
                """
            )

    def insert_check(self, result: CheckResult) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO checks (url, timestamp, status, response_time, error)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    result.url,
                    result.timestamp,
                    result.status,
                    result.response_time,
                    result.error,
                ),
            )

    def get_last_check(self, url: str) -> Optional[CheckResult]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT url, timestamp, status, response_time, error
                FROM checks
                WHERE url = ?
                ORDER BY timestamp DESC
                LIMIT 1;
                """,
                (url,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return CheckResult(*row)

    def get_history(self, url: str, limit: int = 20) -> List[CheckResult]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT url, timestamp, status, response_time, error
                FROM checks
                WHERE url = ?
                ORDER BY timestamp DESC
                LIMIT ?;
                """,
                (url, limit),
            )
            rows = cursor.fetchall()

        return [CheckResult(*r) for r in rows]

    def get_summary(self, url: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'UP' THEN 1 ELSE 0 END) as up_count,
                    SUM(CASE WHEN status = 'DOWN' THEN 1 ELSE 0 END) as down_count,
                    SUM(CASE WHEN status = 'DEGRADED' THEN 1 ELSE 0 END) as degraded_count
                FROM checks
                WHERE url = ?;
                """,
                (url,),
            )
            row = cursor.fetchone()

            last_cursor = conn.execute(
                """
                SELECT status, timestamp
                FROM checks
                WHERE url = ?
                ORDER BY timestamp DESC
                LIMIT 1;
                """,
                (url,),
            )
            last_row = last_cursor.fetchone()

        if not row or row[0] == 0:
            return None

        total = row[0] or 0
        up_count = row[1] or 0
        down_count = row[2] or 0
        degraded_count = row[3] or 0

        uptime_pct = (up_count / total) * 100 if total else 0.0

        return {
            "total_checks": total,
            "up_count": up_count,
            "down_count": down_count,
            "degraded_count": degraded_count,
            "uptime_pct": uptime_pct,
            "last_status": last_row[0] if last_row else None,
            "last_timestamp": last_row[1] if last_row else None,
        }
