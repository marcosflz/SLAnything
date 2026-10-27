"""API JSON versionada para el frontend Next.js.

La API convive con las rutas HTML de Jinja. Es la frontera estable entre el
backend FastAPI y el frontend React: serializa el catálogo, el contenido, el
progreso y las operaciones de escritura sin exponer las respuestas correctas del
quiz.
"""

from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from webapp import config, repositories
from webapp.content import ContentBundle, Course, content_for
from webapp.db import get_db
from webapp.deps import ensure_csrf, get_current_user, require_teacher, require_user
from webapp.i18n import request_lang, translate
from webapp.labs import lab_meta_for
from webapp.routers.course import _example_position, _python_code
from webapp.security import (
    hash_password,
    login_limiter,
    new_csrf_token,
    new_token,
    token_hash,
    verify_password,
)

router = APIRouter(prefix="/api/v1", tags=["api"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# Modelos de entrada
# ---------------------------------------------------------------------------

class LoginBody(BaseModel):
    email: str
    password: str
    next: str = "/"


class RegisterBody(BaseModel):
    name: str
    email: str
    password: str
    password2: str
    next: str = "/"


class CompleteBody(BaseModel):
    completed: bool = True


class NoteBody(BaseModel):
    body: str = Field(default="", max_length=20000)


class QuizBody(BaseModel):
    answers: dict[str, int | None] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers de serialización
# ---------------------------------------------------------------------------

def _lang(request: Request) -> str:
    return request_lang(request)


def _requested_course(request: Request) -> str | None:
    return request.query_params.get("course") or request.query_params.get("curso")


def _bundle(request: Request, course_slug: str | None = None) -> ContentBundle:
    return content_for(_lang(request), course_slug or _requested_course(request))


def _safe_next(value: str | None, fallback: str = "/") -> str:
    if not value or not value.startswith("/") or value.startswith("//"):
        return fallback
    return value


def _user_payload(user: dict | None) -> dict | None:
    if not user:
        return None
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "initials": _initials(user["name"]),
        "csrf_token": user.get("csrf_token", ""),
    }


def _initials(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0].upper() for part in parts[:2]) or "?"


def _book_payload(course: Course) -> dict | None:
    if course.book is None:
        return None
    return {
        "title": course.book.title,
        "author": course.book.author,
        "year": course.book.year,
        "url": course.book.url,
    }


def _lesson_summary(lesson, chapter=None, course: Course | None = None) -> dict:
    payload = {
        "number": lesson.number,
        "slug": lesson.slug,
        "title": lesson.title,
        "summary": lesson.summary,
        "minutes": lesson.minutes,
        "objectives": list(lesson.objectives),
        "labs": list(lesson.labs),
        "quiz_id": lesson.quiz_id,
    }
    if chapter is not None:
        payload["chapter_number"] = chapter.number
        payload["chapter_title"] = chapter.title
    if course is not None:
        payload["course_slug"] = course.slug
        payload["course_title"] = course.title
    return payload


def _lesson_full(lesson, chapter=None, course: Course | None = None) -> dict:
    payload = _lesson_summary(lesson, chapter, course)
    payload.update(
        {
            "key_points": list(lesson.key_points),
            "blocks": [dict(block) for block in lesson.blocks],
            "python_blocks": [index for index, _ in lesson.python_blocks],
            "word_count": lesson.word_count,
        }
    )
    return payload


def _chapter_payload(chapter, course: Course | None = None) -> dict:
    return {
        "number": chapter.number,
        "slug": chapter.slug,
        "title": chapter.title,
        "subtitle": chapter.subtitle,
        "description": chapter.description,
        "level": chapter.level,
        "total_minutes": chapter.total_minutes,
        "lesson_count": len(chapter.lessons),
        "lessons": [
            _lesson_summary(lesson, chapter, course) for lesson in chapter.lessons
        ],
    }


def _course_payload(course: Course) -> dict:
    labs = {
        lab_id
        for lesson in course.lessons
        for lab_id in lesson.labs
    }
    return {
        "slug": course.slug,
        "title": course.title,
        "subtitle": course.subtitle,
        "description": course.description,
        "level": course.level,
        "status": course.status,
        "accent": course.accent,
        "cover": course.cover,
        "book": _book_payload(course),
        "tags": list(course.tags),
        "total_minutes": course.total_minutes,
        "lesson_count": course.lesson_count,
        "chapter_count": course.chapter_count,
        "lab_count": len(labs),
        "chapters": [
            _chapter_payload(chapter, course) for chapter in course.chapters
        ],
        "lessons": [
            _lesson_summary(lesson, chapter, course)
            for chapter in course.chapters
            for lesson in chapter.lessons
        ],
    }


def _stats_payload(stats: dict) -> dict:
    return {
        "completed": stats["completed"],
        "total": stats["total"],
        "pct": stats["pct"],
    }


def _course_summary(
    course: Course,
    stats: dict,
    next_lesson,
) -> dict:
    return {
        "slug": course.slug,
        "title": course.title,
        "subtitle": course.subtitle,
        "description": course.description,
        "level": course.level,
        "status": course.status,
        "accent": course.accent,
        "cover": course.cover,
        "book": _book_payload(course),
        "tags": list(course.tags),
        "total_minutes": course.total_minutes,
        "lesson_count": course.lesson_count,
        "chapter_count": course.chapter_count,
        "lab_count": course.lab_count,
        "stats": _stats_payload(stats),
        "next_lesson": _summary_for(course, next_lesson),
    }


def _next_lesson(course: Course, progress: dict[str, dict]):
    for lesson in course.lessons:
        row = progress.get(lesson.slug)
        if not row or not row.get("completed"):
            return lesson
    return course.lessons[-1] if course.lessons else None


def _summary_for(course: Course, lesson) -> dict | None:
    if lesson is None:
        return None
    return _lesson_summary(
        lesson,
        course.chapter_for(lesson.slug),
        course,
    )


def _empty_stats(course: Course) -> dict:
    return {"completed": 0, "total": course.lesson_count, "pct": 0}


def _catalog_payload(
    bundle: ContentBundle,
    conn: sqlite3.Connection | None,
    user: dict | None,
) -> list[dict]:
    progress_by_course = (
        repositories.progress_by_course(conn, user["id"])
        if conn is not None and user is not None
        else {}
    )
    courses = []
    for course in bundle.published_catalog:
        progress = progress_by_course.get(course.slug, {})
        stats = (
            repositories.completion_stats(
                conn, user["id"], course.slug, course.lesson_count
            )
            if conn is not None and user is not None
            else _empty_stats(course)
        )
        courses.append(
            _course_summary(course, stats, _next_lesson(course, progress))
        )
    return courses


def _quiz_meta(quiz) -> dict:
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "pass_score": quiz.pass_score,
        "total": quiz.total,
    }


def _quiz_payload(quiz) -> dict:
    payload = _quiz_meta(quiz)
    payload["questions"] = [
        {"id": question.id, "prompt": question.prompt, "options": list(question.options)}
        for question in quiz.questions
    ]
    return payload


def _attempt_payload(row, pass_score: int = 80) -> dict | None:
    if row is None:
        return None
    percent = round(row["score"] * 100 / row["total"]) if row["total"] else 0
    return {
        "id": row["id"],
        "course_slug": row["course_slug"],
        "quiz_id": row["quiz_id"],
        "score": row["score"],
        "total": row["total"],
        "percent": percent,
        "passed": percent >= pass_score,
        "created_at": row["created_at"],
    }


def _progress_payload(progress: dict[str, dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for slug, row in progress.items():
        if row is None:
            continue
        result[slug] = {
            "completed": bool(row.get("completed")),
            "first_seen_at": row.get("first_seen_at"),
            "last_seen_at": row.get("last_seen_at"),
            "completed_at": row.get("completed_at"),
            "views": row.get("views", 0),
        }
    return result


def _site_payload(lang: str, course: Course, catalog_count: int) -> dict:
    return {
        "name": config.SITE_NAME,
        "tagline": translate(config.SITE_TAGLINE, lang),
        "course_title": course.title,
        "course_chapter": translate(
            "{n} capítulos · {m} lecciones",
            lang,
            n=course.chapter_count,
            m=course.lesson_count,
        ),
        "catalog_count": catalog_count,
        "year": date.today().year,
    }


def _activity(conn: sqlite3.Connection, user_id: int, days: int) -> list[dict]:
    return repositories.activity_last_days(conn, user_id, days)


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _initial(term: str) -> str:
    normalized = _normalize(term).strip()
    return normalized[0].upper() if normalized else "#"


def _snippet(lesson, needle: str) -> str:
    text = lesson.plain_text
    index = text.casefold().find(needle)
    if index < 0:
        return lesson.summary
    start = max(0, index - 120)
    end = min(len(text), index + len(needle) + 180)
    fragment = text[start:end].strip()
    if start > 0:
        fragment = "…" + fragment
    if end < len(text):
        fragment = fragment + "…"
    return fragment


def _resolve_lesson(bundle: ContentBundle, slug: str):
    course = bundle.course_for_lesson(slug)
    if course is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    selected = bundle.select(course.slug)
    lesson = selected.course.lesson(slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    return selected, lesson


def _resolve_quiz(bundle: ContentBundle, quiz_id: str):
    course = bundle.course_for_quiz(quiz_id)
    if course is None:
        raise HTTPException(
            status_code=404,
            detail=translate("Cuestionario no encontrado.", bundle.lang),
        )
    return bundle.select(course.slug), course


# ---------------------------------------------------------------------------
# Sesión y datos públicos
# ---------------------------------------------------------------------------

@router.get("/session")
def session(
    request: Request,
    user: dict | None = Depends(get_current_user),
):
    return {
        "user": _user_payload(user),
        "csrf_token": user.get("csrf_token", "") if user else "",
        "lang": _lang(request),
    }


@router.get("/public")
def public(request: Request):
    bundle = _bundle(request)
    lang = _lang(request)
    return {
        "course": _course_payload(bundle.course),
        "catalog": _catalog_payload(bundle, None, None),
        "site": _site_payload(lang, bundle.course, len(bundle.published_catalog)),
        "lab_meta": lab_meta_for(lang),
        "lang": lang,
    }


@router.get("/catalog")
def catalog(
    request: Request,
    user: dict | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    lang = _lang(request)
    return {
        "courses": _catalog_payload(bundle, conn, user),
        "featured": _course_payload(bundle.course),
        "site": _site_payload(lang, bundle.course, len(bundle.published_catalog)),
        "lang": lang,
    }


@router.get("/courses/{course_slug}")
def course_detail(
    course_slug: str,
    request: Request,
    user: dict | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request, course_slug)
    course = bundle.course_for(course_slug)
    if course is None:
        raise HTTPException(
            status_code=404,
            detail=translate("Curso no encontrado.", bundle.lang),
        )
    bundle = bundle.select(course.slug)
    progress = (
        repositories.progress_for_user(conn, user["id"], course.slug)
        if user
        else {}
    )
    stats = (
        repositories.completion_stats(
            conn, user["id"], course.slug, course.lesson_count
        )
        if user
        else _empty_stats(course)
    )
    return {
        "course": _course_payload(course),
        "progress": _progress_payload(progress),
        "stats": _stats_payload(stats),
        "next_lesson": _summary_for(course, _next_lesson(course, progress)),
        "courses": _catalog_payload(bundle, conn, user),
        "site": _site_payload(_lang(request), course, len(bundle.published_catalog)),
        "lang": _lang(request),
    }


@router.get("/shell")
def shell(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    progress = repositories.progress_for_user(conn, user["id"], bundle.course.slug)
    stats = repositories.completion_stats(
        conn, user["id"], bundle.course.slug, len(bundle.course.lessons)
    )
    nxt = _next_lesson(bundle.course, progress)
    return {
        "user": _user_payload(user),
        "course": _course_payload(bundle.course),
        "courses": _catalog_payload(bundle, conn, user),
        "default_course_slug": bundle.default_course.slug,
        "progress": _progress_payload(progress),
        "stats": _stats_payload(stats),
        "next_lesson": _summary_for(bundle.course, nxt),
        "lab_meta": lab_meta_for(_lang(request)),
        "site": _site_payload(
            _lang(request), bundle.course, len(bundle.published_catalog)
        ),
        "lang": _lang(request),
    }


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------

def _login_response(
    request: Request,
    conn: sqlite3.Connection,
    user_id: int,
    next_path: str,
) -> JSONResponse:
    token = new_token()
    repositories.create_session(
        conn,
        user_id,
        token_hash(token),
        new_csrf_token(),
        config.SESSION_DAYS,
    )
    repositories.record_activity(conn, user_id, "login")
    conn.commit()
    row = repositories.get_user(conn, user_id)
    response = JSONResponse(
        {
            "ok": True,
            "next": _safe_next(next_path),
            "user": _user_payload(
                {
                    "id": row["id"],
                    "email": row["email"],
                    "name": row["name"],
                    "role": row["role"],
                    "csrf_token": "",
                }
            ),
        }
    )
    response.set_cookie(
        key=config.COOKIE_NAME,
        value=token,
        max_age=config.SESSION_DAYS * 86400,
        httponly=True,
        samesite="lax",
        secure=config.SECURE_COOKIES,
        path="/",
    )
    return response


@router.post("/auth/login")
def api_login(
    body: LoginBody,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    email = body.email.strip()
    lang = _lang(request)
    client_host = request.client.host if request.client else "local"
    limiter_key = f"{email.lower()}|{client_host}"

    if login_limiter.is_blocked(limiter_key):
        minutes = max(1, login_limiter.retry_after(limiter_key) // 60)
        return JSONResponse(
            {
                "detail": translate(
                    "Demasiados intentos de inicio de sesión. Espera {minutes} minutos antes de volver a intentarlo.",
                    lang,
                    minutes=minutes,
                )
            },
            status_code=429,
        )

    row = repositories.get_user_by_email(conn, email)
    if row is None or not verify_password(body.password, row["password_hash"]):
        login_limiter.register_failure(limiter_key)
        return JSONResponse(
            {"detail": translate("Correo o contraseña incorrectos.", lang)},
            status_code=401,
        )

    login_limiter.reset(limiter_key)
    return _login_response(request, conn, row["id"], body.next)


@router.post("/auth/register")
def api_register(
    body: RegisterBody,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
):
    lang = _lang(request)
    clean_name = body.name.strip()
    clean_email = body.email.strip()

    def error(message: str) -> JSONResponse:
        return JSONResponse(
            {"detail": translate(message, lang)},
            status_code=400,
        )

    if not 2 <= len(clean_name) <= 80:
        return error("El nombre debe tener entre 2 y 80 caracteres.")
    if not EMAIL_RE.match(clean_email):
        return error("Introduce un correo electrónico válido.")
    if len(body.password) < 8:
        return error("La contraseña debe tener al menos 8 caracteres.")
    if body.password != body.password2:
        return error("Las contraseñas no coinciden.")
    if repositories.get_user_by_email(conn, clean_email) is not None:
        return error("Ya existe una cuenta con ese correo. Prueba a iniciar sesión.")

    try:
        user = repositories.create_user(
            conn,
            email=clean_email,
            name=clean_name,
            password_hash=hash_password(body.password),
            role="student",
        )
    except sqlite3.IntegrityError:
        return error("Ya existe una cuenta con ese correo. Prueba a iniciar sesión.")

    return _login_response(request, conn, user["id"], body.next)


@router.post("/auth/logout")
def api_logout(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    ensure_csrf(request, user)
    repositories.delete_session(conn, user["session_id"])
    conn.commit()
    response = JSONResponse({"ok": True})
    response.delete_cookie(config.COOKIE_NAME, path="/")
    return response


# ---------------------------------------------------------------------------
# Inicio, curso y lecciones
# ---------------------------------------------------------------------------

@router.get("/dashboard")
def dashboard(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    course = bundle.course
    progress = repositories.progress_for_user(conn, user["id"], course.slug)
    stats = repositories.completion_stats(
        conn, user["id"], course.slug, len(course.lessons)
    )
    nxt = _next_lesson(course, progress)
    next_progress = (
        _progress_payload({nxt.slug: progress.get(nxt.slug)}).get(nxt.slug)
        if nxt
        else None
    )
    return {
        "course": _course_payload(course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(progress),
        "stats": _stats_payload(stats),
        "next_lesson": _summary_for(course, nxt),
        "next_progress": next_progress,
        "avg_score": repositories.average_score(conn, user["id"], course.slug),
        "streak": repositories.current_streak(conn, user["id"]),
        "activity": _activity(conn, user["id"], 14),
        "attempts": [
            _attempt_payload(row, bundle.quizzes[row["quiz_id"]].pass_score)
            for row in repositories.attempts_for_user(
                conn, user["id"], course.slug, 3
            )
            if row["quiz_id"] in bundle.quizzes
        ],
    }


@router.get("/course")
def course_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    course = bundle.course
    progress = repositories.progress_for_user(conn, user["id"], course.slug)
    stats = repositories.completion_stats(
        conn, user["id"], course.slug, len(course.lessons)
    )
    nxt = _next_lesson(course, progress)
    return {
        "course": _course_payload(course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(progress),
        "stats": _stats_payload(stats),
        "next_lesson": _summary_for(course, nxt),
    }


@router.get("/lessons/{slug}")
def lesson_detail(
    slug: str,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, lesson = _resolve_lesson(_bundle(request), slug)
    course = bundle.course
    chapter = course.chapter_for(slug)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")

    repositories.touch_lesson(conn, user["id"], course.slug, slug)
    repositories.record_activity(conn, user["id"], "lesson")
    conn.commit()

    progress_row = repositories.get_lesson_progress(
        conn, user["id"], course.slug, slug
    )
    quiz = bundle.quizzes.get(lesson.quiz_id) if lesson.quiz_id else None
    best = (
        repositories.best_attempt(conn, user["id"], quiz.id) if quiz is not None else None
    )
    prev_lesson, next_lesson = course.neighbours(slug)
    progress = repositories.progress_for_user(conn, user["id"], course.slug)

    return {
        "lesson": _lesson_full(lesson, chapter, course),
        "chapter": _chapter_payload(chapter, course),
        "course": _course_payload(course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload({slug: progress_row}).get(slug)
        if progress_row
        else None,
        "note": repositories.get_note(conn, user["id"], course.slug, slug),
        "bookmarked": repositories.is_bookmarked(
            conn, user["id"], course.slug, slug
        ),
        "prev_lesson": _summary_for(course, prev_lesson),
        "next_lesson": _summary_for(course, next_lesson),
        "quiz": _quiz_meta(quiz) if quiz else None,
        "best_attempt": _attempt_payload(best, quiz.pass_score) if best and quiz else None,
        "all_progress": _progress_payload(progress),
        "stats": _stats_payload(
            repositories.completion_stats(
                conn, user["id"], course.slug, len(course.lessons)
            )
        ),
        "lab_meta": lab_meta_for(_lang(request)),
    }


@router.post("/lessons/{slug}/complete")
def complete_lesson(
    slug: str,
    body: CompleteBody,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, lesson = _resolve_lesson(_bundle(request), slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    ensure_csrf(request, user)
    course = bundle.course
    repositories.set_lesson_completed(
        conn, user["id"], course.slug, slug, body.completed
    )
    repositories.record_activity(conn, user["id"], "lesson")
    conn.commit()
    progress = repositories.progress_for_user(conn, user["id"], course.slug)
    return {
        "ok": True,
        "message": translate(
            "Lección marcada como completada."
            if body.completed
            else "Lección marcada como pendiente.",
            _lang(request),
        ),
        "completed": body.completed,
        "stats": _stats_payload(
            repositories.completion_stats(
                conn, user["id"], course.slug, len(course.lessons)
            )
        ),
        "progress": _progress_payload(progress),
    }


@router.post("/lessons/{slug}/note")
def save_note(
    slug: str,
    body: NoteBody,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, lesson = _resolve_lesson(_bundle(request), slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    ensure_csrf(request, user)
    repositories.save_note(
        conn, user["id"], bundle.course.slug, slug, body.body[:20000]
    )
    repositories.record_activity(conn, user["id"], "lesson")
    conn.commit()
    return {"ok": True, "message": translate("Apuntes guardados.", _lang(request))}


@router.post("/lessons/{slug}/bookmark")
def toggle_bookmark(
    slug: str,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, lesson = _resolve_lesson(_bundle(request), slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    ensure_csrf(request, user)
    bookmarked = repositories.toggle_bookmark(
        conn, user["id"], bundle.course.slug, slug
    )
    conn.commit()
    return {
        "ok": True,
        "bookmarked": bookmarked,
        "message": translate("Marcador actualizado.", _lang(request)),
    }


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------

@router.get("/quiz/{quiz_id}")
def quiz_detail(
    quiz_id: str,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, course = _resolve_quiz(_bundle(request), quiz_id)
    quiz = bundle.quizzes.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail=translate("Cuestionario no encontrado.", _lang(request)),
        )
    chapter = course.chapter_for_quiz(quiz_id)
    attempts = repositories.attempts_for_quiz(conn, user["id"], quiz_id)
    best = repositories.best_attempt(conn, user["id"], quiz_id)
    return {
        "quiz": _quiz_payload(quiz),
        "chapter": _chapter_payload(chapter, course) if chapter else None,
        "course": _course_payload(course),
        "courses": _catalog_payload(bundle, conn, user),
        "attempts": [_attempt_payload(row, quiz.pass_score) for row in attempts],
        "best_attempt": _attempt_payload(best, quiz.pass_score) if best else None,
        "progress": _progress_payload(
            repositories.progress_for_user(conn, user["id"], course.slug)
        ),
    }


@router.post("/quiz/{quiz_id}")
def submit_quiz(
    quiz_id: str,
    body: QuizBody,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, course = _resolve_quiz(_bundle(request), quiz_id)
    quiz = bundle.quizzes.get(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail=translate("Cuestionario no encontrado.", _lang(request)),
        )
    ensure_csrf(request, user)

    answers: dict[str, int | None] = {}
    score = 0
    for question in quiz.questions:
        raw = body.answers.get(question.id)
        selected: int | None = None
        if isinstance(raw, int) and not isinstance(raw, bool):
            if 0 <= raw < len(question.options):
                selected = raw
        answers[question.id] = selected
        if selected == question.correct:
            score += 1

    attempt_id = repositories.create_attempt(
        conn, user["id"], course.slug, quiz.id, score, quiz.total, answers
    )
    repositories.record_activity(conn, user["id"], "quiz")
    conn.commit()
    percent = round(score * 100 / quiz.total) if quiz.total else 0
    return {
        "ok": True,
        "attempt_id": attempt_id,
        "score": score,
        "total": quiz.total,
        "percent": percent,
        "passed": percent >= quiz.pass_score,
    }


@router.get("/quiz/attempts/{attempt_id}")
def attempt_review(
    attempt_id: int,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    attempt = repositories.get_attempt(conn, attempt_id, user["id"])
    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail=translate("Intento no encontrado.", _lang(request)),
        )

    bundle = _bundle(request)
    quiz = bundle.quizzes.get(attempt["quiz_id"])
    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail=translate("Cuestionario no encontrado.", _lang(request)),
        )
    course = bundle.course_for_quiz(quiz.id) or bundle.course
    bundle = bundle.select(course.slug)

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
                "question": question.prompt,
                "selected": selected,
                "selected_text": (
                    question.options[selected]
                    if selected is not None
                    else translate("Sin respuesta", _lang(request))
                ),
                "correct_text": question.correct_option,
                "is_correct": selected == question.correct,
                "explanation": question.explanation,
            }
        )

    chapter = course.chapter_for_quiz(quiz.id)
    return {
        "quiz": _quiz_meta(quiz),
        "chapter": _chapter_payload(chapter, course) if chapter else None,
        "course": _course_payload(course),
        "courses": _catalog_payload(bundle, conn, user),
        "attempt": _attempt_payload(attempt, quiz.pass_score),
        "review": review,
        "progress": _progress_payload(
            repositories.progress_for_user(conn, user["id"], course.slug)
        ),
    }


# ---------------------------------------------------------------------------
# Progreso, glosario, recursos, búsqueda y profesorado
# ---------------------------------------------------------------------------

@router.get("/progress")
def progress_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    course = bundle.course
    progress = repositories.progress_for_user(conn, user["id"], course.slug)
    stats = repositories.completion_stats(
        conn, user["id"], course.slug, len(course.lessons)
    )
    return {
        "course": _course_payload(course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(progress),
        "stats": _stats_payload(stats),
        "rows": [
            {
                "lesson": _lesson_summary(lesson, chapter, course),
                "progress": _progress_payload(
                    {lesson.slug: progress.get(lesson.slug)}
                ).get(lesson.slug),
            }
            for chapter in course.chapters
            for lesson in chapter.lessons
        ],
        "attempts": [
            _attempt_payload(row, bundle.quizzes[row["quiz_id"]].pass_score)
            for row in repositories.attempts_for_user(conn, user["id"], course.slug)
            if row["quiz_id"] in bundle.quizzes
        ],
        "activity": _activity(conn, user["id"], 28),
        "avg_score": repositories.average_score(conn, user["id"], course.slug),
        "streak": repositories.current_streak(conn, user["id"]),
    }


@router.get("/glossary")
def glossary_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    terms = sorted(bundle.glossary, key=lambda item: item.term.casefold())
    groups: list[dict] = []
    for term in terms:
        letter = _initial(term.term)
        if groups and groups[-1]["letter"] == letter:
            groups[-1]["terms"].append(
                {
                    "term": term.term,
                    "definition": term.definition,
                    "lesson": term.lesson,
                }
            )
        else:
            groups.append(
                {
                    "letter": letter,
                    "terms": [
                        {
                            "term": term.term,
                            "definition": term.definition,
                            "lesson": term.lesson,
                        }
                    ],
                }
            )
    return {
        "groups": groups,
        "course": _course_payload(bundle.course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(
            repositories.progress_for_user(conn, user["id"], bundle.course.slug)
        ),
    }


@router.get("/resources")
def resources_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    lang = _lang(request)
    items = [
        {
            "title": translate("Cuaderno interactivo", lang),
            "description": translate(
                "El capítulo completo en Jupyter, con las celdas y experimentos originales del libro.",
                lang,
            ),
            "href": "/api/v1/downloads/notebook",
            "icon": "notebook",
            "meta": "Jupyter · 0.86 MB",
            "download": True,
        },
        {
            "title": translate("Corpus de El Quijote", lang),
            "description": translate(
                "Fragmento de texto en dominio público para entrenar el generador de n-gramas del laboratorio.",
                lang,
            ),
            "href": "/static/data/quijote_fragmento.txt",
            "icon": "database",
            "meta": "Text · 408 KB" if lang == "en" else "Texto · 408 KB",
            "download": False,
        },
        {
            "title": translate("Figuras del capítulo", lang),
            "description": translate(
                "Diagramas de la jerarquía de la IA, el transformer y las dos etapas del entrenamiento.",
                lang,
            ),
            "href": "/static/img/ch01/fig_1_1_jerarquia_ia.png",
            "icon": "folder",
            "meta": "PNG · 11 figures" if lang == "en" else "PNG · 11 figuras",
            "download": False,
        },
        {
            "title": translate("Plan de la plataforma", lang),
            "description": translate(
                "Documento de diseño con el alcance, la arquitectura, las fases y las decisiones técnicas del proyecto.",
                lang,
            ),
            "href": "/api/v1/downloads/plan",
            "icon": "list",
            "meta": "Markdown · Plan",
            "download": True,
        },
        {
            "title": translate("Guía de créditos", lang),
            "description": translate(
                "Fuentes, atribuciones y licencias del material didáctico y de las figuras utilizadas.",
                lang,
            ),
            "href": "#creditos",
            "icon": "info",
            "meta": translate("Licencias y atribución", lang),
            "download": False,
        },
    ]
    bundle = _bundle(request)
    return {
        "resources": items,
        "course": _course_payload(bundle.course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(
            repositories.progress_for_user(conn, user["id"], bundle.course.slug)
        ),
    }


@router.get("/search")
def search_page(
    request: Request,
    q: str = "",
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    query = q.strip()
    results: list[dict] = []
    bundle = _bundle(request)
    if len(query) >= 2:
        needle = query.casefold()
        matches: list[tuple[bool, int, int, dict]] = []
        for course in bundle.published_catalog:
            for chapter in course.chapters:
                for lesson in chapter.lessons:
                    in_title = needle in lesson.title.casefold()
                    in_summary = needle in lesson.summary.casefold()
                    in_text = needle in lesson.plain_text.casefold()
                    if in_title or in_summary or in_text:
                        matches.append(
                            (
                                in_title,
                                course.order,
                                chapter.number,
                                {
                                    "lesson": _lesson_summary(
                                        lesson, chapter, course
                                    ),
                                    "snippet": _snippet(lesson, needle),
                                },
                            )
                        )
        matches.sort(key=lambda item: (not item[0], item[1], item[2]))
        results = [item[3] for item in matches]
    return {
        "query": query,
        "results": results,
        "course": _course_payload(bundle.course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(
            repositories.progress_for_user(conn, user["id"], bundle.course.slug)
        ),
    }


@router.get("/teacher")
def teacher_page(
    request: Request,
    user: dict = Depends(require_teacher),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    total_lessons = sum(
        course.lesson_count for course in bundle.published_catalog
    )
    return {
        "students": repositories.teacher_overview(conn),
        "stats": repositories.teacher_stats(conn, total_lessons),
        "course": _course_payload(bundle.course),
        "courses": _catalog_payload(bundle, conn, user),
        "progress": _progress_payload(
            repositories.progress_for_user(conn, user["id"], bundle.course.slug)
        ),
    }


# ---------------------------------------------------------------------------
# Descargas
# ---------------------------------------------------------------------------

def _download_lesson(request: Request, slug: str):
    bundle, lesson = _resolve_lesson(_bundle(request), slug)
    return bundle, lesson


@router.get("/downloads/lessons/{slug}/code")
def download_lesson_code(
    slug: str,
    request: Request,
    user: dict = Depends(require_user),
):
    lang = _lang(request)
    _, lesson = _download_lesson(request, slug)
    blocks = lesson.python_blocks
    if not blocks:
        raise HTTPException(status_code=404, detail="Esta lección no tiene ejemplos ejecutables.")
    parts: list[str] = []
    if lang == "en":
        parts.append(f"# {lesson.title}\n# Runnable examples for the lesson.\n\n")
    else:
        parts.append(f"# {lesson.title}\n# Ejemplos ejecutables de la lección.\n\n")
    for index, block in blocks:
        parts.append("=" * 72 + "\n")
        parts.append(_python_code(lesson, index, block, lang))
        parts.append("\n")
    filename = f"leccion-{slug}-ejemplos.py" if lang == "es" else f"lesson-{slug}-examples.py"
    return PlainTextResponse(
        "".join(parts),
        media_type="text/x-python; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/downloads/lessons/{slug}/code/{index}")
def download_python_block(
    slug: str,
    index: int,
    request: Request,
    user: dict = Depends(require_user),
):
    lang = _lang(request)
    _, lesson = _download_lesson(request, slug)
    matches = [(i, block) for i, block in lesson.python_blocks if i == index]
    if not matches:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado.")
    _, block = matches[0]
    position = _example_position(lesson, index)
    filename = (
        f"leccion-{slug}-ejemplo-{position}.py"
        if lang == "es"
        else f"lesson-{slug}-example-{position}.py"
    )
    return PlainTextResponse(
        _python_code(lesson, index, block, lang),
        media_type="text/x-python; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/downloads/notebook")
def download_notebook(user: dict = Depends(require_user)):
    path = config.NOTEBOOKS_DIR / "capitulo_01_entender_los_llms.ipynb"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Cuaderno no disponible.")
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/x-ipynb+json",
    )


@router.get("/downloads/plan")
def download_plan(user: dict = Depends(require_user)):
    path = config.BASE_DIR / "docs" / "PLAN_PLATAFORMA_WEB.md"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Plan no disponible.")
    return FileResponse(
        path,
        filename=path.name,
        media_type="text/markdown; charset=utf-8",
    )
