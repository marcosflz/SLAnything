"""Proveedores de IA: los de cada persona, los compartidos de una academia y el selector (ADR-024, ADR-025).

- ``/api/v1/account/ai``: quien tiene permiso de autoría configura varios proveedores a la
  vez (claves de API y suscripciones personales), elige sus modelos visibles y su
  predeterminado. El alumnado recibe 403: consumir un curso nunca llama al modelo.
- ``/api/v1/admin/ai``: la administración de una academia comparte claves de API (nunca
  suscripciones) con su profesorado.
- ``/api/v1/ai/models``: modelos que la persona puede usar ahora, agrupados (Estudio).
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from webapp import audit, config
from webapp.authoring import catalog, credentials, links, providers
from webapp.deps import ensure_csrf, require_admin, require_author

router = APIRouter(prefix="/api/v1/account/ai", tags=["account"])
workspace_router = APIRouter(prefix="/api/v1/admin/ai", tags=["admin"])
models_router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class ModelEntry(BaseModel):
    id: str = Field(min_length=1, max_length=160)
    label: str = Field(default="", max_length=160)


class ProviderBody(BaseModel):
    provider: str = Field(min_length=1, max_length=40)
    secret: str | None = Field(default=None, max_length=credentials.MAX_SECRET_LENGTH)
    enabled: bool | None = None
    models: list[ModelEntry] | None = Field(default=None, max_length=credentials.MAX_MODELS)
    model: str | None = Field(default=None, max_length=160)
    accept_personal: bool = False


class ChoiceBody(BaseModel):
    source: Literal["user", "workspace", "platform"]
    provider: str = Field(min_length=1, max_length=40)
    model: str = Field(min_length=1, max_length=160)


class LinkFinishBody(BaseModel):
    link_id: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=8000)
    accept_personal: bool = False


class LinkCancelBody(BaseModel):
    link_id: str = Field(min_length=1, max_length=200)


def _save(scope_kind: str, scope_id: int, body: ProviderBody, actor_id: int) -> None:
    try:
        credentials.save_provider(
            scope_kind,
            scope_id,
            body.provider,
            actor_id=actor_id,
            secret=body.secret,
            enabled=body.enabled,
            models=[m.model_dump() for m in body.models] if body.models is not None else None,
            model=body.model,
            accept_personal=body.accept_personal,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _probe(resolved: dict[str, Any]) -> dict[str, Any]:
    if config.LLM_FAKE:
        return {"ok": True, "message": "Modo sin red: la prueba se simula.", "provider": resolved["provider"]}
    try:
        providers.router_kwargs(resolved)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    from nas.adk.models import LlmRequest

    from webapp.generation import models, runtime

    async def probe():
        model = models.build_model(resolved)
        try:
            return await model.generate_content_async(
                LlmRequest(messages=[{"role": "user", "content": "Responde únicamente: OK"}])
            )
        finally:
            await model.aclose()

    try:
        response = runtime._run_coroutine(probe)
    except Exception as exc:  # noqa: BLE001 - el usuario necesita el motivo
        return {"ok": False, "message": runtime.explain(exc, str(exc)), "provider": resolved["provider"]}
    text = (response.content or "").strip()[:80]
    return {"ok": True, "message": f"El modelo respondió: {text or '(vacío)'}", "provider": resolved["provider"]}


def _catalog(scope_kind: str, scope_id: int, provider: str, user_id: int) -> dict[str, Any]:
    try:
        found = catalog.list_models(scope_kind, scope_id, provider, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - CLI o red del proveedor
        from webapp.generation import runtime

        raise HTTPException(status_code=502, detail=runtime.explain(exc, "No se pudieron consultar los modelos.")) from exc
    if not found:
        raise HTTPException(status_code=400, detail="El proveedor no devolvió ningún modelo.")
    return {"models": found}


# --- Cuenta ------------------------------------------------------------------


@router.get("")
def get_ai(user: dict = Depends(require_author)):
    return credentials.public(user["id"])


@router.put("/providers")
def put_provider(body: ProviderBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    _save("user", user["id"], body, user["id"])
    audit.record(None, actor_id=user["id"], action="account.ai.update", target=body.provider, request=request,
                 meta={"enabled": body.enabled, "models": len(body.models or [])})
    return credentials.public(user["id"])


@router.delete("/providers/{provider}")
def delete_provider(provider: str, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    credentials.delete_provider("user", user["id"], provider)
    default = credentials.user_default(user["id"])
    if default and default["source"] == "user" and default["provider"] == provider:
        credentials.set_default(user["id"], None)
    audit.record(None, actor_id=user["id"], action="account.ai.delete", target=provider, request=request)
    return credentials.public(user["id"])


@router.post("/providers/{provider}/models")
def provider_models(provider: str, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    return _catalog("user", user["id"], provider, user["id"])


@router.post("/providers/{provider}/test")
def test_provider(provider: str, request: Request, user: dict = Depends(require_author)):
    """Prueba la credencial propia con una llamada mínima al modelo."""
    ensure_csrf(request, user)
    own = credentials.user_settings(user["id"], provider)
    if own is None:
        raise HTTPException(status_code=400, detail="Primero completa la configuración de ese proveedor.")
    return _probe(own)


@router.put("/default")
def put_default(body: ChoiceBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    workspace = (user.get("workspace") or {}).get("id")
    groups = credentials.model_groups(user["id"], workspace)["groups"]
    if not any(
        g["source"] == body.source and g["provider"] == body.provider and any(m["id"] == body.model for m in g["models"])
        for g in groups
    ):
        raise HTTPException(status_code=400, detail="Ese modelo no está activo.")
    credentials.set_default(user["id"], body.model_dump())
    return credentials.public(user["id"])


# Vinculación de suscripciones (rutas async: el proceso del CLI vive en el bucle del servidor).


def _personal_allowed(provider: str) -> None:
    info = providers.provider(provider)
    if not credentials.usable(info, "user"):
        raise HTTPException(status_code=403, detail="Esta plataforma no permite vincular esa suscripción.")


@router.post("/claude/link/start")
async def claude_link_start(request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    _personal_allowed("claude-code")
    try:
        link_id, url = await links.start_claude(user["id"])
    except links.LinkError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from exc
    return {"link_id": link_id, "url": url}


@router.post("/claude/link/finish")
async def claude_link_finish(body: LinkFinishBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    _personal_allowed("claude-code")
    if not body.accept_personal:
        raise HTTPException(status_code=400, detail="Confirma que es tu suscripción personal y que solo la usarás tú.")
    try:
        token = await links.finish_claude(body.link_id, user["id"], body.code.strip())
    except links.LinkError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from exc
    credentials.store_secret("user", user["id"], "claude-code", token, actor_id=user["id"], accept_personal=True)
    _enable_catalog("claude-code", user["id"])
    audit.record(None, actor_id=user["id"], action="account.ai.link", target="claude-code", request=request)
    return credentials.public(user["id"])


@router.post("/chatgpt/link/start")
async def chatgpt_link_start(request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    _personal_allowed("chatgpt")
    previous = credentials.secret_for("user", user["id"], "chatgpt")
    client_id = None
    if previous:
        import json

        try:
            client_id = json.loads(previous).get("client_id")
        except (ValueError, AttributeError):
            client_id = None
    link_id, url = await links.start_chatgpt(user["id"], client_id)
    return {"link_id": link_id, "url": url}


@router.post("/chatgpt/link/finish")
async def chatgpt_link_finish(body: LinkFinishBody, request: Request, user: dict = Depends(require_author)):
    import json

    ensure_csrf(request, user)
    _personal_allowed("chatgpt")
    if not body.accept_personal:
        raise HTTPException(status_code=400, detail="Confirma que es tu plan personal y que solo lo usarás tú.")
    try:
        creds = await links.finish_chatgpt(body.link_id, user["id"], body.code.strip())
    except links.LinkError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message) from exc
    credentials.store_secret("user", user["id"], "chatgpt", json.dumps(creds), actor_id=user["id"], accept_personal=True)
    _enable_catalog("chatgpt", user["id"])
    audit.record(None, actor_id=user["id"], action="account.ai.link", target="chatgpt", request=request)
    return credentials.public(user["id"])


@router.post("/link/cancel")
async def link_cancel(body: LinkCancelBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    await links.cancel(body.link_id, user["id"])
    return {"ok": True}


def _enable_catalog(provider: str, user_id: int) -> None:
    """Primera vinculación: se activan los modelos que anuncia la cuenta."""
    view = next((p for p in credentials.public(user_id)["providers"] if p["id"] == provider), None)
    if not view or not view.get("config") or len(view["config"]["models"]) > 1:
        return
    try:
        found = catalog.list_models("user", user_id, provider, user_id=user_id)
    except Exception:  # noqa: BLE001 - sin catálogo se puede elegir después
        return
    advertised = [{"id": m["id"], "label": m["label"]} for m in found if not m.get("hint")]
    if advertised:
        credentials.save_provider("user", user_id, provider, actor_id=user_id, models=advertised)


# --- Academia ----------------------------------------------------------------


def _workspace_id(user: dict) -> int:
    workspace = user.get("workspace") or {}
    if workspace.get("kind") != "organization":
        raise HTTPException(status_code=403, detail="Solo las academias comparten claves de API.")
    return int(workspace["id"])


@workspace_router.get("")
def get_workspace_ai(user: dict = Depends(require_admin)):
    return credentials.public_workspace(_workspace_id(user))


@workspace_router.put("/providers")
def put_workspace_provider(body: ProviderBody, request: Request, user: dict = Depends(require_admin)):
    ensure_csrf(request, user)
    workspace_id = _workspace_id(user)
    _save("workspace", workspace_id, body, user["id"])
    audit.record(None, workspace_id=workspace_id, actor_id=user["id"], action="workspace.ai.update", target=body.provider, request=request)
    return credentials.public_workspace(workspace_id)


@workspace_router.delete("/providers/{provider}")
def delete_workspace_provider(provider: str, request: Request, user: dict = Depends(require_admin)):
    ensure_csrf(request, user)
    workspace_id = _workspace_id(user)
    credentials.delete_provider("workspace", workspace_id, provider)
    audit.record(None, workspace_id=workspace_id, actor_id=user["id"], action="workspace.ai.delete", target=provider, request=request)
    return credentials.public_workspace(workspace_id)


@workspace_router.post("/providers/{provider}/models")
def workspace_provider_models(provider: str, request: Request, user: dict = Depends(require_admin)):
    ensure_csrf(request, user)
    return _catalog("workspace", _workspace_id(user), provider, user["id"])


@workspace_router.post("/providers/{provider}/test")
def test_workspace_provider(provider: str, request: Request, user: dict = Depends(require_admin)):
    ensure_csrf(request, user)
    resolved = credentials.workspace_settings(_workspace_id(user), provider)
    if resolved is None:
        raise HTTPException(status_code=400, detail="Primero completa la configuración de ese proveedor.")
    return _probe(resolved)


# --- Selector ----------------------------------------------------------------


@models_router.get("/models")
def available_models(user: dict = Depends(require_author)):
    """Modelos activos que la persona puede usar ahora, agrupados por proveedor."""
    return credentials.model_groups(user["id"], (user.get("workspace") or {}).get("id"))
