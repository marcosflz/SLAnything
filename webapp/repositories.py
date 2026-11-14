"""Consultas SQL reutilizables.

Los routers no escriben SQL directamente salvo casos muy concretos. Así el
esquema y las reglas de negocio quedan en un único lugar. Todo lo que pertenece
a un curso se filtra por ``course_slug``: el progreso de dos cursos nunca se
mezcla, aunque compartan un slug de lección.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta, timezone

from webapp.db import utcnow


def _today() -> date:
    """Día actual en UTC, igual que el resto de marcas de tiempo."""
    return datetime.now(timezone.utc).date()


# ---------------------------------------------------------------------------
# Usuarios y sesiones
# ---------------------------------------------------------------------------

def get_user_by_email(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
    ).fetchone()


def get_user(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(
    conn: sqlite3.Connection,
    email: str,
    name: str,
    password_hash: str,
    role: str = "student",
) -> sqlite3.Row:
    conn.execute(
        """INSERT INTO users (email, name, password_hash, role, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (email.strip().lower(), name.strip(), password_hash, role, utcnow()),
    )
    user = get_user_by_email(conn, email)
    from webapp import workspaces

    workspaces.ensure_personal_workspace(conn, int(user["id"]), name)
    conn.commit()
    return get_user_by_email(conn, email)  # type: ignore[return-value]


def touch_login(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (utcnow(), user_id))


def create_session(
    conn: sqlite3.Connection,
    user_id: int,
    session_id: str,
    csrf_token: str,
    days: int,
) -> None:
    now = datetime.now(timezone.utc)
    conn.execute(
        """INSERT INTO sessions (id, user_id, csrf_token, created_at, expires_at)
           VALUES (?, ?, ?, ?, ?)""",
        (
            session_id,
            user_id,
            csrf_token,
            now.isoformat(timespec="seconds"),
            (now + timedelta(days=days)).isoformat(timespec="seconds"),
        ),
    )


def delete_session(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


# ---------------------------------------------------------------------------
# Progreso
# ---------------------------------------------------------------------------

def touch_lesson(
    conn: sqlite3.Connection, user_id: int, course_slug: str, slug: str
) -> None:
    now = utcnow()
    conn.execute(
        """INSERT INTO lesson_progress
               (user_id, course_slug, lesson_slug, completed, first_seen_at,
                last_seen_at, views)
           VALUES (?, ?, ?, 0, ?, ?, 1)
           ON CONFLICT(user_id, course_slug, lesson_slug) DO UPDATE SET
               last_seen_at = excluded.last_seen_at,
               views = lesson_progress.views + 1""",
        (user_id, course_slug, slug, now, now),
    )


def set_lesson_completed(
    conn: sqlite3.Connection,
    user_id: int,
    course_slug: str,
    slug: str,
    completed: bool,
) -> None:
    now = utcnow()
    conn.execute(
        """INSERT INTO lesson_progress
               (user_id, course_slug, lesson_slug, completed, first_seen_at,
                last_seen_at, completed_at, views)
           VALUES (?, ?, ?, ?, ?, ?, ?, 0)
           ON CONFLICT(user_id, course_slug, lesson_slug) DO UPDATE SET
               completed = excluded.completed,
               completed_at = excluded.completed_at""",
        (user_id, course_slug, slug, int(completed), now, now, now if completed else None),
    )


def progress_for_user(
    conn: sqlite3.Connection, user_id: int, course_slug: str
) -> dict[str, dict]:
    rows = conn.execute(
        """SELECT * FROM lesson_progress
           WHERE user_id = ? AND course_slug = ?""",
        (user_id, course_slug),
    ).fetchall()
    return {row["lesson_slug"]: dict(row) for row in rows}


def progress_by_course(conn: sqlite3.Connection, user_id: int) -> dict[str, dict[str, dict]]:
    """Progreso agrupado por curso; útil para el catálogo y el dashboard."""
    rows = conn.execute(
        "SELECT * FROM lesson_progress WHERE user_id = ?", (user_id,)
    ).fetchall()
    result: dict[str, dict[str, dict]] = {}
    for row in rows:
        result.setdefault(row["course_slug"], {})[row["lesson_slug"]] = dict(row)
    return result


def get_lesson_progress(
    conn: sqlite3.Connection, user_id: int, course_slug: str, slug: str
) -> dict | None:
    row = conn.execute(
        """SELECT * FROM lesson_progress
           WHERE user_id = ? AND course_slug = ? AND lesson_slug = ?""",
        (user_id, course_slug, slug),
    ).fetchone()
    return dict(row) if row else None


def completion_stats(
    conn: sqlite3.Connection, user_id: int, course_slug: str, total: int
) -> dict:
    row = conn.execute(
        """SELECT COUNT(*) AS completed
           FROM lesson_progress
           WHERE user_id = ? AND course_slug = ? AND completed = 1""",
        (user_id, course_slug),
    ).fetchone()
    completed = int(row["completed"]) if row else 0
    pct = round(completed * 100 / total) if total else 0
    return {"completed": completed, "total": total, "pct": pct}


# ---------------------------------------------------------------------------
# Notas y marcadores
# ---------------------------------------------------------------------------

def get_note(
    conn: sqlite3.Connection, user_id: int, course_slug: str, slug: str
) -> str:
    row = conn.execute(
        """SELECT body FROM notes
           WHERE user_id = ? AND course_slug = ? AND lesson_slug = ?""",
        (user_id, course_slug, slug),
    ).fetchone()
    return row["body"] if row else ""


def save_note(
    conn: sqlite3.Connection,
    user_id: int,
    course_slug: str,
    slug: str,
    body: str,
) -> None:
    conn.execute(
        """INSERT INTO notes (user_id, course_slug, lesson_slug, body, updated_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(user_id, course_slug, lesson_slug) DO UPDATE SET
               body = excluded.body,
               updated_at = excluded.updated_at""",
        (user_id, course_slug, slug, body, utcnow()),
    )


def is_bookmarked(
    conn: sqlite3.Connection, user_id: int, course_slug: str, slug: str
) -> bool:
    row = conn.execute(
        """SELECT 1 FROM bookmarks
           WHERE user_id = ? AND course_slug = ? AND lesson_slug = ?""",
        (user_id, course_slug, slug),
    ).fetchone()
    return row is not None


def toggle_bookmark(
    conn: sqlite3.Connection, user_id: int, course_slug: str, slug: str
) -> bool:
    if is_bookmarked(conn, user_id, course_slug, slug):
        conn.execute(
            """DELETE FROM bookmarks
               WHERE user_id = ? AND course_slug = ? AND lesson_slug = ?""",
            (user_id, course_slug, slug),
        )
        return False
    conn.execute(
        """INSERT INTO bookmarks (user_id, course_slug, lesson_slug, created_at)
           VALUES (?, ?, ?, ?)""",
        (user_id, course_slug, slug, utcnow()),
    )
    return True


def bookmarked_lessons(
    conn: sqlite3.Connection, user_id: int, course_slug: str
) -> set[str]:
    rows = conn.execute(
        """SELECT lesson_slug FROM bookmarks
           WHERE user_id = ? AND course_slug = ?""",
        (user_id, course_slug),
    ).fetchall()
    return {row["lesson_slug"] for row in rows}


# ---------------------------------------------------------------------------
# Actividad y racha
# ---------------------------------------------------------------------------

def record_activity(conn: sqlite3.Connection, user_id: int, kind: str) -> None:
    today = _today().isoformat()
    conn.execute(
        """INSERT INTO activity (user_id, day, kind, count)
           VALUES (?, ?, ?, 1)
           ON CONFLICT(user_id, day, kind) DO UPDATE SET
               count = activity.count + 1""",
        (user_id, today, kind),
    )


def activity_days(conn: sqlite3.Connection, user_id: int, limit: int = 30) -> list[str]:
    rows = conn.execute(
        """SELECT DISTINCT day FROM activity
           WHERE user_id = ?
           ORDER BY day DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    return [row["day"] for row in rows]


def activity_last_days(conn: sqlite3.Connection, user_id: int, days: int = 14) -> list[dict]:
    today = _today()
    start = today - timedelta(days=days - 1)
    rows = conn.execute(
        """SELECT day, SUM(count) AS total FROM activity
           WHERE user_id = ? AND day >= ? AND kind != 'login'
           GROUP BY day""",
        (user_id, start.isoformat()),
    ).fetchall()
    by_day = {row["day"]: int(row["total"]) for row in rows}
    result = []
    for offset in range(days):
        current = start + timedelta(days=offset)
        key = current.isoformat()
        result.append(
            {
                "day": key,
                "label": current.strftime("%d/%m"),
                "count": by_day.get(key, 0),
                "is_today": current == today,
            }
        )
    return result


def current_streak(conn: sqlite3.Connection, user_id: int) -> int:
    rows = conn.execute(
        """SELECT DISTINCT day FROM activity
           WHERE user_id = ? AND kind != 'login' ORDER BY day DESC""",
        (user_id,),
    ).fetchall()
    if not rows:
        return 0
    days = {row["day"] for row in rows}
    cursor = _today()
    if cursor.isoformat() not in days:
        cursor -= timedelta(days=1)
        if cursor.isoformat() not in days:
            return 0
    streak = 0
    while cursor.isoformat() in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------

def create_attempt(
    conn: sqlite3.Connection,
    user_id: int,
    course_slug: str,
    quiz_id: str,
    score: int,
    total: int,
    answers: dict,
) -> int:
    cursor = conn.execute(
        """INSERT INTO quiz_attempts
               (user_id, course_slug, quiz_id, score, total, answers_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            course_slug,
            quiz_id,
            score,
            total,
            json.dumps(answers, ensure_ascii=False),
            utcnow(),
        ),
    )
    return int(cursor.lastrowid)


def get_attempt(
    conn: sqlite3.Connection, attempt_id: int, user_id: int
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM quiz_attempts WHERE id = ? AND user_id = ?",
        (attempt_id, user_id),
    ).fetchone()


def attempts_for_user(
    conn: sqlite3.Connection,
    user_id: int,
    course_slug: str | None = None,
    limit: int = 30,
) -> list[sqlite3.Row]:
    if course_slug is None:
        return conn.execute(
            """SELECT * FROM quiz_attempts
               WHERE user_id = ?
               ORDER BY created_at DESC, id DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    return conn.execute(
        """SELECT * FROM quiz_attempts
           WHERE user_id = ? AND course_slug = ?
           ORDER BY created_at DESC, id DESC
           LIMIT ?""",
        (user_id, course_slug, limit),
    ).fetchall()


def attempts_for_quiz(
    conn: sqlite3.Connection, user_id: int, quiz_id: str
) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT * FROM quiz_attempts
           WHERE user_id = ? AND quiz_id = ?
           ORDER BY created_at DESC, id DESC""",
        (user_id, quiz_id),
    ).fetchall()


def best_attempt(
    conn: sqlite3.Connection, user_id: int, quiz_id: str
) -> sqlite3.Row | None:
    return conn.execute(
        """SELECT * FROM quiz_attempts
           WHERE user_id = ? AND quiz_id = ?
           ORDER BY (score * 1.0 / total) DESC, created_at DESC
           LIMIT 1""",
        (user_id, quiz_id),
    ).fetchone()


def average_score(
    conn: sqlite3.Connection, user_id: int, course_slug: str | None = None
) -> int | None:
    if course_slug is None:
        row = conn.execute(
            """SELECT AVG(score * 100.0 / total) AS avg
               FROM quiz_attempts WHERE user_id = ?""",
            (user_id,),
        ).fetchone()
    else:
        row = conn.execute(
            """SELECT AVG(score * 100.0 / total) AS avg
               FROM quiz_attempts WHERE user_id = ? AND course_slug = ?""",
            (user_id, course_slug),
        ).fetchone()
    return round(row["avg"]) if row and row["avg"] is not None else None


def attempts_passed(conn: sqlite3.Connection, user_id: int, quiz_id: str) -> bool:
    row = conn.execute(
        """SELECT 1 FROM quiz_attempts
           WHERE user_id = ? AND quiz_id = ? AND (score * 100.0 / total) >= 80
           LIMIT 1""",
        (user_id, quiz_id),
    ).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Panel del profesor
# ---------------------------------------------------------------------------

def _student_filter(workspace_id: int | None) -> tuple[str, tuple]:
    if workspace_id is None:
        return "u.role = 'student'", ()
    return (
        """u.id IN (SELECT user_id FROM memberships
                    WHERE workspace_id = ? AND role = 'student')""",
        (workspace_id,),
    )


def teacher_overview(
    conn: sqlite3.Connection,
    workspace_id: int | None = None,
    course_slugs: tuple[str, ...] | None = None,
) -> list[dict]:
    """Una fila por estudiante del espacio, limitada a los cursos indicados."""
    where, params = _student_filter(workspace_id)
    course_clause = ""
    course_params: tuple = ()
    if course_slugs:
        marks = ",".join("?" for _ in course_slugs)
        course_clause = f" AND course_slug IN ({marks})"
        course_params = tuple(course_slugs)
    rows = conn.execute(
        f"""SELECT u.id, u.name, u.email, u.created_at,
                  (SELECT COUNT(*) FROM lesson_progress p
                    WHERE p.user_id = u.id AND p.completed = 1{course_clause}) AS completed,
                  (SELECT MAX(p.last_seen_at) FROM lesson_progress p
                    WHERE p.user_id = u.id{course_clause}) AS last_seen,
                  (SELECT MAX(a.score * 100.0 / a.total) FROM quiz_attempts a
                    WHERE a.user_id = u.id{course_clause}) AS best_score,
                  (SELECT COUNT(*) FROM quiz_attempts a
                    WHERE a.user_id = u.id{course_clause}) AS attempts
           FROM users u
           WHERE {where}
           ORDER BY completed DESC, u.name ASC""",
        course_params * 4 + params,
    ).fetchall()
    return [dict(row) for row in rows]


def teacher_stats(
    conn: sqlite3.Connection,
    total_lessons: int,
    course_slug: str | None = None,
    workspace_id: int | None = None,
) -> dict:
    where, params = _student_filter(workspace_id)
    students = conn.execute(
        f"SELECT COUNT(*) AS n FROM users u WHERE {where}", params
    ).fetchone()["n"]
    course_clause = " AND a.course_slug = ?" if course_slug else ""
    course_params = (course_slug,) if course_slug else ()
    row = conn.execute(
        f"""SELECT COUNT(*) AS n, AVG(a.score * 100.0 / a.total) AS avg
            FROM quiz_attempts a JOIN users u ON u.id = a.user_id
            WHERE {where}{course_clause}""",
        params + course_params,
    ).fetchone()
    cutoff = (_today() - timedelta(days=7)).isoformat()
    active = conn.execute(
        f"""SELECT COUNT(DISTINCT a.user_id) AS n
            FROM activity a JOIN users u ON u.id = a.user_id
            WHERE {where} AND a.kind != 'login' AND a.day >= ?""",
        params + (cutoff,),
    ).fetchone()["n"]
    return {
        "students": int(students),
        "attempts": int(row["n"]),
        "avg_score": round(row["avg"]) if row["avg"] is not None else None,
        "active_week": int(active),
        "total_lessons": total_lessons,
    }
