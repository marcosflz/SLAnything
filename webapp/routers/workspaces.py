"""Espacios de trabajo: listar, cambiar, crear academias y unirse por código."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from webapp import audit, config, workspaces
from webapp.db import get_db
from webapp.deps import ensure_csrf, require_user
from webapp.i18n import request_lang, translate

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


class SwitchBody(BaseModel):
    workspace_id: int


class CreateOrgBody(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class JoinBody(BaseModel):
    code: str = Field(min_length=4, max_length=16)


def _set_active(response: JSONResponse, workspace_id: int) -> JSONResponse:
    response.set_cookie(
        config.WORKSPACE_COOKIE,
        str(workspace_id),
        max_age=365 * 86400,
        httponly=True,
        samesite="lax",
        secure=config.SECURE_COOKIES,
        path="/",
    )
    return response


@router.get("")
def list_workspaces(user: dict = Depends(require_user)):
    return {
        "active": user.get("workspace"),
        "workspaces": user.get("memberships", []),
        "permissions": user.get("permissions"),
    }


@router.post("/switch")
def switch_workspace(
    body: SwitchBody,
    request: Request,
    user: dict = Depends(require_user),
):
    ensure_csrf(request, user)
    if body.workspace_id not in user.get("workspace_ids", frozenset()):
        raise HTTPException(status_code=404, detail="Espacio no encontrado.")
    return _set_active(JSONResponse({"ok": True}), body.workspace_id)


@router.post("")
def create_organization(
    body: CreateOrgBody,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Crea una academia. Quien la crea es su owner."""
    ensure_csrf(request, user)
    workspace_id = workspaces.create_workspace(
        conn, "organization", body.name, user["id"]
    )
    audit.record(
        conn, actor_id=user["id"], action="workspace.create",
        workspace_id=workspace_id, target=body.name, request=request,
    )
    conn.commit()
    workspace = workspaces.get_workspace(conn, workspace_id)
    return _set_active(JSONResponse({"ok": True, "workspace": workspace}), workspace_id)


@router.post("/join")
def join_with_code(
    body: JoinBody,
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Unirse a una academia como estudiante con su código de clase."""
    ensure_csrf(request, user)
    lang = request_lang(request)
    try:
        workspace, created = workspaces.join_with_code(conn, body.code, user["id"])
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=translate(exc.detail, lang)) from exc
    if created:
        audit.record(
            conn, actor_id=user["id"], action="member.join_code",
            workspace_id=workspace["id"], target=user["email"], request=request,
        )
        conn.commit()
    return _set_active(
        JSONResponse({"ok": True, "workspace": {"id": workspace["id"], "name": workspace["name"]}}),
        workspace["id"],
    )


@router.post("/personal")
def create_personal_workspace(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    """Crea (o recupera) la cuenta individual del usuario.

    Un alumno de academia no tiene espacio personal; si quiere generar unidades
    para sí mismo, lo crea de forma explícita. Dentro de la academia sigue
    siendo estudiante.
    """
    ensure_csrf(request, user)
    existing = workspaces.personal_workspace_id(conn, user["id"])
    workspace_id = workspaces.ensure_personal_workspace(conn, user["id"], user["name"])
    if existing is None:
        audit.record(
            conn, actor_id=user["id"], action="workspace.personal",
            workspace_id=workspace_id, target=user["email"], request=request,
        )
    conn.commit()
    workspace = workspaces.get_workspace(conn, workspace_id)
    return _set_active(JSONResponse({"ok": True, "workspace": workspace}), workspace_id)
