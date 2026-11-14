"""Migraciones, espacios de trabajo, roles y aislamiento entre tenants."""

from __future__ import annotations

import sqlite3

from webapp import config, migrations
from webapp.db import SCHEMA

from conftest import csrf, login, login_and_csrf, register, self_learner_login, teacher_login


def test_migrations_upgrade_a_v3_database(tmp_path):
    path = tmp_path / "v3.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA user_version = 3")
    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, created_at) "
        "VALUES ('old@example.com', 'Old', 'x', 'teacher', '2026-01-01')"
    )
    conn.commit()

    applied = migrations.migrate(conn)

    assert applied == [4, 5, 6, 7]
    assert migrations.current_version(conn) == migrations.LATEST_VERSION
    columns = {row[1] for row in conn.execute("PRAGMA table_info(generated_courses)")}
    assert {"workspace_id", "visibility"} <= columns
    # Los usuarios de una base v3 reciben su cuenta individual (v6).
    kinds = [row[0] for row in conn.execute(
        "SELECT w.kind FROM workspaces w JOIN users u ON u.id = w.owner_id "
        "WHERE u.email = 'old@example.com'"
    )]
    assert kinds == ["personal"]
    # Idempotente: una segunda pasada no aplica nada.
    assert migrations.migrate(conn) == []
    conn.close()


def test_individual_signup_gets_a_personal_workspace(client, db_path):
    assert register(client, "nuevo@example.com", name="Nuevo Usuario").status_code == 200
    body = client.get("/api/v1/workspaces").json()

    kinds = [item["kind"] for item in body["workspaces"]]
    assert kinds == ["personal"]
    assert body["active"]["role"] == "owner"
    # Cuenta individual: crea unidades, pero no gestiona un aula.
    assert body["permissions"]["author"] is True
    assert body["permissions"]["teach"] is False
    assert body["permissions"]["manage"] is False


def test_demo_student_only_belongs_to_the_demo_academy(client):
    login(client)
    body = client.get("/api/v1/workspaces").json()
    assert body["active"]["slug"] == "academia-demo"
    assert body["active"]["role"] == "student"
    assert body["permissions"]["author"] is False
    # El alumnado de una academia no recibe espacio personal.
    assert [item["kind"] for item in body["workspaces"]] == ["organization"]


def test_student_can_open_an_individual_account_to_use_the_studio(client):
    token = login_and_csrf(client)
    assert client.get("/api/v1/authoring").status_code == 403

    created = client.post("/api/v1/workspaces/personal", headers={"X-CSRF-Token": token})
    assert created.status_code == 200
    personal_id = created.json()["workspace"]["id"]
    assert client.get("/api/v1/workspaces").json()["active"]["id"] == personal_id
    assert client.get("/api/v1/authoring").status_code == 200

    # Idempotente y, de vuelta en la academia, sigue siendo estudiante.
    again = client.post("/api/v1/workspaces/personal", headers={"X-CSRF-Token": token})
    assert again.json()["workspace"]["id"] == personal_id
    academy = next(
        item for item in client.get("/api/v1/workspaces").json()["workspaces"]
        if item["kind"] == "organization"
    )
    client.post(
        "/api/v1/workspaces/switch",
        json={"workspace_id": academy["id"]},
        headers={"X-CSRF-Token": token},
    )
    assert client.get("/api/v1/authoring").status_code == 403


def test_cannot_switch_to_a_foreign_workspace(client, db_path):
    token = login_and_csrf(client)
    conn = sqlite3.connect(db_path)
    foreign = conn.execute(
        "SELECT w.id FROM workspaces w JOIN users u ON u.id = w.owner_id "
        "WHERE w.kind = 'personal' AND u.email = ?",
        (config.SELF_LEARNER_EMAIL,),
    ).fetchone()[0]
    conn.close()

    response = client.post(
        "/api/v1/workspaces/switch",
        json={"workspace_id": foreign},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 404


def test_create_academy_and_join_with_code(client, db_path):
    token = teacher_login(client)
    created = client.post(
        "/api/v1/workspaces", json={"name": "Academia Norte"}, headers={"X-CSRF-Token": token}
    )
    assert created.status_code == 200
    code = created.json()["workspace"]["join_code"]
    assert code

    client.cookies.clear()
    assert register(client, "alumna-norte@example.com").status_code == 200
    joined = client.post(
        "/api/v1/workspaces/join", json={"code": code}, headers={"X-CSRF-Token": csrf(client)}
    )
    assert joined.status_code == 200
    active = client.get("/api/v1/workspaces").json()["active"]
    assert active["name"] == "Academia Norte"
    assert active["role"] == "student"


def test_teacher_panel_only_lists_students_of_the_active_workspace(client):
    register(client, "fuera@example.com", name="Alumno Ajeno")
    client.cookies.clear()
    teacher_login(client)

    names = [row["name"] for row in client.get("/api/v1/teacher").json()["students"]]
    assert "Estudiante demo" in names
    assert "Alumno Ajeno" not in names


def test_generated_courses_are_isolated_between_workspaces(client, db_path):
    """Un curso publicado en la academia no aparece en el catálogo de otro tenant."""
    from webapp.authoring import store

    teacher_login(client)
    ws = client.get("/api/v1/workspaces").json()["active"]["id"]
    conn = sqlite3.connect(db_path)
    owner = conn.execute("SELECT id FROM users WHERE email = ?", (config.TEACHER_EMAIL,)).fetchone()[0]
    conn.close()

    from test_authoring import sample_package  # noqa: PLC0415

    from webapp.authoring.package import parse_package

    package = sample_package("aislado")
    store.save_generated_course(
        slug=parse_package(package).slug, owner_id=owner, job_id=None,
        title="Aislado", package=package, status="published", workspace_id=ws,
    )

    teacher_catalog = client.get("/api/v1/catalog").json()["courses"]
    client.cookies.clear()
    register(client, "otro-tenant@example.com")
    outsider_catalog = client.get("/api/v1/catalog").json()["courses"]
    anon = client.get("/api/v1/public").json()["catalog"]

    teacher_titles = {course["title"] for course in teacher_catalog}
    outsider_titles = {course["title"] for course in outsider_catalog}
    assert len(teacher_titles) > len(outsider_titles)
    assert len(anon) == len(outsider_catalog)
