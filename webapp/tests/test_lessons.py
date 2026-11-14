"""Lecciones: lectura, progreso, apuntes, marcadores y CSRF."""

from __future__ import annotations

import sqlite3

from conftest import csrf, login, login_and_csrf, register

LESSON = "que-es-un-llm"


def _complete(client, token: str | None, completed: bool = True):
    headers = {"X-CSRF-Token": token} if token else {}
    return client.post(
        f"/api/v1/lessons/{LESSON}/complete",
        json={"completed": completed},
        headers=headers,
    )


def _note(client, token: str | None, body: str):
    headers = {"X-CSRF-Token": token} if token else {}
    return client.post(
        f"/api/v1/lessons/{LESSON}/note", json={"body": body}, headers=headers
    )


def test_lesson_payload_has_title_content_and_lab(client):
    assert login(client).status_code == 200

    response = client.get(f"/api/v1/lessons/{LESSON}")

    assert response.status_code == 200
    lesson = response.json()["lesson"]
    assert lesson["title"] == "¿Qué es un LLM?"
    assert lesson["objectives"]
    assert any(block.get("lab") == "memory" for block in lesson["blocks"])


def test_complete_lesson_with_csrf_marks_it_completed(client):
    token = login_and_csrf(client)

    response = _complete(client, token)

    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["stats"]["completed"] == 1

    lesson = client.get(f"/api/v1/lessons/{LESSON}").json()
    assert lesson["progress"]["completed"]

    progress = client.get("/api/v1/progress").json()
    assert progress["stats"]["completed"] == 1
    assert progress["stats"]["total"] == 56


def test_complete_lesson_without_csrf_is_forbidden(client):
    assert login(client).status_code == 200

    response = _complete(client, None)

    assert response.status_code == 403
    assert "Token de seguridad inválido" in response.json()["detail"]


def test_note_is_saved_verbatim_as_json(client):
    token = login_and_csrf(client)
    note = "Recordar: la atención pesa mucho.<script>alert('xss')</script>"

    assert _note(client, token, note).status_code == 200

    payload = client.get(f"/api/v1/lessons/{LESSON}").json()
    # La API devuelve el texto tal cual; React lo escapa al pintarlo.
    assert payload["note"] == note


def test_note_with_invalid_csrf_is_forbidden(client):
    assert login(client).status_code == 200

    response = _note(client, "token-invalido", "No debería guardarse")

    assert response.status_code == 403
    assert "Token de seguridad inválido" in response.json()["detail"]


def test_csrf_token_from_a_previous_session_is_rejected(client):
    old_token = login_and_csrf(client)
    new_token = login_and_csrf(client)

    assert old_token != new_token
    assert _note(client, old_token, "Token de una sesión anterior").status_code == 403


def test_note_respects_the_documented_limit(client, db_path):
    token = login_and_csrf(client)

    assert _note(client, token, "a" * 20_001).status_code == 422
    assert _note(client, token, "a" * 20_000).status_code == 200

    conn = sqlite3.connect(db_path)
    try:
        stored = conn.execute(
            "SELECT length(body) FROM notes WHERE lesson_slug = ?", (LESSON,)
        ).fetchone()
    finally:
        conn.close()
    assert stored == (20_000,)


def test_notes_are_private_per_user(client):
    token = login_and_csrf(client)
    assert _note(client, token, "nota-privada-de-demo").status_code == 200

    assert register(client, "privacidad@example.com").status_code == 200
    payload = client.get(f"/api/v1/lessons/{LESSON}").json()

    assert payload["note"] == ""


def test_progress_notes_and_bookmarks_are_isolated_per_course(client, db_path):
    from webapp import repositories

    login(client)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@aulallm.local",)
        ).fetchone()["id"]
        repositories.touch_lesson(conn, user_id, "curso-a", "leccion-compartida")
        repositories.set_lesson_completed(
            conn, user_id, "curso-a", "leccion-compartida", True
        )
        repositories.save_note(conn, user_id, "curso-a", "leccion-compartida", "nota de A")
        repositories.toggle_bookmark(conn, user_id, "curso-a", "leccion-compartida")
        conn.commit()

        progress_a = repositories.progress_for_user(conn, user_id, "curso-a")
        progress_b = repositories.progress_for_user(conn, user_id, "curso-b")
        assert progress_a["leccion-compartida"]["completed"] == 1
        assert progress_b == {}
        assert repositories.get_note(conn, user_id, "curso-b", "leccion-compartida") == ""
        assert not repositories.is_bookmarked(conn, user_id, "curso-b", "leccion-compartida")
    finally:
        conn.close()


def test_progress_persists_across_app_restarts(client):
    from fastapi.testclient import TestClient

    from webapp.main import app

    token = login_and_csrf(client)
    assert _complete(client, token).status_code == 200

    # Un segundo TestClient arranca el lifespan de nuevo sobre la misma BD.
    with TestClient(app) as restarted:
        assert login(restarted).status_code == 200
        progress = restarted.get("/api/v1/progress").json()
        assert progress["stats"]["completed"] == 1


def test_bookmark_toggles(client):
    token = login_and_csrf(client)
    assert client.get(f"/api/v1/lessons/{LESSON}").json()["bookmarked"] is False

    first = client.post(
        f"/api/v1/lessons/{LESSON}/bookmark", headers={"X-CSRF-Token": token}
    )
    assert first.json()["bookmarked"] is True
    assert client.get(f"/api/v1/lessons/{LESSON}").json()["bookmarked"] is True

    second = client.post(
        f"/api/v1/lessons/{LESSON}/bookmark", headers={"X-CSRF-Token": csrf(client)}
    )
    assert second.json()["bookmarked"] is False
