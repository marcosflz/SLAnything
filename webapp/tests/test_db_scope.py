"""La transacción se confirma antes de enviar la respuesta.

Con el ámbito por defecto de FastAPI (``request``), el código de salida de una
dependencia con ``yield`` corre después de responder: una petición inmediata
(crear un grupo y añadirle miembros, por ejemplo) podía leer datos sin
confirmar. Todas las rutas deben usar ``Depends(get_db, scope="function")``.
"""

from __future__ import annotations

from fastapi.routing import APIRoute

from webapp.db import get_db


def _walk(dependant):
    for sub in dependant.dependencies:
        yield sub
        yield from _walk(sub)


def test_every_route_commits_before_responding():
    from webapp.main import app

    offenders = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for dep in _walk(route.dependant):
            if dep.call is get_db and dep.scope != "function":
                offenders.append(route.path)
    assert offenders == []


def test_write_is_visible_to_the_next_request(client):
    from conftest import teacher_login

    token = teacher_login(client)
    group = client.post(
        "/api/v1/admin/groups", json={"name": "Inmediato"}, headers={"X-CSRF-Token": token}
    ).json()["id"]
    response = client.put(
        f"/api/v1/admin/groups/{group}/members", json={"user_ids": []}, headers={"X-CSRF-Token": token}
    )
    assert response.status_code == 200
