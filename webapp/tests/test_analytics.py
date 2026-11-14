"""Eventos de aprendizaje y KPIs de alumno, profesorado y administración."""

from __future__ import annotations

import sqlite3

from webapp.content import QUIZZES

from conftest import csrf, login_and_csrf, teacher_login

QUIZ_ID = "quiz-capitulo-1"
QUIZ = QUIZZES[QUIZ_ID]


def _submit(client, token: str, correct: bool):
    answers = {
        question.id: question.correct if correct else (question.correct + 1) % len(question.options)
        for question in QUIZ.questions
    }
    return client.post(
        f"/api/v1/quiz/{QUIZ_ID}", json={"answers": answers}, headers={"X-CSRF-Token": token}
    )


def test_client_events_require_csrf_and_reject_server_verbs(client, db_path):
    token = login_and_csrf(client)
    events = [
        {"verb": "lesson.heartbeat", "course": "llm-desde-cero", "lesson": "que-es-un-llm",
         "duration_ms": 999_999},
        {"verb": "lesson.completed", "lesson": "que-es-un-llm"},  # solo servidor
        {"verb": "inventado"},
    ]
    assert client.post("/api/v1/events", json={"events": events}).status_code == 403

    # sendBeacon: el token viaja en el cuerpo.
    response = client.post("/api/v1/events", json={"events": events, "csrf_token": token})
    assert response.status_code == 200
    assert response.json()["stored"] == 1

    conn = sqlite3.connect(db_path)
    duration = conn.execute(
        "SELECT duration_ms FROM learning_events WHERE verb = 'lesson.heartbeat'"
    ).fetchone()[0]
    conn.close()
    assert duration == 60_000  # recortado al máximo por latido


def test_server_records_views_completions_and_answers(client, db_path):
    token = login_and_csrf(client)
    client.get("/api/v1/lessons/que-es-un-llm")
    client.post(
        "/api/v1/lessons/que-es-un-llm/complete",
        json={"completed": True},
        headers={"X-CSRF-Token": token},
    )
    _submit(client, token, correct=True)

    conn = sqlite3.connect(db_path)
    verbs = dict(
        conn.execute("SELECT verb, COUNT(*) FROM learning_events GROUP BY verb").fetchall()
    )
    conn.close()
    assert verbs["lesson.viewed"] == 1
    assert verbs["lesson.completed"] == 1
    assert verbs["quiz.submitted"] == 1
    assert verbs["question.answered"] == len(QUIZ.questions)


def test_student_kpis(client):
    token = login_and_csrf(client)
    client.post(
        "/api/v1/events",
        json={"events": [{"verb": "lesson.heartbeat", "course": "llm-desde-cero",
                          "lesson": "que-es-un-llm", "duration_ms": 60_000}] * 5,
              "csrf_token": token},
    )
    client.post(
        "/api/v1/lessons/que-es-un-llm/complete",
        json={"completed": True},
        headers={"X-CSRF-Token": token},
    )
    _submit(client, token, correct=False)

    body = client.get("/api/v1/analytics/me").json()
    assert body["study"]["week_minutes"] == 5
    assert body["streak"] == 1
    assert body["completion"]["done"] == 1
    assert body["completion"]["eta"] is not None
    assert body["score_trend"][0]["percent"] == 0
    assert body["review_count"] == len(QUIZ.questions)
    assert len(body["chapters"]) == 7


def test_login_alone_does_not_build_a_streak(client):
    login_and_csrf(client)
    assert client.get("/api/v1/analytics/me").json()["streak"] == 0


def test_teacher_course_analytics_with_item_analysis(client):
    token = login_and_csrf(client)
    client.get("/api/v1/lessons/que-es-un-llm")
    _submit(client, token, correct=True)
    client.cookies.clear()

    teacher_login(client)
    response = client.get("/api/v1/analytics/course")
    assert response.status_code == 200
    body = response.json()
    assert body["kpis"]["students"] == 1
    assert body["kpis"]["pass_rate"] == 100
    assert body["funnel"][0]["started"] == 1
    items = body["quizzes"][0]["items"]
    assert len(items) == len(QUIZ.questions)
    assert items[0]["p_value"] == 1.0
    assert body["heatmap"]["rows"][0]["name"] == "Estudiante demo"

    csv_export = client.get("/api/v1/analytics/course.csv")
    assert csv_export.status_code == 200
    assert "Estudiante demo" in csv_export.text


def test_students_cannot_read_course_analytics_or_admin_metrics(client):
    login_and_csrf(client)
    assert client.get("/api/v1/analytics/course").status_code == 403
    assert client.get("/api/v1/admin/metrics").status_code == 403


def test_admin_metrics(client):
    teacher_login(client)
    body = client.get("/api/v1/admin/metrics").json()
    assert body["members"] == 2
    assert body["roles"] == {"owner": 1, "student": 1}
    assert len(body["daily_active"]) == 30


def test_event_endpoint_requires_session(client):
    assert client.post("/api/v1/events", json={"events": []}).status_code == 401
    assert csrf(client) == ""
