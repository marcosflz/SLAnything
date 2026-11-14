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
    conn: sqlite3.Connection = Depends(get_db),
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
    conn: sqlite3.Connection = Depends(get_db),
):
    """Unirse a una academia como estudiante con su código de clase."""
    ensure_csrf(request, user)
    workspace = workspaces.get_workspace_by_join_code(conn, body.code)
    if workspace is None or workspace["kind"] != "organization":
        raise HTTPException(
            status_code=404,
            detail=translate("Código de clase no válido.", request_lang(request)),
        )
    if workspaces.membership(conn, workspace["id"], user["id"]) is None:
        limit = workspace.get("seat_limit")
        if limit and workspaces.seat_count(conn, workspace["id"]) >= limit:
            raise HTTPException(
                status_code=409,
                detail=translate("La academia no tiene plazas libres.", request_lang(request)),
            )
        workspaces.add_member(conn, workspace["id"], user["id"], "student")
        audit.record(
            conn, actor_id=user["id"], action="member.join_code",
            workspace_id=workspace["id"], target=user["email"], request=request,
        )
        conn.commit()
    return _set_active(
        JSONResponse({"ok": True, "workspace": {"id": workspace["id"], "name": workspace["name"]}}),
        workspace["id"],
    )
