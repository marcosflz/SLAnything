"""Catálogo de modelos de cada proveedor, para elegir cuáles se muestran (ADR-025).

- Claude (suscripción): el propio CLI con el token de la persona (``list_models`` de
  nas-adk, sin inferencia).
- ChatGPT: ``GET /v1/models`` del plan con su token de acceso.
- Claves de API: la URL fija del proveedor (``Provider.models_url``), nunca una del usuario.
"""

from __future__ import annotations

from typing import Any

import httpx

from webapp import config
from webapp.authoring import credentials, providers


def extract_models(payload: Any) -> list[dict[str, str]]:
    """``{data:[{id,name?}]}``, ``{models:[…]}`` o una lista → ``[{id,label}]`` sin duplicados."""
    found: dict[str, str] = {}

    def push(item: Any) -> None:
        if isinstance(item, str):
            if item.strip() and item.strip() not in found:
                found[item.strip()] = item.strip()
            return
        if not isinstance(item, dict):
            return

        def text(key: str) -> str | None:
            value = item.get(key)
            return value.strip() if isinstance(value, str) and value.strip() else None

        model_id = text("id") or text("slug") or text("name")
        if not model_id or model_id in found:
            return
        label = text("display_name") or text("displayName") or (text("name") if text("id") else None) or model_id
        found[model_id] = label

    if isinstance(payload, list):
        for item in payload:
            push(item)
    elif isinstance(payload, dict):
        items = payload.get("data") if isinstance(payload.get("data"), list) else payload.get("models")
        for item in items if isinstance(items, list) else []:
            push(item)
    return sorted(({"id": k, "label": v} for k, v in found.items()), key=lambda m: m["id"])


def _http_models(info: providers.Provider, key: str) -> list[dict[str, str]]:
    if not info.models_url:
        raise ValueError("Este proveedor no permite listar modelos: escribe su nombre.")
    if info.models_auth == "anthropic":
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    elif info.models_auth == "bearer":
        if not key:
            raise ValueError("Falta la clave para listar los modelos.")
        headers = {"Authorization": f"Bearer {key}"}
    else:
        headers = {}
    try:
        response = httpx.get(
            info.models_url, headers={**headers, "Accept": "application/json"}, timeout=12.0, follow_redirects=False
        )
    except httpx.HTTPError as exc:
        raise ValueError("No se pudo contactar con el proveedor.") from exc
    if response.status_code in (401, 403):
        raise ValueError("La clave no es válida o ha caducado.")
    if response.status_code >= 400:
        raise ValueError(f"El proveedor respondió {response.status_code}.")
    try:
        return extract_models(response.json())
    except ValueError as exc:
        raise ValueError("El proveedor no devolvió una lista válida.") from exc


def list_models(scope_kind: str, scope_id: int, provider: str, *, user_id: int | None = None) -> list[dict[str, str]]:
    """Catálogo del proveedor con la credencial guardada en ese ámbito."""
    info = providers.provider(provider)
    if config.LLM_FAKE:
        return [{"id": m, "label": m} for m in info.models if m] or [{"id": "fake-model", "label": "fake-model"}]
    if info.link == "claude":
        token = credentials.secret_for(scope_kind, scope_id, provider)
        if not token:
            raise ValueError("Primero vincula tu cuenta de Claude.")
        from webapp.generation import models, runtime

        found = runtime._run_coroutine(lambda: models.claude_code_llm(token, user_id).list_models())
        return [
            {
                "id": m.id,
                "label": m.label,
                **({"hint": "Versión conocida: tu token no la anuncia y puede no estar en tu plan"} if m.source == "known" else {}),
            }
            for m in found
        ]
    if info.link == "chatgpt":
        token = credentials.chatgpt_access_token(int(user_id or scope_id))
        if not token:
            raise ValueError("Vuelve a vincular tu cuenta de ChatGPT.")
        from nas.adk.models.chatgpt import oauth

        from webapp.generation import runtime

        return list(runtime._run_coroutine(lambda: oauth.list_models(token)))
    return _http_models(info, credentials.secret_for(scope_kind, scope_id, provider))
