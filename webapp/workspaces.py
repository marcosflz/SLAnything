"""Espacios de trabajo (tenancy), membresías y roles.

Cada usuario tiene un espacio **personal** del que es ``owner``: ahí puede subir
documentos y generar unidades para sí mismo. Una academia es un espacio de tipo
``organization`` con miembros ``owner``, ``admin``, ``teacher`` y ``student``.
Todo el contenido generado, los trabajos del Estudio, los grupos y las
invitaciones cuelgan de ``workspace_id``.
"""

from __future__ import annotations

import json
import sqlite3

from webapp.db import utcnow
from webapp.migrations import new_join_code, slugify_name

ROLES = ("student", "teacher", "admin", "owner")
ROLE_RANK = {role: rank for rank, role in enumerate(ROLES)}


def role_at_least(role: str | None, minimum: str) -> bool:
    return ROLE_RANK.get(role or "", -1) >= ROLE_RANK[minimum]


def _unique_slug(conn: sqlite3.Connection, base: str) -> str:
    slug = slugify_name(base)
    candidate, n = slug, 2
    while conn.execute("SELECT 1 FROM workspaces WHERE slug = ?", (candidate,)).fetchone():
        candidate = f"{slug}-{n}"
        n += 1
    return candidate


def create_workspace(
    conn: sqlite3.Connection,
    kind: str,
    name: str,
    owner_id: int | None,
    *,
    seat_limit: int | None = None,
    slug: str | None = None,
) -> int:
    cursor = conn.execute(
        """INSERT INTO workspaces (kind, name, slug, owner_id, seat_limit, join_code, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            kind,
            name.strip()[:80] or "Espacio",
            _unique_slug(conn, slug or name),
            owner_id,
            seat_limit,
            new_join_code() if kind == "organization" else None,
            utcnow(),
        ),
    )
    workspace_id = int(cursor.lastrowid)
    if owner_id is not None:
        add_member(conn, workspace_id, owner_id, "owner")
    return workspace_id


def add_member(conn: sqlite3.Connection, workspace_id: int, user_id: int, role: str) -> None:
    if role not in ROLES:
        raise ValueError(f"Rol desconocido: {role}")
    conn.execute(
        """INSERT INTO memberships (workspace_id, user_id, role, created_at)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(workspace_id, user_id) DO UPDATE SET role = excluded.role""",
        (workspace_id, user_id, role, utcnow()),
    )


def remove_member(conn: sqlite3.Connection, workspace_id: int, user_id: int) -> bool:
    cursor = conn.execute(
        "DELETE FROM memberships WHERE workspace_id = ? AND user_id = ?",
        (workspace_id, user_id),
    )
    conn.execute(
        """DELETE FROM group_members WHERE user_id = ? AND group_id IN
               (SELECT id FROM groups WHERE workspace_id = ?)""",
        (user_id, workspace_id),
    )
    return cursor.rowcount > 0


def personal_workspace_id(conn: sqlite3.Connection, user_id: int) -> int | None:
    row = conn.execute(
        """SELECT id FROM workspaces WHERE kind = 'personal' AND owner_id = ?
           ORDER BY id LIMIT 1""",
        (user_id,),
    ).fetchone()
    return int(row[0]) if row else None


def ensure_personal_workspace(conn: sqlite3.Connection, user_id: int, name: str) -> int:
    existing = personal_workspace_id(conn, user_id)
    if existing is not None:
        return existing
    first = name.strip().split(" ")[0] if name.strip() else "Mi"
    return create_workspace(
        conn, "personal", f"Espacio de {first}", user_id, slug=f"personal-{user_id}"
    )


def ensure_all_personal_workspaces(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """SELECT u.id, u.name FROM users u
           WHERE NOT EXISTS (SELECT 1 FROM workspaces w
                             WHERE w.kind = 'personal' AND w.owner_id = u.id)"""
    ).fetchall()
    for row in rows:
        ensure_personal_workspace(conn, int(row[0]), row[1])


def get_workspace(conn: sqlite3.Connection, workspace_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,)).fetchone()
    return _workspace_dict(row) if row else None


def get_workspace_by_join_code(conn: sqlite3.Connection, code: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM workspaces WHERE join_code = ?", (code.strip().upper(),)
    ).fetchone()
    return _workspace_dict(row) if row else None


def _workspace_dict(row: sqlite3.Row) -> dict:
    data = dict(row)
    try:
        data["settings"] = json.loads(data.pop("settings_json") or "{}")
    except (TypeError, ValueError):
        data["settings"] = {}
    return data


def memberships_for_user(conn: sqlite3.Connection, user_id: int) -> list[dict]:
    rows = conn.execute(
        """SELECT w.id, w.kind, w.name, w.slug, w.plan, m.role
           FROM memberships m JOIN workspaces w ON w.id = m.workspace_id
           WHERE m.user_id = ?
           ORDER BY CASE w.kind WHEN 'organization' THEN 0 ELSE 1 END, w.id""",
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def membership(conn: sqlite3.Connection, workspace_id: int, user_id: int) -> str | None:
    row = conn.execute(
        "SELECT role FROM memberships WHERE workspace_id = ? AND user_id = ?",
        (workspace_id, user_id),
    ).fetchone()
    return row[0] if row else None


def resolve_active(memberships: list[dict], requested: str | int | None) -> dict | None:
    """Elige el espacio activo: el pedido si el usuario es miembro; si no, el
    primero de organización y, en su defecto, el personal."""
    if not memberships:
        return None
    try:
        wanted = int(requested) if requested is not None else None
    except (TypeError, ValueError):
        wanted = None
    if wanted is not None:
        for item in memberships:
            if item["id"] == wanted:
                return item
    return memberships[0]


def members(conn: sqlite3.Connection, workspace_id: int, role: str | None = None) -> list[dict]:
    query = """SELECT u.id, u.name, u.email, u.created_at, u.last_login_at,
                      u.disabled_at, m.role, m.created_at AS joined_at
               FROM memberships m JOIN users u ON u.id = m.user_id
               WHERE m.workspace_id = ?"""
    params: list = [workspace_id]
    if role:
        query += " AND m.role = ?"
        params.append(role)
    query += " ORDER BY u.name COLLATE NOCASE"
    return [dict(row) for row in conn.execute(query, params).fetchall()]


def member_ids(conn: sqlite3.Connection, workspace_id: int, role: str | None = None) -> list[int]:
    return [item["id"] for item in members(conn, workspace_id, role)]


def seat_count(conn: sqlite3.Connection, workspace_id: int) -> int:
    return int(
        conn.execute(
            "SELECT COUNT(*) FROM memberships WHERE workspace_id = ?", (workspace_id,)
        ).fetchone()[0]
    )


def ensure_demo_organization(conn: sqlite3.Connection, teacher_email: str, student_email: str) -> None:
    """Academia de demostración: la profesora es owner y el alumno demo, student."""
    teacher = conn.execute("SELECT id FROM users WHERE email = ?", (teacher_email,)).fetchone()
    student = conn.execute("SELECT id FROM users WHERE email = ?", (student_email,)).fetchone()
    if teacher is None:
        return
    row = conn.execute("SELECT id FROM workspaces WHERE slug = 'academia-demo'").fetchone()
    if row is None:
        workspace_id = create_workspace(
            conn, "organization", "Academia Demo", int(teacher[0]), slug="academia-demo"
        )
    else:
        workspace_id = int(row[0])
    if student is not None and membership(conn, workspace_id, int(student[0])) is None:
        add_member(conn, workspace_id, int(student[0]), "student")
