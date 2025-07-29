"""
Database operations for AI Voice Generator.
"""

import sqlite3
from contextlib import contextmanager

from .config import DB_PATH


def init_database():
    """Initialize SQLite database for history storage."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                service TEXT NOT NULL,
                voice TEXT NOT NULL,
                text_snippet TEXT,
                filename TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT
            )
        """
        )
        conn.commit()


@contextmanager
def get_db_connection():
    """Get database connection with automatic closing."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()
