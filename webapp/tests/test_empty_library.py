"""Plataforma genérica (ADR-020): sin cursos de ejemplo la app sigue funcionando.

Una instalación nueva no trae ningún curso. Todas las páginas de la aplicación
deben responder con ``course: null`` en lugar de fallar, y el curso de ejemplo
solo aparece si se activa ``AULA_SAMPLE_COURSES``.
"""

from __future__ import annotations

import sqlite3

import pytest

from webapp import config

from conftest import login, self_learner_login, teacher_login


@pytest.fixture
def empty(no_samples, client):
    return client


def test_public_pages_work_without_courses(empty):
    public = empty.get("/api/v1/public").json()
    assert public["course"] is None
    assert public["catalog"] == []
    assert public["site"]["course_title"] is None
    assert "LLM" not in public["site"]["tagline"]
    assert public["demo_accounts"]
    assert empty.get("/api/v1/catalog").json()["featured"] is None
    assert empty.get("/salud").json() == {"status": "ok", "ejemplos": False}


@pytest.mark.parametrize(
    "url",
    [
        "/api/v1/shell",
        "/api/v1/dashboard",
        "/api/v1/progress",
        "/api/v1/glossary",
        "/api/v1/resources",
        "/api/v1/search?q=atencion",
        "/api/v1/analytics/me",
    ],
)
def test_app_pages_answer_with_an_empty_course(empty, url):
    assert login(empty).status_code == 200
    response = empty.get(url)
    assert response.status_code == 200, response.text
    assert response.json()["course"] is None


def test_course_dependent_routes_return_404(empty):
    login(empty)
    assert empty.get("/api/v1/course").status_code == 404
    assert empty.get("/api/v1/lessons/que-es-un-llm").status_code == 404
    assert empty.get("/api/v1/downloads/notebook").status_code == 404


def test_teacher_tools_work_without_courses(empty):
    teacher_login(empty)
    assert empty.get("/api/v1/teacher").status_code == 200
    report = empty.get("/api/v1/analytics/course")
    assert report.status_code == 200
    assert report.json()["course"] is None
    assert empty.get("/api/v1/analytics/course.csv").status_code == 200


def test_sample_course_is_marked_and_listed_last(client):
    """Con ejemplos activos, el curso LLM aparece como ejemplo."""
    login(client)
    courses = client.get("/api/v1/catalog").json()["courses"]
    sample = next(course for course in courses if course["slug"] == config.SAMPLE_COURSE_SLUG)
    assert sample["is_sample"] is True
    resources = client.get("/api/v1/resources").json()["resources"]
    assert any(item["href"] == "/api/v1/downloads/notebook" for item in resources)


def _publish(db_path, workspace_email: str, slug_hint: str) -> str:
    from test_authoring import sample_package  # noqa: PLC0415

    from webapp.authoring import store
    from webapp.authoring.package import parse_package

    conn = sqlite3.connect(db_path)
    owner = conn.execute("SELECT id FROM users WHERE email = ?", (workspace_email,)).fetchone()[0]
    ws = conn.execute(
        "SELECT workspace_id FROM memberships WHERE user_id = ? ORDER BY workspace_id LIMIT 1",
        (owner,),
    ).fetchone()[0]
    conn.close()
    package = sample_package(slug_hint)
    slug = parse_package(package).slug
    store.save_generated_course(
        slug=slug, owner_id=owner, job_id=None, title=slug_hint,
        package=package, status="published", workspace_id=ws,
    )
    return slug


def test_generated_course_becomes_the_active_course(empty, db_path):
    self_learner_login(empty)
    slug = _publish(db_path, config.SELF_LEARNER_EMAIL, "propio")

    shell = empty.get("/api/v1/shell").json()
    assert shell["course"]["slug"] == slug
    assert shell["default_course_slug"] == slug
    glossary = empty.get("/api/v1/glossary").json()
    assert glossary["course"]["slug"] == slug


def test_active_course_is_the_last_one_opened(client, db_path):
    self_learner_login(client)
    slug = _publish(db_path, config.SELF_LEARNER_EMAIL, "ultimo")
    # Con ejemplos activos, el curso del espacio va antes que el ejemplo.
    assert client.get("/api/v1/shell").json()["course"]["slug"] == slug

    assert client.get("/api/v1/lessons/que-es-un-llm").status_code == 200
    assert client.get("/api/v1/shell").json()["course"]["slug"] == config.SAMPLE_COURSE_SLUG


def test_library_follows_the_active_workspace(empty, db_path):
    """Un curso de la academia no se ve desde la cuenta individual y viceversa."""
    slug = _publish(db_path, config.TEACHER_EMAIL, "academia")
    token = login(empty).status_code
    assert token == 200
    student_courses = {course["slug"] for course in empty.get("/api/v1/catalog").json()["courses"]}
    assert slug in student_courses

    empty.cookies.clear()
    self_learner_login(empty)
    own = {course["slug"] for course in empty.get("/api/v1/catalog").json()["courses"]}
    assert slug not in own


def test_glossary_is_scoped_to_the_active_course(client, db_path):
    self_learner_login(client)
    slug = _publish(db_path, config.SELF_LEARNER_EMAIL, "glosario")
    terms = {
        term["term"]
        for group in client.get(f"/api/v1/glossary?course={slug}").json()["groups"]
        for term in group["terms"]
    }
    sample_terms = {
        term["term"]
        for group in client.get(f"/api/v1/glossary?course={config.SAMPLE_COURSE_SLUG}").json()["groups"]
        for term in group["terms"]
    }
    assert terms and sample_terms
    assert terms.isdisjoint(sample_terms)
