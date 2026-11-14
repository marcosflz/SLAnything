"""API de ejecución de ejemplos de Python."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from webapp import analytics, execution
from webapp.db import session_scope
from webapp.deps import ensure_csrf, require_user
from webapp.i18n import request_lang, t

router = APIRouter()
logger = logging.getLogger("aula.execution")


class RunRequest(BaseModel):
    code: str = Field(min_length=1, max_length=16_000)
    lesson: str | None = Field(default=None, max_length=120)


@router.post("/api/ejecutar")
def run_python(
    payload: RunRequest,
    request: Request,
    user: dict = Depends(require_user),
):
    """Ejecuta un ejemplo en el sandbox y devuelve la salida estructurada."""
    ensure_csrf(request, user)
    try:
        result = execution.execute_for_lesson(
            payload.code,
            user_id=user["id"],
            lang=request_lang(request),
        )
    except execution.RateLimitError as exc:
        return JSONResponse(
            {"ok": False, "error": t(request, str(exc))},
            status_code=429,
        )
    except execution.ExecutionError as exc:
        return JSONResponse(
            {"ok": False, "error": t(request, str(exc))},
            status_code=503 if not execution.settings.enabled else 400,
        )
    except Exception:
        logger.exception("Fallo inesperado al ejecutar código")
        return JSONResponse(
            {
                "ok": False,
                "error": t(
                    request,
                    "Ha ocurrido un error interno. Vuelve a intentarlo en unos segundos.",
                ),
            },
            status_code=500,
        )
    try:
        with session_scope() as conn:
            analytics.record_event(
                conn,
                user["id"],
                "code.run",
                lesson_slug=payload.lesson or "",
                success=bool(result.get("ok")),
                duration_ms=int(result.get("duration_ms") or 0),
            )
    except Exception:  # noqa: BLE001 - la analítica nunca rompe la ejecución
        logger.exception("No se pudo registrar la ejecución")
    return JSONResponse(result)
