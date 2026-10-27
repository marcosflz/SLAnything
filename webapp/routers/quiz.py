"""Cuestionarios: vista previa, envío y revisión de intentos."""

from __future__ import annotations

import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from webapp import repositories
from webapp.content import ContentBundle, content_for
from webapp.db import get_db
from webapp.deps import ensure_csrf, require_user
from webapp.i18n import request_lang, t
from webapp.templating import render

router = APIRouter()


def _bundle_for_quiz(request: Request, quiz_id: str) -> ContentBundle:
    bundle = content_for(request_lang(request))
    course = bundle.course_for_quiz(quiz_id)
    if course is None:
        raise HTTPException(
            status_code=404, detail=t(request, "Cuestionario no encontrado.")
        )
    return bundle.select(course.slug)


@router.get("/quiz/intento/{attempt_id}")
def attempt_review(
    attempt_id: int,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    attempt = repositories.get_attempt(conn, attempt_id, user["id"])
    if attempt is None:
        raise HTTPException(status_code=404, detail=t(request, "Intento no encontrado."))

    bundle = content_for(request_lang(request))
    quiz = bundle.quizzes.get(attempt["quiz_id"])
    if quiz is None:
        raise HTTPException(
            status_code=404, detail=t(request, "Cuestionario no encontrado.")
        )
    course = bundle.course_for_quiz(quiz.id) or bundle.course
    bundle = bundle.select(course.slug)
    chapter = course.chapter_for_quiz(quiz.id)

    try:
        answers = json.loads(attempt["answers_json"] or "{}")
    except (TypeError, ValueError):
        answers = {}
    if not isinstance(answers, dict):
        answers = {}

    review = []
    for number, question in enumerate(quiz.questions, start=1):
        raw = answers.get(question.id)
        selected: int | None = None
        if isinstance(raw, int) and not isinstance(raw, bool):
            if 0 <= raw < len(question.options):
                selected = raw
        review.append(
            {
                "number": number,
                "question": question,
                "selected": selected,
                "selected_text": (
                    question.options[selected]
                    if selected is not None
                    else "Sin respuesta"
                ),
                "correct_text": question.correct_option,
                "is_correct": selected == question.correct,
                "explanation": question.explanation,
            }
        )

    return render(
        request,
        "pages/quiz_result.html",
        course=course,
        quiz=quiz,
        chapter=chapter,
        attempt=attempt,
        review=review,
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], course.slug
        ),
    )


@router.get("/quiz/{quiz_id}")
def quiz_detail(
    quiz_id: str,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle_for_quiz(request, quiz_id)
    course = bundle.course
    quiz = bundle.quizzes[quiz_id]
    chapter = course.chapter_for_quiz(quiz.id)

    attempts = repositories.attempts_for_quiz(conn, user["id"], quiz_id)
    best = repositories.best_attempt(conn, user["id"], quiz_id)

    return render(
        request,
        "pages/quiz.html",
        course=course,
        quiz=quiz,
        chapter=chapter,
        attempts=attempts,
        best_attempt=best,
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], course.slug
        ),
    )


@router.post("/quiz/{quiz_id}")
async def submit_quiz(
    quiz_id: str,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle_for_quiz(request, quiz_id)
    course = bundle.course
    quiz = bundle.quizzes[quiz_id]

    form = await request.form()
    csrf_value = form.get("csrf_token")
    ensure_csrf(request, user, csrf_value if isinstance(csrf_value, str) else None)

    answers: dict[str, int | None] = {}
    score = 0
    for question in quiz.questions:
        raw = form.get(f"q_{question.id}")
        selected: int | None = None
        if isinstance(raw, str) and raw.isascii() and raw.isdigit():
            candidate = int(raw)
            if 0 <= candidate < len(question.options):
                selected = candidate
        answers[question.id] = selected
        if selected == question.correct:
            score += 1

    attempt_id = repositories.create_attempt(
        conn,
        user["id"],
        course.slug,
        quiz.id,
        score,
        quiz.total,
        answers,
    )
    repositories.record_activity(conn, user["id"], "quiz")
    conn.commit()

    return RedirectResponse(f"/quiz/intento/{attempt_id}", status_code=303)
