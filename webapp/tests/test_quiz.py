"""Quiz: corrección en servidor, revisión, privacidad y CSRF."""

from __future__ import annotations

import sqlite3

from webapp.content import QUIZZES

from conftest import login, login_and_csrf, register

QUIZ_ID = "quiz-capitulo-1"
QUIZ = QUIZZES[QUIZ_ID]


def _answers(correct: bool) -> dict[str, int]:
    return {
        question.id: (
            question.correct
            if correct
            else (question.correct + 1) % len(question.options)
        )
        for question in QUIZ.questions
    }


def _submit(client, token: str | None, answers: dict[str, int]):
    headers = {"X-CSRF-Token": token} if token else {}
    return client.post(
        f"/api/v1/quiz/{QUIZ_ID}", json={"answers": answers}, headers=headers
    )


def test_quiz_get_does_not_leak_answers_or_explanations(client):
    assert login(client).status_code == 200
    response = client.get(f"/api/v1/quiz/{QUIZ_ID}")

    assert response.status_code == 200
    text = response.text
    for question in QUIZ.questions:
        assert question.explanation not in text
    for question in response.json()["quiz"]["questions"]:
        assert "correct" not in question
        assert "explanation" not in question


def test_all_correct_answers_pass_with_100_percent(client):
    token = login_and_csrf(client)
    response = _submit(client, token, _answers(correct=True))

    assert response.status_code == 200
    body = response.json()
    assert body["percent"] == 100
    assert body["passed"] is True
    assert body["score"] == 10

    review = client.get(f"/api/v1/quiz/attempts/{body['attempt_id']}").json()
    assert review["attempt"]["score"] == 10
    assert all(item["is_correct"] for item in review["review"])
    assert review["review"][0]["explanation"] == QUIZ.questions[0].explanation


def test_all_wrong_answers_fail(client):
    token = login_and_csrf(client)
    body = _submit(client, token, _answers(correct=False)).json()

    assert body["percent"] == 0
    assert body["passed"] is False

    review = client.get(f"/api/v1/quiz/attempts/{body['attempt_id']}").json()
    assert not any(item["is_correct"] for item in review["review"])


def test_attempt_review_is_private_to_its_owner(client):
    token = login_and_csrf(client)
    attempt_id = _submit(client, token, _answers(correct=True)).json()["attempt_id"]

    assert client.get(f"/api/v1/quiz/attempts/{attempt_id}").status_code == 200

    assert register(client, "intruso@example.com").status_code == 200
    assert client.get(f"/api/v1/quiz/attempts/{attempt_id}").status_code == 404


def test_quiz_submit_without_csrf_is_forbidden(client, db_path):
    assert login(client).status_code == 200

    response = _submit(client, None, _answers(correct=True))

    assert response.status_code == 403
    assert "Token de seguridad inválido" in response.json()["detail"]

    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
    finally:
        conn.close()
    assert count == 0
