"""Glosario global de la plataforma agrupado por letra."""

from __future__ import annotations

import sqlite3
import unicodedata

from fastapi import APIRouter, Depends, Request

from webapp import repositories
from webapp.content import content_for
from webapp.db import get_db
from webapp.deps import require_user
from webapp.i18n import request_lang
from webapp.templating import render

router = APIRouter()


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _initial(term: str) -> str:
    normalized = _normalize(term).strip()
    return normalized[0].upper() if normalized else "#"


@router.get("/glosario")
def glossary_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    requested = request.query_params.get("course") or request.query_params.get("curso")
    bundle = content_for(request_lang(request), requested)
    terms = sorted(bundle.glossary, key=lambda item: item.term.casefold())

    groups: list[tuple[str, list]] = []
    for term in terms:
        letter = _initial(term.term)
        if groups and groups[-1][0] == letter:
            groups[-1][1].append(term)
        else:
            groups.append((letter, [term]))

    return render(
        request,
        "pages/glossary.html",
        groups=groups,
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], bundle.course.slug
        ),
    )
