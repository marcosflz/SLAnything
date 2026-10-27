"""Panel de métricas para el profesorado."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, Request

from webapp import repositories
from webapp.content import content_for
from webapp.db import get_db
from webapp.deps import require_teacher
from webapp.i18n import request_lang
from webapp.templating import render

router = APIRouter()


@router.get("/profesor")
def teacher_page(
    request: Request,
    user: dict = Depends(require_teacher),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = content_for(request_lang(request))
    total_lessons = sum(course.lesson_count for course in bundle.published_catalog)
    students = repositories.teacher_overview(conn)
    stats = repositories.teacher_stats(conn, total_lessons)

    return render(
        request,
        "pages/teacher.html",
        students=students,
        stats=stats,
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], bundle.course.slug
        ),
    )
