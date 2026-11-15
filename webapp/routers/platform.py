"""Superadministración de la plataforma (ADR-021).

Alcance global, por encima de cualquier academia o cuenta individual: usuarios,
espacios, cursos generados y cuotas. El proveedor de IA se sigue configurando en
``PUT /api/v1/authoring/settings`` (también exige superadmin). Cada escritura
queda en ``audit_log`` sin espacio asociado.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from webapp import analytics, audit, repositories, workspaces
from webapp.authoring import settings as authoring_settings
from webapp.authoring import store
from webapp.db import get_db, utcnow
from webapp.deps import ensure_csrf, require_platform_admin
from webapp.security import hash_password, new_token, token_hash

INVITE_DAYS = 14

router = APIRouter(prefix="/api/v1/platform", tags=["platform"])


def _count(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> int:
    return int(conn.execute(sql, params).fetchone()[0])


# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------

@router.get("/overview")
def overview(
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    week_ago = (analytics.today() - timedelta(days=6)).isoformat()
    month = analytics.today().strftime("%Y-%m")
    return {
        "users": {
            "total": _count(conn, "SELECT COUNT(*) FROM users"),
            "disabled": _count(conn, "SELECT COUNT(*) FROM users WHERE disabled_at IS NOT NULL"),
            "platform_admins": _count(conn, "SELECT COUNT(*) FROM users WHERE is_platform_admin = 1"),
            "wau": _count(
                conn, "SELECT COUNT(DISTINCT user_id) FROM learning_events WHERE day >= ?", (week_ago,)
            ),
            "dau": _count(
                conn,
                "SELECT COUNT(DISTINCT user_id) FROM learning_events WHERE day = ?",
                (analytics.today().isoformat(),),
            ),
        },
        "workspaces": {
            "personal": _count(conn, "SELECT COUNT(*) FROM workspaces WHERE kind = 'personal'"),
            "organization": _count(conn, "SELECT COUNT(*) FROM workspaces WHERE kind = 'organization'"),
        },
        "courses": {
            "published": _count(conn, "SELECT COUNT(*) FROM generated_courses WHERE status = 'published'"),
            "draft": _count(conn, "SELECT COUNT(*) FROM generated_courses WHERE status = 'draft'"),
            "public": _count(
                conn,
                "SELECT COUNT(*) FROM generated_courses WHERE status = 'published' AND visibility = 'public'",
            ),
        },
        "jobs": {
            "month": _count(
                conn, "SELECT COUNT(*) FROM authoring_jobs WHERE substr(created_at, 1, 7) = ?", (month,)
            ),
            "failed_month": _count(
                conn,
                "SELECT COUNT(*) FROM authoring_jobs WHERE status = 'failed' AND substr(created_at, 1, 7) = ?",
                (month,),
            ),
        },
    }


@router.get("/ai")
def ai_settings(user: dict = Depends(require_platform_admin)):
    """Proveedor de IA global (sin la API key). Se guarda con ``PUT /authoring/settings``."""
    return authoring_settings.public_settings()


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserPatch(BaseModel):
    disabled: bool | None = None
    is_platform_admin: bool | None = None
    name: str | None = Field(default=None, min_length=2, max_length=80)
    email: str | None = Field(default=None, max_length=200)
    password: str | None = Field(default=None, min_length=8, max_length=200)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=200)
    password: str = Field(min_length=8, max_length=200)
    is_platform_admin: bool = False
    workspace_id: int | None = None
    role: Literal["student", "teacher", "admin", "owner"] = "student"


def _clean_email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Introduce un correo electrónico válido.")
    return email


@router.get("/users")
def list_users(
    q: str = "",
    limit: int = 50,
    offset: int = 0,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    limit = max(1, min(limit, 200))
    where, params = "", []
    if q.strip():
        where = "WHERE u.email LIKE ? OR u.name LIKE ?"
        needle = f"%{q.strip()}%"
        params = [needle, needle]
    rows = conn.execute(
        f"""SELECT u.id, u.name, u.email, u.created_at, u.last_login_at, u.disabled_at,
                   u.is_platform_admin
            FROM users u {where}
            ORDER BY u.created_at DESC, u.id DESC LIMIT ? OFFSET ?""",
        (*params, limit, max(0, offset)),
    ).fetchall()
    total = _count(conn, f"SELECT COUNT(*) FROM users u {where}", tuple(params))
    users = []
    for row in rows:
        item = dict(row)
        item["is_platform_admin"] = bool(item["is_platform_admin"])
        item["workspaces"] = workspaces.memberships_for_user(conn, int(row["id"]))
        users.append(item)
    academies = [
        dict(r)
        for r in conn.execute("SELECT id, name FROM workspaces WHERE kind = 'organization' ORDER BY name").fetchall()
    ]
    return {"users": users, "total": total, "me": user["id"], "academies": academies}


@router.post("/users", status_code=201)
def create_user(
    body: UserCreate,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Da de alta una cuenta. Sin ``workspace_id`` es una cuenta individual; con él, miembro de esa academia."""
    ensure_csrf(request, user)
    email = _clean_email(body.email)
    if repositories.get_user_by_email(conn, email) is not None:
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con ese correo.")
    target = None
    if body.workspace_id is not None:
        target = workspaces.get_workspace(conn, body.workspace_id)
        if target is None or target["kind"] != "organization":
            raise HTTPException(status_code=404, detail="Academia no encontrada.")
        if target["seat_limit"] is not None and workspaces.seat_count(conn, target["id"]) >= target["seat_limit"]:
            raise HTTPException(status_code=409, detail="La academia ha alcanzado su límite de plazas.")
    created = repositories.create_user(
        conn,
        email=email,
        name=body.name,
        password_hash=hash_password(body.password),
        role="student",
        personal_workspace=target is None,
    )
    new_id = int(created["id"])
    if body.is_platform_admin:
        conn.execute("UPDATE users SET is_platform_admin = 1 WHERE id = ?", (new_id,))
    if target is not None:
        workspaces.add_member(conn, target["id"], new_id, body.role)
    audit.record(
        conn, actor_id=user["id"], action="platform.user.create", target=email, request=request,
        meta={"is_platform_admin": body.is_platform_admin, "workspace_id": body.workspace_id, "role": body.role if target else None},
    )
    return {"ok": True, "id": new_id}


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    body: UserPatch,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    row = conn.execute("SELECT id, email, is_platform_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if user_id == user["id"] and (body.disabled or body.is_platform_admin is False):
        raise HTTPException(status_code=409, detail="No puedes desactivarte ni retirarte la superadministración.")
    if body.is_platform_admin is False and row["is_platform_admin"]:
        admins = _count(conn, "SELECT COUNT(*) FROM users WHERE is_platform_admin = 1 AND disabled_at IS NULL")
        if admins <= 1:
            raise HTTPException(status_code=409, detail="La plataforma necesita al menos un superadministrador.")
    changes: dict = {}
    if body.name is not None:
        conn.execute("UPDATE users SET name = ? WHERE id = ?", (body.name.strip(), user_id))
        changes["name"] = body.name.strip()
    if body.email is not None:
        email = _clean_email(body.email)
        taken = conn.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id)).fetchone()
        if taken is not None:
            raise HTTPException(status_code=409, detail="Ya existe una cuenta con ese correo.")
        conn.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
        changes["email"] = email
    if body.password is not None:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(body.password), user_id))
        if user_id != user["id"]:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        else:
            conn.execute("DELETE FROM sessions WHERE user_id = ? AND id != ?", (user_id, user["session_id"]))
        changes["password"] = "reset"
    if body.disabled is not None:
        conn.execute(
            "UPDATE users SET disabled_at = CASE WHEN ? THEN datetime('now') ELSE NULL END WHERE id = ?",
            (1 if body.disabled else 0, user_id),
        )
        if body.disabled:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        changes["disabled"] = body.disabled
    if body.is_platform_admin is not None:
        conn.execute(
            "UPDATE users SET is_platform_admin = ? WHERE id = ?", (1 if body.is_platform_admin else 0, user_id)
        )
        changes["is_platform_admin"] = body.is_platform_admin
    audit.record(
        conn, actor_id=user["id"], action="platform.user", target=row["email"], request=request, meta=changes
    )
    return {"ok": True}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Borra una cuenta y lo que es solo suyo (espacio individual, borradores, trabajos, sesiones)."""
    ensure_csrf(request, user)
    row = conn.execute("SELECT id, email, is_platform_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if user_id == user["id"]:
        raise HTTPException(status_code=409, detail="No puedes eliminar tu propia cuenta.")
    if row["is_platform_admin"]:
        admins = _count(conn, "SELECT COUNT(*) FROM users WHERE is_platform_admin = 1 AND disabled_at IS NULL AND id != ?", (user_id,))
        if admins < 1:
            raise HTTPException(status_code=409, detail="La plataforma necesita al menos un superadministrador.")
    owned = conn.execute(
        "SELECT name FROM workspaces WHERE owner_id = ? AND kind = 'organization' ORDER BY name", (user_id,)
    ).fetchall()
    if owned:
        names = ", ".join(r["name"] for r in owned)
        raise HTTPException(
            status_code=409,
            detail=f"Es propietaria de una academia ({names}). Transfiere la propiedad o borra la academia antes.",
        )
    published = _count(
        conn, "SELECT COUNT(*) FROM generated_courses WHERE owner_id = ? AND status = 'published'", (user_id,)
    )
    if published:
        raise HTTPException(
            status_code=409,
            detail="Tiene cursos publicados. Despublícalos o desactiva la cuenta en lugar de eliminarla.",
        )
    personal = workspaces.personal_workspace_id(conn, user_id)
    if personal is not None:
        conn.execute("DELETE FROM workspaces WHERE id = ?", (personal,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    audit.record(
        conn, actor_id=user["id"], action="platform.user.delete", target=row["email"], request=request,
    )
    return {"ok": True}


# ---------------------------------------------------------------------------
# Espacios
# ---------------------------------------------------------------------------

class WorkspacePatch(BaseModel):
    plan: str | None = Field(default=None, max_length=40)
    seat_limit: int | None = Field(default=None, ge=0, le=100000)
    gen_monthly: int | None = Field(default=None, ge=0, le=100000)
    clear_seat_limit: bool = False
    clear_gen_monthly: bool = False


def _workspace_row(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    data = dict(row)
    try:
        data["settings"] = json.loads(data.pop("settings_json") or "{}")
    except (TypeError, ValueError):
        data["settings"] = {}
    data.pop("join_code", None)
    return data


@router.get("/workspaces")
def list_workspaces(
    kind: str | None = None,
    q: str = "",
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    clauses, params = [], []
    if kind in ("personal", "organization"):
        clauses.append("w.kind = ?")
        params.append(kind)
    if q.strip():
        clauses.append("(w.name LIKE ? OR u.email LIKE ?)")
        params += [f"%{q.strip()}%"] * 2
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = conn.execute(
        f"""SELECT w.*, u.email AS owner_email,
                   (SELECT COUNT(*) FROM memberships m WHERE m.workspace_id = w.id) AS members,
                   (SELECT COUNT(*) FROM generated_courses g WHERE g.workspace_id = w.id) AS courses,
                   (SELECT COUNT(*) FROM authoring_jobs j WHERE j.workspace_id = w.id
                       AND substr(j.created_at, 1, 7) = strftime('%Y-%m', 'now')) AS jobs_month
            FROM workspaces w LEFT JOIN users u ON u.id = w.owner_id
            {where} ORDER BY w.kind DESC, w.created_at DESC LIMIT 500""",
        params,
    ).fetchall()
    return {"workspaces": [_workspace_row(conn, row) for row in rows]}


@router.patch("/workspaces/{workspace_id}")
def update_workspace(
    workspace_id: int,
    body: WorkspacePatch,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    workspace = workspaces.get_workspace(conn, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado.")
    settings = dict(workspace.get("settings") or {})
    if body.gen_monthly is not None:
        settings["gen_monthly"] = body.gen_monthly
    if body.clear_gen_monthly:
        settings.pop("gen_monthly", None)
    seat_limit = workspace.get("seat_limit")
    if body.seat_limit is not None:
        seat_limit = body.seat_limit
    if body.clear_seat_limit:
        seat_limit = None
    conn.execute(
        "UPDATE workspaces SET plan = ?, seat_limit = ?, settings_json = ? WHERE id = ?",
        (
            (body.plan or workspace["plan"]).strip() or "free",
            seat_limit,
            json.dumps(settings, ensure_ascii=False),
            workspace_id,
        ),
    )
    audit.record(
        conn, actor_id=user["id"], action="platform.workspace", workspace_id=workspace_id,
        target=workspace["name"], request=request, meta=body.model_dump(exclude_none=True),
    )
    return {"ok": True}


@router.delete("/workspaces/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Borra una academia sin cursos generados. Las cuentas individuales no se borran aquí."""
    ensure_csrf(request, user)
    workspace = workspaces.get_workspace(conn, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Espacio no encontrado.")
    if workspace["kind"] != "organization":
        raise HTTPException(status_code=409, detail="Solo se pueden borrar academias.")
    if _count(conn, "SELECT COUNT(*) FROM generated_courses WHERE workspace_id = ?", (workspace_id,)):
        raise HTTPException(status_code=409, detail="La academia tiene cursos. Bórralos o despublícalos antes.")
    conn.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
    audit.record(
        conn, actor_id=user["id"], action="platform.workspace.delete",
        target=workspace["name"], request=request,
    )
    return {"ok": True}


# ---------------------------------------------------------------------------
# Cursos generados
# ---------------------------------------------------------------------------

class VisibilityBody(BaseModel):
    visibility: str = Field(pattern="^(workspace|public)$")


@router.get("/courses")
def list_courses(
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    names = {
        int(row["id"]): row["name"] for row in conn.execute("SELECT id, name FROM workspaces")
    }
    courses = store.list_courses(limit=500)
    for course in courses:
        course["workspace_name"] = names.get(course.get("workspace_id") or -1)
    return {"courses": courses}


@router.post("/courses/{slug}/visibility")
def set_visibility(
    slug: str,
    body: VisibilityBody,
    request: Request,
    user: dict = Depends(require_platform_admin),
):
    ensure_csrf(request, user)
    if not store.set_course_visibility(slug, body.visibility):
        raise HTTPException(status_code=404, detail="Curso generado no encontrado.")
    audit.record(
        None, actor_id=user["id"], action="platform.course.visibility",
        target=slug, request=request, meta={"visibility": body.visibility},
    )
    return {"ok": True}


@router.post("/courses/{slug}/unpublish")
def unpublish(
    slug: str,
    request: Request,
    user: dict = Depends(require_platform_admin),
):
    ensure_csrf(request, user)
    if not store.set_course_status(slug, "draft"):
        raise HTTPException(status_code=404, detail="Curso generado no encontrado.")
    audit.record(None, actor_id=user["id"], action="platform.course.unpublish", target=slug, request=request)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Invitaciones de plataforma (ADR-022)
# ---------------------------------------------------------------------------

class PlatformInviteBody(BaseModel):
    """``individual``: cuenta individual. ``teacher``: profesorado de una
    academia existente (``workspace_id``) o propietario de una academia nueva
    (``academy_name`` opcional; si falta, lo escribe al aceptar)."""

    kind: Literal["individual", "teacher"]
    email: str | None = Field(default=None, max_length=200)
    workspace_id: int | None = None
    academy_name: str | None = Field(default=None, max_length=80)


def _platform_invite_payload(row: sqlite3.Row) -> dict:
    data = dict(row)
    data.pop("token_hash", None)
    data["state"] = workspaces.invitation_state(row)
    return data


@router.get("/invitations")
def list_platform_invitations(
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    rows = conn.execute(
        """SELECT p.*, w.name AS workspace_name, u.email AS accepted_email
           FROM platform_invitations p
           LEFT JOIN workspaces w ON w.id = p.workspace_id
           LEFT JOIN users u ON u.id = p.accepted_by
           ORDER BY p.created_at DESC, p.id DESC LIMIT 300"""
    ).fetchall()
    academies = [
        {"id": int(row["id"]), "name": row["name"]}
        for row in conn.execute(
            "SELECT id, name FROM workspaces WHERE kind = 'organization' ORDER BY name COLLATE NOCASE"
        )
    ]
    return {"invitations": [_platform_invite_payload(row) for row in rows], "academies": academies}


@router.post("/invitations")
def create_platform_invitation(
    body: PlatformInviteBody,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    workspace_id = body.workspace_id if body.kind == "teacher" else None
    academy_name = (body.academy_name or "").strip() or None
    if workspace_id is not None:
        workspace = workspaces.get_workspace(conn, workspace_id)
        if workspace is None or workspace["kind"] != "organization":
            raise HTTPException(status_code=404, detail="Academia no encontrada.")
        academy_name = None
    if body.kind != "teacher":
        academy_name = None
    if academy_name is not None and len(academy_name) < 2:
        raise HTTPException(status_code=400, detail="El nombre de la academia debe tener entre 2 y 80 caracteres.")
    token = new_token()
    expires = (datetime.now(timezone.utc) + timedelta(days=INVITE_DAYS)).isoformat(timespec="seconds")
    email = (body.email or "").strip().lower() or None
    cursor = conn.execute(
        """INSERT INTO platform_invitations
               (kind, email, workspace_id, academy_name, token_hash, created_by, created_at, expires_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (body.kind, email, workspace_id, academy_name, token_hash(token), user["id"], utcnow(), expires),
    )
    audit.record(
        conn, actor_id=user["id"], action="platform.invite.create", workspace_id=workspace_id,
        target=email or "(enlace)", request=request,
        meta={"kind": body.kind, "new_academy": body.kind == "teacher" and workspace_id is None},
    )
    # El token solo se muestra una vez; en la base se guarda su hash.
    return {"id": cursor.lastrowid, "path": f"/invitacion/{token}", "expires_at": expires}


@router.delete("/invitations/{invite_id}")
def revoke_platform_invitation(
    invite_id: int,
    request: Request,
    user: dict = Depends(require_platform_admin),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    ensure_csrf(request, user)
    cursor = conn.execute(
        "UPDATE platform_invitations SET revoked_at = ? WHERE id = ? AND accepted_at IS NULL AND revoked_at IS NULL",
        (utcnow(), invite_id),
    )
    if not cursor.rowcount:
        raise HTTPException(status_code=404, detail="Invitación no encontrada.")
    audit.record(conn, actor_id=user["id"], action="platform.invite.revoke", target=str(invite_id), request=request)
    return {"ok": True}
