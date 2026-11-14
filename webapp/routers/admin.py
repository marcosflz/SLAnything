"""Administración del espacio (miembros, grupos, invitaciones, auditoría) y cuenta.

Todo se limita al espacio activo del usuario. Los cambios sensibles quedan en
``audit_log``. No hay servicio de correo: las invitaciones generan un enlace
que la administración copia y envía por su canal habitual.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from webapp import audit, config, repositories, workspaces
from webapp.db import get_db, utcnow
from webapp.deps import ensure_csrf, require_admin, require_teaching, require_user
from webapp.migrations import new_join_code
from webapp.security import hash_password, new_token, token_hash, verify_password

router = APIRouter(prefix="/api/v1", tags=["admin"])

INVITE_DAYS = 14


def _ws(user: dict) -> int:
    return int(user["workspace"]["id"])


def _org(user: dict) -> int:
    if (user.get("workspace") or {}).get("kind") != "organization":
        raise HTTPException(status_code=409, detail="Esta acción solo existe en academias.")
    return _ws(user)


# ---------------------------------------------------------------------------
# Miembros
# ---------------------------------------------------------------------------

class RoleBody(BaseModel):
    role: Literal["owner", "admin", "teacher", "student"]


@router.get("/admin/members")
def list_members(user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ws = _org(user)
    workspace = workspaces.get_workspace(conn, ws)
    groups_by_user: dict[int, list[str]] = {}
    for row in conn.execute(
        """SELECT gm.user_id, g.name FROM group_members gm JOIN groups g ON g.id = gm.group_id
           WHERE g.workspace_id = ?""",
        (ws,),
    ):
        groups_by_user.setdefault(int(row[0]), []).append(row[1])
    members = workspaces.members(conn, ws)
    for member in members:
        member["groups"] = groups_by_user.get(member["id"], [])
    return {
        "workspace": {
            "id": ws,
            "name": workspace["name"],
            "join_code": workspace["join_code"],
            "seat_limit": workspace["seat_limit"],
            "plan": workspace["plan"],
        },
        "members": members,
        "me": user["id"],
        "my_role": user["ws_role"],
    }


@router.patch("/admin/members/{member_id}")
def change_role(
    member_id: int,
    body: RoleBody,
    request: Request,
    user: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    ws = _org(user)
    current = workspaces.membership(conn, ws, member_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Miembro no encontrado.")
    is_owner = user["ws_role"] == "owner"
    if (current == "owner" or body.role == "owner") and not is_owner:
        raise HTTPException(status_code=403, detail="Solo el propietario gestiona la propiedad.")
    if current == "owner" and body.role != "owner":
        owners = conn.execute(
            "SELECT COUNT(*) FROM memberships WHERE workspace_id = ? AND role = 'owner'", (ws,)
        ).fetchone()[0]
        if owners <= 1:
            raise HTTPException(status_code=409, detail="La academia necesita al menos un propietario.")
    workspaces.add_member(conn, ws, member_id, body.role)
    audit.record(conn, actor_id=user["id"], action="member.role", workspace_id=ws,
                 target=str(member_id), request=request, meta={"from": current, "to": body.role})
    return {"ok": True}


@router.delete("/admin/members/{member_id}")
def remove_member(
    member_id: int,
    request: Request,
    user: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    ws = _org(user)
    current = workspaces.membership(conn, ws, member_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Miembro no encontrado.")
    if current == "owner":
        raise HTTPException(status_code=409, detail="No se puede expulsar al propietario.")
    if member_id == user["id"]:
        raise HTTPException(status_code=409, detail="No puedes expulsarte a ti mismo.")
    workspaces.remove_member(conn, ws, member_id)
    audit.record(conn, actor_id=user["id"], action="member.remove", workspace_id=ws,
                 target=str(member_id), request=request)
    return {"ok": True}


@router.post("/admin/join-code")
def rotate_join_code(request: Request, user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    ws = _org(user)
    code = new_join_code()
    conn.execute("UPDATE workspaces SET join_code = ? WHERE id = ?", (code, ws))
    audit.record(conn, actor_id=user["id"], action="workspace.join_code", workspace_id=ws, request=request)
    return {"join_code": code}


# ---------------------------------------------------------------------------
# Grupos
# ---------------------------------------------------------------------------

class GroupBody(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=400)


class GroupMembersBody(BaseModel):
    user_ids: list[int] = Field(default_factory=list, max_length=2000)


class EnrollBody(BaseModel):
    course_slug: str = Field(min_length=2, max_length=160)
    due_at: str | None = None


def _group(conn: sqlite3.Connection, ws: int, group_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM groups WHERE id = ? AND workspace_id = ?", (group_id, ws)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Grupo no encontrado.")
    return row


@router.get("/admin/groups")
def list_groups(user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ws = _org(user)
    groups = []
    for row in conn.execute("SELECT * FROM groups WHERE workspace_id = ? ORDER BY name", (ws,)):
        members = [r[0] for r in conn.execute("SELECT user_id FROM group_members WHERE group_id = ?", (row["id"],))]
        courses = [
            dict(r) for r in conn.execute(
                "SELECT course_slug, due_at FROM enrollments WHERE group_id = ? ORDER BY created_at", (row["id"],)
            )
        ]
        groups.append({**dict(row), "member_ids": members, "enrollments": courses})
    students = workspaces.members(conn, ws)
    return {"groups": groups, "members": [{"id": m["id"], "name": m["name"], "role": m["role"]} for m in students]}


@router.post("/admin/groups")
def create_group(body: GroupBody, request: Request, user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    ws = _org(user)
    cursor = conn.execute(
        "INSERT INTO groups (workspace_id, name, description, created_at) VALUES (?, ?, ?, ?)",
        (ws, body.name.strip(), body.description.strip(), utcnow()),
    )
    audit.record(conn, actor_id=user["id"], action="group.create", workspace_id=ws, target=body.name, request=request)
    return {"id": cursor.lastrowid}


@router.delete("/admin/groups/{group_id}")
def delete_group(group_id: int, request: Request, user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    ws = _org(user)
    row = _group(conn, ws, group_id)
    conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    audit.record(conn, actor_id=user["id"], action="group.delete", workspace_id=ws, target=row["name"], request=request)
    return {"ok": True}


@router.put("/admin/groups/{group_id}/members")
def set_group_members(
    group_id: int, body: GroupMembersBody, request: Request,
    user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    ws = _org(user)
    _group(conn, ws, group_id)
    valid = set(workspaces.member_ids(conn, ws))
    conn.execute("DELETE FROM group_members WHERE group_id = ?", (group_id,))
    now = utcnow()
    conn.executemany(
        "INSERT INTO group_members (group_id, user_id, created_at) VALUES (?, ?, ?)",
        [(group_id, uid, now) for uid in sorted(set(body.user_ids) & valid)],
    )
    return {"ok": True}


@router.post("/admin/groups/{group_id}/enrollments")
def enroll_group(
    group_id: int, body: EnrollBody, request: Request,
    user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Asigna un curso a un grupo (con fecha límite opcional)."""
    ensure_csrf(request, user)
    ws = _org(user)
    _group(conn, ws, group_id)
    conn.execute(
        """INSERT INTO enrollments (workspace_id, course_slug, group_id, due_at, created_by, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (ws, body.course_slug, group_id, body.due_at, user["id"], utcnow()),
    )
    audit.record(conn, actor_id=user["id"], action="group.enroll", workspace_id=ws,
                 target=body.course_slug, request=request, meta={"group": group_id})
    return {"ok": True}


# ---------------------------------------------------------------------------
# Invitaciones
# ---------------------------------------------------------------------------

class InviteBody(BaseModel):
    email: str | None = Field(default=None, max_length=200)
    role: Literal["admin", "teacher", "student"] = "student"
    group_id: int | None = None


def _invite_payload(row: sqlite3.Row) -> dict:
    data = dict(row)
    data.pop("token_hash", None)
    data["state"] = workspaces.invitation_state(row)
    return data


def _invite_roles(user: dict) -> tuple[str, ...]:
    """Roles que el usuario puede invitar a su academia (ADR-022).

    Con el registro cerrado (por defecto) el profesorado y la administración
    solo invitan alumnado: incorporar profesorado o cuentas individuales es cosa
    de la superadministración. Con registro abierto se mantiene lo anterior
    (la administración invita profesorado; el owner, además, admins).
    """
    perms = user.get("permissions") or {}
    if not config.OPEN_SIGNUP or not perms.get("manage"):
        return ("student",)
    if user.get("ws_role") == "owner":
        return ("student", "teacher", "admin")
    return ("student", "teacher")


def _sees_all_invitations(user: dict) -> bool:
    return bool((user.get("permissions") or {}).get("manage"))


@router.get("/admin/invitations")
def list_invitations(user: dict = Depends(require_teaching), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    """La administración ve todas; el profesorado, solo las que ha creado."""
    ws = _org(user)
    if _sees_all_invitations(user):
        rows = conn.execute(
            "SELECT * FROM invitations WHERE workspace_id = ? ORDER BY created_at DESC LIMIT 200", (ws,)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM invitations WHERE workspace_id = ? AND created_by = ?
               ORDER BY created_at DESC LIMIT 200""",
            (ws, user["id"]),
        ).fetchall()
    return {"invitations": [_invite_payload(row) for row in rows], "roles": list(_invite_roles(user))}


@router.post("/admin/invitations")
def create_invitation(body: InviteBody, request: Request, user: dict = Depends(require_teaching), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    ws = _org(user)
    if body.role not in _invite_roles(user):
        detail = (
            "Solo el propietario invita administradores."
            if body.role == "admin" and config.OPEN_SIGNUP and (user.get("permissions") or {}).get("manage")
            else "Solo puedes invitar alumnado. El profesorado lo invita la administración de la plataforma."
        )
        raise HTTPException(status_code=403, detail=detail)
    if body.group_id is not None:
        _group(conn, ws, body.group_id)
    token = new_token()
    expires = (datetime.now(timezone.utc) + timedelta(days=INVITE_DAYS)).isoformat(timespec="seconds")
    email = (body.email or "").strip().lower() or None
    cursor = conn.execute(
        """INSERT INTO invitations (workspace_id, email, role, group_id, token_hash, created_by, created_at, expires_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (ws, email, body.role, body.group_id, token_hash(token), user["id"], utcnow(), expires),
    )
    audit.record(conn, actor_id=user["id"], action="invite.create", workspace_id=ws,
                 target=email or "(enlace)", request=request, meta={"role": body.role})
    # El token solo se muestra una vez; en la base se guarda su hash.
    return {"id": cursor.lastrowid, "path": f"/invitacion/{token}", "expires_at": expires}


@router.delete("/admin/invitations/{invite_id}")
def revoke_invitation(invite_id: int, request: Request, user: dict = Depends(require_teaching), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    ws = _org(user)
    query = "UPDATE invitations SET revoked_at = ? WHERE id = ? AND workspace_id = ? AND accepted_at IS NULL"
    params: tuple = (utcnow(), invite_id, ws)
    if not _sees_all_invitations(user):
        query += " AND created_by = ?"
        params += (user["id"],)
    cursor = conn.execute(query, params)
    if not cursor.rowcount:
        raise HTTPException(status_code=404, detail="Invitación no encontrada.")
    audit.record(conn, actor_id=user["id"], action="invite.revoke", workspace_id=ws, target=str(invite_id), request=request)
    return {"ok": True}


@router.get("/invitations/{token}")
def invitation_info(token: str, conn: sqlite3.Connection = Depends(get_db, scope="function")):
    """Invitación pendiente de academia o de plataforma (ADR-022)."""
    return workspaces.describe_invitation(conn, token)


class AcceptBody(BaseModel):
    academy_name: str | None = Field(default=None, max_length=80)


@router.post("/invitations/{token}/accept")
def accept_invitation(
    token: str,
    request: Request,
    body: AcceptBody | None = None,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    ws = workspaces.accept_any_invitation(
        conn, token, user["id"], user["email"], user["name"], (body or AcceptBody()).academy_name
    )
    audit.record(conn, actor_id=user["id"], action="invite.accept", workspace_id=ws, target=user["email"], request=request)
    return {"ok": True, "workspace_id": ws}


# ---------------------------------------------------------------------------
# Auditoría
# ---------------------------------------------------------------------------

@router.get("/admin/audit")
def audit_log(user: dict = Depends(require_admin), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    return {"entries": audit.list_entries(conn, _org(user))}


# ---------------------------------------------------------------------------
# Cuenta
# ---------------------------------------------------------------------------

class ProfileBody(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class PasswordBody(BaseModel):
    current: str
    new: str = Field(min_length=8, max_length=200)


@router.get("/account")
def account(user: dict = Depends(require_user), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    row = repositories.get_user(conn, user["id"])
    sessions = conn.execute(
        "SELECT id, created_at, expires_at FROM sessions WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    return {
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
        "last_login_at": row["last_login_at"],
        "workspaces": user.get("memberships", []),
        "sessions": [
            {"created_at": s["created_at"], "expires_at": s["expires_at"], "current": s["id"] == user["session_id"]}
            for s in sessions
        ],
    }


@router.patch("/account")
def update_profile(body: ProfileBody, request: Request, user: dict = Depends(require_user), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    conn.execute("UPDATE users SET name = ? WHERE id = ?", (body.name.strip(), user["id"]))
    return {"ok": True}


@router.post("/account/password")
def change_password(body: PasswordBody, request: Request, user: dict = Depends(require_user), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    row = repositories.get_user(conn, user["id"])
    if not verify_password(body.current, row["password_hash"]):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta.")
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(body.new), user["id"]))
    # Cambiar la contraseña cierra el resto de sesiones.
    conn.execute("DELETE FROM sessions WHERE user_id = ? AND id != ?", (user["id"], user["session_id"]))
    audit.record(conn, actor_id=user["id"], action="account.password", request=request)
    return {"ok": True}


@router.post("/account/sessions/revoke-others")
def revoke_other_sessions(request: Request, user: dict = Depends(require_user), conn: sqlite3.Connection = Depends(get_db, scope="function")):
    ensure_csrf(request, user)
    cursor = conn.execute("DELETE FROM sessions WHERE user_id = ? AND id != ?", (user["id"], user["session_id"]))
    return {"ok": True, "closed": cursor.rowcount}


