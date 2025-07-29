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


def reset_database():
    """Reset database to clean state."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DROP TABLE IF EXISTS generation_history")
        conn.commit()
    init_database()


def add_sample_data():
    """Add sample generation history for demo purposes."""
    sample_entries = [
        {
            "title": "Welcome Message",
            "service": "openai", 
            "voice": "alloy",
            "text_snippet": "Welcome to AI Voice Generator! This is a sample...",
            "filename": "sample_welcome_openai.mp3",
            "file_path": "sample_data/sample_welcome_openai.mp3"
        },
        {
            "title": "Demo Content",
            "service": "elevenlabs",
            "voice": "Rachel", 
            "text_snippet": "This is sample content to demonstrate the history...",
            "filename": "sample_demo_elevenlabs.mp3",
            "file_path": "sample_data/sample_demo_elevenlabs.mp3"
        }
    ]
    
    with sqlite3.connect(DB_PATH) as conn:
        for entry in sample_entries:
            conn.execute(
                """INSERT INTO generation_history 
                   (title, service, voice, text_snippet, filename, file_path)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (entry["title"], entry["service"], entry["voice"], 
                 entry["text_snippet"], entry["filename"], entry["file_path"])
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
