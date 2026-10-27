"""Panel personal de progreso."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, Request

from webapp import repositories
from webapp.content import content_for
from webapp.db import get_db
from webapp.deps import require_user
from webapp.i18n import request_lang
from webapp.templating import render

router = APIRouter()


@router.get("/progreso")
def progress_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    requested = request.query_params.get("course") or request.query_params.get("curso")
    bundle = content_for(request_lang(request), requested)
    course = bundle.course
    progress = repositories.progress_for_user(conn, user["id"], course.slug)
    stats = repositories.completion_stats(
        conn, user["id"], course.slug, len(course.lessons)
    )
    progress_rows = [
        {"lesson": lesson, "progress": progress.get(lesson.slug)}
        for lesson in course.lessons
    ]
    attempts = repositories.attempts_for_user(conn, user["id"], course.slug)
    activity = repositories.activity_last_days(conn, user["id"], 28)
    avg_score = repositories.average_score(conn, user["id"], course.slug)
    streak = repositories.current_streak(conn, user["id"])

    quiz_id = next(
        (lesson.quiz_id for lesson in course.lessons if lesson.quiz_id), None
    )
    return render(
        request,
        "pages/progress.html",
        course=course,
        quiz_id=quiz_id,
        stats=stats,
        progress_rows=progress_rows,
        attempts=attempts,
        activity=activity,
        avg_score=avg_score,
        streak=streak,
        sidebar_progress=progress,
    )
