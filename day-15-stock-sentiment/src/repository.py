from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Optional, Tuple

from .db import get_connection, initialize_db


class Repository:
    """
    Handles all DB operations for the sentiment tracker.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.conn = get_connection(db_path)
        initialize_db(self.conn)

    # -------------------
    # Raw news operations
    # -------------------
    def insert_raw_news(
        self, ticker: str, headline: str, source: str, published_at: str
    ) -> Optional[int]:
        """
        Inserts a raw headline.
        Returns the new row ID, or None if duplicate.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO raw_news (ticker, headline, source, published_at)
                VALUES (?, ?, ?, ?)
                """,
                (ticker.upper(), headline, source, published_at),
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Duplicate headline
            return None

    def fetch_all_raw_news(self) -> List[sqlite3.Row]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM raw_news")
        return cursor.fetchall()

    # ---------------------
    # Scored news operations
    # ---------------------
    def insert_scored_news(self, raw_id: int, score: int) -> Optional[int]:
        """
        Inserts a scored headline linked to raw_news.
        Returns the new row ID, or None if empty.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO scored_news (raw_id, score)
            VALUES (?, ?)
            """,
            (raw_id, score),
        )
        self.conn.commit()
        return cursor.lastrowid

    def fetch_scored_news_since(
        self, last_id: Optional[int] = None
    ) -> List[sqlite3.Row]:
        """
        Fetch scored_news rows with id > last_id.
        If last_id is None, fetch all.
        """
        cursor = self.conn.cursor()
        if last_id is None:
            cursor.execute("SELECT * FROM scored_news")
        else:
            cursor.execute("SELECT * FROM scored_news WHERE id > ?", (last_id,))
        return cursor.fetchall()

    # -------------------
    # Daily aggregate operations
    # -------------------
    def upsert_daily_aggregate(
        self,
        ticker: str,
        date: str,
        avg_score: float,
        volume: int,
        positive_ratio: float,
        negative_ratio: float,
    ) -> None:
        """
        Inserts or updates daily aggregate for a ticker/date.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO daily_aggregate
                (ticker, date, avg_score, volume, positive_ratio, negative_ratio)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) DO UPDATE SET
                avg_score=excluded.avg_score,
                volume=excluded.volume,
                positive_ratio=excluded.positive_ratio,
                negative_ratio=excluded.negative_ratio,
                last_updated=CURRENT_TIMESTAMP
            """,
            (ticker, date, avg_score, volume, positive_ratio, negative_ratio),
        )
        self.conn.commit()

    def fetch_daily_aggregates(self, ticker: Optional[str] = None) -> List[sqlite3.Row]:
        """
        Fetch all daily aggregates, optionally filtered by ticker.
        """
        cursor = self.conn.cursor()
        if ticker is None:
            cursor.execute("SELECT * FROM daily_aggregate ORDER BY date ASC")
        else:
            cursor.execute(
                "SELECT * FROM daily_aggregate WHERE ticker=? ORDER BY date ASC",
                (ticker.upper(),),
            )
        return cursor.fetchall()

    # -------------------
    # Utility
    # -------------------
    def get_last_scored_id(self) -> Optional[int]:
        """
        Return the max scored_news id, or None if table empty.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) as max_id FROM scored_news")
        row = cursor.fetchone()
        return row["max_id"] if row["max_id"] is not None else None
