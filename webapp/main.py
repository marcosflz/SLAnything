"""Punto de entrada de SLAnything.

Arranque local:

    uv run python aula.py

Producción:

    uv run uvicorn webapp.main:app --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from webapp import config
from webapp.authoring import runner as authoring_runner
from webapp.authoring import store as authoring_store
from webapp.generation import worker as generation_worker
from webapp.content import (
    CATALOGS,
    GLOSSARIES,
    QUIZZES_BY_LANG,
    validate_catalog,
)
from webapp.db import init_db
from webapp.i18n import LANG_COOKIE, normalize_lang, request_lang, translate

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
        resumed = generation_worker.resume_pending()
        if resumed:
            logger.info("%s generaciones reanudadas tras el reinicio.", resumed)
    except OSError:
        logger.exception("No se pudo preparar el directorio del Estudio")
    # Los cursos de ejemplo del repositorio solo se validan si están activos;
    # la plataforma arranca igual con la biblioteca vacía (ADR-020).
    if config.SAMPLE_COURSES:
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
            logger.exception("El contenido de ejemplo no supera la validación")
            raise
    logger.info(
        "SLAnything lista · cursos de ejemplo %s · %s idiomas",
        "activos" if config.SAMPLE_COURSES else "desactivados",
        len(CATALOGS),
    )
    try:
        yield
    finally:
        authoring_runner.shutdown()
        generation_worker.shutdown()


app = FastAPI(
    title="SLAnything",
    description="Aula virtual que convierte cualquier material de aprendizaje en cursos.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


# Routers (se importan después de crear la app para evitar ciclos).
from webapp.routers import (  # noqa: E402
    admin,
    analytics,
    api,
    authoring,
    execution,
    platform,
    workspaces,
)

app.include_router(api.router)
app.include_router(authoring.router)
app.include_router(execution.router)
app.include_router(workspaces.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(platform.router)


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
        "ejemplos": config.SAMPLE_COURSES,
    }


@app.get("/health", include_in_schema=False)
async def health_alias():
    """Alias habitual en despliegues y comprobadores de disponibilidad."""
    return await health()


def _json_error(request: Request, detail: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        {"detail": translate(detail, request_lang(request))}, status_code=status_code
    )


@app.exception_handler(401)
async def auth_required(request: Request, exc):
    return _json_error(request, "No autenticado", 401)


@app.exception_handler(403)
async def forbidden(request: Request, exc):
    detail = getattr(exc, "detail", None) or "No tienes permiso para ver esta página."
    return _json_error(request, detail, 403)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    detail = getattr(exc, "detail", None)
    if not isinstance(detail, str) or detail == "Not Found":
        detail = "Not found"
    return JSONResponse({"detail": detail}, status_code=404)


@app.exception_handler(Exception)
async def server_error(request: Request, exc):
    logger.exception("Error interno en %s", request.url.path)
    return _json_error(
        request,
        "Ha ocurrido un error interno. Vuelve a intentarlo en unos segundos.",
        500,
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
