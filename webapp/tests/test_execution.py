"""Ejecución de ejemplos Python y descargas de código."""

from __future__ import annotations

from dataclasses import replace

from webapp import execution
from conftest import login_and_csrf


def _run(client, code: str, csrf: str):
    return client.post(
        "/api/ejecutar",
        json={"code": code, "lesson": "que-es-un-llm"},
        headers={"X-CSRF-Token": csrf},
    )


def test_python_examples_are_embedded_in_lessons(client):
    login_and_csrf(client)
    lesson = client.get("/api/v1/lessons/que-es-un-llm").json()["lesson"]
    assert lesson["python_blocks"]
    assert any(block["type"] == "python" for block in lesson["blocks"])


def test_execute_prints_stdout(client):
    csrf = login_and_csrf(client)
    response = _run(client, "print(6 * 7)", csrf)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["stdout"] == "42\n"
    assert payload["error"] is None


def test_execute_returns_tables_and_plots(client):
    csrf = login_and_csrf(client)
    response = _run(
        client,
        "import pandas as pd\ndisplay(pd.DataFrame({'a': [1, 2]}))",
        csrf,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert any(item["type"] == "table" for item in payload["outputs"])

    response = _run(
        client,
        "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3])\nplt.show()",
        csrf,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert any(item["type"] == "image" for item in payload["outputs"])


def test_execute_blocks_dangerous_imports(client):
    csrf = login_and_csrf(client)
    response = _run(client, "import os\nprint(os.listdir('.'))", csrf)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert "import no permitido: os" in payload["error"]


def test_execute_requires_csrf(client):
    login_and_csrf(client)
    response = client.post("/api/ejecutar", json={"code": "print(1)"})
    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/json")


def test_execute_timeout(client, monkeypatch):
    csrf = login_and_csrf(client)
    monkeypatch.setattr(
        execution,
        "settings",
        replace(execution.settings, timeout_seconds=1),
    )
    response = _run(client, "while True:\n    pass", csrf)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert "tiempo máximo" in payload["error"]


def test_download_single_example(client):
    login_and_csrf(client)
    lesson = client.get("/api/v1/lessons/que-es-un-llm").json()["lesson"]
    index = lesson["python_blocks"][0]
    response = client.get(f"/api/v1/downloads/lessons/que-es-un-llm/code/{index}")
    assert response.status_code == 200
    assert response.headers["content-disposition"].endswith('.py"')
    assert "MODELOS" in response.text
    assert "def memoria_gb" in response.text


def test_download_all_examples(client):
    login_and_csrf(client)
    response = client.get("/api/v1/downloads/lessons/que-es-un-llm/code")
    assert response.status_code == 200
    assert "attachment;" in response.headers["content-disposition"]
    assert "MODELOS" in response.text


def test_english_examples_are_translated(client):
    login_and_csrf(client)
    response = client.get("/api/v1/downloads/lessons/que-es-un-llm/code?lang=en")
    assert response.status_code == 200
    assert "MODELS" in response.text
    assert "def memory_gb" in response.text
