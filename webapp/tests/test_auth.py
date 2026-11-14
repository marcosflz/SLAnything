"""Registro, inicio y cierre de sesión, next seguro y almacenamiento de secretos."""

from __future__ import annotations

import sqlite3

import pytest

from webapp import config
from webapp.security import login_limiter, token_hash

from conftest import csrf, login, register


def _fetchone(db_path, query: str, params: tuple = ()):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(query, params).fetchone()
    finally:
        conn.close()


def _fetchall(db_path, query: str, params: tuple = ()):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def test_demo_login_creates_session_and_grants_course_access(client):
    response = login(client)

    assert response.status_code == 200
    assert response.json()["next"] == "/"
    assert response.json()["user"]["name"] == "Estudiante demo"
    assert "aula_session" in client.cookies

    assert client.get("/api/v1/dashboard").status_code == 200
    course = client.get("/api/v1/course")
    assert course.status_code == 200
    assert course.json()["course"]["slug"] == "llm-desde-cero"


def test_session_cookie_is_httponly_and_lax(client):
    response = login(client)
    cookie = response.headers.get("set-cookie", "").lower()

    assert "aula_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie


def test_wrong_password_does_not_create_session(client):
    response = login(client, password="contraseña-incorrecta")

    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos."
    assert "aula_session" not in client.cookies
    assert client.get("/api/v1/course").status_code == 401


def test_unknown_email_does_not_create_session(client):
    response = login(client, email="nadie@example.com", password="loquesea123")

    assert response.status_code == 401
    assert "aula_session" not in client.cookies


def test_register_creates_session_and_personal_workspace(client, db_path):
    email = "nueva@example.com"
    response = register(client, email, name="Alumno Nuevo")

    assert response.status_code == 200
    assert "aula_session" in client.cookies
    assert client.get("/api/v1/dashboard").status_code == 200

    row = _fetchone(db_path, "SELECT name, role FROM users WHERE email = ?", (email,))
    assert row == ("Alumno Nuevo", "student")


def test_register_rejects_duplicate_email_case_insensitive(client, db_path):
    email = "duplicado@example.com"
    assert register(client, email).status_code == 200

    response = register(client, "DUPLICADO@EXAMPLE.COM", name="Otra Persona")

    assert response.status_code == 400
    assert "Ya existe una cuenta con ese correo" in response.json()["detail"]
    row = _fetchone(
        db_path, "SELECT COUNT(*) FROM users WHERE lower(email) = ?", (email,)
    )
    assert row == (1,)


def test_register_rejects_short_password(client, db_path):
    response = register(client, "corta@example.com", password="corta", password2="corta")

    assert response.status_code == 400
    assert "al menos 8 caracteres" in response.json()["detail"]
    assert "aula_session" not in client.cookies
    assert _fetchone(
        db_path, "SELECT COUNT(*) FROM users WHERE email = ?", ("corta@example.com",)
    ) == (0,)


def test_register_rejects_mismatched_passwords(client, db_path):
    response = register(
        client,
        "mismatch@example.com",
        password="clave-segura-123",
        password2="otra-clave-123",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Las contraseñas no coinciden."
    assert _fetchone(
        db_path, "SELECT COUNT(*) FROM users WHERE email = ?", ("mismatch@example.com",)
    ) == (0,)


def test_logout_invalidates_session(client, db_path):
    assert login(client).status_code == 200
    token = csrf(client)

    response = client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": token})

    assert response.status_code == 200
    assert "aula_session" not in client.cookies
    assert _fetchone(db_path, "SELECT COUNT(*) FROM sessions") == (0,)
    assert client.get("/api/v1/course").status_code == 401


def test_logout_requires_csrf(client):
    assert login(client).status_code == 200
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 403


@pytest.mark.parametrize(
    "external_next",
    ["https://evil.example", "//evil.example", "http://evil.example/phishing"],
)
def test_login_ignores_external_next(client, external_next):
    response = login(client, next=external_next)

    assert response.status_code == 200
    assert response.json()["next"] == "/"


def test_login_keeps_internal_next(client):
    response = login(client, next="/progreso")

    assert response.status_code == 200
    assert response.json()["next"] == "/progreso"


def test_login_rate_limit_blocks_after_repeated_failures(client):
    for _ in range(login_limiter.max_attempts):
        assert login(client, password="contraseña-incorrecta").status_code == 401

    blocked = login(client, password=config.DEMO_PASSWORD)

    assert blocked.status_code == 429
    assert "Demasiados intentos" in blocked.json()["detail"]
    assert "aula_session" not in client.cookies


def test_expired_session_is_rejected(client, db_path):
    assert login(client).status_code == 200

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("UPDATE sessions SET expires_at = ?", ("2000-01-01T00:00:00+00:00",))
        conn.commit()
    finally:
        conn.close()

    assert client.get("/api/v1/course").status_code == 401
    assert client.get("/api/v1/session").json()["user"] is None


def test_password_and_session_token_are_stored_hashed(client, db_path):
    email = "hash@example.com"
    password = "clave-super-segura"

    assert register(client, email, password=password).status_code == 200
    token = client.cookies.get("aula_session")
    assert token

    password_hash = _fetchone(
        db_path, "SELECT password_hash FROM users WHERE email = ?", (email,)
    )[0]
    assert password_hash.startswith("scrypt$")
    assert password not in password_hash

    sessions = _fetchall(db_path, "SELECT id FROM sessions")
    assert len(sessions) == 1
    assert sessions[0][0] == token_hash(token)
    assert sessions[0][0] != token
