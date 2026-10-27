"""Estudio de autoría: paquetes, extracción, ajustes y publicación."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from webapp import config
from webapp.authoring import providers, settings, store
from webapp.authoring.package import parse_package
from webapp.authoring.sanitize import sanitize_html
from webapp.db import connect

from conftest import login


@pytest.fixture
def authoring_dir(tmp_path, monkeypatch):
    path = tmp_path / "authoring"
    monkeypatch.setattr(config, "AUTHORING_DIR", path)
    monkeypatch.setattr(config, "AUTHORING_HOME", path / "home")
    monkeypatch.setattr(config, "AUTHORING_ENABLED", True)
    monkeypatch.setattr(config, "AUTHORING_MAX_UPLOAD_MB", 5)
    monkeypatch.setattr(config, "AUTHORING_MAX_FILES", 3)
    store.reset_cache()
    store.ensure_dir()
    yield path
    store.reset_cache()


def _long_html(words: int = 140) -> str:
    return " ".join(["concepto"] * words)


def _blocks(lang: str) -> list[dict]:
    suffix = "EN" if lang == "en" else "ES"
    return [
        {"type": "lead", "html": f"<strong>Introducción {suffix}</strong> " + _long_html(140)},
        {"type": "p", "html": f"Párrafo de desarrollo {suffix}. " + _long_html(140)},
        {"type": "h2", "text": f"Una idea {suffix}"},
        {
            "type": "callout",
            "tone": "tip",
            "title": f"Clave {suffix}",
            "html": f"Recuerda esto {suffix}. " + _long_html(30),
        },
        {
            "type": "check",
            "question": f"¿Qué has aprendido {suffix}?",
            "answer": f"Una respuesta razonada {suffix}. " + _long_html(20),
        },
        {
            "type": "keypoints",
            "items": [f"Idea uno {suffix}", f"Idea dos {suffix}", f"Idea tres {suffix}"],
        },
    ]


def _quiz(lang: str, number: int = 1) -> dict:
    suffix = "EN" if lang == "en" else "ES"
    return {
        "id": "intro-quiz",
        "title": {"es": "Quiz de introducción", "en": "Introduction quiz"},
        "description": {
            "es": "Comprueba los conceptos principales de la unidad.",
            "en": "Check the main concepts of the unit.",
        },
        "pass_score": 80,
        "questions": [
            {
                "id": f"q{index + 1}",
                "prompt": {
                    "es": f"Pregunta {index + 1} de {suffix}",
                    "en": f"Question {index + 1} of {suffix}",
                },
                "options": {
                    "es": ["Opción A", "Opción B", "Opción C", "Opción D"],
                    "en": ["Option A", "Option B", "Option C", "Option D"],
                },
                "correct": index % 4,
                "explanation": {
                    "es": f"Explicación razonada número {index + 1}.",
                    "en": f"Reasoned explanation number {index + 1}.",
                },
            }
            for index in range(4)
        ],
    }


def sample_package(slug: str = "redes-neuronales") -> dict:
    def localized(value_es: str, value_en: str) -> dict:
        return {"es": value_es, "en": value_en}

    lessons = []
    for number, base in enumerate(("que-es", "neuronas", "aprendizaje"), start=1):
        lessons.append(
            {
                "number": number,
                "slug": base,
                "title": localized(f"Lección {number}", f"Lesson {number}"),
                "summary": localized(
                    f"Resumen de la lección {number} con suficiente detalle.",
                    f"Summary of lesson {number} with enough detail.",
                ),
                "minutes": 10,
                "objectives": {
                    "es": ["Objetivo uno", "Objetivo dos"],
                    "en": ["Objective one", "Objective two"],
                },
                "key_points": {
                    "es": ["Clave uno", "Clave dos", "Clave tres"],
                    "en": ["Key one", "Key two", "Key three"],
                },
                "blocks": {"es": _blocks("es"), "en": _blocks("en")},
            }
        )
    return {
        "schema_version": 1,
        "slug": slug,
        "languages": ["es", "en"],
        "course": {
            "title": localized("Redes neuronales", "Neural networks"),
            "subtitle": localized("Una introducción práctica", "A practical introduction"),
            "description": localized(
                "Una unidad didáctica para entender cómo aprende una red neuronal.",
                "A teaching unit to understand how a neural network learns.",
            ),
            "level": localized("Principiante", "Beginner"),
            "accent": "violet",
            "tags": ["redes", "fundamentos"],
            "source": {"title": "Documento de prueba", "author": "Equipo", "year": 2026},
        },
        "chapters": [
            {
                "number": 1,
                "slug": "introduccion",
                "title": localized("Introducción", "Introduction"),
                "subtitle": localized("La idea central", "The core idea"),
                "description": localized(
                    "Un recorrido breve por los conceptos que sostienen la unidad.",
                    "A short tour of the concepts behind the unit.",
                ),
                "level": localized("Principiante", "Beginner"),
                "lessons": lessons,
                "quiz": _quiz("es"),
                "glossary": [
                    {
                        "term": localized(f"Término {index}", f"Term {index}"),
                        "definition": localized(
                            f"Definición clara del término {index}.",
                            f"Clear definition of term {index}.",
                        ),
                        "lesson": "que-es",
                    }
                    for index in range(6)
                ],
            }
        ],
    }


def _teacher(client):
    response = login(client, email=config.TEACHER_EMAIL, password=config.TEACHER_PASSWORD)
    assert response.status_code == 303
    session = client.get("/api/v1/session")
    assert session.status_code == 200
    return session.json()["csrf_token"]


def _student(client):
    response = login(client)
    assert response.status_code == 303
    return client.get("/api/v1/session").json()["csrf_token"]


def _teacher_id() -> int:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?", (config.TEACHER_EMAIL,)
        ).fetchone()
        return int(row["id"])
    finally:
        conn.close()


def test_sanitizer_removes_scripts_handlers_and_unknown_tags():
    cleaned = sanitize_html(
        '<p onclick="alert(1)">Hola <script>alert(2)</script>'
        '<a href="javascript:alert(3)">mal</a><strong>bien</strong></p>'
    )
    assert "<script" not in cleaned
    assert "onclick" not in cleaned
    assert "javascript:" not in cleaned
    assert "<strong>bien</strong>" in cleaned
    assert "Hola" in cleaned


def test_parse_package_builds_bilingual_course(authoring_dir):
    parsed = parse_package(sample_package())
    assert parsed.slug == "gen-redes-neuronales"
    assert parsed.languages == ("es", "en")
    course = parsed.courses["es"]
    assert course.title == "Redes neuronales"
    assert course.chapter_count == 1
    assert course.lesson_count == 3
    assert course.lessons[0].slug == "gen-redes-neuronales-que-es"
    quiz = parsed.quizzes["es"]["gen-redes-neuronales-intro-quiz"]
    assert quiz.total == 4
    assert parsed.glossaries["es"][0].lesson == "gen-redes-neuronales-que-es"


def test_parse_package_rejects_missing_language(authoring_dir):
    package = sample_package()
    package["languages"] = ["es", "en"]
    del package["chapters"][0]["lessons"][0]["blocks"]["en"]
    with pytest.raises(ValueError, match="falta la lista de bloques"):
        parse_package(package)


def test_parse_package_normalizes_common_callout_tones(authoring_dir):
    package = sample_package()
    package["chapters"][0]["lessons"][0]["blocks"]["es"][3]["tone"] = "warn"
    package["chapters"][0]["lessons"][0]["blocks"]["en"][3]["tone"] = "error"
    parsed = parse_package(package)
    assert parsed.courses["es"].lessons[0].blocks[3]["tone"] == "warning"
    assert parsed.courses["en"].lessons[0].blocks[3]["tone"] == "danger"


def test_parse_package_rejects_unsafe_html(authoring_dir):
    package = sample_package()
    package["chapters"][0]["lessons"][0]["blocks"]["es"][1]["html"] = (
        '<img src=x onerror="alert(1)">' + _long_html(40)
    )
    parsed = parse_package(package)
    html = parsed.courses["es"].lessons[0].blocks[1]["html"]
    assert "onerror" not in html
    assert "<img" not in html


def test_extract_text_and_chunks(tmp_path):
    from webapp.authoring import extract

    source = tmp_path / "documento.md"
    source.write_text("# Título\n\n" + "contenido " * 20_000, encoding="utf-8")
    text = extract.extract_text(source)
    parts, truncated = extract.chunk_text(text, max_chars=10_000, chunk_chars=3_000)
    assert truncated
    assert len(parts) >= 3
    assert all(len(part) <= 3_000 for part in parts)
    assert "Título" in text


def test_settings_round_trip_does_not_expose_key(authoring_dir):
    updated = settings.save_settings(
        provider="opencode-go",
        model="deepseek-v4.1-flash",
        api_key="sk-secreto-1234",
    )
    assert updated["key_configured"] is True
    assert updated["key_hint"] == "••••1234"
    assert "api_key" not in updated
    assert "sk-secreto" not in json.dumps(updated)

    kept = settings.save_settings(
        provider="opencode-go",
        model="glm-5.3",
        api_key=None,
    )
    assert kept["key_configured"] is True
    assert settings.load_settings()["api_key"] == "sk-secreto-1234"

    cleared = settings.save_settings(
        provider="opencode-go",
        model="glm-5.3",
        clear_key=True,
    )
    assert cleared["key_configured"] is False
    assert settings.load_settings()["api_key"] == ""


def test_provider_config_uses_env_and_denies_shell(authoring_dir):
    config_data, env, model_ref = providers.build_config(
        {
            "provider": "opencode-go",
            "model": "deepseek-v4.1-flash",
            "api_key": "sk-test",
        }
    )
    assert model_ref == "opencode-go/deepseek-v4.1-flash"
    assert env == {"OPENCODE_API_KEY": "sk-test"}
    assert config_data["model"] == model_ref
    actions = {
        (rule["action"], rule["effect"]) for rule in config_data["permissions"]
    }
    assert ("shell", "deny") in actions
    assert ("external_directory", "deny") in actions

    custom, custom_env, custom_ref = providers.build_config(
        {
            "provider": "custom",
            "model": "qwen3",
            "base_url": "http://localhost:8000/v1",
            "api_key": "",
        }
    )
    assert custom_ref == "slanything/qwen3"
    assert custom_env == {}
    assert custom["providers"]["slanything"]["settings"]["baseURL"] == "http://localhost:8000/v1"


def test_api_authoring_is_teacher_only(client, authoring_dir):
    _student(client)
    assert client.get("/api/v1/authoring").status_code == 403
    assert client.get("/estudio").status_code == 403


def test_studio_page_renders_for_teacher(client, authoring_dir, monkeypatch):
    monkeypatch.setattr(
        settings,
        "engine_status",
        lambda: {
            "enabled": True,
            "available": True,
            "version": "test",
            "binary": "opencode",
            "message": "ok",
        },
    )
    _teacher(client)
    response = client.get("/estudio")
    assert response.status_code == 200
    assert "Nueva unidad a partir de documentos" in response.text
    assert 'action="/estudio/jobs"' in response.text
    assert "Guardar configuración" in response.text


def test_api_settings_save_and_preserve_key(client, authoring_dir):
    token = _teacher(client)
    response = client.put(
        "/api/v1/authoring/settings",
        json={
            "provider": "opencode-go",
            "model": "deepseek-v4.1-flash",
            "api_key": "sk-test-9876",
        },
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["key_configured"] is True
    assert body["key_hint"] == "••••9876"
    assert "api_key" not in body

    again = client.put(
        "/api/v1/authoring/settings",
        json={
            "provider": "opencode-go",
            "model": "glm-5.3",
            "api_key": "",
        },
        headers={"X-CSRF-Token": token},
    )
    assert again.status_code == 200
    assert again.json()["key_configured"] is True

    missing_csrf = client.put(
        "/api/v1/authoring/settings",
        json={"provider": "opencode-go", "model": "glm-5.3"},
    )
    assert missing_csrf.status_code == 403


def test_api_create_job_stores_upload(client, authoring_dir, monkeypatch):
    token = _teacher(client)
    settings.save_settings(
        provider="opencode-go",
        model="deepseek-v4.1-flash",
        api_key="sk-test-job",
    )
    monkeypatch.setattr(
        settings,
        "engine_status",
        lambda: {
            "enabled": True,
            "available": True,
            "version": "test",
            "binary": "opencode",
            "message": "ok",
        },
    )
    monkeypatch.setattr(
        "webapp.routers.authoring.runner.submit_job", lambda job_id: None
    )
    response = client.post(
        "/api/v1/authoring/jobs",
        data={
            "title": "Redes neuronales",
            "slug": "redes-neuronales",
            "languages": "es,en",
            "notes": "Nivel principiante",
        },
        files={
            "files": (
                "documento.md",
                ("# Redes\n\n" + "Una neurona aprende ajustando pesos. " * 100).encode(),
                "text/markdown",
            )
        },
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 202, response.text
    job = response.json()
    assert job["status"] == "queued"
    assert job["languages"] == ["es", "en"]
    stored = store.get_job(job["id"])
    assert stored is not None
    upload = store.job_dir(job["id"]) / "uploads" / stored["source_names"][0]
    assert upload.is_file()
    assert "Una neurona" in upload.read_text(encoding="utf-8")


def test_published_generated_course_enters_catalog_and_quiz(client, authoring_dir):
    token = _teacher(client)
    parsed = parse_package(sample_package())
    store.save_generated_course(
        slug=parsed.slug,
        owner_id=_teacher_id(),
        job_id="job-test",
        title="Redes neuronales",
        package=sample_package(),
        status="draft",
    )
    publish = client.post(
        f"/api/v1/authoring/courses/{parsed.slug}/publish",
        headers={"X-CSRF-Token": token},
    )
    assert publish.status_code == 200, publish.text

    catalog = client.get("/api/v1/catalog?lang=es").json()
    assert any(course["slug"] == parsed.slug for course in catalog["courses"])
    detail = client.get(f"/api/v1/courses/{parsed.slug}?lang=es")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["course"]["lesson_count"] == 3
    assert payload["course"]["title"] == "Redes neuronales"
    assert payload["course"]["book"]["title"] == "Documento de prueba"

    lesson = client.get(f"/api/v1/lessons/gen-redes-neuronales-que-es?lang=es")
    assert lesson.status_code == 200
    assert lesson.json()["lesson"]["title"] == "Lección 1"

    quiz = client.get("/api/v1/quiz/gen-redes-neuronales-intro-quiz?lang=es")
    assert quiz.status_code == 200
    assert quiz.json()["quiz"]["total"] == 4

    # La misma unidad se navega por el fallback Jinja sin cambios de plantilla.
    assert client.get(f"/cursos/{parsed.slug}").status_code == 200
    assert client.get("/leccion/gen-redes-neuronales-que-es").status_code == 200

    unpublish = client.post(
        f"/api/v1/authoring/courses/{parsed.slug}/unpublish",
        headers={"X-CSRF-Token": token},
    )
    assert unpublish.status_code == 200
    catalog = client.get("/api/v1/catalog?lang=es").json()
    assert all(course["slug"] != parsed.slug for course in catalog["courses"])


def test_runner_end_to_end_with_stubbed_opencode(client, authoring_dir, monkeypatch):
    from webapp.authoring import runner

    owner = _teacher_id()
    settings.save_settings(
        provider="opencode-go",
        model="deepseek-v4.1-flash",
        api_key="sk-test-runner",
    )
    job_id = "job-runner-test"
    store.create_job(
        job_id=job_id,
        owner_id=owner,
        title="Redes neuronales",
        source_names=["01-documento.md"],
        provider="opencode-go",
        model="deepseek-v4.1-flash",
        languages=["es", "en"],
    )
    upload = runner.uploads_dir(job_id) / "01-documento.md"
    upload.write_text(
        "# Redes\n\n" + "Una neurona ajusta sus pesos con cada ejemplo. " * 80,
        encoding="utf-8",
    )
    runner.write_meta(
        job_id,
        {"title": "Redes neuronales", "slug": "redes-neuronales", "languages": ["es", "en"]},
    )

    def fake_run(
        job_id,
        run_dir,
        config_data,
        env_extra,
        model_ref,
        meta,
        key,
        *,
        prompt=None,
        continue_session=False,
    ):
        assert (run_dir / "source" / "source-01.md").is_file()
        assert config_data["model"] == "opencode-go/deepseek-v4.1-flash"
        assert env_extra["OPENCODE_API_KEY"] == "sk-test-runner"
        (run_dir / "course.json").write_text(
            json.dumps(sample_package(), ensure_ascii=False), encoding="utf-8"
        )
        return 0

    monkeypatch.setattr(runner, "_run_opencode", fake_run)
    runner.run_job(job_id)

    job = store.get_job(job_id)
    assert job is not None
    assert job["status"] == "ready", job
    assert job["course_slug"] == "gen-redes-neuronales"
    course = store.get_course("gen-redes-neuronales", with_package=True)
    assert course is not None
    assert course["summary"]["lesson_count"] == 3
    assert "Lista:" in job["log"]


def test_runner_repairs_a_rejected_package_once(client, authoring_dir, monkeypatch):
    from webapp.authoring import runner

    owner = _teacher_id()
    settings.save_settings(
        provider="opencode-go",
        model="deepseek-v4.1-flash",
        api_key="sk-test-repair",
    )
    job_id = "job-repair-test"
    store.create_job(
        job_id=job_id,
        owner_id=owner,
        title="Reparación",
        source_names=["01-documento.md"],
        provider="opencode-go",
        model="deepseek-v4.1-flash",
        languages=["es", "en"],
    )
    (runner.uploads_dir(job_id) / "01-documento.md").write_text(
        "# Reparación\n\n" + "Una unidad necesita estructura. " * 100,
        encoding="utf-8",
    )
    runner.write_meta(
        job_id,
        {"title": "Reparación", "slug": "reparacion", "languages": ["es", "en"]},
    )
    calls = {"n": 0}

    def fake_run(job_id, run_dir, config_data, env_extra, model_ref, meta, key, *, prompt=None, continue_session=False):
        calls["n"] += 1
        if calls["n"] == 1:
            (run_dir / "course.json").write_text(
                json.dumps({"schema_version": 1, "languages": ["es"]}),
                encoding="utf-8",
            )
        else:
            assert continue_session is True
            assert "Error exacto" in (prompt or "")
            (run_dir / "course.json").write_text(
                json.dumps(sample_package("reparacion"), ensure_ascii=False),
                encoding="utf-8",
            )
        return 0

    monkeypatch.setattr(runner, "_run_opencode", fake_run)
    runner.run_job(job_id)
    job = store.get_job(job_id)
    assert job is not None
    assert job["status"] == "ready", job
    assert calls["n"] == 2
    assert "Reparación validada" in job["log"]


def test_interrupted_jobs_are_marked_failed(client, authoring_dir):
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO authoring_jobs
                   (id, owner_id, title, source_names, status, provider, model,
                    languages, created_at)
               VALUES ('job-interrupted', ?, 'Test', '[]', 'generating',
                       'opencode-go', 'm', '[\"es\"]', '2026-01-01T00:00:00+00:00')""",
            (_teacher_id(),),
        )
        conn.commit()
    finally:
        conn.close()
    assert store.mark_interrupted_jobs() == 1
    job = store.get_job("job-interrupted")
    assert job is not None
    assert job["status"] == "failed"
    assert "reinició" in (job["error"] or "")
