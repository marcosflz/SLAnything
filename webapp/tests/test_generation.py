"""Generación por etapas con el modelo falso: ingesta → temario → lecciones →
verificación → revisión → publicación."""

from __future__ import annotations

import time

import pytest

from webapp import config
from webapp.authoring import store
from webapp.generation import document as doc
from webapp.generation import verify

from conftest import csrf, login_and_csrf, register, teacher_login

PARAGRAPH = (
    "La fotosíntesis transforma la energía luminosa en energía química dentro de los "
    "cloroplastos. Las plantas capturan dióxido de carbono y liberan oxígeno mientras "
    "producen glucosa, que almacenan como almidón para crecer y reproducirse."
)
MARKDOWN = "\n\n".join(
    [
        "# Capítulo 1 · La célula vegetal",
        *[PARAGRAPH] * 6,
        "## Orgánulos",
        *[PARAGRAPH.replace("fotosíntesis", "membrana")] * 4,
        "# Capítulo 2 · Fotosíntesis",
        *[PARAGRAPH] * 8,
        "# Capítulo 3 · Respiración",
        *[PARAGRAPH.replace("fotosíntesis", "respiración celular")] * 6,
    ]
)


@pytest.fixture
def gen_env(tmp_path, monkeypatch):
    path = tmp_path / "authoring"
    monkeypatch.setattr(config, "AUTHORING_DIR", path)
    monkeypatch.setattr(config, "AUTHORING_ENABLED", True)
    monkeypatch.setattr(config, "LLM_FAKE", True)
    monkeypatch.setattr(config, "GEN_INPROCESS", True)
    store.reset_cache()
    store.ensure_dir()
    yield path
    store.reset_cache()


def _wait(client, job_id: str, statuses: set[str], timeout: float = 30) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = client.get(f"/api/v1/authoring/jobs/{job_id}").json()
        if job["status"] in statuses:
            return job
        if job["status"] == "failed":
            raise AssertionError(job["error"])
        time.sleep(0.1)
    raise AssertionError(f"timeout esperando {statuses}: {job['status']}")


def _upload(client, token: str) -> str:
    response = client.post(
        "/api/v1/authoring/jobs",
        data={"title": "Biología vegetal", "languages": ["es", "en"]},
        files={"files": ("biologia.md", MARKDOWN.encode("utf-8"), "text/markdown")},
        headers={"X-CSRF-Token": token},
    )
    assert response.status_code == 202, response.text
    return response.json()["id"]


def test_document_structure_detects_chapters(tmp_path):
    source = tmp_path / "libro.md"
    source.write_text(MARKDOWN, encoding="utf-8")
    document = doc.build_document([source])
    tops = [s for s in document["sections"] if s["level"] == 1]
    assert [s["title"] for s in tops] == [
        "Capítulo 1 · La célula vegetal",
        "Capítulo 2 · Fotosíntesis",
        "Capítulo 3 · Respiración",
    ]
    assert any(s["level"] == 2 and s["parent"] == tops[0]["id"] for s in document["sections"])
    ids = [chunk["id"] for chunk in document["chunks"]]
    assert len(ids) == len(set(ids))
    # Ningún fragmento cruza secciones de nivel 1.
    for section in tops:
        assert all(cid in ids for cid in section["chunk_ids"])


def test_plain_text_without_headings_gets_synthetic_parts(tmp_path):
    source = tmp_path / "apuntes.txt"
    source.write_text("\n\n".join([PARAGRAPH] * 120), encoding="utf-8")
    document = doc.build_document([source])
    assert document["stats"]["sections"] >= 2
    assert document["sections"][0]["title"].startswith("apuntes · parte 1")


def test_verify_flags_unsupported_and_invalid_citations():
    chunks = {"d1:c1": {"text": PARAGRAPH}}
    package = {
        "languages": ["es"],
        "chapters": [
            {
                "lessons": [
                    {
                        "slug": "l1",
                        "blocks": {
                            "es": [
                                {"type": "p", "html": PARAGRAPH, "sources": ["d1:c1"]},
                                {"type": "p", "html": "Los volcanes submarinos expulsan magma basáltico", "sources": ["d1:c1"]},
                                {"type": "p", "html": "Texto", "sources": ["d9:c9"]},
                                {"type": "p", "html": "Sin cita"},
                            ]
                        },
                    }
                ]
            }
        ],
    }
    report = verify.verify_package(package, chunks)
    blocks = package["chapters"][0]["lessons"][0]["blocks"]["es"]
    assert "unsupported" not in blocks[0]
    assert blocks[1]["unsupported"] is True
    assert report["invalid_refs"][0]["refs"] == ["d9:c9"]
    assert report["content_blocks"] == 4
    assert report["cited_pct"] == 50


def test_staged_generation_end_to_end(client, gen_env):
    token = teacher_login(client)
    job_id = _upload(client, token)
    job = _wait(client, job_id, {"awaiting_scope"})
    assert job["engine"] == "adk"
    assert job["progress"]["sections"] == 3

    outline_doc = client.get(f"/api/v1/authoring/jobs/{job_id}/document").json()
    tops = [s for s in outline_doc["sections"] if s["level"] == 1]
    assert "chunk_ids" not in tops[0]  # la UI no recibe el texto

    planned = client.post(
        f"/api/v1/authoring/jobs/{job_id}/plan",
        json={"scope": [tops[0]["id"], tops[1]["id"]], "lessons_per_chapter": 2, "questions_per_chapter": 6},
        headers={"X-CSRF-Token": token},
    )
    assert planned.status_code == 202, planned.text
    _wait(client, job_id, {"awaiting_outline"})

    outline = client.get(f"/api/v1/authoring/jobs/{job_id}/outline").json()
    assert len(outline["chapters"]) == 2
    outline["chapters"][0]["lessons"][0]["title"] = {"es": "Lección renombrada", "en": "Renamed lesson"}
    saved = client.put(
        f"/api/v1/authoring/jobs/{job_id}/outline",
        json={"outline": outline},
        headers={"X-CSRF-Token": token},
    )
    assert saved.status_code == 200, saved.text

    assert client.post(
        f"/api/v1/authoring/jobs/{job_id}/generate", headers={"X-CSRF-Token": token}
    ).status_code == 202
    job = _wait(client, job_id, {"ready"})
    slug = job["course_slug"]
    assert job["tokens_in"] > 0

    course = client.get(f"/api/v1/authoring/courses/{slug}").json()
    assert course["status"] == "draft"
    assert course["report"]["cited_pct"] > 50
    assert course["report"]["lessons"] == 4
    package = course["package"]
    first = package["chapters"][0]["lessons"][0]
    assert first["title"]["es"] == "Lección renombrada"
    kinds = {q["kind"] for q in package["chapters"][0]["quiz"]["questions"]}
    assert kinds == {"single", "multiple", "true_false"}

    history = client.get(f"/api/v1/authoring/jobs/{job_id}/history").json()["events"]
    assert any(event["type"] == "ready" for event in history)

    # Revisión: el profesor edita un bloque y guarda el paquete validado.
    package["chapters"][0]["lessons"][0]["blocks"]["es"][0]["html"] = "<strong>Editado</strong> por la profesora con calma y criterio."
    edited = client.put(
        f"/api/v1/authoring/courses/{slug}/package",
        json={"package": package},
        headers={"X-CSRF-Token": token},
    )
    assert edited.status_code == 200, edited.text

    # Un paquete roto no se guarda.
    broken = {**package, "chapters": []}
    assert client.put(
        f"/api/v1/authoring/courses/{slug}/package", json={"package": broken}, headers={"X-CSRF-Token": token}
    ).status_code == 400

    # Regenerar una lección conserva las ediciones del resto.
    regen = client.post(
        f"/api/v1/authoring/courses/{slug}/regenerate",
        json={"chapter": 1, "lesson": 2, "instructions": "Más ejemplos"},
        headers={"X-CSRF-Token": token},
    )
    assert regen.status_code == 202, regen.text
    deadline = time.time() + 20
    while time.time() < deadline:
        events = client.get(f"/api/v1/authoring/jobs/{job_id}/history").json()["events"]
        if any("regenerada" in event["message"] for event in events):
            break
        time.sleep(0.1)
    after = client.get(f"/api/v1/authoring/courses/{slug}").json()["package"]
    assert after["chapters"][0]["lessons"][0]["blocks"]["es"][0]["html"].startswith("<strong>Editado</strong>")

    published = client.post(
        f"/api/v1/authoring/courses/{slug}/publish", json={"visibility": "workspace"}, headers={"X-CSRF-Token": token}
    )
    assert published.status_code == 200, published.text

    # Un estudiante de la academia ve la unidad y su quiz multirrespuesta se corrige bien.
    client.cookies.clear()
    student_token = login_and_csrf(client)
    lesson_slug = client.get(f"/api/v1/courses/{slug}").json()["course"]["chapters"][0]["lessons"][0]["slug"]
    lesson = client.get(f"/api/v1/lessons/{lesson_slug}").json()["lesson"]
    assert any(block.get("sources") for block in lesson["blocks"])
    quiz_id = f"{slug}-{package['chapters'][0]['slug']}-quiz"
    quiz = client.get(f"/api/v1/quiz/{quiz_id}")
    assert quiz.status_code == 200, quiz.text
    answers = {}
    for question in package["chapters"][0]["quiz"]["questions"]:
        answers[question["id"]] = question["correct"]
    result = client.post(
        f"/api/v1/quiz/{quiz_id}", json={"answers": answers}, headers={"X-CSRF-Token": student_token}
    ).json()
    assert result["percent"] == 100

    multiple = next(q for q in package["chapters"][0]["quiz"]["questions"] if q["kind"] == "multiple")
    partial = {**answers, multiple["id"]: multiple["correct"][:1]}
    result = client.post(
        f"/api/v1/quiz/{quiz_id}", json={"answers": partial}, headers={"X-CSRF-Token": student_token}
    ).json()
    assert result["percent"] < 100


def test_students_of_an_academy_cannot_use_the_studio(client, gen_env):
    login_and_csrf(client)
    assert client.get("/api/v1/authoring").status_code == 403


def test_personal_workspace_can_generate_and_quota_applies(client, gen_env, monkeypatch):
    monkeypatch.setattr(config, "GEN_MONTHLY_PERSONAL", 1)
    register(client, "autodidacta@example.com", name="Ana Autodidacta")
    token = csrf(client)
    body = client.get("/api/v1/authoring").json()
    assert body["quota"] == {"limit": 1, "used": 0, "remaining": 1}
    assert body["can_configure"] is False

    _upload(client, token)
    second = client.post(
        "/api/v1/authoring/jobs",
        data={"title": "Otra"},
        files={"files": ("otra.md", MARKDOWN.encode("utf-8"), "text/markdown")},
        headers={"X-CSRF-Token": token},
    )
    assert second.status_code == 429


def test_only_platform_admins_change_provider_settings(client, gen_env):
    register(client, "sin-admin@example.com")
    response = client.put(
        "/api/v1/authoring/settings",
        json={"provider": "openai", "model": "gpt-x"},
        headers={"X-CSRF-Token": csrf(client)},
    )
    assert response.status_code == 403
