"""Eventos de aprendizaje y KPIs para estudiante, profesorado y administración.

``learning_events`` es la fuente única de los indicadores (ADR-018). Cada fila
es un verbo al estilo xAPI (``lesson.viewed``, ``question.answered``…). Los
agregados se calculan al pedirlos: con SQLite y el volumen de un centro es
suficiente; si crece, se materializan en una tabla diaria.

Todas las fechas son UTC.
"""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from statistics import mean
from typing import Any, Iterable

from webapp.db import utcnow

# Verbos admitidos. Los que manda el navegador están en CLIENT_VERBS; el resto
# solo los registra el servidor (no se pueden falsificar desde el cliente).
SERVER_VERBS = {
    "lesson.viewed",
    "lesson.completed",
    "quiz.submitted",
    "question.answered",
    "code.run",
    "note.saved",
}
CLIENT_VERBS = {
    "lesson.heartbeat",
    "lab.interacted",
    "check.answered",
    "search.performed",
    "flashcard.reviewed",
}
VERBS = SERVER_VERBS | CLIENT_VERBS

HEARTBEAT_MAX_MS = 60_000
DEFAULT_WEEKLY_GOAL_MIN = 120
AT_RISK_INACTIVE_DAYS = 7
AT_RISK_SCORE = 50


def today() -> date:
    return datetime.now(timezone.utc).date()


# ---------------------------------------------------------------------------
# Captura
# ---------------------------------------------------------------------------

def record_event(
    conn: sqlite3.Connection,
    user_id: int,
    verb: str,
    *,
    course_slug: str = "",
    lesson_slug: str = "",
    object_id: str = "",
    score: float | None = None,
    success: bool | None = None,
    duration_ms: int = 0,
    meta: dict | None = None,
) -> None:
    if verb not in VERBS:
        raise ValueError(f"Verbo desconocido: {verb}")
    now = utcnow()
    conn.execute(
        """INSERT INTO learning_events
               (ts, day, user_id, course_slug, lesson_slug, verb, object_id,
                score, success, duration_ms, meta_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            now,
            now[:10],
            user_id,
            course_slug[:120],
            lesson_slug[:160],
            verb,
            str(object_id)[:160],
            score,
            None if success is None else int(bool(success)),
            max(0, min(int(duration_ms or 0), 3_600_000)),
            json.dumps(meta or {}, ensure_ascii=False)[:2000],
        ),
    )


def record_client_events(
    conn: sqlite3.Connection, user_id: int, events: Iterable[dict]
) -> int:
    """Guarda un lote del navegador. Ignora verbos de servidor y valores raros."""
    stored = 0
    for raw in list(events)[:50]:
        verb = str(raw.get("verb", ""))
        if verb not in CLIENT_VERBS:
            continue
        duration = int(raw.get("duration_ms") or 0)
        if verb == "lesson.heartbeat":
            duration = max(0, min(duration, HEARTBEAT_MAX_MS))
        score = raw.get("score")
        record_event(
            conn,
            user_id,
            verb,
            course_slug=str(raw.get("course") or ""),
            lesson_slug=str(raw.get("lesson") or ""),
            object_id=str(raw.get("object") or ""),
            score=float(score) if isinstance(score, (int, float)) else None,
            success=raw.get("success") if isinstance(raw.get("success"), bool) else None,
            duration_ms=duration,
            meta=raw.get("meta") if isinstance(raw.get("meta"), dict) else None,
        )
        stored += 1
    return stored


def record_quiz_answers(
    conn: sqlite3.Connection,
    user_id: int,
    course_slug: str,
    quiz,
    answers: dict[str, int | None],
    percent: int,
) -> None:
    for question in quiz.questions:
        selected = answers.get(question.id)
        record_event(
            conn,
            user_id,
            "question.answered",
            course_slug=course_slug,
            object_id=f"{quiz.id}:{question.id}",
            score=1.0 if question.is_correct(selected) else 0.0,
            success=question.is_correct(selected),
            meta={"selected": selected},
        )
    record_event(
        conn,
        user_id,
        "quiz.submitted",
        course_slug=course_slug,
        object_id=quiz.id,
        score=float(percent),
        success=percent >= quiz.pass_score,
    )


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _days(n: int) -> list[date]:
    end = today()
    return [end - timedelta(days=offset) for offset in range(n - 1, -1, -1)]


def _minutes_by_day(
    conn: sqlite3.Connection, user_ids: list[int], start: date, course_slug: str | None = None
) -> dict[str, float]:
    if not user_ids:
        return {}
    marks = ",".join("?" for _ in user_ids)
    query = f"""SELECT day, SUM(duration_ms) AS ms FROM learning_events
                WHERE verb = 'lesson.heartbeat' AND user_id IN ({marks}) AND day >= ?"""
    params: list[Any] = [*user_ids, start.isoformat()]
    if course_slug:
        query += " AND course_slug = ?"
        params.append(course_slug)
    query += " GROUP BY day"
    return {row[0]: (row[1] or 0) / 60000 for row in conn.execute(query, params)}


def _learning_days(conn: sqlite3.Connection, user_id: int) -> set[str]:
    rows = conn.execute(
        """SELECT DISTINCT day FROM learning_events WHERE user_id = ?
           UNION SELECT DISTINCT day FROM activity WHERE user_id = ? AND kind != 'login'""",
        (user_id, user_id),
    ).fetchall()
    return {row[0] for row in rows}


def streak(conn: sqlite3.Connection, user_id: int) -> int:
    """Días seguidos con actividad de aprendizaje (no cuenta iniciar sesión)."""
    days = _learning_days(conn, user_id)
    cursor = today()
    if cursor.isoformat() not in days:
        cursor -= timedelta(days=1)
    count = 0
    while cursor.isoformat() in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


def _latest_attempts(
    conn: sqlite3.Connection, user_ids: list[int], quiz_id: str
) -> dict[int, sqlite3.Row]:
    if not user_ids:
        return {}
    marks = ",".join("?" for _ in user_ids)
    rows = conn.execute(
        f"""SELECT * FROM quiz_attempts
            WHERE quiz_id = ? AND user_id IN ({marks})
            ORDER BY created_at ASC, id ASC""",
        (quiz_id, *user_ids),
    ).fetchall()
    latest: dict[int, sqlite3.Row] = {}
    for row in rows:
        latest[int(row["user_id"])] = row
    return latest


def _answers(row: sqlite3.Row) -> dict:
    try:
        data = json.loads(row["answers_json"] or "{}")
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _best_by_quiz(conn: sqlite3.Connection, user_id: int, course_slug: str) -> dict[str, int]:
    rows = conn.execute(
        """SELECT quiz_id, MAX(score * 100.0 / total) AS best FROM quiz_attempts
           WHERE user_id = ? AND course_slug = ? GROUP BY quiz_id""",
        (user_id, course_slug),
    ).fetchall()
    return {row["quiz_id"]: round(row["best"]) for row in rows}


def _completed(conn: sqlite3.Connection, user_ids: list[int], course_slug: str) -> dict[int, dict]:
    if not user_ids:
        return {}
    marks = ",".join("?" for _ in user_ids)
    rows = conn.execute(
        f"""SELECT user_id, lesson_slug, completed, completed_at, last_seen_at
            FROM lesson_progress WHERE course_slug = ? AND user_id IN ({marks})""",
        (course_slug, *user_ids),
    ).fetchall()
    result: dict[int, dict] = defaultdict(dict)
    for row in rows:
        result[int(row["user_id"])][row["lesson_slug"]] = dict(row)
    return result


# ---------------------------------------------------------------------------
# KPIs del estudiante
# ---------------------------------------------------------------------------

def student_kpis(
    conn: sqlite3.Connection,
    user_id: int,
    course,
    quizzes: dict,
    weekly_goal: int = DEFAULT_WEEKLY_GOAL_MIN,
) -> dict:
    days28 = _days(28)
    minutes = _minutes_by_day(conn, [user_id], days28[0])
    daily = [
        {"day": d.isoformat(), "minutes": round(minutes.get(d.isoformat(), 0), 1)}
        for d in days28
    ]
    week = round(sum(item["minutes"] for item in daily[-7:]))
    prev_week = round(sum(item["minutes"] for item in daily[-14:-7]))

    progress = _completed(conn, [user_id], course.slug).get(user_id, {})
    done = sum(1 for row in progress.values() if row["completed"])
    total = course.lesson_count
    recent = sum(
        1
        for row in progress.values()
        if row["completed"]
        and row["completed_at"]
        and row["completed_at"][:10] >= (today() - timedelta(days=13)).isoformat()
    )
    remaining = max(0, total - done)
    pace = recent / 14  # lecciones por día
    eta = (
        (today() + timedelta(days=round(remaining / pace))).isoformat()
        if pace > 0 and remaining
        else None
    )

    best = _best_by_quiz(conn, user_id, course.slug)
    chapters = []
    for chapter in course.chapters:
        slugs = [lesson.slug for lesson in chapter.lessons]
        chapter_done = sum(1 for slug in slugs if progress.get(slug, {}).get("completed"))
        quiz_id = next((lesson.quiz_id for lesson in chapter.lessons if lesson.quiz_id), None)
        score = best.get(quiz_id) if quiz_id else None
        completion = round(chapter_done * 100 / len(slugs)) if slugs else 0
        mastery = round(completion * 0.4 + score * 0.6) if score is not None else round(completion * 0.4)
        chapters.append(
            {
                "number": chapter.number,
                "title": chapter.title,
                "completion": completion,
                "quiz_score": score,
                "mastery": mastery,
            }
        )

    attempts = conn.execute(
        """SELECT id, quiz_id, score, total, created_at FROM quiz_attempts
           WHERE user_id = ? AND course_slug = ? ORDER BY created_at ASC, id ASC""",
        (user_id, course.slug),
    ).fetchall()
    score_trend = [
        {
            "id": row["id"],
            "quiz_id": row["quiz_id"],
            "date": row["created_at"][:10],
            "percent": round(row["score"] * 100 / row["total"]) if row["total"] else 0,
        }
        for row in attempts
    ]

    review = []
    latest: dict[str, sqlite3.Row] = {}
    for row in conn.execute(
        """SELECT * FROM quiz_attempts WHERE user_id = ? AND course_slug = ?
           ORDER BY created_at ASC, id ASC""",
        (user_id, course.slug),
    ):
        latest[row["quiz_id"]] = row
    for quiz_id, row in latest.items():
        quiz = quizzes.get(quiz_id)
        if quiz is None:
            continue
        answers = _answers(row)
        for question in quiz.questions:
            if not question.is_correct(question.normalize(answers.get(question.id))):
                review.append(
                    {
                        "quiz_id": quiz_id,
                        "question_id": question.id,
                        "prompt": question.prompt,
                        "answer": question.correct_option,
                        "explanation": question.explanation,
                    }
                )

    counts = dict(
        conn.execute(
            """SELECT verb, COUNT(*) FROM learning_events
               WHERE user_id = ? AND verb IN ('code.run', 'lab.interacted', 'check.answered')
               GROUP BY verb""",
            (user_id,),
        ).fetchall()
    )
    last_viewed = conn.execute(
        """SELECT lesson_slug FROM lesson_progress
           WHERE user_id = ? AND course_slug = ? AND completed = 0
           ORDER BY last_seen_at DESC LIMIT 1""",
        (user_id, course.slug),
    ).fetchone()
    return {
        "study": {
            "week_minutes": week,
            "prev_week_minutes": prev_week,
            "goal_minutes": weekly_goal,
            "goal_pct": min(100, round(week * 100 / weekly_goal)) if weekly_goal else 0,
            "daily": daily,
        },
        "streak": streak(conn, user_id),
        "completion": {
            "done": done,
            "total": total,
            "pct": round(done * 100 / total) if total else 0,
            "eta": eta,
            "pace_per_week": round(pace * 7, 1),
        },
        "chapters": chapters,
        "score_trend": score_trend,
        "avg_score": round(mean(item["percent"] for item in score_trend)) if score_trend else None,
        "review": review[:20],
        "review_count": len(review),
        "practice": {
            "code_runs": int(counts.get("code.run", 0)),
            "lab_interactions": int(counts.get("lab.interacted", 0)),
            "checks": int(counts.get("check.answered", 0)),
        },
        "continue_lesson": last_viewed["lesson_slug"] if last_viewed else None,
    }


# ---------------------------------------------------------------------------
# Analítica del profesorado
# ---------------------------------------------------------------------------

def item_analysis(conn: sqlite3.Connection, user_ids: list[int], quiz) -> list[dict]:
    """Dificultad (p), discriminación (27 % superior − inferior) y distractor."""
    latest = _latest_attempts(conn, user_ids, quiz.id)
    if not latest:
        return []
    attempts = sorted(latest.values(), key=lambda row: row["score"] / max(1, row["total"]))
    group = max(1, round(len(attempts) * 0.27))
    lower, upper = attempts[:group], attempts[-group:]
    items = []
    for number, question in enumerate(quiz.questions, start=1):
        choices: dict[int | None, int] = defaultdict(int)
        correct = 0

        def picked(row) -> int | list[int] | None:
            return question.normalize(_answers(row).get(question.id))

        for row in attempts:
            selected = picked(row)
            for option in selected if isinstance(selected, list) else [selected]:
                choices[option] += 1
            if question.is_correct(selected):
                correct += 1

        def rate(rows) -> float:
            return sum(1 for row in rows if question.is_correct(picked(row))) / len(rows)

        wrong = {
            key: value for key, value in choices.items()
            if key is not None and key not in question.correct_set
        }
        distractor = max(wrong, key=wrong.get) if wrong else None
        p_value = correct / len(attempts)
        discrimination = rate(upper) - rate(lower) if len(attempts) >= 4 else None
        flag = None
        if p_value < 0.3:
            flag = "hard"
        elif p_value > 0.95:
            flag = "easy"
        if discrimination is not None and discrimination < 0.1:
            flag = "low_discrimination"
        items.append(
            {
                "number": number,
                "question_id": question.id,
                "prompt": question.prompt,
                "p_value": round(p_value, 2),
                "discrimination": round(discrimination, 2) if discrimination is not None else None,
                "responses": len(attempts),
                "top_distractor": question.options[distractor] if distractor is not None else None,
                "top_distractor_rate": round(wrong[distractor] / len(attempts), 2)
                if distractor is not None
                else None,
                "flag": flag,
            }
        )
    return items


def course_analytics(
    conn: sqlite3.Connection,
    students: list[dict],
    course,
    quizzes: dict,
    days: int = 30,
) -> dict:
    ids = [int(student["id"]) for student in students]
    names = {int(student["id"]): student["name"] for student in students}
    progress = _completed(conn, ids, course.slug)
    lessons = [lesson for chapter in course.chapters for lesson in chapter.lessons]
    total_lessons = len(lessons)

    funnel = []
    for chapter in course.chapters:
        for lesson in chapter.lessons:
            started = sum(1 for uid in ids if lesson.slug in progress.get(uid, {}))
            completed = sum(
                1 for uid in ids if progress.get(uid, {}).get(lesson.slug, {}).get("completed")
            )
            funnel.append(
                {
                    "slug": lesson.slug,
                    "title": lesson.title,
                    "chapter": chapter.number,
                    "started": started,
                    "completed": completed,
                }
            )
    drop_off = None
    for previous, current in zip(funnel, funnel[1:]):
        loss = previous["completed"] - current["completed"]
        if loss > 0 and (drop_off is None or loss > drop_off["loss"]):
            drop_off = {"slug": current["slug"], "title": current["title"], "loss": loss}

    start = today() - timedelta(days=days - 1)
    minutes_rows = (
        conn.execute(
            f"""SELECT user_id, SUM(duration_ms) AS ms FROM learning_events
                WHERE verb = 'lesson.heartbeat' AND course_slug = ? AND day >= ?
                  AND user_id IN ({",".join("?" for _ in ids)})
                GROUP BY user_id""",
            (course.slug, start.isoformat(), *ids),
        ).fetchall()
        if ids
        else []
    )
    minutes = {int(row["user_id"]): (row["ms"] or 0) / 60000 for row in minutes_rows}

    last_seen: dict[int, str | None] = {}
    for uid in ids:
        seen = [row["last_seen_at"] for row in progress.get(uid, {}).values() if row["last_seen_at"]]
        last_seen[uid] = max(seen) if seen else None

    heatmap, at_risk, table = [], [], []
    for uid in ids:
        user_progress = progress.get(uid, {})
        best = _best_by_quiz(conn, uid, course.slug)
        row = {"user_id": uid, "name": names[uid], "chapters": []}
        for chapter in course.chapters:
            slugs = [lesson.slug for lesson in chapter.lessons]
            done = sum(1 for slug in slugs if user_progress.get(slug, {}).get("completed"))
            row["chapters"].append(round(done * 100 / len(slugs)) if slugs else 0)
        heatmap.append(row)

        done_total = sum(1 for item in user_progress.values() if item["completed"])
        scores = list(best.values())
        avg = round(mean(scores)) if scores else None
        seen = last_seen[uid]
        inactive_days = (
            (today() - date.fromisoformat(seen[:10])).days if seen else None
        )
        reasons = []
        if inactive_days is None:
            reasons.append("never_started")
        elif inactive_days >= AT_RISK_INACTIVE_DAYS:
            reasons.append("inactive")
        if avg is not None and avg < AT_RISK_SCORE:
            reasons.append("low_score")
        entry = {
            "user_id": uid,
            "name": names[uid],
            "completion": round(done_total * 100 / total_lessons) if total_lessons else 0,
            "avg_score": avg,
            "minutes": round(minutes.get(uid, 0)),
            "last_seen": seen,
            "inactive_days": inactive_days,
            "risk": reasons,
        }
        table.append(entry)
        if reasons:
            at_risk.append(entry)

    daily_active = []
    if ids:
        rows = conn.execute(
            f"""SELECT day, COUNT(DISTINCT user_id) AS n FROM learning_events
                WHERE course_slug = ? AND day >= ? AND user_id IN ({",".join("?" for _ in ids)})
                GROUP BY day""",
            (course.slug, start.isoformat(), *ids),
        ).fetchall()
        by_day = {row["day"]: row["n"] for row in rows}
    else:
        by_day = {}
    for offset in range(days):
        current = (start + timedelta(days=offset)).isoformat()
        daily_active.append({"day": current, "active": int(by_day.get(current, 0))})

    quiz_items = []
    pass_flags = []
    for chapter in course.chapters:
        quiz_id = next((lesson.quiz_id for lesson in chapter.lessons if lesson.quiz_id), None)
        quiz = quizzes.get(quiz_id) if quiz_id else None
        if quiz is None:
            continue
        latest = _latest_attempts(conn, ids, quiz.id)
        for attempt in latest.values():
            pass_flags.append(attempt["score"] * 100 / max(1, attempt["total"]) >= quiz.pass_score)
        quiz_items.append(
            {
                "quiz_id": quiz.id,
                "title": quiz.title,
                "chapter": chapter.number,
                "attempts": len(latest),
                "items": item_analysis(conn, ids, quiz),
            }
        )

    week_ago = (today() - timedelta(days=6)).isoformat()
    active_week = sum(1 for item in daily_active if item["day"] >= week_ago and item["active"])
    active_students = len({uid for uid in ids if last_seen[uid] and last_seen[uid][:10] >= week_ago})
    completions = [entry["completion"] for entry in table]
    scores = [entry["avg_score"] for entry in table if entry["avg_score"] is not None]
    buckets = [0, 0, 0, 0, 0]  # 0, <30, 30-120, 120-300, >300 min
    for entry in table:
        value = entry["minutes"]
        index = 0 if value == 0 else 1 if value < 30 else 2 if value < 120 else 3 if value < 300 else 4
        buckets[index] += 1

    return {
        "kpis": {
            "students": len(ids),
            "active_week": active_students,
            "active_days_week": active_week,
            "avg_completion": round(mean(completions)) if completions else 0,
            "avg_score": round(mean(scores)) if scores else None,
            "pass_rate": round(sum(pass_flags) * 100 / len(pass_flags)) if pass_flags else None,
            "study_hours": round(sum(minutes.values()) / 60, 1),
            "at_risk": len(at_risk),
        },
        "funnel": funnel,
        "drop_off": drop_off,
        "heatmap": {
            "chapters": [chapter.number for chapter in course.chapters],
            "rows": heatmap,
        },
        "daily_active": daily_active,
        "time_distribution": [
            {"label": label, "students": count}
            for label, count in zip(["0", "<30 min", "30–120 min", "2–5 h", ">5 h"], buckets)
        ],
        "quizzes": quiz_items,
        "students": sorted(table, key=lambda item: (-len(item["risk"]), item["name"])),
        "at_risk": at_risk,
    }


def workspace_metrics(conn: sqlite3.Connection, workspace_id: int) -> dict:
    """Uso del espacio: usuarios activos, plazas, cursos y trabajos del Estudio."""
    members = conn.execute(
        "SELECT user_id, role FROM memberships WHERE workspace_id = ?", (workspace_id,)
    ).fetchall()
    ids = [int(row["user_id"]) for row in members]
    roles: dict[str, int] = defaultdict(int)
    for row in members:
        roles[row["role"]] += 1
    days30 = _days(30)
    by_day: dict[str, int] = {}
    if ids:
        rows = conn.execute(
            f"""SELECT day, COUNT(DISTINCT user_id) AS n FROM learning_events
                WHERE day >= ? AND user_id IN ({",".join("?" for _ in ids)}) GROUP BY day""",
            (days30[0].isoformat(), *ids),
        ).fetchall()
        by_day = {row["day"]: int(row["n"]) for row in rows}
        wau = conn.execute(
            f"""SELECT COUNT(DISTINCT user_id) FROM learning_events
                WHERE day >= ? AND user_id IN ({",".join("?" for _ in ids)})""",
            ((today() - timedelta(days=6)).isoformat(), *ids),
        ).fetchone()[0]
    else:
        wau = 0
    jobs = conn.execute(
        """SELECT status, COUNT(*) AS n,
                  AVG((julianday(finished_at) - julianday(started_at)) * 86400) AS secs
           FROM authoring_jobs WHERE workspace_id = ? GROUP BY status""",
        (workspace_id,),
    ).fetchall()
    job_counts = {row["status"]: int(row["n"]) for row in jobs}
    finished = job_counts.get("ready", 0) + job_counts.get("failed", 0)
    ready_secs = next((row["secs"] for row in jobs if row["status"] == "ready"), None)
    courses = conn.execute(
        """SELECT status, COUNT(*) FROM generated_courses WHERE workspace_id = ?
           GROUP BY status""",
        (workspace_id,),
    ).fetchall()
    workspace = conn.execute(
        "SELECT seat_limit, plan FROM workspaces WHERE id = ?", (workspace_id,)
    ).fetchone()
    return {
        "members": len(ids),
        "roles": dict(roles),
        "seat_limit": workspace["seat_limit"] if workspace else None,
        "plan": workspace["plan"] if workspace else "free",
        "dau": by_day.get(today().isoformat(), 0),
        "wau": int(wau),
        "daily_active": [
            {"day": d.isoformat(), "active": by_day.get(d.isoformat(), 0)} for d in days30
        ],
        "courses": {row[0]: int(row[1]) for row in courses},
        "jobs": {
            "by_status": job_counts,
            "success_rate": round(job_counts.get("ready", 0) * 100 / finished) if finished else None,
            "avg_minutes": round(ready_secs / 60, 1) if ready_secs else None,
        },
    }
