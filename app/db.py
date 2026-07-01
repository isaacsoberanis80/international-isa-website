import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "leads.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            brokerage TEXT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_lead(name, email, phone, brokerage, message):
    conn = get_connection()
    conn.execute(
        "INSERT INTO leads (name, email, phone, brokerage, message) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, brokerage, message),
    )
    conn.commit()
    conn.close()
