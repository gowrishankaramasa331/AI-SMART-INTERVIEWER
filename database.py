"""
AI Smart Interview System — Database Layer (SQLite)
"""
import sqlite3
import os
from config import DATABASE_PATH


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            college TEXT DEFAULT '',
            branch TEXT DEFAULT '',
            year TEXT DEFAULT '',
            skills TEXT DEFAULT '',
            career_goal TEXT DEFAULT '',
            resume_filename TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS interview_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            interview_type TEXT NOT NULL,
            difficulty TEXT NOT NULL DEFAULT 'medium',
            num_questions INTEGER NOT NULL DEFAULT 5,
            overall_score REAL DEFAULT 0,
            technical_knowledge REAL DEFAULT 0,
            communication REAL DEFAULT 0,
            confidence REAL DEFAULT 0,
            relevance REAL DEFAULT 0,
            clarity REAL DEFAULT 0,
            problem_solving REAL DEFAULT 0,
            strengths TEXT DEFAULT '[]',
            weaknesses TEXT DEFAULT '[]',
            improvements TEXT DEFAULT '[]',
            recommendations TEXT DEFAULT '[]',
            feedback_summary TEXT DEFAULT '',
            readiness_pct REAL DEFAULT 0,
            status TEXT DEFAULT 'in_progress',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            answer_text TEXT DEFAULT '',
            score REAL DEFAULT 0,
            technical_knowledge REAL DEFAULT 0,
            communication REAL DEFAULT 0,
            confidence REAL DEFAULT 0,
            relevance REAL DEFAULT 0,
            clarity REAL DEFAULT 0,
            problem_solving REAL DEFAULT 0,
            feedback TEXT DEFAULT '',
            status TEXT DEFAULT '',
            perfect_answer TEXT DEFAULT '',
            improvement TEXT DEFAULT '',
            is_followup INTEGER DEFAULT 0,
            answered_at TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_student ON interview_sessions(student_id);
        CREATE INDEX IF NOT EXISTS idx_questions_session ON interview_questions(session_id);
    """)

    # Ensure existing databases have the new columns
    cursor.execute("PRAGMA table_info(interview_questions)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    for col in ['status', 'perfect_answer', 'improvement']:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE interview_questions ADD COLUMN {col} TEXT DEFAULT ''")

    conn.commit()
    conn.close()


# ── Student CRUD ──────────────────────────────────────────

def create_student(name, email, password_hash, college=''):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO students (name, email, password_hash, college) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, college)
        )
        conn.commit()
        student = conn.execute(
            "SELECT * FROM students WHERE email = ?", (email,)).fetchone()
        return dict(student) if student else None
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_student_by_email(email):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(student) if student else None


def get_student_by_id(student_id):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(student) if student else None


def update_student(student_id, **kwargs):
    conn = get_db()
    allowed = ['name', 'college', 'branch', 'year',
               'skills', 'career_goal', 'resume_filename']
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        conn.close()
        return False
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [student_id]
    conn.execute(
        f"UPDATE students SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
    conn.commit()
    conn.close()
    return True


# ── Interview Session CRUD ────────────────────────────────

def create_session(student_id, interview_type, difficulty, num_questions):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO interview_sessions (student_id, interview_type, difficulty, num_questions)
           VALUES (?, ?, ?, ?)""",
        (student_id, interview_type, difficulty, num_questions)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_session(session_id):
    conn = get_db()
    session = conn.execute(
        "SELECT * FROM interview_sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(session) if session else None


def update_session(session_id, **kwargs):
    conn = get_db()
    allowed = [
        'overall_score', 'technical_knowledge', 'communication', 'confidence',
        'relevance', 'clarity', 'problem_solving', 'strengths', 'weaknesses',
        'improvements', 'recommendations', 'feedback_summary', 'readiness_pct',
        'status', 'completed_at'
    ]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        conn.close()
        return
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [session_id]
    conn.execute(
        f"UPDATE interview_sessions SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_student_sessions(student_id, limit=50):
    conn = get_db()
    sessions = conn.execute(
        """SELECT * FROM interview_sessions WHERE student_id = ?
           ORDER BY started_at DESC LIMIT ?""",
        (student_id, limit)
    ).fetchall()
    conn.close()
    return [dict(s) for s in sessions]


# ── Interview Questions CRUD ──────────────────────────────

def add_question(session_id, question_number, question_text, is_followup=False):
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO interview_questions (session_id, question_number, question_text, is_followup)
           VALUES (?, ?, ?, ?)""",
        (session_id, question_number, question_text, 1 if is_followup else 0)
    )
    qid = cursor.lastrowid
    conn.commit()
    conn.close()
    return qid


def update_question(question_id, **kwargs):
    conn = get_db()
    allowed = [
        'answer_text', 'score', 'technical_knowledge', 'communication',
        'confidence', 'relevance', 'clarity', 'problem_solving', 'feedback',
        'status', 'perfect_answer', 'improvement', 'answered_at'
    ]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        conn.close()
        return
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [question_id]
    conn.execute(
        f"UPDATE interview_questions SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_session_questions(session_id):
    conn = get_db()
    questions = conn.execute(
        "SELECT * FROM interview_questions WHERE session_id = ? ORDER BY question_number",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(q) for q in questions]


def get_question(question_id):
    conn = get_db()
    q = conn.execute(
        "SELECT * FROM interview_questions WHERE id = ?", (question_id,)).fetchone()
    conn.close()
    return dict(q) if q else None


def get_student_recent_questions(student_id, limit=50):
    """Retrieve recently asked question texts for this student to avoid repetition."""
    conn = get_db()
    rows = conn.execute(
        """SELECT q.question_text 
           FROM interview_questions q
           JOIN interview_sessions s ON q.session_id = s.id
           WHERE s.student_id = ?
           ORDER BY q.id DESC LIMIT ?""",
        (student_id, limit)
    ).fetchall()
    conn.close()
    return [r['question_text'] for r in rows if r['question_text']]


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
