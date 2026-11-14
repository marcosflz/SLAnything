"""Superadministración de la plataforma (ADR-021) y matrículas aplicadas."""

from __future__ import annotations

import sqlite3

from webapp import config

from conftest import admin_login, login, login_and_csrf, teacher_login


def _user_id(db_path, email: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return int(conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0])
    finally:
        conn.close()


def test_only_platform_admins_reach_the_platform_panel(client):
    assert client.get("/api/v1/platform/overview").status_code == 401
    teacher_login(client)
    assert client.get("/api/v1/platform/overview").status_code == 403
    client.cookies.clear()
    admin_login(client)
    body = client.get("/api/v1/platform/overview").json()
    assert body["users"]["total"] >= 4
    assert body["workspaces"]["organization"] >= 1


def test_platform_lists_users_and_workspaces(client):
    admin_login(client)
    users = client.get("/api/v1/platform/users?q=slanything.local").json()
    assert users["total"] == 4
    emails = {item["email"] for item in users["users"]}
    assert config.TEACHER_EMAIL in emails
    spaces = client.get("/api/v1/platform/workspaces?kind=organization").json()["workspaces"]
    assert any(item["slug"] == "academia-demo" for item in spaces)
    assert all("join_code" not in item for item in spaces)


def test_disabling_a_user_closes_their_sessions(client, db_path):
    login(client)
    assert client.get("/api/v1/session").json()["user"] is not None
    student_cookie = dict(client.cookies)
    client.cookies.clear()

    token = admin_login(client)
    student = _user_id(db_path, config.DEMO_EMAIL)
    assert client.patch(
        f"/api/v1/platform/users/{student}", json={"disabled": True}, headers={"X-CSRF-Token": token}
    ).status_code == 200

    client.cookies.clear()
    client.cookies.update(student_cookie)
    assert client.get("/api/v1/session").json()["user"] is None
    assert login(client).status_code == 403


def test_last_platform_admin_is_protected(client, db_path):
    token = admin_login(client)
    me = _user_id(db_path, config.ADMIN_EMAIL)
    response = client.patch(
        f"/api/v1/platform/users/{me}", json={"is_platform_admin": False}, headers={"X-CSRF-Token": token}
    )
    assert response.status_code == 409
    teacher = _user_id(db_path, config.TEACHER_EMAIL)
    assert client.patch(
        f"/api/v1/platform/users/{teacher}", json={"is_platform_admin": True}, headers={"X-CSRF-Token": token}
    ).status_code == 200


def test_platform_sets_a_custom_monthly_quota(client, db_path):
    token = admin_login(client)
    academy = next(
        item for item in client.get("/api/v1/platform/workspaces").json()["workspaces"]
        if item["slug"] == "academia-demo"
    )
    assert client.patch(
        f"/api/v1/platform/workspaces/{academy['id']}",
        json={"gen_monthly": 2, "seat_limit": 30},
        headers={"X-CSRF-Token": token},
    ).status_code == 200

    client.cookies.clear()
    teacher_login(client)
    quota = client.get("/api/v1/authoring").json()["quota"]
    assert quota["limit"] == 2


def test_platform_cannot_delete_personal_spaces(client):
    token = admin_login(client)
    personal = next(
        item for item in client.get("/api/v1/platform/workspaces?kind=personal").json()["workspaces"]
    )
    response = client.delete(
        f"/api/v1/platform/workspaces/{personal['id']}", headers={"X-CSRF-Token": token}
    )
    assert response.status_code == 409


def test_assigned_courses_come_first_with_their_due_date(client):
    token = teacher_login(client)
    group = client.post(
        "/api/v1/admin/groups", json={"name": "Grupo A"}, headers={"X-CSRF-Token": token}
    ).json()["id"]
    demo = next(
        m["id"] for m in client.get("/api/v1/admin/members").json()["members"]
        if m["email"] == config.DEMO_EMAIL
    )
    client.put(f"/api/v1/admin/groups/{group}/members", json={"user_ids": [demo]}, headers={"X-CSRF-Token": token})
    client.post(
        f"/api/v1/admin/groups/{group}/enrollments",
        json={"course_slug": config.SAMPLE_COURSE_SLUG, "due_at": "2026-12-20"},
        headers={"X-CSRF-Token": token},
    )
    client.cookies.clear()

    login_and_csrf(client)
    courses = client.get("/api/v1/catalog").json()["courses"]
    assert courses[0]["slug"] == config.SAMPLE_COURSE_SLUG
    assert courses[0]["assigned"] is True
    assert courses[0]["due_at"] == "2026-12-20"
