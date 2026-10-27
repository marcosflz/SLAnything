"""API JSON que consume el frontend Next.js."""

from __future__ import annotations

from webapp import config
from webapp.content import QUIZZES

from conftest import login, register

QUIZ_ID = "quiz-capitulo-1"
LESSON = "que-es-un-llm"


def api_login(client, email: str = config.DEMO_EMAIL, password: str = config.DEMO_PASSWORD):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "next": "/curso"},
    )
    assert response.status_code == 200, response.text
    return response


def csrf(client) -> str:
    response = client.get("/api/v1/session")
    assert response.status_code == 200
    return response.json()["csrf_token"]


def test_api_login_session_and_shell(client):
    api_login(client)
    session = client.get("/api/v1/session").json()
    assert session["user"]["email"] == config.DEMO_EMAIL
    assert session["csrf_token"]

    shell = client.get("/api/v1/shell")
    assert shell.status_code == 200
    body = shell.json()
    assert body["course"]["lesson_count"] == 56
    assert body["course"]["chapter_count"] == 7
    assert body["user"]["role"] == "student"
    assert body["stats"]["total"] == 56


def test_api_public_course_works_without_session(client):
    response = client.get("/api/v1/public?lang=en")
    assert response.status_code == 200
    body = response.json()
    assert body["course"]["title"] == "Build an LLM from Scratch"
    assert body["lang"] == "en"
    assert body["course"]["chapter_count"] == 7
    assert len(body["course"]["lessons"]) == 56
    assert body["catalog"][0]["slug"] == "llm-desde-cero"
    assert body["catalog"][0]["book"]["author"] == "Sebastian Raschka"


def test_api_catalog_and_course_detail_are_public(client):
    catalog = client.get("/api/v1/catalog?lang=en")
    assert catalog.status_code == 200
    body = catalog.json()
    assert body["courses"][0]["title"] == "Build an LLM from Scratch"
    assert body["courses"][0]["chapter_count"] == 7
    assert body["featured"]["slug"] == "llm-desde-cero"

    detail = client.get("/api/v1/courses/llm-desde-cero")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["course"]["slug"] == "llm-desde-cero"
    assert payload["course"]["lesson_count"] == 56
    assert payload["stats"]["total"] == 56
    assert payload["next_lesson"]["course_slug"] == "llm-desde-cero"

    missing = client.get("/api/v1/courses/no-existe")
    assert missing.status_code == 404


def test_api_catalog_tracks_progress_per_course(client):
    api_login(client)
    token = csrf(client)
    client.post(
        f"/api/v1/lessons/{LESSON}/complete",
        json={"completed": True},
        headers={"X-CSRF-Token": token},
    )

    catalog = client.get("/api/v1/catalog").json()
    assert catalog["courses"][0]["stats"]["completed"] == 1
    assert catalog["courses"][0]["stats"]["total"] == 56


def test_api_search_includes_the_course(client):
    api_login(client)
    body = client.get("/api/v1/search", params={"q": "atención"}).json()
    assert body["results"]
    assert body["results"][0]["lesson"]["course_slug"] == "llm-desde-cero"
    assert body["results"][0]["lesson"]["course_title"] == "Construye un LLM desde cero"


def test_api_lesson_flow_with_csrf(client):
    api_login(client)
    token = csrf(client)

    lesson = client.get(f"/api/v1/lessons/{LESSON}")
    assert lesson.status_code == 200
    body = lesson.json()
    assert body["lesson"]["title"] == "¿Qué es un LLM?"
    assert any(block["type"] == "lab" for block in body["lesson"]["blocks"])
    assert body["quiz"] is None

    review_lesson = client.get("/api/v1/lessons/repaso")
    assert review_lesson.status_code == 200
    assert review_lesson.json()["quiz"]["id"] == QUIZ_ID

    completed = client.post(
        f"/api/v1/lessons/{LESSON}/complete",
        json={"completed": True},
        headers={"X-CSRF-Token": token},
    )
    assert completed.status_code == 200
    assert completed.json()["completed"] is True
    assert completed.json()["stats"]["completed"] == 1

    note = "Una idea clave."
    saved = client.post(
        f"/api/v1/lessons/{LESSON}/note",
        json={"body": note},
        headers={"X-CSRF-Token": token},
    )
    assert saved.status_code == 200

    bookmarked = client.post(
        f"/api/v1/lessons/{LESSON}/bookmark",
        headers={"X-CSRF-Token": token},
    )
    assert bookmarked.status_code == 200
    assert bookmarked.json()["bookmarked"] is True

    again = client.get(f"/api/v1/lessons/{LESSON}").json()
    assert again["progress"]["completed"] is True
    assert again["note"] == note
    assert again["bookmarked"] is True


def test_api_rejects_mutations_without_csrf(client):
    api_login(client)
    response = client.post(
        f"/api/v1/lessons/{LESSON}/complete",
        json={"completed": True},
    )
    assert response.status_code == 403


def test_api_quiz_does_not_leak_answers_and_reviews_attempt(client):
    api_login(client)
    token = csrf(client)
    quiz_response = client.get(f"/api/v1/quiz/{QUIZ_ID}")
    assert quiz_response.status_code == 200
    quiz = quiz_response.json()["quiz"]
    assert len(quiz["questions"]) == 10
    raw = quiz_response.text
    for question in QUIZZES[QUIZ_ID].questions:
        assert question.explanation not in raw
        assert '"correct"' not in raw

    answers = {question.id: 0 for question in QUIZZES[QUIZ_ID].questions}
    submitted = client.post(
        f"/api/v1/quiz/{QUIZ_ID}",
        json={"answers": answers},
        headers={"X-CSRF-Token": token},
    )
    assert submitted.status_code == 200
    result = submitted.json()
    assert result["total"] == 10
    assert 0 <= result["score"] <= 10

    review = client.get(f"/api/v1/quiz/attempts/{result['attempt_id']}")
    assert review.status_code == 200
    review_body = review.json()
    assert len(review_body["review"]) == 10
    assert QUIZZES[QUIZ_ID].questions[0].explanation in review.text


def test_api_attempt_review_is_private(client):
    api_login(client)
    token = csrf(client)
    answers = {question.id: 0 for question in QUIZZES[QUIZ_ID].questions}
    result = client.post(
        f"/api/v1/quiz/{QUIZ_ID}",
        json={"answers": answers},
        headers={"X-CSRF-Token": token},
    ).json()

    assert register(client, "api-intruso@example.com").status_code == 303
    other = client.get(f"/api/v1/quiz/attempts/{result['attempt_id']}")
    assert other.status_code == 404


def test_api_teacher_requires_teacher_role(client):
    api_login(client)
    assert client.get("/api/v1/teacher").status_code == 403

    api_login(client, config.TEACHER_EMAIL, config.TEACHER_PASSWORD)
    response = client.get("/api/v1/teacher")
    assert response.status_code == 200
    assert response.json()["stats"]["students"] >= 1


def test_api_register_and_logout(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alumna API",
            "email": "api@example.com",
            "password": "clave-segura-123",
            "password2": "clave-segura-123",
            "next": "/curso",
        },
    )
    assert response.status_code == 200
    assert client.get("/api/v1/session").json()["user"]["email"] == "api@example.com"

    token = csrf(client)
    assert client.post(
        "/api/v1/auth/logout", headers={"X-CSRF-Token": token}
    ).status_code == 200
    assert client.get("/api/v1/session").json()["user"] is None
