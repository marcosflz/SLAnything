"""Registro de auditoría: quién hizo qué, dónde y cuándo.

Se usa para acciones sensibles (inicios de sesión, cambios de rol,
publicaciones, borrados, invitaciones y cambios de proveedor). Nunca guarda
secretos: ``meta`` debe contener solo identificadores y valores no sensibles.
"""

from __future__ import annotations

import json
import sqlite3

from fastapi import Request

from webapp.db import connect, utcnow


def _client_ip(request: Request | None) -> str:
    if request is None or request.client is None:
        return ""
    return request.client.host or ""


def record(
    conn: sqlite3.Connection | None,
    *,
    actor_id: int | None,
    action: str,
    workspace_id: int | None = None,
    target: str = "",
    request: Request | None = None,
    meta: dict | None = None,
) -> None:
    """Inserta una entrada. Si ``conn`` es None abre y confirma una conexión."""
    own = conn is None
    conn = conn or connect()
    try:
        conn.execute(
            """INSERT INTO audit_log (ts, actor_id, workspace_id, action, target, ip, meta_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                utcnow(),
                actor_id,
                workspace_id,
                action,
                str(target)[:200],
                _client_ip(request),
                json.dumps(meta or {}, ensure_ascii=False)[:4000],
            ),
        )
        if own:
            conn.commit()
    finally:
        if own:
            conn.close()


def list_entries(
    conn: sqlite3.Connection, workspace_id: int, limit: int = 200
) -> list[dict]:
    rows = conn.execute(
        """SELECT a.id, a.ts, a.action, a.target, a.ip, a.meta_json,
                  u.name AS actor_name, u.email AS actor_email
           FROM audit_log a LEFT JOIN users u ON u.id = a.actor_id
           WHERE a.workspace_id = ?
           ORDER BY a.ts DESC, a.id DESC LIMIT ?""",
        (workspace_id, limit),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["meta"] = json.loads(item.pop("meta_json") or "{}")
        except (TypeError, ValueError):
            item["meta"] = {}
        result.append(item)
    return result
