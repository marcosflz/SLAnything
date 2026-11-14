"""Flujo completo de un estudiante nuevo, de registro a revisión del quiz."""

from __future__ import annotations

from webapp.content import QUIZZES

from conftest import csrf, register

QUIZ_ID = "quiz-capitulo-1"


def test_new_student_can_register_learn_and_pass_the_quiz(client):
    # 1. Alta, catálogo y acceso al programa.
    assert register(client, "flujo@example.com", name="Alumna Flujo").status_code == 200
    token = csrf(client)
    assert client.get("/api/v1/dashboard").status_code == 200
    catalog = client.get("/api/v1/catalog").json()
    assert any(course["slug"] == "llm-desde-cero" for course in catalog["courses"])
    assert client.get("/api/v1/courses/llm-desde-cero").status_code == 200

    # 2. Lectura y finalización de una lección.
    assert client.get("/api/v1/lessons/que-es-un-llm").status_code == 200
    completed = client.post(
        "/api/v1/lessons/que-es-un-llm/complete",
        json={"completed": True},
        headers={"X-CSRF-Token": token},
    )
    assert completed.status_code == 200
    assert client.get("/api/v1/progress").json()["stats"]["completed"] == 1

    # 3. Quiz final y revisión.
    quiz = QUIZZES[QUIZ_ID]
    assert client.get(f"/api/v1/quiz/{QUIZ_ID}").status_code == 200
    answers = {question.id: question.correct for question in quiz.questions}
    submitted = client.post(
        f"/api/v1/quiz/{QUIZ_ID}",
        json={"answers": answers},
        headers={"X-CSRF-Token": token},
    ).json()
    assert submitted["passed"] is True
    review = client.get(f"/api/v1/quiz/attempts/{submitted['attempt_id']}")
    assert review.status_code == 200
    assert review.json()["attempt"]["score"] == 10

    # 4. El resultado queda reflejado en el panel personal.
    progress = client.get("/api/v1/progress").json()
    assert progress["attempts"][0]["passed"] is True
