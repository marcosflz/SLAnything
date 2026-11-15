"""Credenciales de IA: varios proveedores a la vez y modelos visibles (ADR-024, ADR-025).

Ámbitos:

- **Plataforma**: el proveedor general del superadmin (``settings.json``, ADR-023).
- **Usuario** (``ai_providers.scope_kind = 'user'``): quien tiene permiso de autoría
  configura sus propios proveedores — claves de API y suscripciones personales (Claude,
  ChatGPT) — y elige qué modelos ve y cuál es su predeterminado.
- **Academia** (``scope_kind = 'workspace'``): la administración de una academia comparte
  **claves de API** con su profesorado. Nunca suscripciones: una suscripción es de su
  titular y no se usa para nadie más.

Reglas:

- Los secretos se guardan cifrados (Fernet, clave derivada de ``AULA_SECRET``); la API
  solo muestra si existen y sus 4 últimos caracteres.
- Se resuelve siempre con **quien lanza la acción**: nunca con la credencial de otra
  persona (``authoring_jobs.actor_id``).
- Los usuarios y academias no fijan base URL: los proveedores con URL propia son solo de
  la plataforma (sin SSRF).
"""

from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from webapp import config, workspaces
from webapp.authoring import providers, settings
from webapp.db import connect, utcnow

MAX_SECRET_LENGTH = 8000
MAX_MODELS = 500
CHATGPT_REFRESH_MARGIN_S = 300
SCOPES = ("user", "workspace")


# ---------------------------------------------------------------------------
# Cifrado
# ---------------------------------------------------------------------------


def _fernet() -> Fernet:
    digest = hashlib.sha256(("slanything-ai-credentials:" + config.SECRET_KEY).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt(secret: str) -> str:
    return _fernet().encrypt(secret.encode("utf-8")).decode("ascii")


def decrypt(token: str | None) -> str:
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError):
        # AULA_SECRET cambió: la credencial ya no se puede leer.
        return ""


def _hint(secret: str) -> str:
    return f"••••{secret[-4:]}" if len(secret) >= 8 else "••••"


# ---------------------------------------------------------------------------
# Disponibilidad de proveedores
# ---------------------------------------------------------------------------


def subscription_enabled() -> bool:
    return config.USER_PROVIDERS and config.SUBSCRIPTION_PROVIDER


def usable(info: providers.Provider, scope_kind: str) -> bool:
    """El proveedor se puede configurar (y usar) en ese ámbito con la configuración actual."""
    if not config.USER_PROVIDERS or not info.allowed_for(scope_kind):
        return False
    return not info.personal or (scope_kind == "user" and subscription_enabled())


def catalog(scope_kind: str) -> list[dict[str, Any]]:
    level = "user" if scope_kind == "user" else "workspace"
    return [item for item in providers.providers_payload(level) if usable(providers.provider(item["id"]), scope_kind)]


# ---------------------------------------------------------------------------
# Filas
# ---------------------------------------------------------------------------


def _parse_models(raw: str | None) -> list[dict[str, str]]:
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in data if isinstance(data, list) else []:
        entry = {"id": item, "label": item} if isinstance(item, str) else item
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            continue
        if entry["id"] in seen:
            continue
        seen.add(entry["id"])
        out.append({"id": entry["id"], "label": str(entry.get("label") or entry["id"])})
    return out


def _rows(scope_kind: str, scope_id: int) -> list[dict[str, Any]]:
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT * FROM ai_providers WHERE scope_kind = ? AND scope_id = ? ORDER BY id",
            (scope_kind, scope_id),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _row(scope_kind: str, scope_id: int, provider: str) -> dict[str, Any] | None:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM ai_providers WHERE scope_kind = ? AND scope_id = ? AND provider = ?",
            (scope_kind, scope_id, provider),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _ready(info: providers.Provider, row: dict[str, Any], scope_kind: str) -> bool:
    """Configuración completa y usable ahora (sin descifrar más de lo necesario)."""
    if not row.get("enabled") or not usable(info, scope_kind):
        return False
    if info.requires_key and not decrypt(row.get("secret_enc")):
        return False
    return not (info.personal and not row.get("accepted_personal_at"))


def _view(info: providers.Provider, row: dict[str, Any] | None, scope_kind: str) -> dict[str, Any]:
    level = "user" if scope_kind == "user" else "workspace"
    item = next((p for p in providers.providers_payload(level) if p["id"] == info.id), None) or {}
    config_view = None
    if row is not None:
        secret = decrypt(row.get("secret_enc")) if row.get("secret_enc") else ""
        account = None
        if info.link == "chatgpt" and secret:
            try:
                account = json.loads(secret).get("account")
            except (json.JSONDecodeError, AttributeError):
                account = None
        config_view = {
            "enabled": bool(row.get("enabled")),
            "key_configured": bool(row.get("secret_enc")),
            "key_readable": bool(secret) or not row.get("secret_enc"),
            "key_hint": row.get("secret_hint") or "",
            "model": row.get("default_model") or "",
            "models": _parse_models(row.get("models_json")),
            "accepted_personal_at": row.get("accepted_personal_at"),
            "account": account,
            "ready": _ready(info, row, scope_kind),
            "updated_at": row.get("updated_at"),
        }
    return {**item, "config": config_view}


def public(user_id: int) -> dict[str, Any]:
    """Vista de «Mi cuenta → Proveedores de IA»."""
    rows = {row["provider"]: row for row in _rows("user", user_id)}
    views = []
    for item in catalog("user"):
        info = providers.provider(item["id"])
        views.append(_view(info, rows.get(info.id), "user"))
    return {
        "enabled": config.USER_PROVIDERS,
        "subscription_enabled": subscription_enabled(),
        "providers": views,
        "default": user_default(user_id),
        "claude_cli": settings.claude_cli_status() if subscription_enabled() else None,
    }


def public_workspace(workspace_id: int) -> dict[str, Any]:
    """Vista de «Academia → IA»: claves de API compartidas con el profesorado."""
    rows = {row["provider"]: row for row in _rows("workspace", workspace_id)}
    return {
        "enabled": config.USER_PROVIDERS,
        "providers": [_view(providers.provider(i["id"]), rows.get(i["id"]), "workspace") for i in catalog("workspace")],
    }


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------


def _clean_models(models: list[dict[str, Any]] | None) -> list[dict[str, str]] | None:
    if models is None:
        return None
    if len(models) > MAX_MODELS:
        raise ValueError("Demasiados modelos.")
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in models:
        model_id = str(item.get("id") or "").strip()
        if not model_id or len(model_id) > 160 or any(ch.isspace() for ch in model_id):
            raise ValueError("El identificador de un modelo no es válido.")
        if model_id in seen:
            continue
        seen.add(model_id)
        out.append({"id": model_id, "label": str(item.get("label") or model_id).strip()[:160] or model_id})
    return out


def save_provider(
    scope_kind: str,
    scope_id: int,
    provider: str,
    *,
    actor_id: int,
    secret: str | None = None,
    enabled: bool | None = None,
    models: list[dict[str, Any]] | None = None,
    model: str | None = None,
    accept_personal: bool = False,
) -> None:
    """Crea o actualiza la configuración de UN proveedor en un ámbito."""
    if scope_kind not in SCOPES:
        raise ValueError("Ámbito no válido.")
    if not config.USER_PROVIDERS:
        raise ValueError("Esta plataforma no permite proveedores propios.")
    info = providers.provider((provider or "").strip())
    if not usable(info, scope_kind):
        raise ValueError("Ese proveedor no está disponible aquí.")
    if info.link == "chatgpt" and secret is not None:
        raise ValueError("ChatGPT se vincula iniciando sesión, no pegando una clave.")
    clean = _clean_models(models)
    current = _row(scope_kind, scope_id, info.id) or {}
    secret_enc = current.get("secret_enc")
    hint = current.get("secret_hint")
    if secret is not None and secret.strip():
        cleaned = secret.strip()
        if len(cleaned) > MAX_SECRET_LENGTH:
            raise ValueError("La credencial es demasiado larga.")
        secret_enc, hint = encrypt(cleaned), _hint(cleaned)
    if info.requires_key and not secret_enc and info.link == "key":
        raise ValueError(f"Falta la credencial de {info.label}.")
    accepted = current.get("accepted_personal_at")
    if info.personal and not accepted:
        if not accept_personal:
            raise ValueError("Confirma que es tu suscripción personal y que solo la usarás tú.")
        accepted = utcnow()
    models_now = clean if clean is not None else _parse_models(current.get("models_json"))
    default_model = model if model is not None else (current.get("default_model") or "")
    if clean is not None and default_model not in {m["id"] for m in models_now}:
        default_model = models_now[0]["id"] if models_now else ""
    if not current and not models_now:
        seed = info.models[0] if info.models else ""
        if seed:
            models_now, default_model = [{"id": seed, "label": seed}], seed
    if default_model and default_model not in {m["id"] for m in models_now}:
        raise ValueError("El modelo predeterminado debe estar entre los activos.")
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO ai_providers
                   (scope_kind, scope_id, provider, secret_enc, secret_hint, enabled, models_json,
                    default_model, accepted_personal_at, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(scope_kind, scope_id, provider) DO UPDATE SET
                   secret_enc = excluded.secret_enc, secret_hint = excluded.secret_hint,
                   enabled = excluded.enabled, models_json = excluded.models_json,
                   default_model = excluded.default_model,
                   accepted_personal_at = excluded.accepted_personal_at,
                   updated_by = excluded.updated_by, updated_at = excluded.updated_at""",
            (
                scope_kind, scope_id, info.id, secret_enc, hint,
                int(enabled if enabled is not None else current.get("enabled", 1)),
                json.dumps(models_now, ensure_ascii=False), default_model, accepted, actor_id, utcnow(),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    if scope_kind == "user" and user_default(scope_id) is None and default_model and _ready(info, _row(scope_kind, scope_id, info.id) or {}, scope_kind):
        set_default(scope_id, {"source": "user", "provider": info.id, "model": default_model})


def delete_provider(scope_kind: str, scope_id: int, provider: str) -> None:
    conn = connect()
    try:
        conn.execute(
            "DELETE FROM ai_providers WHERE scope_kind = ? AND scope_id = ? AND provider = ?",
            (scope_kind, scope_id, provider),
        )
        conn.commit()
    finally:
        conn.close()


def store_secret(scope_kind: str, scope_id: int, provider: str, secret: str, *, actor_id: int, accept_personal: bool) -> None:
    """Guarda una credencial obtenida por vinculación (token de Claude o sesión de ChatGPT)."""
    info = providers.provider(provider)
    if not usable(info, scope_kind):
        raise ValueError("Ese proveedor no está disponible aquí.")
    current = _row(scope_kind, scope_id, provider)
    conn = connect()
    try:
        hint = "ChatGPT" if info.link == "chatgpt" else _hint(secret)
        if current:
            conn.execute(
                "UPDATE ai_providers SET secret_enc = ?, secret_hint = ?, accepted_personal_at = COALESCE(accepted_personal_at, ?), "
                "updated_by = ?, updated_at = ? WHERE id = ?",
                (encrypt(secret), hint, utcnow() if accept_personal else None, actor_id, utcnow(), current["id"]),
            )
        else:
            if info.personal and not accept_personal:
                raise ValueError("Confirma que es tu suscripción personal y que solo la usarás tú.")
            conn.execute(
                """INSERT INTO ai_providers
                       (scope_kind, scope_id, provider, secret_enc, secret_hint, enabled, models_json,
                        default_model, accepted_personal_at, updated_by, updated_at)
                   VALUES (?, ?, ?, ?, ?, 1, '[]', '', ?, ?, ?)""",
                (scope_kind, scope_id, provider, encrypt(secret), hint, utcnow() if accept_personal else None, actor_id, utcnow()),
            )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Predeterminado y grupos para el selector
# ---------------------------------------------------------------------------


def user_default(user_id: int) -> dict[str, str] | None:
    conn = connect()
    try:
        row = conn.execute("SELECT ai_default_json FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    try:
        data = json.loads(row["ai_default_json"]) if row and row["ai_default_json"] else None
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not all(isinstance(data.get(k), str) for k in ("source", "provider", "model")):
        return None
    return {"source": data["source"], "provider": data["provider"], "model": data["model"]}


def set_default(user_id: int, choice: dict[str, str] | None) -> None:
    conn = connect()
    try:
        conn.execute(
            "UPDATE users SET ai_default_json = ? WHERE id = ?",
            (json.dumps(choice) if choice else None, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def _author_workspaces(user_id: int) -> set[int]:
    """Academias en las que la persona es profesorado o más (pueden compartirle claves)."""
    conn = connect()
    try:
        return {
            int(m["id"])
            for m in workspaces.memberships_for_user(conn, user_id)
            if m.get("kind") == "organization" and workspaces.role_at_least(m.get("role"), "teacher")
        }
    finally:
        conn.close()


def _workspace_name(workspace_id: int) -> str:
    conn = connect()
    try:
        ws = workspaces.get_workspace(conn, workspace_id)
        return (ws or {}).get("name") or "Academia"
    finally:
        conn.close()


def model_groups(user_id: int, workspace_id: int | None) -> dict[str, Any]:
    """Modelos activos que esta persona puede usar ahora, agrupados (selector del Estudio)."""
    groups: list[dict[str, Any]] = []
    for row in _rows("user", user_id):
        try:
            info = providers.provider(row["provider"])
        except ValueError:
            continue
        models = _parse_models(row.get("models_json"))
        if models and _ready(info, row, "user"):
            groups.append({"source": "user", "provider": info.id, "label": info.label, "kind": info.kind, "models": models})
    if workspace_id and workspace_id in _author_workspaces(user_id):
        name = _workspace_name(workspace_id)
        for row in _rows("workspace", workspace_id):
            try:
                info = providers.provider(row["provider"])
            except ValueError:
                continue
            models = _parse_models(row.get("models_json"))
            if models and _ready(info, row, "workspace"):
                groups.append(
                    {"source": "workspace", "provider": info.id, "label": f"{info.label} · {name}", "kind": "api", "models": models}
                )
    platform = settings.load_settings()
    if platform.get("provider") and platform.get("model"):
        try:
            label = providers.provider(platform["provider"]).label
        except ValueError:
            label = platform["provider"]
        groups.append(
            {
                "source": "platform",
                "provider": platform["provider"],
                "label": f"{label} · plataforma",
                "kind": "api",
                "models": [{"id": platform["model"], "label": platform["model"]}],
            }
        )
    default = user_default(user_id)
    valid = default and any(
        g["source"] == default["source"] and g["provider"] == default["provider"] and any(m["id"] == default["model"] for m in g["models"])
        for g in groups
    )
    if not valid:
        first = groups[0] if groups else None
        default = {"source": first["source"], "provider": first["provider"], "model": first["models"][0]["id"]} if first else None
    return {"groups": groups, "default": default}


# ---------------------------------------------------------------------------
# Resolución (con quién se genera)
# ---------------------------------------------------------------------------


def _from_row(info: providers.Provider, row: dict[str, Any], model: str, source: str, user_id: int | None) -> dict[str, Any] | None:
    secret = decrypt(row.get("secret_enc"))
    if info.link == "chatgpt":
        if user_id is None:
            return None
        token = chatgpt_access_token(int(user_id))
        if not token:
            return None
        secret = token
    return {
        "provider": info.id,
        "model": "" if (info.adk_provider == "claude-code" and model == "default") else model,
        "base_url": "",
        "api_key": secret,
        "user_id": user_id if source == "user" else None,
        "workspace_id": row["scope_id"] if source == "workspace" else None,
        "source": source,
    }


def _try_choice(user_id: int, workspace_id: int | None, choice: dict[str, Any]) -> dict[str, Any] | None:
    source = choice.get("source")
    provider = str(choice.get("provider") or "")
    model = str(choice.get("model") or "")
    if source == "platform":
        platform = dict(settings.load_settings())
        if platform.get("provider") == provider and platform.get("model") == model:
            platform.update({"source": "platform", "user_id": None})
            return platform
        return None
    if source == "user":
        scope_kind, scope_id = "user", user_id
    elif source == "workspace" and workspace_id and workspace_id in _author_workspaces(user_id):
        scope_kind, scope_id = "workspace", workspace_id
    else:
        return None
    try:
        info = providers.provider(provider)
    except ValueError:
        return None
    row = _row(scope_kind, scope_id, provider)
    if row is None or not _ready(info, row, scope_kind):
        return None
    if model not in {m["id"] for m in _parse_models(row.get("models_json"))}:
        return None
    return _from_row(info, row, model, source, user_id)


def resolve(user_id: int | None, workspace_id: int | None = None, choice: dict[str, Any] | None = None) -> dict[str, Any]:
    """Ajustes con los que genera ``user_id``.

    Orden: el modelo elegido (si esta persona puede usarlo) → su predeterminado → su primer
    proveedor listo → la plataforma. Nunca la credencial de otra persona.
    """
    if user_id:
        uid = int(user_id)
        candidates = [c for c in (choice, user_default(uid)) if c]
        for candidate in candidates:
            resolved = _try_choice(uid, workspace_id, candidate)
            if resolved is not None:
                return resolved
        for row in _rows("user", uid):
            try:
                info = providers.provider(row["provider"])
            except ValueError:
                continue
            models = _parse_models(row.get("models_json"))
            if models and _ready(info, row, "user"):
                model = row.get("default_model") or models[0]["id"]
                resolved = _from_row(info, row, model, "user", uid)
                if resolved is not None:
                    return resolved
    platform = dict(settings.load_settings())
    platform.update({"source": "platform", "user_id": None})
    return platform


def user_settings(user_id: int, provider: str) -> dict[str, Any] | None:
    """Ajustes completos de un proveedor propio (para «Probar»). Solo backend."""
    row = _row("user", user_id, provider)
    if row is None:
        return None
    info = providers.provider(provider)
    if not _ready(info, row, "user"):
        return None
    models = _parse_models(row.get("models_json"))
    model = row.get("default_model") or (models[0]["id"] if models else "")
    return _from_row(info, row, model, "user", user_id)


def workspace_settings(workspace_id: int, provider: str) -> dict[str, Any] | None:
    row = _row("workspace", workspace_id, provider)
    if row is None:
        return None
    info = providers.provider(provider)
    if not _ready(info, row, "workspace"):
        return None
    models = _parse_models(row.get("models_json"))
    model = row.get("default_model") or (models[0]["id"] if models else "")
    return _from_row(info, row, model, "workspace", None)


def secret_for(scope_kind: str, scope_id: int, provider: str) -> str:
    """Secreto descifrado (para listar modelos). Solo backend."""
    row = _row(scope_kind, scope_id, provider)
    return decrypt((row or {}).get("secret_enc"))


def describe(resolved: dict[str, Any]) -> dict[str, Any]:
    """Resumen sin secretos de con qué se va a generar."""
    try:
        info = providers.provider(str(resolved.get("provider") or ""))
        label = info.label
        personal = info.personal
    except ValueError:
        label, personal = str(resolved.get("provider") or ""), False
    return {
        "source": resolved.get("source", "platform"),
        "provider": resolved.get("provider"),
        "provider_label": label,
        "model": resolved.get("model") or ("default" if resolved.get("provider") == "claude-code" else ""),
        "personal": personal,
    }


# ---------------------------------------------------------------------------
# ChatGPT: sesión de cada persona, con renovación serializada
# ---------------------------------------------------------------------------

_chatgpt_locks: dict[int, threading.Lock] = {}
_chatgpt_locks_guard = threading.Lock()


def _chatgpt_lock(user_id: int) -> threading.Lock:
    with _chatgpt_locks_guard:
        return _chatgpt_locks.setdefault(user_id, threading.Lock())


def _refresh_chatgpt(creds: dict[str, Any]) -> dict[str, Any]:
    """Renueva con nas-adk (aislado para poder sustituirlo en tests)."""
    from nas.adk.models.chatgpt import oauth

    from webapp.generation import runtime

    current = oauth.ChatGptCredentials(
        client_id=str(creds["client_id"]),
        access_token=str(creds["access_token"]),
        refresh_token=str(creds["refresh_token"]),
        expires_at=float(creds["expires_at"]),
        account=creds.get("account"),
    )
    renewed = runtime._run_coroutine(lambda: oauth.refresh(current))
    return json.loads(renewed.to_json())


def chatgpt_access_token(user_id: int) -> str | None:
    """Token de acceso vigente del plan de ChatGPT de ``user_id``, o ``None`` si hay que vincular.

    El token de refresco rota en cada uso: dos renovaciones a la vez invalidarían la sesión,
    así que se serializan por persona y se relee la fila dentro del bloqueo.
    """
    def read() -> dict[str, Any] | None:
        row = _row("user", user_id, "chatgpt")
        raw = decrypt((row or {}).get("secret_enc"))
        try:
            data = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) and data.get("access_token") else None

    creds = read()
    if creds is None:
        return None
    if float(creds.get("expires_at") or 0) - time.time() > CHATGPT_REFRESH_MARGIN_S:
        return str(creds["access_token"])
    with _chatgpt_lock(user_id):
        creds = read()
        if creds is None:
            return None
        if float(creds.get("expires_at") or 0) - time.time() > CHATGPT_REFRESH_MARGIN_S:
            return str(creds["access_token"])
        try:
            renewed = _refresh_chatgpt(creds)
        except Exception as exc:  # noqa: BLE001 - se distingue abajo
            from nas.adk.models.errors import LlmAuthError

            if isinstance(exc, LlmAuthError):
                # Sesión revocada o caducada: hay que volver a vincular.
                conn = connect()
                try:
                    conn.execute(
                        "UPDATE ai_providers SET secret_enc = NULL, secret_hint = NULL, updated_at = ? "
                        "WHERE scope_kind = 'user' AND scope_id = ? AND provider = 'chatgpt'",
                        (utcnow(), user_id),
                    )
                    conn.commit()
                finally:
                    conn.close()
                return None
            raise
        conn = connect()
        try:
            conn.execute(
                "UPDATE ai_providers SET secret_enc = ?, updated_at = ? "
                "WHERE scope_kind = 'user' AND scope_id = ? AND provider = 'chatgpt'",
                (encrypt(json.dumps(renewed)), utcnow(), user_id),
            )
            conn.commit()
        finally:
            conn.close()
        return str(renewed["access_token"])
