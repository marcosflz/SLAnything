"""Buscador global de lecciones entre todos los cursos."""

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

SNIPPET_BEFORE = 120
SNIPPET_AFTER = 180


def _snippet(lesson, needle: str) -> str:
    text = lesson.plain_text
    index = text.casefold().find(needle)
    if index < 0:
        fallback = lesson.summary
        if len(fallback) > SNIPPET_BEFORE + SNIPPET_AFTER:
            return fallback[: SNIPPET_BEFORE + SNIPPET_AFTER] + "…"
        return fallback

    start = max(0, index - SNIPPET_BEFORE)
    end = min(len(text), index + len(needle) + SNIPPET_AFTER)
    fragment = text[start:end].strip()
    if start > 0:
        fragment = "…" + fragment
    if end < len(text):
        fragment = fragment + "…"
    return fragment


@router.get("/buscar")
def search_page(
    request: Request,
    q: str = "",
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    query = q.strip()
    results: list[dict] = []
    bundle = content_for(request_lang(request))

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
                                    "lesson": lesson,
                                    "course": course,
                                    "chapter": chapter,
                                    "snippet": _snippet(lesson, needle),
                                },
                            )
                        )
        matches.sort(key=lambda item: (not item[0], item[1], item[2]))
        results = [item[3] for item in matches]

    return render(
        request,
        "pages/search.html",
        results=results,
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], bundle.course.slug
        ),
    )
