"""Capa SQLite: esquema, conexión por petición y datos iniciales."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from webapp import config
from webapp.security import hash_password

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'student'
                  CHECK (role IN ('student', 'teacher')),
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id         TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);

CREATE TABLE IF NOT EXISTS lesson_progress (
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_slug   TEXT NOT NULL,
    lesson_slug   TEXT NOT NULL,
    completed     INTEGER NOT NULL DEFAULT 0,
    first_seen_at TEXT NOT NULL,
    last_seen_at  TEXT NOT NULL,
    completed_at  TEXT,
    views         INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, course_slug, lesson_slug)
);

CREATE INDEX IF NOT EXISTS idx_progress_course
    ON lesson_progress(user_id, course_slug);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_slug  TEXT NOT NULL,
    quiz_id      TEXT NOT NULL,
    score        INTEGER NOT NULL,
    total        INTEGER NOT NULL,
    answers_json TEXT NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_attempts_user_quiz
    ON quiz_attempts(user_id, course_slug, quiz_id, created_at);

CREATE TABLE IF NOT EXISTS notes (
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_slug TEXT NOT NULL,
    lesson_slug TEXT NOT NULL,
    body        TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (user_id, course_slug, lesson_slug)
);

CREATE TABLE IF NOT EXISTS bookmarks (
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_slug TEXT NOT NULL,
    lesson_slug TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    PRIMARY KEY (user_id, course_slug, lesson_slug)
);

CREATE TABLE IF NOT EXISTS activity (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day     TEXT NOT NULL,
    kind    TEXT NOT NULL,
    count   INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, day, kind)
);

CREATE TABLE IF NOT EXISTS authoring_jobs (
    id           TEXT PRIMARY KEY,
    owner_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    source_names TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'queued'
                 CHECK (status IN ('queued', 'extracting', 'generating',
                                   'validating', 'ready', 'failed', 'cancelled')),
    provider     TEXT NOT NULL,
    model        TEXT NOT NULL,
    languages    TEXT NOT NULL,
    course_slug  TEXT,
    error        TEXT,
    created_at   TEXT NOT NULL,
    started_at   TEXT,
    finished_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_authoring_jobs_owner
    ON authoring_jobs(owner_id, created_at DESC);

CREATE TABLE IF NOT EXISTS generated_courses (
    slug         TEXT PRIMARY KEY,
    owner_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id       TEXT,
    title        TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'draft'
                 CHECK (status IN ('draft', 'published')),
    package_json TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_generated_courses_status
    ON generated_courses(status, updated_at DESC);
"""


SCHEMA_VERSION = 3


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _prepare_legacy_tables(conn: sqlite3.Connection) -> None:
    """Aparta tablas de la etapa de un solo curso antes de crear el esquema v2.

    Se hace antes de ``executescript`` porque los índices nuevos referencian
    ``course_slug`` y fallarían sobre una tabla antigua.
    """
    for table in ("lesson_progress", "quiz_attempts", "notes", "bookmarks"):
        if _table_exists(conn, table) and "course_slug" not in _columns(conn, table):
            conn.execute(f"ALTER TABLE {table} RENAME TO {table}_legacy")


def _copy_legacy_tables(conn: sqlite3.Connection) -> None:
    """Copia los datos antiguos al curso por defecto y elimina las tablas v1."""
    course = config.DEFAULT_COURSE_SLUG

    if _table_exists(conn, "lesson_progress_legacy"):
        conn.execute(
            """INSERT OR IGNORE INTO lesson_progress
                   (user_id, course_slug, lesson_slug, completed, first_seen_at,
                    last_seen_at, completed_at, views)
               SELECT user_id, ?, lesson_slug, completed, first_seen_at,
                      last_seen_at, completed_at, views
               FROM lesson_progress_legacy""",
            (course,),
        )
        conn.execute("DROP TABLE lesson_progress_legacy")

    if _table_exists(conn, "quiz_attempts_legacy"):
        conn.execute(
            """INSERT OR IGNORE INTO quiz_attempts
                   (id, user_id, course_slug, quiz_id, score, total,
                    answers_json, created_at)
               SELECT id, user_id, ?, quiz_id, score, total,
                      answers_json, created_at
               FROM quiz_attempts_legacy""",
            (course,),
        )
        conn.execute("DROP TABLE quiz_attempts_legacy")

    if _table_exists(conn, "notes_legacy"):
        conn.execute(
            """INSERT OR IGNORE INTO notes
                   (user_id, course_slug, lesson_slug, body, updated_at)
               SELECT user_id, ?, lesson_slug, body, updated_at
               FROM notes_legacy""",
            (course,),
        )
        conn.execute("DROP TABLE notes_legacy")

    if _table_exists(conn, "bookmarks_legacy"):
        conn.execute(
            """INSERT OR IGNORE INTO bookmarks
                   (user_id, course_slug, lesson_slug, created_at)
               SELECT user_id, ?, lesson_slug, created_at
               FROM bookmarks_legacy""",
            (course,),
        )
        conn.execute("DROP TABLE bookmarks_legacy")


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    # FastAPI puede ejecutar la dependencia y el endpoint en hilos distintos.
    # Cada petición tiene su propia conexión, así que desactivar la comprobación
    # de hilo es seguro y evita errores en el threadpool de Starlette.
    conn = sqlite3.connect(path, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db(db_path: Path | None = None) -> None:
    """Crea el esquema y siembra las cuentas de demostración.

    Es idempotente: se puede llamar en cada arranque y en los tests.
    """
    conn = connect(db_path)
    try:
        _prepare_legacy_tables(conn)
        conn.executescript(SCHEMA)
        _copy_legacy_tables(conn)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        now = utcnow()
        demo = (
            config.DEMO_EMAIL,
            "Estudiante demo",
            hash_password(config.DEMO_PASSWORD),
            "student",
            now,
        )
        teacher = (
            config.TEACHER_EMAIL,
            "Profesora",
            hash_password(config.TEACHER_PASSWORD),
            "teacher",
            now,
        )
        conn.executemany(
            """INSERT OR IGNORE INTO users (email, name, password_hash, role, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            [demo, teacher],
        )
        conn.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
        conn.commit()
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Dependencia de FastAPI: una conexión por petición."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def session_scope(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Contexto para scripts y tareas fuera de una petición HTTP."""
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
