"""Fixtures y utilidades compartidas por la suite de SLAnything.

La suite es deliberadamente de integración: arranca la app real con su
``lifespan`` (esquema + validación de contenido), pero aísla cada test en una
base de datos SQLite temporal y limpia el limitador de login en memoria.
No se usa red ni ningún servicio externo.
"""

from __future__ import annotations

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


def csrf(client: TestClient) -> str:
    """Devuelve el token CSRF de la sesión actual (vacío si no hay sesión)."""
    response = client.get("/api/v1/session")
    assert response.status_code == 200, response.text
    return response.json()["csrf_token"]


def login(
    client: TestClient,
    email: str = config.DEMO_EMAIL,
    password: str = config.DEMO_PASSWORD,
    next: str = "/",
):
    """Inicia sesión por la API JSON y devuelve la respuesta."""
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "next": next},
    )


def register(
    client: TestClient,
    email: str,
    password: str = "clave-segura-123",
    name: str = "Alumno de Prueba",
    password2: str | None = None,
    next: str = "/",
):
    """Crea una cuenta por la API JSON con valores válidos por defecto."""
    return client.post(
        "/api/v1/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
            "password2": password if password2 is None else password2,
            "next": next,
        },
    )


def login_and_csrf(
    client: TestClient,
    email: str = config.DEMO_EMAIL,
    password: str = config.DEMO_PASSWORD,
) -> str:
    """Inicia sesión y devuelve el token CSRF de la nueva sesión."""
    response = login(client, email=email, password=password)
    assert response.status_code == 200, response.text
    return csrf(client)


def teacher_login(client: TestClient) -> str:
    return login_and_csrf(
        client, email=config.TEACHER_EMAIL, password=config.TEACHER_PASSWORD
    )
