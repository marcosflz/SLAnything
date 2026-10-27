"""Páginas de error para recursos inexistentes."""

from __future__ import annotations

import pytest

from conftest import login


@pytest.mark.parametrize(
    "url",
    [
        "/leccion/no-existe",
        "/quiz/no-existe",
        "/quiz/intento/999999",
        "/ruta-que-no-existe",
    ],
)
def test_unknown_resources_return_404(client, url):
    assert login(client).status_code == 303

    response = client.get(url)

    assert response.status_code == 404
    assert "Página no encontrada" in response.text
    assert "404" in response.text
