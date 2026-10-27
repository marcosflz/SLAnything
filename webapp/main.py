"""Punto de entrada de SLAnything.

Arranque local:

    uv run python aula.py

Producción:

    uv run uvicorn webapp.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from webapp import config
from webapp.authoring import runner as authoring_runner
from webapp.authoring import store as authoring_store
from webapp.content import (
    CATALOGS,
    GLOSSARIES,
    QUIZZES_BY_LANG,
    validate_catalog,
)
from webapp.db import init_db
from webapp.i18n import LANG_COOKIE, normalize_lang, request_lang, translate
from webapp.templating import render

logger = logging.getLogger("aula")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        authoring_store.ensure_dir()
        interrupted = authoring_store.mark_interrupted_jobs()
        if interrupted:
            logger.warning(
                "%s trabajos del Estudio quedaron interrumpidos por un reinicio.",
                interrupted,
            )
    except OSError:
        logger.exception("No se pudo preparar el directorio del Estudio")
    try:
        for lang, catalog in CATALOGS.items():
            validate_catalog(
                catalog,
                QUIZZES_BY_LANG[lang],
                config.KNOWN_LABS,
                config.STATIC_DIR,
                GLOSSARIES[lang],
            )
    except ValueError:
        logger.exception("El contenido no supera la validación")
        raise
    logger.info(
        "SLAnything lista · %s cursos · %s lecciones por idioma · %s idiomas",
        len(CATALOGS["es"]),
        len(CATALOGS["es"][0].lessons),
        len(CATALOGS),
    )
    try:
        yield
    finally:
        authoring_runner.shutdown()


app = FastAPI(
    title="SLAnything",
    description="Cursos interactivos y autoría de unidades con OpenCode.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


# Routers (se importan después de crear la app para evitar ciclos).
from webapp.routers import (  # noqa: E402
    api,
    authoring,
    auth,
    course,
    execution,
    glossary,
    language,
    progress,
    quiz,
    resources,
    search,
    teacher,
)

app.include_router(api.router)
app.include_router(authoring.router)
app.include_router(language.router)
app.include_router(auth.router)
app.include_router(course.router)
app.include_router(authoring.pages)
app.include_router(execution.router)
app.include_router(quiz.router)
app.include_router(progress.router)
app.include_router(glossary.router)
app.include_router(resources.router)
app.include_router(search.router)
app.include_router(teacher.router)


@app.middleware("http")
async def language_middleware(request: Request, call_next):
    """Resuelve el idioma antes de renderizar y permite ?lang=en en enlaces."""
    requested = request.query_params.get("lang")
    lang = normalize_lang(requested or request.cookies.get(LANG_COOKIE))
    request.state.lang = lang
    response = await call_next(request)
    if requested in ("es", "en") and request.cookies.get(LANG_COOKIE) != requested:
        response.set_cookie(
            LANG_COOKIE,
            requested,
            max_age=365 * 86400,
            httponly=False,
            samesite="lax",
            path="/",
        )
    return response


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    return response


@app.get("/salud", include_in_schema=False)
async def health():
    return {
        "status": "ok",
        "lecciones": len(CATALOGS["es"][0].lessons),
        "cursos": len(CATALOGS["es"]),
    }


@app.get("/health", include_in_schema=False)
async def health_alias():
    """Alias habitual en despliegues y comprobadores de disponibilidad."""
    return await health()


@app.exception_handler(401)
async def auth_required(request: Request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            {"detail": translate("No autenticado", request_lang(request))},
            status_code=401,
        )
    target = request.url.path
    if request.url.query:
        target += "?" + request.url.query
    return RedirectResponse(f"/entrar?next={quote(target)}", status_code=303)


@app.exception_handler(403)
async def forbidden(request: Request, exc):
    detail = getattr(exc, "detail", None) or "No tienes permiso para ver esta página."
    if request.url.path.startswith("/api"):
        return JSONResponse(
            {"detail": translate(detail, request_lang(request))}, status_code=403
        )
    return render(
        request,
        "pages/error.html",
        code=403,
        title=translate("Acceso restringido", request_lang(request)),
        message=translate(detail, request_lang(request)),
        status_code=403,
    )


@app.exception_handler(404)
async def not_found(request: Request, exc):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return render(
        request,
        "pages/error.html",
        code=404,
        title=translate("Página no encontrada", request_lang(request)),
        message=translate(
            "La dirección no existe o el contenido se ha movido.",
            request_lang(request),
        ),
        status_code=404,
    )


@app.exception_handler(Exception)
async def server_error(request: Request, exc):
    logger.exception("Error interno en %s", request.url.path)
    if request.url.path.startswith("/api"):
        return JSONResponse(
            {
                "detail": translate(
                    "Ha ocurrido un error interno. Vuelve a intentarlo en unos segundos.",
                    request_lang(request),
                )
            },
            status_code=500,
        )
    return render(
        request,
        "pages/error.html",
        code=500,
        title=translate("Algo se ha roto", request_lang(request)),
        message=translate(
            "Ha ocurrido un error interno. Vuelve a intentarlo en unos segundos.",
            request_lang(request),
        ),
        status_code=500,
    )


def run() -> None:
    import os

    import uvicorn

    uvicorn.run(
        "webapp.main:app",
        host="127.0.0.1",
        port=8000,
        # Sin recarga automática por defecto: SQLite escribe en el directorio y
        # un watcher puede reiniciar el servidor en cada visita.
        reload=os.environ.get("AULA_RELOAD", "0") == "1",
    )
