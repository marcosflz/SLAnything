"""Perfiles de cuenta (ADR-021): alta individual, academia, invitación y código.

Matriz de permisos esperada en el espacio activo:

=================  ======  ======  =====  ======
perfil             author  teach   manage platform
=================  ======  ======  =====  ======
autodidacta        sí      no      no     no
estudiante         no      no      no     no
profesorado        sí      sí      no     no
admin de academia  sí      sí      sí     no
superadmin         (según su espacio)     sí
=================  ======  ======  =====  ======
"""

from __future__ import annotations

import pytest

from webapp import config
from webapp.deps import permissions_for, profile_for

from conftest import admin_login, csrf, login_and_csrf, self_learner_login, teacher_login


def _register(client, email: str, **extra):
    body = {
        "name": "Persona de Prueba",
        "email": email,
        "password": "clave-segura-123",
        "password2": "clave-segura-123",
        "next": "/",
        **extra,
    }
    return client.post("/api/v1/auth/register", json=body)


def _me(client) -> dict:
    return client.get("/api/v1/session").json()["user"]


@pytest.mark.parametrize(
    ("role", "kind", "expected"),
    [
        ("owner", "personal", {"author": True, "teach": False, "manage": False}),
        ("student", "organization", {"author": False, "teach": False, "manage": False}),
        ("teacher", "organization", {"author": True, "teach": True, "manage": False}),
        ("admin", "organization", {"author": True, "teach": True, "manage": True}),
        ("owner", "organization", {"author": True, "teach": True, "manage": True}),
        (None, None, {"author": False, "teach": False, "manage": False}),
    ],
)
def test_permission_matrix(role, kind, expected):
    perms = permissions_for(role, kind)
    assert {key: perms[key] for key in expected} == expected
    assert perms["admin"] == perms["manage"]
    assert perms["platform"] is False
    assert permissions_for(role, kind, True)["platform"] is True


def test_profiles_are_derived_from_the_active_space():
    assert profile_for("owner", "personal") == "self_learner"
    assert profile_for("student", "organization") == "student"
    assert profile_for("teacher", "organization") == "teacher"
    assert profile_for("admin", "organization") == "academy_admin"
    assert profile_for("owner", "organization") == "academy_admin"
    assert profile_for(None, None) is None


def test_demo_accounts_cover_every_profile(client):
    login_and_csrf(client)
    assert _me(client)["profile"] == "student"
    client.cookies.clear()
    teacher_login(client)
    me = _me(client)
    assert me["profile"] == "academy_admin"
    assert me["is_platform_admin"] is False
    client.cookies.clear()
    self_learner_login(client)
    assert _me(client)["profile"] == "self_learner"
    client.cookies.clear()
    admin_login(client)
    assert _me(client)["permissions"]["platform"] is True


def test_self_learner_creates_units_but_does_not_manage_a_classroom(client):
    self_learner_login(client)
    assert client.get("/api/v1/authoring").status_code == 200
    for url in (
        "/api/v1/teacher",
        "/api/v1/analytics/course",
        "/api/v1/admin/members",
        "/api/v1/admin/groups",
        "/api/v1/admin/metrics",
        "/api/v1/platform/overview",
    ):
        assert client.get(url).status_code == 403, url


def test_student_only_consumes(client):
    login_and_csrf(client)
    for url in (
        "/api/v1/authoring",
        "/api/v1/authoring/jobs",
        "/api/v1/teacher",
        "/api/v1/analytics/course",
        "/api/v1/admin/members",
        "/api/v1/platform/users",
    ):
        assert client.get(url).status_code == 403, url
    assert client.get("/api/v1/dashboard").status_code == 200
    assert client.get("/api/v1/analytics/me").status_code == 200


def test_academy_signup_creates_the_academy_and_its_owner(client):
    response = _register(client, "directora@example.com", account="academy", academy_name="Academia Sur")
    assert response.status_code == 200, response.text
    body = client.get("/api/v1/workspaces").json()
    assert [item["kind"] for item in body["workspaces"]] == ["organization"]
    assert body["active"]["name"] == "Academia Sur"
    assert body["active"]["role"] == "owner"
    assert body["permissions"]["manage"] is True
    assert client.get("/api/v1/admin/members").status_code == 200


def test_academy_signup_needs_a_name(client):
    response = _register(client, "sin-nombre@example.com", account="academy", academy_name=" ")
    assert response.status_code == 400
    assert client.get("/api/v1/session").json()["user"] is None


def test_signup_with_class_code_joins_as_student_without_personal_space(client):
    teacher_login(client)
    code = client.get("/api/v1/admin/members").json()["workspace"]["join_code"]
    client.cookies.clear()

    response = _register(client, "alumna-codigo@example.com", account="join", join_code=code)
    assert response.status_code == 200, response.text
    body = client.get("/api/v1/workspaces").json()
    assert [item["kind"] for item in body["workspaces"]] == ["organization"]
    assert body["active"]["role"] == "student"
    assert client.get("/api/v1/authoring").status_code == 403


def test_signup_with_wrong_code_does_not_create_the_account(client, db_path):
    import sqlite3

    response = _register(client, "codigo-malo@example.com", account="join", join_code="NOPE0000")
    assert response.status_code == 404
    conn = sqlite3.connect(db_path)
    exists = conn.execute("SELECT 1 FROM users WHERE email = 'codigo-malo@example.com'").fetchone()
    conn.close()
    assert exists is None


def test_signup_from_invitation_takes_the_invited_role(client):
    token = teacher_login(client)
    invite = client.post(
        "/api/v1/admin/invitations",
        json={"role": "teacher", "email": "nuevo-profe@example.com"},
        headers={"X-CSRF-Token": token},
    ).json()
    invite_token = invite["path"].rsplit("/", 1)[-1]
    client.cookies.clear()

    wrong = _register(client, "otra@example.com", invite=invite_token)
    assert wrong.status_code == 403

    response = _register(client, "nuevo-profe@example.com", invite=invite_token)
    assert response.status_code == 200, response.text
    me = _me(client)
    assert me["profile"] == "teacher"
    assert [item["kind"] for item in me["workspaces"]] == ["organization"]
    assert client.get("/api/v1/authoring").status_code == 200
    assert client.get("/api/v1/teacher").status_code == 200
    assert client.get("/api/v1/admin/members").status_code == 403


def test_teacher_of_an_academy_cannot_administer_it(client):
    token = teacher_login(client)
    invite = client.post(
        "/api/v1/admin/invitations", json={"role": "teacher"}, headers={"X-CSRF-Token": token}
    ).json()
    client.cookies.clear()
    _register(client, "profe2@example.com", invite=invite["path"].rsplit("/", 1)[-1])
    # Gestiona solo sus propias invitaciones de alumnado (ADR-022), no la academia.
    assert client.get("/api/v1/admin/invitations").json()["invitations"] == []
    assert client.get("/api/v1/admin/members").status_code == 403
    assert client.get("/api/v1/admin/groups").status_code == 403
    assert client.get("/api/v1/analytics/course").status_code == 200


def test_user_without_any_space_gets_no_permissions(client, db_path):
    import sqlite3

    login_and_csrf(client)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "DELETE FROM memberships WHERE user_id = (SELECT id FROM users WHERE email = ?)",
        (config.DEMO_EMAIL,),
    )
    conn.commit()
    conn.close()

    me = _me(client)
    assert me["workspace"] is None
    assert me["profile"] is None
    assert not any(me["permissions"].values())
    assert client.get("/api/v1/shell").status_code == 200
    assert client.get("/api/v1/authoring").status_code == 403
    # Puede abrir su cuenta individual o unirse con un código.
    created = client.post("/api/v1/workspaces/personal", headers={"X-CSRF-Token": csrf(client)})
    assert created.status_code == 200
    assert _me(client)["profile"] == "self_learner"
