"""Administración de la academia: miembros, grupos, invitaciones, auditoría y cuenta."""

from __future__ import annotations

from webapp import config

from conftest import csrf, login, login_and_csrf, register, teacher_login


def _demo_id(client) -> int:
    members = client.get("/api/v1/admin/members").json()["members"]
    return next(m["id"] for m in members if m["email"] == config.DEMO_EMAIL)


def test_students_cannot_manage_the_academy(client):
    login_and_csrf(client)
    for url in ("/api/v1/admin/members", "/api/v1/admin/groups", "/api/v1/admin/invitations", "/api/v1/admin/audit"):
        assert client.get(url).status_code == 403, url


def test_owner_changes_roles_and_cannot_remove_last_owner(client):
    token = teacher_login(client)
    body = client.get("/api/v1/admin/members").json()
    assert body["workspace"]["join_code"]
    demo = _demo_id(client)

    response = client.patch(f"/api/v1/admin/members/{demo}", json={"role": "teacher"}, headers={"X-CSRF-Token": token})
    assert response.status_code == 200
    roles = {m["email"]: m["role"] for m in client.get("/api/v1/admin/members").json()["members"]}
    assert roles[config.DEMO_EMAIL] == "teacher"

    me = body["me"]
    assert client.patch(f"/api/v1/admin/members/{me}", json={"role": "admin"}, headers={"X-CSRF-Token": token}).status_code == 409
    assert client.delete(f"/api/v1/admin/members/{me}", headers={"X-CSRF-Token": token}).status_code == 409

    actions = [entry["action"] for entry in client.get("/api/v1/admin/audit").json()["entries"]]
    assert "member.role" in actions


def test_groups_filter_course_analytics(client):
    token = teacher_login(client)
    created = client.post("/api/v1/admin/groups", json={"name": "1º A"}, headers={"X-CSRF-Token": token}).json()
    group_id = created["id"]
    demo = _demo_id(client)
    assert client.put(
        f"/api/v1/admin/groups/{group_id}/members", json={"user_ids": [demo, 999999]}, headers={"X-CSRF-Token": token}
    ).status_code == 200
    assert client.post(
        f"/api/v1/admin/groups/{group_id}/enrollments",
        json={"course_slug": "llm-desde-cero", "due_at": "2026-12-20"},
        headers={"X-CSRF-Token": token},
    ).status_code == 200
    groups = client.get("/api/v1/admin/groups").json()["groups"]
    assert groups[0]["member_ids"] == [demo]
    assert groups[0]["enrollments"][0]["course_slug"] == "llm-desde-cero"

    analytics = client.get(f"/api/v1/analytics/course?group={group_id}").json()
    assert analytics["kpis"]["students"] == 1
    assert analytics["groups"][0]["name"] == "1º A"


def test_invitation_link_adds_member_and_group(client):
    token = teacher_login(client)
    group_id = client.post("/api/v1/admin/groups", json={"name": "Tarde"}, headers={"X-CSRF-Token": token}).json()["id"]
    invite = client.post(
        "/api/v1/admin/invitations",
        json={"email": "nueva@example.com", "role": "teacher", "group_id": group_id},
        headers={"X-CSRF-Token": token},
    ).json()
    path = invite["path"]
    raw = path.rsplit("/", 1)[1]
    listed = client.get("/api/v1/admin/invitations").json()["invitations"]
    assert listed[0]["state"] == "pending"
    assert "token_hash" not in listed[0]

    client.cookies.clear()
    assert client.get(f"/api/v1/invitations/{raw}").json()["workspace"] == "Academia Demo"
    register(client, "otra@example.com")
    wrong = client.post(f"/api/v1/invitations/{raw}/accept", headers={"X-CSRF-Token": csrf(client)})
    assert wrong.status_code == 403  # la invitación es para otro correo

    client.cookies.clear()
    register(client, "nueva@example.com")
    accepted = client.post(f"/api/v1/invitations/{raw}/accept", headers={"X-CSRF-Token": csrf(client)})
    assert accepted.status_code == 200
    roles = {w["name"]: w["role"] for w in client.get("/api/v1/workspaces").json()["workspaces"]}
    assert roles["Academia Demo"] == "teacher"
    # Un solo uso.
    assert client.get(f"/api/v1/invitations/{raw}").status_code == 404


def test_revoked_invitation_cannot_be_used(client):
    token = teacher_login(client)
    invite = client.post("/api/v1/admin/invitations", json={"role": "student"}, headers={"X-CSRF-Token": token}).json()
    assert client.delete(f"/api/v1/admin/invitations/{invite['id']}", headers={"X-CSRF-Token": token}).status_code == 200
    raw = invite["path"].rsplit("/", 1)[1]
    assert client.get(f"/api/v1/invitations/{raw}").status_code == 404


def test_account_profile_password_and_sessions(client):
    register(client, "cuenta@example.com", password="clave-original-1")
    token = csrf(client)
    assert client.patch("/api/v1/account", json={"name": "Nombre Nuevo"}, headers={"X-CSRF-Token": token}).status_code == 200
    body = client.get("/api/v1/account").json()
    assert body["name"] == "Nombre Nuevo"
    assert body["sessions"][0]["current"] is True

    bad = client.post("/api/v1/account/password", json={"current": "x", "new": "clave-nueva-123"}, headers={"X-CSRF-Token": token})
    assert bad.status_code == 400
    ok = client.post(
        "/api/v1/account/password", json={"current": "clave-original-1", "new": "clave-nueva-123"}, headers={"X-CSRF-Token": token}
    )
    assert ok.status_code == 200
    client.cookies.clear()
    assert login(client, email="cuenta@example.com", password="clave-nueva-123").status_code == 200
