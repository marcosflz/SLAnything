"""Recursos descargables y créditos."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from webapp import config, repositories
from webapp.content import content_for
from webapp.db import get_db
from webapp.deps import require_user
from webapp.i18n import request_lang, t
from webapp.templating import render

router = APIRouter()

NOTEBOOK_NAME = "capitulo_01_entender_los_llms.ipynb"
PLAN_NAME = "PLAN_PLATAFORMA_WEB.md"


def _resource_items(request: Request) -> list[dict[str, str]]:
    items: list[dict[str, str]] = [
        {
            "title": t(request, "Cuaderno interactivo"),
            "description": t(
                request,
                "El capítulo completo en Jupyter, con las celdas y experimentos originales del libro.",
            ),
            "href": "/recursos/cuaderno",
            "icon": "notebook",
            "meta": "Jupyter · 0.86 MB",
        },
        {
            "title": t(request, "Corpus de El Quijote"),
            "description": t(
                request,
                "Fragmento de texto en dominio público para entrenar el generador de n-gramas del laboratorio.",
            ),
            "href": "/static/data/quijote_fragmento.txt",
            "icon": "database",
            "meta": "Text · 408 KB" if request.state.lang == "en" else "Texto · 408 KB",
        },
        {
            "title": t(request, "Figuras del capítulo"),
            "description": t(
                request,
                "Diagramas de la jerarquía de la IA, el transformer y las dos etapas del entrenamiento.",
            ),
            "href": "/static/img/ch01/fig_1_1_jerarquia_ia.png",
            "icon": "folder",
            "meta": "PNG · 11 figures" if request.state.lang == "en" else "PNG · 11 figuras",
        },
        {
            "title": t(request, "Plan de la plataforma"),
            "description": t(
                request,
                "Documento de diseño con el alcance, la arquitectura, las fases y las decisiones técnicas del proyecto.",
            ),
            "href": "/recursos/plan",
            "icon": "list",
            "meta": "Markdown · Plan",
        },
        {
            "title": t(request, "Guía de créditos"),
            "description": t(
                request,
                "Fuentes, atribuciones y licencias del material didáctico y de las figuras utilizadas.",
            ),
            "href": "#creditos",
            "icon": "info",
            "meta": t(request, "Licencias y atribución"),
        },
    ]
    return items


@router.get("/recursos")
def resources_page(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = content_for(request_lang(request))
    return render(
        request,
        "pages/resources.html",
        resources=_resource_items(request),
        sidebar_progress=repositories.progress_for_user(
            conn, user["id"], bundle.course.slug
        ),
    )


@router.get("/recursos/cuaderno")
def download_notebook(user: dict = Depends(require_user)):
    path = config.NOTEBOOKS_DIR / NOTEBOOK_NAME
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Cuaderno no disponible.")
    return FileResponse(
        path,
        filename=NOTEBOOK_NAME,
        media_type="application/x-ipynb+json",
    )


@router.get("/recursos/plan")
def download_plan(user: dict = Depends(require_user)):
    path = config.BASE_DIR / "docs" / PLAN_NAME
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Plan no disponible.")
    return FileResponse(
        path,
        filename=PLAN_NAME,
        media_type="text/markdown; charset=utf-8",
    )
