"""
db.py
------
SQLite persistence layer for the portfolio version of the resume
screening system. Stores job sessions, candidates, statuses, and notes
so data survives between app restarts.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "screening_data.db"


def get_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all required tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            job_description TEXT,
            created_at TEXT,
            browser_id TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(sessions)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if "browser_id" not in existing_columns:
        cursor.execute("ALTER TABLE sessions ADD COLUMN browser_id TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            name TEXT,
            email TEXT,
            overall_score REAL,
            data_json TEXT,
            status TEXT DEFAULT 'New',
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            note_text TEXT,
            created_at TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)

    conn.commit()
    conn.close()

def create_session(job_title: str, job_description: str, browser_id: str) -> int:
    """Create a new screening session (one job posting) tied to a browser, and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (job_title, job_description, created_at, browser_id) VALUES (?, ?, ?, ?)",
        (job_title, job_description, datetime.now().isoformat(), browser_id),
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def get_all_sessions(browser_id: str) -> list:
    """Return sessions created by this browser, most recent first.

    Sessions created before this feature existed have no browser_id (NULL) —
    those are included too so old test data doesn't just disappear.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sessions WHERE browser_id = ? OR browser_id IS NULL ORDER BY created_at DESC",
        (browser_id,),
    )
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions


def get_session(session_id: int) -> dict:
    """Return a single session by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_candidate(session_id: int, candidate_data: dict) -> int:
    """Save a scored candidate to a session, storing the full dict as JSON."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO candidates (session_id, name, email, overall_score, data_json, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            candidate_data["name"],
            candidate_data["email"],
            candidate_data["overall"],
            json.dumps(candidate_data),
            "New",
        ),
    )
    conn.commit()
    candidate_id = cursor.lastrowid
    conn.close()
    return candidate_id


def get_candidates_for_session(session_id: int) -> list:
    """Return all candidates for a session, ranked by overall score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM candidates WHERE session_id = ? ORDER BY overall_score DESC",
        (session_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    candidates = []
    for row in rows:
        c = dict(row)
        c["data"] = json.loads(c["data_json"])
        candidates.append(c)
    return candidates


def update_candidate_status(candidate_id: int, new_status: str):
    """Update a candidate's status (e.g. Shortlisted, Interview, Rejected)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE candidates SET status = ? WHERE id = ?",
        (new_status, candidate_id),
    )
    conn.commit()
    conn.close()

def delete_session(session_id: int):
    """Delete a session along with all its candidates and their notes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM notes WHERE candidate_id IN (SELECT id FROM candidates WHERE session_id = ?)",
        (session_id,),
    )
    cursor.execute("DELETE FROM candidates WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def add_note(candidate_id: int, note_text: str) -> int:
    """Add a private recruiter note for a candidate."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (candidate_id, note_text, created_at) VALUES (?, ?, ?)",
        (candidate_id, note_text, datetime.now().isoformat()),
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id


def get_notes_for_candidate(candidate_id: int) -> list:
    """Return all notes for a candidate, most recent first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM notes WHERE candidate_id = ? ORDER BY created_at DESC",
        (candidate_id,),
    )
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notes