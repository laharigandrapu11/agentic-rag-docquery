# Populated in F7 - Conversation Memory
# Lightweight SQLite store — one row per turn, keyed by session_id.
# No ORM needed; stdlib sqlite3 is sufficient for single-process use.

import sqlite3
import json
from app.core.config import settings


def _get_conn() -> sqlite3.Connection:
    """Open a connection to the SQLite DB and ensure the turns table exists."""
    conn = sqlite3.connect(settings.sqlite_db_path, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS turns (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role      TEXT NOT NULL,   -- 'user' or 'assistant'
            content   TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def get_history(session_id: str) -> list[dict]:
    """Return all turns for a session as a list of {role, content} dicts, oldest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT role, content FROM turns WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]


def append_turn(session_id: str, role: str, content: str) -> None:
    """Append one turn (user question or assistant answer) to the session history."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO turns (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()


def clear_session(session_id: str) -> None:
    """Delete all turns for a session — called when user clicks 'New session'."""
    conn = _get_conn()
    conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()