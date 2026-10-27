"""Panel del profesorado: autenticación, autorización y tabla de estudiantes."""

from __future__ import annotations

from webapp import config

from conftest import login


def test_anonymous_teacher_panel_redirects_to_login(client):
    response = client.get("/profesor", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/entrar?next=/profesor"


def test_student_cannot_access_teacher_panel(client):
    assert login(client).status_code == 303

    response = client.get("/profesor")

    assert response.status_code == 403
    assert "Acceso restringido" in response.text
    assert "solo para el profesorado" in response.text


def test_teacher_sees_the_students_table(client):
    assert login(
        client,
        email=config.TEACHER_EMAIL,
        password=config.TEACHER_PASSWORD,
    ).status_code == 303

    response = client.get("/profesor")

    assert response.status_code == 200
    assert "teacher-table" in response.text
    assert "Estudiantes" in response.text
    assert "Estudiante demo" in response.text
    assert "demo@aulallm.local" in response.text
