"""Dependencias de autenticación y protección CSRF."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request

from webapp import config
from webapp.db import get_db, utcnow
from webapp.security import csrf_matches, token_hash


def get_current_user(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> dict | None:
    """Carga la sesión desde la cookie y la deja también en `request.state`."""
    token = request.cookies.get(config.COOKIE_NAME)
    user = None
    if token:
        row = conn.execute(
            """SELECT s.id AS session_id, s.csrf_token, s.expires_at,
                      u.id, u.email, u.name, u.role
               FROM sessions s
               JOIN users u ON u.id = s.user_id
               WHERE s.id = ? AND s.expires_at > ?""",
            (token_hash(token), utcnow()),
        ).fetchone()
        if row:
            user = dict(row)
            expires_at = user.pop("expires_at", None)
            # Renovación deslizante: si quedan menos de 7 días, se amplía la
            # sesión para no expulsar a quien entra con regularidad.
            try:
                remaining = datetime.fromisoformat(expires_at) - datetime.now(timezone.utc)
                if remaining < timedelta(days=7):
                    conn.execute(
                        "UPDATE sessions SET expires_at = ? WHERE id = ?",
                        (
                            (
                                datetime.now(timezone.utc)
                                + timedelta(days=config.SESSION_DAYS)
                            ).isoformat(timespec="seconds"),
                            user["session_id"],
                        ),
                    )
            except (TypeError, ValueError):
                pass
    request.state.user = user
    return user


def require_user(user: dict | None = Depends(get_current_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=401, detail="Inicia sesión para continuar.")
    return user


def require_teacher(user: dict = Depends(require_user)) -> dict:
    if user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Esta sección es solo para el profesorado.")
    return user


def ensure_csrf(request: Request, user: dict, form_token: str | None = None) -> None:
    """Valida el token de formulario o la cabecera usada por `fetch`."""
    supplied = form_token or request.headers.get("X-CSRF-Token")
    if not csrf_matches(user.get("csrf_token", ""), supplied):
        raise HTTPException(status_code=403, detail="Token de seguridad inválido o caducado.")
