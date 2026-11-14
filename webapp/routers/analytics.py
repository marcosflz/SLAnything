"""Eventos de aprendizaje y paneles de KPIs (alumno, profesorado y admin)."""

from __future__ import annotations

import csv
import io
import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from webapp import analytics, workspaces
from webapp.db import get_db
from webapp.deps import require_admin, require_teacher, require_user
from webapp.routers.api import _bundle
from webapp.security import csrf_matches

router = APIRouter(prefix="/api/v1", tags=["analytics"])


class EventsBody(BaseModel):
    events: list[dict] = Field(default_factory=list, max_length=50)
    csrf_token: str = ""


@router.post("/events")
async def ingest_events(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Lote de eventos del navegador.

    ``navigator.sendBeacon`` no puede poner cabeceras, así que el token CSRF
    también se admite dentro del cuerpo JSON.
    """
    try:
        raw = json.loads(await request.body() or b"{}")
        body = EventsBody.model_validate(raw)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="Lote de eventos no válido.") from exc
    supplied = request.headers.get("X-CSRF-Token") or body.csrf_token
    if not csrf_matches(user.get("csrf_token", ""), supplied):
        raise HTTPException(status_code=403, detail="Token de seguridad inválido o caducado.")
    stored = analytics.record_client_events(conn, user["id"], body.events)
    conn.commit()
    return {"ok": True, "stored": stored}


@router.get("/analytics/me")
def my_analytics(
    request: Request,
    user: dict = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    bundle = _bundle(request)
    course = bundle.course
    return {
        "course": {"slug": course.slug, "title": course.title},
        **analytics.student_kpis(conn, user["id"], course, bundle.quizzes),
    }


def _students(conn: sqlite3.Connection, user: dict, group_id: int | None) -> list[dict]:
    workspace_id = user["workspace"]["id"]
    students = workspaces.members(conn, workspace_id, role="student")
    if group_id is not None:
        group = conn.execute(
            "SELECT id FROM groups WHERE id = ? AND workspace_id = ?", (group_id, workspace_id)
        ).fetchone()
        if group is None:
            raise HTTPException(status_code=404, detail="Grupo no encontrado.")
        in_group = {
            row[0]
            for row in conn.execute(
                "SELECT user_id FROM group_members WHERE group_id = ?", (group_id,)
            )
        }
        students = [student for student in students if student["id"] in in_group]
    return students


def _course_report(request: Request, user: dict, conn, group: int | None, days: int) -> dict:
    bundle = _bundle(request)
    course = bundle.course
    report = analytics.course_analytics(
        conn, _students(conn, user, group), course, bundle.quizzes, days=max(7, min(days, 180))
    )
    groups = [
        dict(row)
        for row in conn.execute(
            "SELECT id, name FROM groups WHERE workspace_id = ? ORDER BY name",
            (user["workspace"]["id"],),
        )
    ]
    return {
        "course": {"slug": course.slug, "title": course.title},
        "courses": [
            {"slug": item.slug, "title": item.title} for item in bundle.published_catalog
        ],
        "groups": groups,
        "group": group,
        "days": days,
        **report,
    }


@router.get("/analytics/course")
def course_analytics(
    request: Request,
    group: int | None = None,
    days: int = 30,
    user: dict = Depends(require_teacher),
    conn: sqlite3.Connection = Depends(get_db),
):
    return _course_report(request, user, conn, group, days)


@router.get("/analytics/course.csv")
def course_analytics_csv(
    request: Request,
    group: int | None = None,
    days: int = 30,
    user: dict = Depends(require_teacher),
    conn: sqlite3.Connection = Depends(get_db),
):
    report = _course_report(request, user, conn, group, days)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["student", "completion_pct", "avg_score", "minutes", "last_seen", "risk"]
    )
    for row in report["students"]:
        writer.writerow(
            [
                row["name"],
                row["completion"],
                "" if row["avg_score"] is None else row["avg_score"],
                row["minutes"],
                row["last_seen"] or "",
                "|".join(row["risk"]),
            ]
        )
    filename = f"analitica-{report['course']['slug']}.csv"
    return PlainTextResponse(
        buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/admin/metrics")
def admin_metrics(
    user: dict = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_db),
):
    return {
        "workspace": user["workspace"],
        **analytics.workspace_metrics(conn, user["workspace"]["id"]),
    }
