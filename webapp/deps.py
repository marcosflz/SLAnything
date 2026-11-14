"""Dependencias de autenticación y protección CSRF."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request

from webapp import config, workspaces
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
                      u.id, u.email, u.name, u.role, u.is_platform_admin
               FROM sessions s
               JOIN users u ON u.id = s.user_id
               WHERE s.id = ? AND s.expires_at > ? AND u.disabled_at IS NULL""",
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
            _attach_workspace(request, conn, user)
    request.state.user = user
    return user


def _attach_workspace(request: Request, conn: sqlite3.Connection, user: dict) -> None:
    """Añade al usuario sus membresías, el espacio activo y sus permisos."""
    memberships = workspaces.memberships_for_user(conn, user["id"])
    requested = request.headers.get("X-Workspace") or request.cookies.get(
        config.WORKSPACE_COOKIE
    )
    active = workspaces.resolve_active(memberships, requested)
    user["memberships"] = memberships
    user["workspace_ids"] = frozenset(item["id"] for item in memberships)
    user["workspace"] = active
    role = active["role"] if active else None
    user["ws_role"] = role
    user["permissions"] = permissions_for(role, bool(user.get("is_platform_admin")))


def permissions_for(role: str | None, platform_admin: bool = False) -> dict:
    return {
        "author": workspaces.role_at_least(role, "teacher"),
        "teach": workspaces.role_at_least(role, "teacher"),
        "admin": workspaces.role_at_least(role, "admin"),
        "owner": workspaces.role_at_least(role, "owner"),
        "platform": platform_admin,
    }


def require_user(user: dict | None = Depends(get_current_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=401, detail="Inicia sesión para continuar.")
    return user


def require_role(minimum: str, detail: str | None = None):
    """Dependencia: exige un rol mínimo en el espacio de trabajo activo."""

    def dependency(user: dict = Depends(require_user)) -> dict:
        if not workspaces.role_at_least(user.get("ws_role"), minimum):
            raise HTTPException(
                status_code=403,
                detail=detail or "No tienes permiso para ver esta página.",
            )
        return user

    return dependency


# Profesorado: teacher, admin u owner del espacio activo. En un espacio personal
# el usuario es owner, así que también puede usar el Estudio para sí mismo.
require_teacher = require_role("teacher", "Esta sección es solo para el profesorado.")
require_admin = require_role("admin", "Esta sección es solo para la administración del espacio.")


def require_platform_admin(user: dict = Depends(require_user)) -> dict:
    if not user.get("is_platform_admin"):
        raise HTTPException(status_code=403, detail="Solo para la administración de la plataforma.")
    return user


def ensure_csrf(request: Request, user: dict, form_token: str | None = None) -> None:
    """Valida el token de formulario o la cabecera usada por `fetch`."""
    supplied = form_token or request.headers.get("X-CSRF-Token")
    if not csrf_matches(user.get("csrf_token", ""), supplied):
        raise HTTPException(status_code=403, detail="Token de seguridad inválido o caducado.")
