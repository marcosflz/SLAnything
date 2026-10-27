"""Portada pública, formularios de acceso y redirección de zonas privadas."""

from __future__ import annotations


def test_landing_is_public_and_shows_the_programme(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Aprende IA desde los libros" in response.text
    assert "Explorar cursos" in response.text
    assert "56 lecciones" in response.text
    assert "584 minutos" in response.text
    assert response.text.count('class="program-item"') == 7


def test_catalog_and_course_detail_are_public(client):
    catalog = client.get("/cursos")

    assert catalog.status_code == 200
    assert "Construye un LLM desde cero" in catalog.text
    assert 'href="/cursos/llm-desde-cero"' in catalog.text
    assert "En preparación" in catalog.text

    detail = client.get("/cursos/llm-desde-cero")
    assert detail.status_code == 200
    assert "Construye un LLM desde cero" in detail.text
    assert "Acceso abierto" in detail.text
    assert "Capítulos y lecciones" in detail.text
    assert "Build a Large Language Model (From Scratch)" in detail.text

    missing = client.get("/cursos/no-existe")
    assert missing.status_code == 404


def test_login_and_register_forms_are_public(client):
    login_page = client.get("/entrar")
    register_page = client.get("/registro")

    assert login_page.status_code == 200
    assert 'action="/entrar"' in login_page.text
    assert "Cuenta de demostración" in login_page.text

    assert register_page.status_code == 200
    assert 'action="/registro"' in register_page.text
    assert 'name="password2"' in register_page.text


def test_anonymous_course_access_redirects_to_login_with_next(client):
    response = client.get("/curso", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/entrar?next=/curso"
    assert not response.headers.get("set-cookie")


def test_anonymous_progress_access_redirects_to_login_with_next(client):
    response = client.get("/progreso", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/entrar?next=/progreso"


def test_static_assets_are_served(client):
    css = client.get("/static/css/app.css")
    figure = client.get("/static/img/ch01/fig_1_1_jerarquia_ia.png")

    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]
    assert figure.status_code == 200
    assert figure.headers["content-type"].startswith("image/png")


def test_health_endpoint_and_security_headers(client):
    response = client.get("/salud")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "lecciones": 56, "cursos": 1}

    headers = {key.lower(): value for key, value in response.headers.items()}
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in headers["permissions-policy"]
