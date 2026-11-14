"""Buscador, glosario y recursos descargables."""

from __future__ import annotations

import json

from conftest import login


def test_search_finds_attention_lesson(client):
    assert login(client).status_code == 200

    body = client.get("/api/v1/search", params={"q": "atención"}).json()

    slugs = [item["lesson"]["slug"] for item in body["results"]]
    assert "transformer-y-atencion" in slugs


def test_search_without_results_is_empty(client):
    assert login(client).status_code == 200
    body = client.get("/api/v1/search", params={"q": "zzzz-no-existe"}).json()
    assert body["results"] == []


def test_glossary_lists_terms_and_lesson_links(client):
    assert login(client).status_code == 200
    response = client.get("/api/v1/glossary")
    assert response.status_code == 200
    assert "self-attention" in response.text
    assert any(
        term.get("lesson")
        for group in response.json()["groups"]
        for term in group["terms"]
    )


def test_resources_and_notebook_download(client):
    assert login(client).status_code == 200
    resources = client.get("/api/v1/resources").json()["resources"]
    assert any(item["href"] == "/api/v1/downloads/notebook" for item in resources)

    notebook = client.get("/api/v1/downloads/notebook")
    assert notebook.status_code == 200
    assert notebook.headers["content-type"].startswith("application/x-ipynb+json")
    payload = json.loads(notebook.content)
    assert payload["cells"]
