"""Rutas de autenticación: entrar, registro y salir."""

from __future__ import annotations

import re
import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from webapp import config, repositories
from webapp.db import get_db
from webapp.deps import ensure_csrf, get_current_user, require_user
from webapp.i18n import t
from webapp.security import (
    hash_password,
    login_limiter,
    new_csrf_token,
    new_token,
    token_hash,
    verify_password,
)
from webapp.templating import render

router = APIRouter()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _safe_next(value: str | None, fallback: str = "/") -> str:
    """Solo permite rutas internas absolutas (evita redirecciones abiertas)."""
    if not value or not value.startswith("/") or value.startswith("//"):
        return fallback
    return value


def _log_in(
    conn: sqlite3.Connection,
    user_id: int,
    token: str,
    response: RedirectResponse,
) -> RedirectResponse:
    """Crea la sesión, registra la actividad y deja la cookie en la respuesta."""
    repositories.create_session(
        conn,
        user_id,
        token_hash(token),
        new_csrf_token(),
        config.SESSION_DAYS,
    )
    repositories.record_activity(conn, user_id, "login")
    conn.commit()
    response.set_cookie(
        key=config.COOKIE_NAME,
        value=token,
        max_age=config.SESSION_DAYS * 86400,
        httponly=True,
        samesite="lax",
        secure=config.SECURE_COOKIES,
        path="/",
    )
    return response


@router.get("/entrar")
def login_form(
    request: Request,
    next: str = "/",
    user: dict | None = Depends(get_current_user),
):
    if user is not None:
        return RedirectResponse("/", status_code=303)
    return render(
        request,
        "pages/auth_login.html",
        next=_safe_next(next),
        error=None,
    )


@router.post("/entrar")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    conn: sqlite3.Connection = Depends(get_db),
):
    email = email.strip()
    client_host = request.client.host if request.client else "local"
    limiter_key = f"{email.lower()}|{client_host}"

    if login_limiter.is_blocked(limiter_key):
        minutes = max(1, login_limiter.retry_after(limiter_key) // 60)
        return render(
            request,
            "pages/auth_login.html",
            next=_safe_next(next),
            error=t(
                request,
                "Demasiados intentos de inicio de sesión. Espera {minutes} minutos antes de volver a intentarlo.",
                minutes=minutes,
            ),
            values={"email": email},
            status_code=429,
        )

    row = repositories.get_user_by_email(conn, email)
    if row is None or not verify_password(password, row["password_hash"]):
        login_limiter.register_failure(limiter_key)
        return render(
            request,
            "pages/auth_login.html",
            next=_safe_next(next),
            error=t(request, "Correo o contraseña incorrectos."),
            values={"email": email},
        )

    login_limiter.reset(limiter_key)
    token = new_token()
    response = RedirectResponse(_safe_next(next), status_code=303)
    return _log_in(conn, row["id"], token, response)


@router.get("/registro")
def register_form(
    request: Request,
    next: str = "/",
    user: dict | None = Depends(get_current_user),
):
    if user is not None:
        return RedirectResponse("/", status_code=303)
    return render(
        request,
        "pages/auth_register.html",
        next=_safe_next(next),
        error=None,
        values={},
    )


@router.post("/registro")
def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    next: str = Form("/"),
    conn: sqlite3.Connection = Depends(get_db),
):
    clean_name = name.strip()
    clean_email = email.strip()
    values = {"name": clean_name, "email": clean_email}

    def error_response(message: str):
        return render(
            request,
            "pages/auth_register.html",
            next=_safe_next(next),
            error=message,
            values=values,
        )

    if not 2 <= len(clean_name) <= 80:
        return error_response(t(request, "El nombre debe tener entre 2 y 80 caracteres."))
    if not EMAIL_RE.match(clean_email):
        return error_response(t(request, "Introduce un correo electrónico válido."))
    if len(password) < 8:
        return error_response(t(request, "La contraseña debe tener al menos 8 caracteres."))
    if password != password2:
        return error_response(t(request, "Las contraseñas no coinciden."))
    if repositories.get_user_by_email(conn, clean_email) is not None:
        return error_response(
            t(request, "Ya existe una cuenta con ese correo. Prueba a iniciar sesión.")
        )

    try:
        user = repositories.create_user(
            conn,
            email=clean_email,
            name=clean_name,
            password_hash=hash_password(password),
            role="student",
        )
    except sqlite3.IntegrityError:
        return error_response(
            t(request, "Ya existe una cuenta con ese correo. Prueba a iniciar sesión.")
        )

    token = new_token()
    response = RedirectResponse(_safe_next(next), status_code=303)
    return _log_in(conn, user["id"], token, response)


@router.post("/salir")
def logout(
    request: Request,
    csrf_token: str = Form(""),
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    ensure_csrf(request, user, csrf_token)
    repositories.delete_session(conn, user["session_id"])
    conn.commit()
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(config.COOKIE_NAME, path="/")
    return response
