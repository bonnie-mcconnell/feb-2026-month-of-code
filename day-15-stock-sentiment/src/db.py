import sqlite3
from pathlib import Path
from typing import Union

DB_PATH = Path("data/sentiment.db")


def get_connection(db_path: Union[Path, str, None] = None) -> sqlite3.Connection:
    """
    Returns a SQLite connection.
    Creates the database file if it does not exist.
    """

    # Use default DB path if none provided
    if db_path is None:
        db_path = DB_PATH

    # In-memory DB for tests
    if isinstance(db_path, str):
        conn = sqlite3.connect(db_path)
    else:
        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))

    conn.row_factory = sqlite3.Row
    return conn


def initialize_db(conn: sqlite3.Connection) -> None:
    """
    Create tables if they do not exist.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            headline TEXT NOT NULL,
            source TEXT NOT NULL,
            published_at TEXT NOT NULL,
            UNIQUE(ticker, headline, published_at)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scored_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_id INTEGER NOT NULL,
            score REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(raw_id) REFERENCES raw_news(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_aggregate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            avg_score REAL NOT NULL,
            volume INTEGER NOT NULL,
            positive_ratio REAL NOT NULL,
            negative_ratio REAL NOT NULL,
            last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, date)
        )
        """
    )

    conn.commit()


if __name__ == "__main__":
    connection = get_connection()
    initialize_db(connection)
    print(f"Database initialized at {DB_PATH}")
