"""Registro, inicio y cierre de sesión, next seguro y almacenamiento de secretos."""

from __future__ import annotations

import sqlite3

import pytest

from webapp import config
from webapp.security import login_limiter, token_hash

from conftest import csrf_from, login, register


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


def test_demo_login_redirects_and_grants_course_access(client):
    response = login(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "aula_session" in client.cookies

    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "Hola, Estudiante." in dashboard.text

    course = client.get("/curso")
    assert course.status_code == 200
    assert "Programa del curso" in course.text
    assert "Estudiante demo" in course.text


def test_session_cookie_is_httponly_and_lax(client):
    response = login(client)
    cookie = response.headers.get("set-cookie", "").lower()

    assert "aula_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie


def test_wrong_password_does_not_create_session(client):
    response = login(client, password="contraseña-incorrecta")

    assert response.status_code == 200
    assert "Correo o contraseña incorrectos." in response.text
    assert "aula_session" not in client.cookies

    course = client.get("/curso", follow_redirects=False)
    assert course.status_code == 303
    assert course.headers["location"] == "/entrar?next=/curso"


def test_unknown_email_does_not_create_session(client):
    response = login(client, email="nadie@example.com", password="loquesea123")

    assert response.status_code == 200
    assert "Correo o contraseña incorrectos." in response.text
    assert "aula_session" not in client.cookies


def test_register_creates_session_and_opens_dashboard(client, db_path):
    email = "nueva@example.com"
    response = register(client, email, name="Alumno Nuevo")

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "aula_session" in client.cookies

    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "Hola, Alumno." in dashboard.text

    course = client.get("/curso")
    assert course.status_code == 200

    row = _fetchone(db_path, "SELECT name, role FROM users WHERE email = ?", (email,))
    assert row == ("Alumno Nuevo", "student")


def test_register_rejects_duplicate_email_case_insensitive(client, db_path):
    email = "duplicado@example.com"
    assert register(client, email).status_code == 303

    response = register(client, "DUPLICADO@EXAMPLE.COM", name="Otra Persona")

    assert response.status_code == 200
    assert "Ya existe una cuenta con ese correo" in response.text

    row = _fetchone(
        db_path,
        "SELECT COUNT(*) FROM users WHERE lower(email) = ?",
        (email,),
    )
    assert row == (1,)


def test_register_rejects_short_password(client, db_path):
    response = register(client, "corta@example.com", password="corta", password2="corta")

    assert response.status_code == 200
    assert "al menos 8 caracteres" in response.text
    assert "aula_session" not in client.cookies

    row = _fetchone(
        db_path,
        "SELECT COUNT(*) FROM users WHERE email = ?",
        ("corta@example.com",),
    )
    assert row == (0,)


def test_register_rejects_mismatched_passwords(client, db_path):
    response = register(
        client,
        "mismatch@example.com",
        password="clave-segura-123",
        password2="otra-clave-123",
    )

    assert response.status_code == 200
    assert "Las contraseñas no coinciden." in response.text
    assert _fetchone(
        db_path,
        "SELECT COUNT(*) FROM users WHERE email = ?",
        ("mismatch@example.com",),
    ) == (0,)


def test_logout_invalidates_session(client, db_path):
    assert login(client).status_code == 303
    page = client.get("/leccion/que-es-un-llm")
    token = csrf_from(page.text)

    response = client.post(
        "/salir",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "aula_session" not in client.cookies
    assert _fetchone(db_path, "SELECT COUNT(*) FROM sessions") == (0,)

    course = client.get("/curso", follow_redirects=False)
    assert course.status_code == 303
    assert course.headers["location"] == "/entrar?next=/curso"


@pytest.mark.parametrize(
    "external_next",
    [
        "https://evil.example",
        "//evil.example",
        "http://evil.example/phishing",
    ],
)
def test_login_ignores_external_next(client, external_next):
    response = login(client, next=external_next)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "evil.example" not in response.headers["location"]
    assert client.get("/curso").status_code == 200


def test_login_keeps_internal_next(client):
    response = login(client, next="/progreso")

    assert response.status_code == 303
    assert response.headers["location"] == "/progreso"
    assert client.get("/progreso").status_code == 200


def test_login_rate_limit_blocks_after_repeated_failures(client):
    for _ in range(login_limiter.max_attempts):
        response = login(client, password="contraseña-incorrecta")
        assert response.status_code == 200

    blocked = login(client, password=config.DEMO_PASSWORD)

    assert blocked.status_code == 429
    assert "Demasiados intentos" in blocked.text
    assert "aula_session" not in client.cookies


def test_expired_session_is_rejected(client, db_path):
    assert login(client).status_code == 303

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "UPDATE sessions SET expires_at = ?",
            ("2000-01-01T00:00:00+00:00",),
        )
        conn.commit()
    finally:
        conn.close()

    response = client.get("/curso", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/entrar?next=/curso"


def test_password_and_session_token_are_stored_hashed(client, db_path):
    email = "hash@example.com"
    password = "clave-super-segura"

    assert register(client, email, password=password).status_code == 303
    token = client.cookies.get("aula_session")
    assert token

    password_hash = _fetchone(
        db_path,
        "SELECT password_hash FROM users WHERE email = ?",
        (email,),
    )[0]
    assert password_hash.startswith("scrypt$")
    assert password not in password_hash

    sessions = _fetchall(db_path, "SELECT id FROM sessions")
    assert len(sessions) == 1
    assert sessions[0][0] == token_hash(token)
    assert sessions[0][0] != token
