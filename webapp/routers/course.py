"""Portada, catálogo de cursos, lecciones, notas, marcadores y descargas."""

from __future__ import annotations

import sqlite3
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse

from webapp import repositories
from webapp.content import ContentBundle, Course, content_for
from webapp.db import get_db
from webapp.deps import ensure_csrf, get_current_user, require_user
from webapp.i18n import request_lang, t
from webapp.templating import render

router = APIRouter()


def _requested_course(request: Request) -> str | None:
    return request.query_params.get("course") or request.query_params.get("curso")


def _bundle(request: Request, course_slug: str | None = None) -> ContentBundle:
    return content_for(request_lang(request), course_slug or _requested_course(request))


def _next_lesson(course: Course, progress: dict[str, dict]):
    """Primera lección sin completar; si están todas, la última."""
    for lesson in course.lessons:
        row = progress.get(lesson.slug)
        if not row or not row.get("completed"):
            return lesson
    return course.lessons[-1] if course.lessons else None


def _stats_from_progress(progress: dict[str, dict], total: int) -> dict:
    completed = sum(1 for row in progress.values() if row.get("completed"))
    return {
        "completed": completed,
        "total": total,
        "pct": round(completed * 100 / total) if total else 0,
    }


def _catalog_rows(bundle: ContentBundle, progress_by_course: dict[str, dict[str, dict]]):
    rows = []
    for course in bundle.published_catalog:
        progress = progress_by_course.get(course.slug, {})
        rows.append(
            {
                "course": course,
                "stats": _stats_from_progress(progress, course.lesson_count),
                "next_lesson": _next_lesson(course, progress),
            }
        )
    return rows


def _resolve_lesson(bundle: ContentBundle, slug: str):
    course = bundle.course_for_lesson(slug)
    if course is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    selected = bundle.select(course.slug)
    lesson = selected.course.lesson(slug)
    chapter = selected.course.chapter_for(slug)
    if lesson is None or chapter is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada.")
    return selected, lesson, chapter


def _course_or_404(bundle: ContentBundle, slug: str) -> Course:
    course = bundle.course_for(slug)
    if course is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")
    return course


@router.get("/")
def home(
    request: Request,
    user: dict | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    if user is None:
        return render(
            request,
            "pages/landing.html",
            featured=bundle.course,
            catalog=bundle.published_catalog,
            total_minutes=sum(course.total_minutes for course in bundle.published_catalog),
            total_lessons=sum(course.lesson_count for course in bundle.published_catalog),
        )

    progress_by_course = repositories.progress_by_course(conn, user["id"])
    progress = progress_by_course.get(bundle.course.slug, {})
    stats = repositories.completion_stats(
        conn, user["id"], bundle.course.slug, len(bundle.course.lessons)
    )
    next_lesson = _next_lesson(bundle.course, progress)
    next_chapter = (
        bundle.course.chapter_for(next_lesson.slug) if next_lesson else None
    )
    next_progress = progress.get(next_lesson.slug) if next_lesson else None
    avg_score = repositories.average_score(conn, user["id"], bundle.course.slug)
    streak = repositories.current_streak(conn, user["id"])
    activity = repositories.activity_last_days(conn, user["id"], 14)
    attempts = repositories.attempts_for_user(conn, user["id"], bundle.course.slug, 3)

    return render(
        request,
        "pages/dashboard.html",
        stats=stats,
        progress=progress,
        catalog_rows=_catalog_rows(bundle, progress_by_course),
        next_lesson=next_lesson,
        next_chapter=next_chapter,
        next_progress=next_progress,
        avg_score=avg_score,
        streak=streak,
        activity=activity,
        attempts=attempts,
        sidebar_progress=progress,
    )


@router.get("/cursos")
def catalog_page(
    request: Request,
    user: dict | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    progress_by_course = (
        repositories.progress_by_course(conn, user["id"]) if user else {}
    )
    return render(
        request,
        "pages/catalog.html",
        catalog_rows=_catalog_rows(bundle, progress_by_course),
        sidebar_progress=progress_by_course.get(bundle.course.slug, {}),
    )


@router.get("/cursos/{course_slug}")
def course_detail_page(
    course_slug: str,
    request: Request,
    user: dict | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request, course_slug)
    course = _course_or_404(bundle, course_slug)
    bundle = bundle.select(course.slug)
    progress = (
        repositories.progress_for_user(conn, user["id"], course.slug)
        if user
        else {}
    )
    stats = (
        repositories.completion_stats(conn, user["id"], course.slug, course.lesson_count)
        if user
        else _stats_from_progress(progress, course.lesson_count)
    )
    next_lesson = _next_lesson(course, progress)
    return render(
        request,
        "pages/course.html",
        course=course,
        stats=stats,
        progress=progress,
        next_lesson=next_lesson,
        sidebar_progress=progress,
        public_course=user is None,
    )


@router.get("/curso")
def course_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    progress = repositories.progress_for_user(conn, user["id"], bundle.course.slug)
    stats = repositories.completion_stats(
        conn, user["id"], bundle.course.slug, len(bundle.course.lessons)
    )
    next_lesson = _next_lesson(bundle.course, progress)
    return render(
        request,
        "pages/course.html",
        stats=stats,
        progress=progress,
        next_lesson=next_lesson,
        sidebar_progress=progress,
    )


@router.get("/leccion/{slug}")
def lesson_detail(
    slug: str,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, lesson, chapter = _resolve_lesson(_bundle(request), slug)
    course = bundle.course

    repositories.touch_lesson(conn, user["id"], course.slug, slug)
    repositories.record_activity(conn, user["id"], "lesson")
    conn.commit()

    progress_row = repositories.get_lesson_progress(
        conn, user["id"], course.slug, slug
    )
    note = repositories.get_note(conn, user["id"], course.slug, slug)
    bookmarked = repositories.is_bookmarked(conn, user["id"], course.slug, slug)
    prev_lesson, next_lesson = course.neighbours(slug)

    quiz = bundle.quizzes.get(lesson.quiz_id) if lesson.quiz_id else None
    best = (
        repositories.best_attempt(conn, user["id"], quiz.id) if quiz is not None else None
    )

    return render(
        request,
        "pages/lesson.html",
        course=course,
        lesson=lesson,
        chapter=chapter,
        progress=progress_row,
        note=note,
        bookmarked=bookmarked,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        quiz=quiz,
        best_attempt=best,
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], course.slug
        ),
    )


@router.post("/leccion/{slug}/completar")
def complete_lesson(
    slug: str,
    request: Request,
    csrf_token: str = Form(""),
    completed: str = Form("0"),
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, _, _ = _resolve_lesson(_bundle(request), slug)
    ensure_csrf(request, user, csrf_token)

    done = completed == "1"
    repositories.set_lesson_completed(
        conn, user["id"], bundle.course.slug, slug, done
    )
    repositories.record_activity(conn, user["id"], "lesson")
    conn.commit()

    message = t(
        request,
        "Lección marcada como completada."
        if done
        else "Lección marcada como pendiente.",
    )
    return RedirectResponse(
        f"/leccion/{quote(slug)}?ok={quote(message)}",
        status_code=303,
    )


@router.post("/leccion/{slug}/nota")
def save_lesson_note(
    slug: str,
    request: Request,
    csrf_token: str = Form(""),
    body: str = Form(""),
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, _, _ = _resolve_lesson(_bundle(request), slug)
    ensure_csrf(request, user, csrf_token)

    repositories.save_note(
        conn, user["id"], bundle.course.slug, slug, body[:20000]
    )
    repositories.record_activity(conn, user["id"], "lesson")
    conn.commit()

    message = t(request, "Apuntes guardados.")
    return RedirectResponse(
        f"/leccion/{quote(slug)}?ok={quote(message)}",
        status_code=303,
    )


@router.post("/leccion/{slug}/marcador")
def toggle_lesson_bookmark(
    slug: str,
    request: Request,
    csrf_token: str = Form(""),
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle, _, _ = _resolve_lesson(_bundle(request), slug)
    ensure_csrf(request, user, csrf_token)

    repositories.toggle_bookmark(conn, user["id"], bundle.course.slug, slug)
    conn.commit()

    message = t(request, "Marcador actualizado.")
    return RedirectResponse(
        f"/leccion/{quote(slug)}?ok={quote(message)}",
        status_code=303,
    )


# ---------------------------------------------------------------------------
# Descargas de código
# ---------------------------------------------------------------------------

def _python_header(lesson, index: int, total: int, lang: str) -> str:
    if lang == "en":
        title = f"# {lesson.title} · runnable example {index} of {total}"
        hint = (
            "# You can run this file with: python nombre-del-archivo.py\n"
            "# Some examples may need: pip install matplotlib pandas numpy\n"
        )
    else:
        title = f"# {lesson.title} · ejemplo ejecutable {index} de {total}"
        hint = (
            "# Puedes ejecutar este archivo con: python nombre-del-archivo.py\n"
            "# Algunos ejemplos pueden necesitar: pip install matplotlib pandas numpy\n"
        )
    return f"{title}\n{hint}\n"


def _example_position(lesson, index: int) -> int:
    for position, (block_index, _) in enumerate(lesson.python_blocks, start=1):
        if block_index == index:
            return position
    return index


def _python_code(lesson, index: int, block: dict, lang: str) -> str:
    total = len(lesson.python_blocks)
    position = _example_position(lesson, index)
    parts = [_python_header(lesson, position, total, lang)]
    if block.get("caption"):
        parts.append(f"# {block['caption']}\n\n")
    parts.append(block["code"].rstrip() + "\n")
    return "".join(parts)


@router.get("/leccion/{slug}/codigo")
def download_lesson_code(
    slug: str,
    request: Request,
    user: dict = Depends(require_user),
):
    """Descarga todos los ejemplos ejecutables de una lección en un solo .py."""
    lang = request_lang(request)
    _, lesson, _ = _resolve_lesson(_bundle(request), slug)
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


@router.get("/leccion/{slug}/codigo/{index}")
def download_python_block(
    slug: str,
    index: int,
    request: Request,
    user: dict = Depends(require_user),
):
    lang = request_lang(request)
    _, lesson, _ = _resolve_lesson(_bundle(request), slug)
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
