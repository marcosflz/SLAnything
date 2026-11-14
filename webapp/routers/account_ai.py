"""Proveedor de IA propio de cada usuario con permiso de autoría (ADR-024).

El alumnado no tiene permiso ``author``: estas rutas le devuelven 403 y, como
consumir un curso publicado nunca llama al modelo, la credencial de un profesor
jamás se usa en nombre de sus alumnos.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from webapp import audit, config
from webapp.authoring import credentials, providers
from webapp.deps import ensure_csrf, require_author

router = APIRouter(prefix="/api/v1/account/ai", tags=["account"])


class UserAiBody(BaseModel):
    provider: str = Field(min_length=1, max_length=40)
    model: str = Field(default="", max_length=160)
    secret: str | None = Field(default=None, max_length=credentials.MAX_SECRET_LENGTH)
    accept_personal: bool = False


@router.get("")
def get_ai(user: dict = Depends(require_author)):
    return credentials.public(user["id"])


@router.put("")
def put_ai(body: UserAiBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    try:
        data = credentials.save(
            user["id"],
            provider=body.provider,
            model=body.model,
            secret=body.secret,
            accept_personal=body.accept_personal,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    audit.record(
        None, actor_id=user["id"], action="account.ai.update", target=body.provider,
        request=request, meta={"model": body.model},
    )
    return data


@router.delete("")
def delete_ai(request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    data = credentials.delete(user["id"])
    audit.record(None, actor_id=user["id"], action="account.ai.delete", request=request)
    return data


@router.post("/test")
def test_ai(request: Request, user: dict = Depends(require_author)):
    """Prueba la credencial propia con una llamada mínima al modelo."""
    ensure_csrf(request, user)
    own = credentials.user_settings(user["id"])
    if own is None:
        raise HTTPException(status_code=400, detail="Primero guarda un proveedor propio completo.")
    if config.LLM_FAKE:
        return {"ok": True, "message": "Modo sin red: la prueba se simula.", "provider": own["provider"]}
    try:
        providers.router_kwargs(own)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    from nas.adk.models import LlmRequest

    from webapp.generation import models, runtime

    async def probe():
        model = models.build_model(own)
        try:
            return await model.generate_content_async(
                LlmRequest(messages=[{"role": "user", "content": "Responde únicamente: OK"}])
            )
        finally:
            await model.aclose()

    try:
        response = runtime._run_coroutine(probe)
    except Exception as exc:  # noqa: BLE001 - el usuario necesita el motivo
        return {"ok": False, "message": runtime.explain(exc, str(exc)), "provider": own["provider"]}
    text = (response.content or "").strip()[:80]
    return {"ok": True, "message": f"El modelo respondió: {text or '(vacío)'}", "provider": own["provider"]}
