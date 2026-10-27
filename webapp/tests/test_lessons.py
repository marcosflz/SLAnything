"""Lecciones: lectura, progreso, apuntes, marcadores y CSRF."""

from __future__ import annotations

import sqlite3

from conftest import login, login_and_csrf, register

LESSON = "que-es-un-llm"


def test_lesson_page_shows_title_content_and_lab(client):
    assert login(client).status_code == 303

    response = client.get(f"/leccion/{LESSON}")

    assert response.status_code == 200
    assert "¿Qué es un LLM?" in response.text
    assert "Al terminar sabrás…" in response.text
    assert 'data-lab="memory"' in response.text
    assert 'name="csrf_token"' in response.text


def test_complete_lesson_with_csrf_marks_it_completed(client):
    token = login_and_csrf(client)

    response = client.post(
        f"/leccion/{LESSON}/completar",
        data={"csrf_token": token, "completed": "1"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].startswith(f"/leccion/{LESSON}?ok=")

    lesson = client.get(f"/leccion/{LESSON}")
    assert lesson.status_code == 200
    assert "Completada" in lesson.text

    progress = client.get("/progreso")
    assert progress.status_code == 200
    assert "Completada" in progress.text
    assert "1 / 56" in progress.text


def test_complete_lesson_without_csrf_is_forbidden(client):
    assert login(client).status_code == 303

    response = client.post(
        f"/leccion/{LESSON}/completar",
        data={"completed": "1"},
        follow_redirects=False,
    )

    assert response.status_code == 403
    assert "Token de seguridad inválido" in response.text


def test_note_is_saved_and_user_html_is_escaped(client):
    token = login_and_csrf(client)
    note = "Recordar: la atención pesa mucho.<script>alert('xss')</script>"

    saved = client.post(
        f"/leccion/{LESSON}/nota",
        data={"csrf_token": token, "body": note},
        follow_redirects=False,
    )
    assert saved.status_code == 303

    page = client.get(f"/leccion/{LESSON}")
    assert page.status_code == 200
    assert "Recordar: la atención pesa mucho." in page.text
    assert "&lt;script&gt;" in page.text
    assert note not in page.text
    assert "<script>alert('xss')</script>" not in page.text


def test_note_with_invalid_csrf_is_forbidden(client):
    assert login(client).status_code == 303

    response = client.post(
        f"/leccion/{LESSON}/nota",
        data={"csrf_token": "token-invalido", "body": "No debería guardarse"},
        follow_redirects=False,
    )

    assert response.status_code == 403
    assert "Token de seguridad inválido" in response.text


def test_csrf_header_is_accepted_for_fetch_style_requests(client):
    token = login_and_csrf(client)

    response = client.post(
        f"/leccion/{LESSON}/completar",
        data={"completed": "1"},
        headers={"X-CSRF-Token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert client.get("/curso").status_code == 200


def test_csrf_token_from_a_previous_session_is_rejected(client):
    old_token = login_and_csrf(client)
    new_token = login_and_csrf(client)

    assert old_token != new_token

    response = client.post(
        f"/leccion/{LESSON}/nota",
        data={"csrf_token": old_token, "body": "Token de una sesión anterior"},
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_note_is_truncated_to_the_documented_limit(client, db_path):
    token = login_and_csrf(client)

    response = client.post(
        f"/leccion/{LESSON}/nota",
        data={"csrf_token": token, "body": "a" * 20_001},
        follow_redirects=False,
    )
    assert response.status_code == 303

    conn = sqlite3.connect(db_path)
    try:
        stored = conn.execute(
            "SELECT length(body) FROM notes WHERE lesson_slug = ?",
            (LESSON,),
        ).fetchone()
    finally:
        conn.close()
    assert stored == (20_000,)


def test_notes_are_private_per_user(client):
    token = login_and_csrf(client)
    saved = client.post(
        f"/leccion/{LESSON}/nota",
        data={"csrf_token": token, "body": "nota-privada-de-demo"},
        follow_redirects=False,
    )
    assert saved.status_code == 303

    assert register(client, "privacidad@example.com").status_code == 303
    page = client.get(f"/leccion/{LESSON}")

    assert page.status_code == 200
    assert "nota-privada-de-demo" not in page.text


def test_progress_notes_and_bookmarks_are_isolated_per_course(client, db_path):
    from webapp import repositories

    login(client)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        user_id = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@aulallm.local",)).fetchone()["id"]
        repositories.touch_lesson(conn, user_id, "curso-a", "leccion-compartida")
        repositories.set_lesson_completed(
            conn, user_id, "curso-a", "leccion-compartida", True
        )
        repositories.save_note(
            conn, user_id, "curso-a", "leccion-compartida", "nota de A"
        )
        repositories.toggle_bookmark(
            conn, user_id, "curso-a", "leccion-compartida"
        )
        conn.commit()

        progress_a = repositories.progress_for_user(conn, user_id, "curso-a")
        progress_b = repositories.progress_for_user(conn, user_id, "curso-b")
        assert progress_a["leccion-compartida"]["completed"] == 1
        assert progress_b == {}
        assert repositories.get_note(
            conn, user_id, "curso-b", "leccion-compartida"
        ) == ""
        assert not repositories.is_bookmarked(
            conn, user_id, "curso-b", "leccion-compartida"
        )
    finally:
        conn.close()


def test_progress_persists_across_app_restarts(client):
    from fastapi.testclient import TestClient

    from webapp.main import app

    token = login_and_csrf(client)
    saved = client.post(
        f"/leccion/{LESSON}/completar",
        data={"csrf_token": token, "completed": "1"},
        follow_redirects=False,
    )
    assert saved.status_code == 303

    # Un segundo TestClient arranca el lifespan de nuevo sobre la misma BD.
    with TestClient(app) as restarted:
        assert login(restarted).status_code == 303
        progress = restarted.get("/progreso")
        assert progress.status_code == 200
        assert "Completada" in progress.text
        assert "1 / 56" in progress.text


def test_bookmark_toggles_the_button_text(client):
    token = login_and_csrf(client)

    page = client.get(f"/leccion/{LESSON}")
    assert "Guardar en marcadores" in page.text
    assert "Quitar marcador" not in page.text

    first = client.post(
        f"/leccion/{LESSON}/marcador",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert first.status_code == 303

    page = client.get(f"/leccion/{LESSON}")
    assert "Quitar marcador" in page.text

    second = client.post(
        f"/leccion/{LESSON}/marcador",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert second.status_code == 303

    page = client.get(f"/leccion/{LESSON}")
    assert "Guardar en marcadores" in page.text
    assert "Quitar marcador" not in page.text
