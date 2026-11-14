"""Datos públicos, zonas privadas y estáticos."""

from __future__ import annotations


def test_public_payload_shows_the_programme(client):
    body = client.get("/api/v1/public").json()
    assert body["course"]["lesson_count"] == 56
    assert body["course"]["chapter_count"] == 7


def test_catalog_and_course_detail_are_public(client):
    catalog = client.get("/api/v1/catalog").json()
    assert any(course["slug"] == "llm-desde-cero" for course in catalog["courses"])

    detail = client.get("/api/v1/courses/llm-desde-cero")
    assert detail.status_code == 200
    assert detail.json()["course"]["title"] == "Construye un LLM desde cero"
    assert client.get("/api/v1/courses/no-existe").status_code == 404


def test_private_endpoints_require_a_session(client):
    for url in ("/api/v1/course", "/api/v1/progress", "/api/v1/dashboard", "/api/v1/shell"):
        response = client.get(url)
        assert response.status_code == 401, url
        assert not response.headers.get("set-cookie")


def test_static_assets_are_served(client):
    figure = client.get("/static/img/ch01/fig_1_1_jerarquia_ia.png")
    lab = client.get("/static/js/labs/memory.js")
    assert figure.status_code == 200
    assert figure.headers["content-type"].startswith("image/png")
    assert lab.status_code == 200


def test_health_endpoint_and_security_headers(client):
    response = client.get("/salud")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "ejemplos": True}

    headers = {key.lower(): value for key, value in response.headers.items()}
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in headers["permissions-policy"]
