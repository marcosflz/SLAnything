"""Configuración de Jinja2 y helper de render."""

from __future__ import annotations

from datetime import date, datetime
from urllib.parse import quote, urlencode

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from webapp import config
from webapp.content import content_for
from webapp.i18n import request_lang, translate
from webapp.labs import lab_meta_for

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))

_MONTHS = {
    "es": (
        "ene", "feb", "mar", "abr", "may", "jun",
        "jul", "ago", "sep", "oct", "nov", "dic",
    ),
    "en": (
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ),
}


@pass_context
def _fecha(context, value: str | None) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    lang = context.get("lang", "es")
    months = _MONTHS.get(lang, _MONTHS["es"])
    return f"{parsed.day} {months[parsed.month - 1]} {parsed.year}"


def _fecha_corta(value: str | None) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%d/%m/%Y")


def _iniciales(name: str) -> str:
    parts = [part for part in name.split() if part]
    return "".join(part[0].upper() for part in parts[:2]) or "?"


def _safe_next(value: str | None, fallback: str = "/curso") -> str:
    if not value or not value.startswith("/") or value.startswith("//"):
        return fallback
    return value


templates.env.filters["fecha"] = _fecha
templates.env.filters["fecha_corta"] = _fecha_corta
templates.env.filters["iniciales"] = _iniciales
templates.env.globals.update(
    site_name=config.SITE_NAME,
    current_year=date.today().year,
    safe_next=_safe_next,
)


def render(request: Request, name: str, **context):
    """Renderiza una plantilla añadiendo el contexto común.

    `status_code` se extrae del contexto para poder devolver errores 403/404
    con su código HTTP real.
    """
    status_code = int(context.pop("status_code", 200))
    user = getattr(request.state, "user", None)
    lang = request_lang(request)
    requested = request.query_params.get("course") or request.query_params.get("curso")
    bundle = content_for(lang, requested)
    program = bundle.course
    catalog = bundle.published_catalog
    chapter_count = getattr(program, "chapter_count", 1)
    lesson_count = getattr(program, "lesson_count", len(program.lessons))
    active_chapter = None
    if request.url.path.startswith("/leccion/"):
        slug = request.url.path.removeprefix("/leccion/").split("/")[0]
        chapter = getattr(program, "chapter_for", lambda _slug: None)(slug)
        active_chapter = chapter.number if chapter is not None else None
    other_query = [
        (key, value)
        for key, value in request.query_params.multi_items()
        if key != "lang"
    ]
    base = {
        "request": request,
        "user": user,
        "lang": lang,
        "t": lambda text, **kwargs: translate(text, lang, **kwargs),
        "course": program,
        "catalog": catalog,
        "catalog_count": len(catalog),
        "active_chapter": active_chapter,
        "lab_meta": lab_meta_for(lang),
        "course_title": program.title,
        "course_slug": program.slug,
        "course_chapter": translate(
            "{n} capítulos · {m} lecciones",
            lang,
            n=chapter_count,
            m=lesson_count,
        ),
        "site_tagline": translate(config.SITE_TAGLINE, lang),
        "current_path": request.url.path,
        "current_full_path": request.url.path
        + (("?" + urlencode(other_query)) if other_query else ""),
        "query": request.query_params.get("q", ""),
        "ok_message": request.query_params.get("ok"),
        "error_message": request.query_params.get("error"),
    }
    base.update(context)
    # El curso activo puede venir del contexto de la ruta (por ejemplo, una
    # lección o /cursos/{slug}); recalcula sus metadatos después del merge.
    resolved_course = base.get("course", program)
    if "course_chapter" not in context:
        base["course_chapter"] = translate(
            "{n} capítulos · {m} lecciones",
            lang,
            n=getattr(resolved_course, "chapter_count", chapter_count),
            m=getattr(resolved_course, "lesson_count", lesson_count),
        )
    if "course_title" not in context:
        base["course_title"] = getattr(resolved_course, "title", program.title)
    if "course_slug" not in context:
        base["course_slug"] = getattr(resolved_course, "slug", program.slug)
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=base,
        status_code=status_code,
    )


def redirect_target(request: Request, fallback: str = "/") -> str:
    """URL interna segura para volver tras cambiar de idioma."""
    from urllib.parse import parse_qsl, urlparse

    target = request.query_params.get("next") or request.headers.get("referer") or fallback
    if target.startswith("http://") or target.startswith("https://"):
        # Solo aceptamos el mismo origen.
        parsed = urlparse(target)
        if parsed.netloc != request.url.netloc:
            return fallback
        target = parsed.path + (("?" + parsed.query) if parsed.query else "")
    if not target.startswith("/") or target.startswith("//"):
        return fallback
    parsed = urlparse(target)
    query = [(key, value) for key, value in parse_qsl(parsed.query) if key != "lang"]
    clean = parsed.path + (("?" + urlencode(query)) if query else "")
    return quote(clean, safe="/?=&")
