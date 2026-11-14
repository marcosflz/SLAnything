"""Contenido en inglés servido por la API."""

from __future__ import annotations

from webapp import config
from webapp.content import COURSES, GLOSSARIES, QUIZZES_BY_LANG, validate_program

from conftest import login, login_and_csrf


def test_both_languages_are_valid():
    for lang, program in COURSES.items():
        validate_program(
            program,
            QUIZZES_BY_LANG[lang],
            config.KNOWN_LABS,
            config.STATIC_DIR,
            GLOSSARIES[lang],
        )
        assert program.chapter_count == 7
        assert len(program.lessons) == 56


def test_english_public_payload(client):
    body = client.get("/api/v1/public?lang=en").json()
    assert body["lang"] == "en"
    assert body["course"]["title"] == "Build an LLM from Scratch"


def test_english_lessons(client):
    login(client)
    payload = client.get("/api/v1/lessons/que-es-un-llm?lang=en").json()
    assert payload["lesson"]["title"] == "What is an LLM?"
    assert payload["chapter"]["number"] == 1


def test_english_quiz_and_glossary(client):
    login(client)
    quiz = client.get("/api/v1/quiz/quiz-capitulo-1?lang=en")
    assert quiz.status_code == 200
    assert "What two things does the “large”" in quiz.text

    glossary = client.get("/api/v1/glossary?lang=en")
    assert glossary.status_code == 200
    assert "hallucination" in glossary.text
    assert "context window" in glossary.text


def test_language_cookie_selects_content(client):
    login(client)
    client.cookies.set("aula_lang", "en")
    assert client.get("/api/v1/lessons/que-es-un-llm").json()["lesson"]["title"] == "What is an LLM?"
    client.cookies.set("aula_lang", "es")
    assert client.get("/api/v1/lessons/que-es-un-llm").json()["lesson"]["title"] == "¿Qué es un LLM?"


def test_english_lesson_can_run_code(client):
    token = login_and_csrf(client)
    response = client.post(
        "/api/ejecutar",
        json={"code": "print('hello')"},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 200
    assert response.json()["stdout"] == "hello\n"
