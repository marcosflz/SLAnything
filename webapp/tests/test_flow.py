"""Flujo completo de un estudiante nuevo, de registro a revisión del quiz."""

from __future__ import annotations

from webapp.content import QUIZZES

from conftest import csrf_from, register

QUIZ_ID = "quiz-capitulo-1"


def test_new_student_can_register_learn_and_pass_the_quiz(client):
    # 1. Alta, catálogo y acceso al programa.
    assert register(client, "flujo@example.com", name="Alumna Flujo").status_code == 303
    assert client.get("/").status_code == 200
    catalog = client.get("/cursos")
    assert catalog.status_code == 200
    assert "/cursos/llm-desde-cero" in catalog.text
    assert client.get("/cursos/llm-desde-cero").status_code == 200
    assert client.get("/curso").status_code == 200

    # 2. Lectura y finalización de una lección.
    lesson = client.get("/leccion/que-es-un-llm")
    assert lesson.status_code == 200
    lesson_token = csrf_from(lesson.text)
    completed = client.post(
        "/leccion/que-es-un-llm/completar",
        data={"csrf_token": lesson_token, "completed": "1"},
        follow_redirects=False,
    )
    assert completed.status_code == 303
    assert "Completada" in client.get("/progreso").text

    # 3. Quiz final y revisión.
    quiz = QUIZZES[QUIZ_ID]
    quiz_page = client.get(f"/quiz/{QUIZ_ID}")
    assert quiz_page.status_code == 200
    answers = {f"q_{question.id}": str(question.correct) for question in quiz.questions}
    submitted = client.post(
        f"/quiz/{QUIZ_ID}",
        data={"csrf_token": csrf_from(quiz_page.text), **answers},
        follow_redirects=False,
    )
    assert submitted.status_code == 303

    review = client.get(submitted.headers["location"])
    assert review.status_code == 200
    assert "Capítulo superado" in review.text
    assert "10 de 10" in review.text

    # 4. El resultado queda reflejado en el panel personal.
    progress = client.get("/progreso")
    assert progress.status_code == 200
    assert "Aprobado" in progress.text
