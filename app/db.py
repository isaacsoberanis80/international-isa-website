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
            status TEXT NOT NULL DEFAULT 'New',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
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


def get_all_leads():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


def update_lead_status(lead_id, status):
    conn = get_connection()
    conn.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
    conn.commit()
    conn.close()


def create_user(username, password_hash):
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def add_task(user_id, description):
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, description) VALUES (?, ?)",
        (user_id, description),
    )
    conn.commit()
    conn.close()


def get_tasks_for_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY done ASC, created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def complete_task(task_id, user_id):
    conn = get_connection()
    conn.execute(
        "UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    )
    conn.commit()
    conn.close()
