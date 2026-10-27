"""Buscador, glosario y recursos descargables."""

from __future__ import annotations

import json

from conftest import login


def test_search_finds_attention_lesson(client):
    assert login(client).status_code == 303

    response = client.get("/buscar", params={"q": "atención"})

    assert response.status_code == 200
    assert "Resultados para" in response.text
    assert 'href="/leccion/transformer-y-atencion"' in response.text
    assert "Transformer y atención" in response.text


def test_search_without_results_shows_empty_state(client):
    assert login(client).status_code == 303

    response = client.get("/buscar", params={"q": "zzzz-no-existe"})

    assert response.status_code == 200
    assert "Sin resultados" in response.text


def test_glossary_lists_terms_and_lesson_links(client):
    assert login(client).status_code == 303

    response = client.get("/glosario")

    assert response.status_code == 200
    assert "self-attention" in response.text
    assert 'data-glossary-grid' in response.text
    assert "Ver en la lección" in response.text


def test_resources_page_and_notebook_download(client):
    assert login(client).status_code == 303

    page = client.get("/recursos")
    assert page.status_code == 200
    assert "Cuaderno interactivo" in page.text
    assert 'href="/recursos/cuaderno"' in page.text

    notebook = client.get("/recursos/cuaderno")
    assert notebook.status_code == 200
    assert notebook.headers["content-type"].startswith("application/x-ipynb+json")
    payload = json.loads(notebook.content)
    assert "cells" in payload
    assert payload["cells"]
