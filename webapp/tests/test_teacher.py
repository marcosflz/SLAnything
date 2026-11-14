"""Panel del profesorado: autenticación, autorización y tabla de estudiantes."""

from __future__ import annotations

from conftest import login, teacher_login


def test_anonymous_teacher_panel_is_unauthorized(client):
    assert client.get("/api/v1/teacher").status_code == 401


def test_student_cannot_access_teacher_panel(client):
    assert login(client).status_code == 200

    response = client.get("/api/v1/teacher")

    assert response.status_code == 403
    assert "solo para el profesorado" in response.json()["detail"]


def test_teacher_sees_the_students_table(client):
    teacher_login(client)

    response = client.get("/api/v1/teacher")

    assert response.status_code == 200
    students = response.json()["students"]
    assert any(row["name"] == "Estudiante demo" for row in students)
