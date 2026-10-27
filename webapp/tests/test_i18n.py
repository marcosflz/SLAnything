"""Selector de idioma y contenido en inglés."""

from __future__ import annotations

from webapp.content import COURSES, GLOSSARIES, QUIZZES_BY_LANG, validate_program
from webapp import config
from conftest import csrf_from, login


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


def test_english_landing(client):
    response = client.get("/?lang=en")
    assert response.status_code == 200
    assert 'lang="en"' in response.text
    assert "Understand how ChatGPT works" in response.text
    assert "7 chapters" in response.text


def test_english_lessons(client):
    login(client)
    page = client.get("/leccion/que-es-un-llm?lang=en")
    assert page.status_code == 200
    assert "What is an LLM?" in page.text
    assert "By the end you will be able to" in page.text
    assert "Chapter 1" in page.text


def test_english_quiz_and_glossary(client):
    login(client)
    quiz = client.get("/quiz/quiz-capitulo-1?lang=en")
    assert quiz.status_code == 200
    assert "Self-assessment" in quiz.text
    assert "What two things does the “large”" in quiz.text

    glossary = client.get("/glosario?lang=en")
    assert glossary.status_code == 200
    assert "hallucination" in glossary.text
    assert "context window" in glossary.text


def test_language_switch_sets_cookie(client):
    login(client)
    response = client.get("/idioma/en?next=/curso")
    assert response.status_code == 200
    assert client.cookies.get("aula_lang") == "en"
    page = client.get("/curso")
    assert "Lessons" in page.text
    assert "Programa del curso" not in page.text

    response = client.get("/idioma/es?next=/curso")
    assert response.status_code == 200
    page = client.get("/curso")
    assert "Programa del curso" in page.text


def test_english_lesson_has_english_example(client):
    login(client)
    page = client.get("/leccion/que-es-un-llm?lang=en")
    csrf = csrf_from(page.text)
    response = client.post(
        "/api/ejecutar",
        json={"code": "print('hello')"},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200
    assert response.json()["stdout"] == "hello\n"
