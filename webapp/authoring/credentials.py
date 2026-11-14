"""Credenciales de IA de cada usuario (ADR-024).

Quien tiene permiso de autoría puede usar su propio proveedor (una API key o su
suscripción personal de Claude) en lugar del de la plataforma. Reglas:

- El secreto se guarda cifrado (Fernet, clave derivada de ``AULA_SECRET``) en
  ``user_ai_settings``; la API solo muestra si existe y sus 4 últimos caracteres.
- Las credenciales se resuelven siempre con **quien lanza la acción**: nunca se
  usa la credencial de una persona en un trabajo que lanza otra.
- La suscripción (``claude-code``) solo existe a nivel de usuario; la plataforma
  no puede tenerla como proveedor general.
- Los usuarios no fijan base URL (los proveedores con URL propia son solo de la
  plataforma), para no abrir peticiones del servidor a hosts arbitrarios.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from webapp import config
from webapp.authoring import providers, settings
from webapp.db import connect, utcnow

MAX_SECRET_LENGTH = 4000


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


def _row(user_id: int) -> dict[str, Any] | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM user_ai_settings WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def subscription_enabled() -> bool:
    return config.USER_PROVIDERS and config.SUBSCRIPTION_PROVIDER


def _usable(info: providers.Provider) -> bool:
    if not config.USER_PROVIDERS or not info.allowed_for("user"):
        return False
    return not info.personal or subscription_enabled()


def user_settings(user_id: int) -> dict[str, Any] | None:
    """Ajustes propios completos (con el secreto descifrado). Solo backend."""
    row = _row(user_id)
    if row is None:
        return None
    try:
        info = providers.provider(row["provider"])
    except ValueError:
        return None
    if not _usable(info):
        return None
    secret = decrypt(row.get("secret_enc"))
    if info.requires_key and not secret:
        return None
    if info.personal and not row.get("accepted_personal_at"):
        return None
    return {
        "provider": info.id,
        "model": row.get("model") or "",
        "base_url": "",
        "api_key": secret,
        "user_id": user_id,
        "source": "user",
    }


def resolve(user_id: int | None) -> dict[str, Any]:
    """Ajustes con los que genera ``user_id``: los suyos o los de la plataforma."""
    if user_id:
        own = user_settings(int(user_id))
        if own is not None:
            return own
    platform = dict(settings.load_settings())
    platform.update({"source": "platform", "user_id": None})
    return platform


def public(user_id: int) -> dict[str, Any]:
    row = _row(user_id)
    active = user_settings(user_id)
    data: dict[str, Any] = {
        "enabled": config.USER_PROVIDERS,
        "subscription_enabled": subscription_enabled(),
        "configured": row is not None,
        "active": active is not None,
        "provider": row["provider"] if row else None,
        "model": row["model"] if row else "",
        "key_configured": bool(row and row.get("secret_enc")),
        "key_hint": (row or {}).get("secret_hint") or "",
        "accepted_personal_at": (row or {}).get("accepted_personal_at"),
        "updated_at": (row or {}).get("updated_at"),
        "providers": providers_for_user(),
        "claude_cli": settings.claude_cli_status() if subscription_enabled() else None,
    }
    if row and active is None:
        data["warning"] = (
            "Tus ajustes guardados no se pueden usar ahora (credencial ilegible, "
            "proveedor desactivado o falta aceptar el uso personal). Se usa el de la plataforma."
        )
    return data


def providers_for_user() -> list[dict[str, Any]]:
    return [
        item
        for item in providers.providers_payload("user")
        if not item["personal"] or subscription_enabled()
    ]


def save(
    user_id: int,
    *,
    provider: str,
    model: str = "",
    secret: str | None = None,
    accept_personal: bool = False,
) -> dict[str, Any]:
    if not config.USER_PROVIDERS:
        raise ValueError("Esta plataforma no permite proveedores propios.")
    info = providers.provider((provider or "").strip())
    if not _usable(info):
        raise ValueError("Ese proveedor no está disponible para cuentas de usuario.")
    model = (model or "").strip()
    if info.adk_provider != "claude-code" and not model:
        raise ValueError("Indica el modelo.")
    if len(model) > 160 or any(char.isspace() for char in model):
        raise ValueError("El identificador del modelo no es válido.")
    current = _row(user_id) or {}
    same_provider = current.get("provider") == info.id
    secret_enc = current.get("secret_enc") if same_provider else None
    hint = current.get("secret_hint") if same_provider else None
    if secret is not None and secret.strip():
        cleaned = secret.strip()
        if len(cleaned) > MAX_SECRET_LENGTH:
            raise ValueError("La credencial es demasiado larga.")
        secret_enc = encrypt(cleaned)
        hint = f"••••{cleaned[-4:]}" if len(cleaned) >= 8 else "••••"
    if info.requires_key and not secret_enc:
        raise ValueError(f"Falta la credencial de {info.label}.")
    accepted = None
    if info.personal:
        if not accept_personal:
            raise ValueError("Confirma que es tu suscripción personal y que solo la usarás tú.")
        accepted = utcnow()
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO user_ai_settings
                   (user_id, provider, model, secret_enc, secret_hint, accepted_personal_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   provider = excluded.provider, model = excluded.model,
                   secret_enc = excluded.secret_enc, secret_hint = excluded.secret_hint,
                   accepted_personal_at = excluded.accepted_personal_at,
                   updated_at = excluded.updated_at""",
            (user_id, info.id, model, secret_enc, hint, accepted, utcnow()),
        )
        conn.commit()
    finally:
        conn.close()
    return public(user_id)


def delete(user_id: int) -> dict[str, Any]:
    conn = connect()
    try:
        conn.execute("DELETE FROM user_ai_settings WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
    return public(user_id)


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
        "model": resolved.get("model") or "",
        "personal": personal,
    }
