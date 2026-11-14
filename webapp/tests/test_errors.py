"""Errores JSON para recursos inexistentes."""

from __future__ import annotations

import pytest

from conftest import login


@pytest.mark.parametrize(
    "url",
    [
        "/api/v1/lessons/no-existe",
        "/api/v1/quiz/no-existe",
        "/api/v1/quiz/attempts/999999",
        "/api/v1/ruta-que-no-existe",
        "/ruta-que-no-existe",
    ],
)
def test_unknown_resources_return_json_404(client, url):
    assert login(client).status_code == 200

    response = client.get(url)

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"]


def test_html_routes_are_gone(client):
    """La interfaz Jinja se retiró: las rutas HTML ya no existen en FastAPI."""
    for url in ("/entrar", "/curso", "/leccion/que-es-un-llm", "/profesor", "/estudio"):
        assert client.get(url, follow_redirects=False).status_code == 404
