"""Registro solo por invitación (ADR-022).

Por defecto no hay registro abierto: la superadministración invita a cuentas
individuales y a profesorado (con academia nueva o en una existente) y el
profesorado invita a su alumnado.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from webapp import config

from conftest import admin_login, csrf, login_and_csrf, teacher_login


@pytest.fixture
def app(closed_signup, client):
    return client


def _register(client, email: str, **extra):
    body = {
        "name": "Persona Invitada",
        "email": email,
        "password": "clave-segura-123",
        "password2": "clave-segura-123",
        "next": "/",
        **extra,
    }
    return client.post("/api/v1/auth/register", json=body)


def _platform_invite(client, **body) -> str:
    token = admin_login(client)
    response = client.post("/api/v1/platform/invitations", json=body, headers={"X-CSRF-Token": token})
    assert response.status_code == 200, response.text
    client.cookies.clear()
    return response.json()["path"].rsplit("/", 1)[-1]


def _me(client) -> dict:
    return client.get("/api/v1/session").json()["user"]


def test_signup_is_closed_by_default():
    env = {key: value for key, value in os.environ.items() if key != "AULA_OPEN_SIGNUP"}
    result = subprocess.run(
        [sys.executable, "-c", "from webapp import config; print(config.OPEN_SIGNUP)"],
        capture_output=True, text=True, env=env, cwd=str(config.BASE_DIR), check=True,
    )
    assert result.stdout.strip() == "False"


@pytest.mark.parametrize(
    "extra",
    [{}, {"account": "individual"}, {"account": "academy", "academy_name": "Mi academia"}, {"account": "join", "join_code": "ABCD2345"}],
)
def test_signup_without_invitation_is_rejected(app, db_path, extra):
    import sqlite3

    response = _register(app, "sin-invitacion@example.com", **extra)
    assert response.status_code == 403
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT 1 FROM users WHERE email = 'sin-invitacion@example.com'").fetchone() is None
    conn.close()
    assert app.get("/api/v1/public").json()["site"]["signup_open"] is False


def test_only_platform_admins_issue_platform_invitations(app):
    token = teacher_login(app)
    response = app.post(
        "/api/v1/platform/invitations", json={"kind": "individual"}, headers={"X-CSRF-Token": token}
    )
    assert response.status_code == 403


def test_individual_invitation_opens_a_self_learner_account(app):
    token = _platform_invite(app, kind="individual", email="autonoma@example.com")
    info = app.get(f"/api/v1/invitations/{token}").json()
    assert info["kind"] == "individual"

    assert _register(app, "otra@example.com", invite=token).status_code == 403
    response = _register(app, "autonoma@example.com", invite=token)
    assert response.status_code == 200, response.text
    me = _me(app)
    assert me["profile"] == "self_learner"
    assert me["permissions"]["author"] is True
    # De un solo uso.
    app.cookies.clear()
    assert _register(app, "segunda@example.com", invite=token).status_code == 404


def test_teacher_invitation_with_new_academy(app):
    token = _platform_invite(app, kind="teacher")
    info = app.get(f"/api/v1/invitations/{token}").json()
    assert info["kind"] == "academy_owner"
    assert info["needs_academy_name"] is True

    assert _register(app, "directora@example.com", invite=token).status_code == 400
    response = _register(app, "directora@example.com", invite=token, academy_name="Academia Norte")
    assert response.status_code == 200, response.text
    me = _me(app)
    assert me["workspace"]["name"] == "Academia Norte"
    assert me["ws_role"] == "owner"
    assert [ws["kind"] for ws in me["workspaces"]] == ["organization"]


def test_teacher_invitation_into_an_existing_academy(app):
    token = admin_login(app)
    academy = next(
        item for item in app.get("/api/v1/platform/invitations").json()["academies"]
        if item["name"] == "Academia Demo"
    )
    invite = app.post(
        "/api/v1/platform/invitations",
        json={"kind": "teacher", "workspace_id": academy["id"]},
        headers={"X-CSRF-Token": token},
    ).json()["path"].rsplit("/", 1)[-1]
    app.cookies.clear()

    info = app.get(f"/api/v1/invitations/{invite}").json()
    assert (info["kind"], info["role"], info["workspace"]) == ("member", "teacher", "Academia Demo")
    assert _register(app, "profe-nuevo@example.com", invite=invite).status_code == 200
    me = _me(app)
    assert me["profile"] == "teacher"
    assert app.get("/api/v1/teacher").status_code == 200


def test_teachers_invite_only_students(app):
    owner_token = _platform_invite(app, kind="teacher", academy_name="Academia Sur")
    _register(app, "duena@example.com", invite=owner_token)
    token = csrf(app)
    # Ni siquiera el owner incorpora profesorado: eso es de la plataforma.
    assert app.post(
        "/api/v1/admin/invitations", json={"role": "teacher"}, headers={"X-CSRF-Token": token}
    ).status_code == 403
    assert app.get("/api/v1/admin/invitations").json()["roles"] == ["student"]
    student_invite = app.post(
        "/api/v1/admin/invitations", json={"role": "student"}, headers={"X-CSRF-Token": token}
    ).json()["path"].rsplit("/", 1)[-1]
    app.cookies.clear()

    assert _register(app, "alumna-sur@example.com", invite=student_invite).status_code == 200
    me = _me(app)
    assert me["profile"] == "student"
    assert me["workspace"]["name"] == "Academia Sur"


def test_plain_teacher_invites_students_and_sees_only_own_invitations(app):
    # Profesora invitada a la Academia Demo por la plataforma.
    token = admin_login(app)
    academy = next(
        item for item in app.get("/api/v1/platform/invitations").json()["academies"]
        if item["name"] == "Academia Demo"
    )
    invite = app.post(
        "/api/v1/platform/invitations",
        json={"kind": "teacher", "workspace_id": academy["id"]},
        headers={"X-CSRF-Token": token},
    ).json()["path"].rsplit("/", 1)[-1]
    app.cookies.clear()
    _register(app, "profe-b@example.com", invite=invite)
    token = csrf(app)

    created = app.post("/api/v1/admin/invitations", json={"role": "student"}, headers={"X-CSRF-Token": token})
    assert created.status_code == 200
    mine = app.get("/api/v1/admin/invitations").json()["invitations"]
    assert len(mine) == 1
    # Sigue sin acceso a la gestión de la academia.
    assert app.get("/api/v1/admin/members").status_code == 403

    app.cookies.clear()
    owner = teacher_login(app)
    other = app.post("/api/v1/admin/invitations", json={"role": "student"}, headers={"X-CSRF-Token": owner})
    assert other.status_code == 200
    all_rows = app.get("/api/v1/admin/invitations").json()["invitations"]
    assert len(all_rows) == 2
    # La profesora no puede revocar la invitación de la propietaria.
    app.cookies.clear()
    from conftest import login

    login(app, email="profe-b@example.com", password="clave-segura-123")
    other_id = other.json()["id"]
    assert app.delete(f"/api/v1/admin/invitations/{other_id}", headers={"X-CSRF-Token": csrf(app)}).status_code == 404


def test_students_cannot_invite(app):
    token = login_and_csrf(app)
    assert app.post(
        "/api/v1/admin/invitations", json={"role": "student"}, headers={"X-CSRF-Token": token}
    ).status_code == 403


def test_users_cannot_create_spaces_on_their_own(app):
    token = login_and_csrf(app)
    assert app.post("/api/v1/workspaces", json={"name": "Mi academia"}, headers={"X-CSRF-Token": token}).status_code == 403
    assert app.post("/api/v1/workspaces/personal", headers={"X-CSRF-Token": token}).status_code == 403
    app.cookies.clear()
    admin = admin_login(app)
    assert app.post("/api/v1/workspaces", json={"name": "Academia de pruebas"}, headers={"X-CSRF-Token": admin}).status_code == 200


def test_logged_in_user_accepts_an_individual_invitation(app):
    invite = _platform_invite(app, kind="individual", email=config.DEMO_EMAIL)
    token = login_and_csrf(app)
    response = app.post(f"/api/v1/invitations/{invite}/accept", json={}, headers={"X-CSRF-Token": token})
    assert response.status_code == 200, response.text
    kinds = sorted(ws["kind"] for ws in _me(app)["workspaces"])
    assert kinds == ["organization", "personal"]


def test_revoked_platform_invitation_is_unusable(app):
    token = admin_login(app)
    created = app.post(
        "/api/v1/platform/invitations", json={"kind": "individual"}, headers={"X-CSRF-Token": token}
    ).json()
    assert app.delete(f"/api/v1/platform/invitations/{created['id']}", headers={"X-CSRF-Token": token}).status_code == 200
    app.cookies.clear()
    invite = created["path"].rsplit("/", 1)[-1]
    assert app.get(f"/api/v1/invitations/{invite}").status_code == 404
    assert _register(app, "tarde@example.com", invite=invite).status_code == 404
