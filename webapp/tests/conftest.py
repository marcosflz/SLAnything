"""Fixtures y utilidades compartidas por la suite de SLAnything.

La suite es deliberadamente de integración: arranca la app real con su
``lifespan`` (esquema + validación de contenido), pero aísla cada test en una
base de datos SQLite temporal y limpia el limitador de login en memoria.
No se usa red ni ningún servicio externo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# `uv run pytest` no añade la raíz del repositorio a sys.path (el proyecto no se
# instala como paquete). Lo hacemos aquí para que `import webapp` funcione
# también al invocar el ejecutable de pytest directamente.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from webapp import config, execution  # noqa: E402
from webapp.security import login_limiter  # noqa: E402

CSRF_RE = re.compile(r'name="csrf_token" value="([^"]+)"')


def _clear_login_limiter() -> None:
    """Vacía el estado global del limitador para no contaminar otros tests."""
    with login_limiter._lock:
        login_limiter._attempts.clear()


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Apunta ``config.DB_PATH`` a una base de datos nueva por test.

    ``webapp.db.connect`` lee ``config.DB_PATH`` en cada llamada, así que el
    parche surte efecto tanto en el ``lifespan`` como en las peticiones.
    """
    path = tmp_path / "test_aula.db"
    monkeypatch.setattr(config, "DB_PATH", path)
    # El Estudio también se aísla: ningún test debe escribir en authoring-data/
    # del repositorio ni leer cursos generados reales.
    monkeypatch.setattr(config, "AUTHORING_DIR", tmp_path / "authoring")
    monkeypatch.setattr(config, "AUTHORING_HOME", tmp_path / "authoring" / "home")
    return path


@pytest.fixture
def client(db_path):
    """TestClient con lifespan activo (init_db + validate_content)."""
    from webapp.main import app

    _clear_login_limiter()
    execution.reset_rate_limits()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        _clear_login_limiter()
        execution.reset_rate_limits()


def csrf_from(html: str) -> str:
    """Extrae el token CSRF del primer formulario autenticado del HTML."""
    match = CSRF_RE.search(html)
    if match is None:
        raise AssertionError("No se encontró ningún campo csrf_token en el HTML")
    return match.group(1)


def login(
    client: TestClient,
    email: str = config.DEMO_EMAIL,
    password: str = config.DEMO_PASSWORD,
    next: str = "/",
    follow_redirects: bool = False,
):
    """Envía el formulario de acceso y devuelve la respuesta sin seguir saltos."""
    return client.post(
        "/entrar",
        data={"email": email, "password": password, "next": next},
        follow_redirects=follow_redirects,
    )


def register(
    client: TestClient,
    email: str,
    password: str = "clave-segura-123",
    name: str = "Alumno de Prueba",
    password2: str | None = None,
    next: str = "/",
    follow_redirects: bool = False,
):
    """Envía el formulario de registro con valores válidos por defecto."""
    return client.post(
        "/registro",
        data={
            "name": name,
            "email": email,
            "password": password,
            "password2": password if password2 is None else password2,
            "next": next,
        },
        follow_redirects=follow_redirects,
    )


def login_and_csrf(
    client: TestClient,
    lesson: str = "que-es-un-llm",
    email: str = config.DEMO_EMAIL,
    password: str = config.DEMO_PASSWORD,
) -> str:
    """Inicia sesión, abre una lección y devuelve su token CSRF."""
    response = login(client, email=email, password=password)
    assert response.status_code == 303, response.text
    page = client.get(f"/leccion/{lesson}")
    assert page.status_code == 200, page.text
    return csrf_from(page.text)


def login_and_open_quiz(client: TestClient, quiz_id: str = "quiz-capitulo-1"):
    """Inicia sesión y devuelve la página GET del quiz indicado."""
    response = login(client)
    assert response.status_code == 303, response.text
    page = client.get(f"/quiz/{quiz_id}")
    assert page.status_code == 200, page.text
    return page
