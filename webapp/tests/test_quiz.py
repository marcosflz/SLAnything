"""Quiz: corrección en servidor, revisión, privacidad y CSRF."""

from __future__ import annotations

import re
import sqlite3

from webapp.content import QUIZZES

from conftest import csrf_from, login, login_and_open_quiz, register

QUIZ_ID = "quiz-capitulo-1"
QUIZ = QUIZZES[QUIZ_ID]


def _answers(correct: bool) -> dict[str, str]:
    answers = {}
    for question in QUIZ.questions:
        if correct:
            answers[f"q_{question.id}"] = str(question.correct)
        else:
            answers[f"q_{question.id}"] = str((question.correct + 1) % len(question.options))
    return answers


def _submit(client, token: str, answers: dict[str, str]):
    data = {"csrf_token": token, **answers}
    return client.post(f"/quiz/{QUIZ_ID}", data=data, follow_redirects=False)


def test_quiz_get_does_not_leak_answers_or_explanations(client):
    assert login(client).status_code == 303
    response = client.get(f"/quiz/{QUIZ_ID}")

    assert response.status_code == 200
    assert "result-explanation" not in response.text
    for question in QUIZ.questions:
        assert f'name="q_{question.id}"' in response.text
        assert question.explanation not in response.text


def test_all_correct_answers_pass_with_100_percent(client):
    page = login_and_open_quiz(client)
    response = _submit(client, csrf_from(page.text), _answers(correct=True))

    assert response.status_code == 303
    location = response.headers["location"]
    assert re.fullmatch(r"/quiz/intento/\d+", location)

    review = client.get(location)
    assert review.status_code == 200
    assert '<div class="result-score">100<small>%</small></div>' in review.text
    assert "Capítulo superado" in review.text
    assert "10 de 10" in review.text
    assert QUIZ.questions[0].explanation in review.text


def test_all_wrong_answers_show_failure_feedback(client):
    page = login_and_open_quiz(client)
    response = _submit(client, csrf_from(page.text), _answers(correct=False))

    assert response.status_code == 303
    assert re.fullmatch(r"/quiz/intento/\d+", response.headers["location"])

    review = client.get(response.headers["location"])
    assert review.status_code == 200
    assert '<div class="result-score">0<small>%</small></div>' in review.text
    assert "Todavía no, pero vas por buen camino" in review.text
    assert "0 de 10" in review.text
    assert QUIZ.questions[0].explanation in review.text

    progress = client.get("/progreso")
    assert progress.status_code == 200
    assert "A repasar" in progress.text


def test_attempt_review_is_private_to_its_owner(client):
    page = login_and_open_quiz(client)
    response = _submit(client, csrf_from(page.text), _answers(correct=True))
    location = response.headers["location"]

    own_review = client.get(location)
    assert own_review.status_code == 200

    assert register(client, "intruso@example.com").status_code == 303
    other_review = client.get(location)

    assert other_review.status_code == 404
    assert "Página no encontrada" in other_review.text


def test_quiz_submit_without_csrf_is_forbidden(client, db_path):
    page = login_and_open_quiz(client)
    answers = _answers(correct=True)

    response = client.post(f"/quiz/{QUIZ_ID}", data=answers, follow_redirects=False)

    assert response.status_code == 403
    assert "Token de seguridad inválido" in response.text

    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
    finally:
        conn.close()
    assert count == 0
