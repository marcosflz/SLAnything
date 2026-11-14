"""Estudio de autoría: ajustes, subida de documentos y publicación.

La API JSON es la que consume Next.js.
"""

from __future__ import annotations

import asyncio
import json
import secrets
import shutil
from pathlib import Path
from typing import Any, Literal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from webapp import audit, config, workspaces
from webapp.authoring import extract, providers, runner, settings, store
from webapp.authoring.package import parse_package, slugify
from webapp.db import session_scope
from webapp.deps import ensure_csrf, require_author, require_platform_admin
from webapp.generation import document as gen_document
from webapp.generation import pipeline, worker
from webapp.i18n import request_lang, translate

router = APIRouter(prefix="/api/v1/authoring", tags=["authoring"])


class SettingsBody(BaseModel):
    provider: str
    model: str
    base_url: str = ""
    api_key: str | None = None
    clear_key: bool = False


def _error(message: str, status_code: int = 400) -> HTTPException:
    return HTTPException(status_code=status_code, detail=message)


def _safe_filename(name: str | None, index: int) -> str:
    raw = Path(name or f"documento-{index}").name
    raw = "".join(char for char in raw if char.isalnum() or char in " ._-()[]")
    raw = raw.strip().replace(" ", "_")[:120] or f"documento-{index}"
    if not Path(raw).suffix:
        raw += ".txt"
    return f"{index:02d}-{raw}"


def _languages(value: str | list[str]) -> list[str]:
    values = value if isinstance(value, list) else [value]
    result: list[str] = []
    for raw in values:
        for item in str(raw).replace(";", ",").split(","):
            item = item.strip().lower()
            if item in {"es", "en"} and item not in result:
                result.append(item)
    return result or ["es"]


def _ws_id(user: dict) -> int | None:
    workspace = user.get("workspace")
    return workspace["id"] if workspace else None


def _can_manage(user: dict, item: dict) -> bool:
    """Autor del recurso o admin/owner del espacio al que pertenece."""
    if item.get("workspace_id") not in (None, _ws_id(user)):
        return False
    if item.get("workspace_id") is None:
        return workspaces.role_at_least(user.get("ws_role"), "admin")
    return item.get("owner_id") == user["id"] or workspaces.role_at_least(
        user.get("ws_role"), "admin"
    )


def _job_for(job_id: str, user: dict) -> dict[str, Any]:
    job = store.get_job(job_id)
    if job is None or not _can_manage(user, job):
        raise _error("Trabajo no encontrado.", 404)
    return job


def _course_for(slug: str, user: dict, with_package: bool = False) -> dict[str, Any]:
    course = store.get_course(slug, with_package=with_package)
    if course is None or not _can_manage(user, course):
        raise _error("Curso generado no encontrado.", 404)
    return course


def _visible_jobs(user: dict) -> list[dict[str, Any]]:
    owner = None if workspaces.role_at_least(user.get("ws_role"), "admin") else user["id"]
    return store.list_jobs(owner_id=owner, workspace_id=_ws_id(user))


def _visible_courses(user: dict) -> list[dict[str, Any]]:
    courses = store.list_courses(workspace_id=_ws_id(user))
    return [course for course in courses if _can_manage(user, course)]


def _payload(user: dict) -> dict[str, Any]:
    return {
        "settings": settings.public_settings(),
        "jobs": _visible_jobs(user),
        "courses": _visible_courses(user),
        "can_configure": bool(user.get("is_platform_admin")),
        "default_engine": config.GEN_DEFAULT_ENGINE,
        "quota": _quota(user),
        "limits": {
            "max_upload_mb": config.AUTHORING_MAX_UPLOAD_MB,
            "max_files": config.AUTHORING_MAX_FILES,
            "max_chars": config.AUTHORING_MAX_CHARS,
            "timeout_seconds": config.AUTHORING_TIMEOUT,
            "max_active_jobs": config.AUTHORING_MAX_JOBS,
        },
    }


def _quota(user: dict) -> dict[str, Any]:
    """Cuota mensual del espacio: la fijada por la plataforma o la global."""
    workspace = user.get("workspace") or {}
    limit = (
        config.GEN_MONTHLY_ORGANIZATION
        if workspace.get("kind") == "organization"
        else config.GEN_MONTHLY_PERSONAL
    )
    if workspace.get("id") is not None:
        with session_scope() as conn:
            stored = workspaces.get_workspace(conn, int(workspace["id"]))
        custom = ((stored or {}).get("settings") or {}).get("gen_monthly")
        if isinstance(custom, int) and custom >= 0:
            limit = custom
    used = store.jobs_this_month(workspace.get("id"))
    return {"limit": limit, "used": used, "remaining": max(0, limit - used)}


def _assert_ready_direct(user: dict) -> None:
    quota = _quota(user)
    if quota["remaining"] <= 0:
        raise _error(
            f"Has alcanzado el límite de {quota['limit']} generaciones este mes en este espacio.",
            429,
        )
    if store.count_active_jobs(user["id"]) >= config.AUTHORING_MAX_JOBS:
        raise _error(
            "Ya hay varios trabajos en marcha. Espera a que terminen antes de subir otro documento.",
            429,
        )
    if config.LLM_FAKE:
        return
    current = settings.load_settings()
    provider = providers.provider(current["provider"])
    if provider.requires_key and not str(current.get("api_key") or "").strip():
        raise _error(
            "La plataforma todavía no tiene configurado un proveedor de IA. Pide a la administración que lo configure.",
            400,
        )


def _assert_ready(user: dict) -> None:
    info = settings.engine_status()
    if not info.get("enabled"):
        raise _error(info.get("message") or "El Estudio está desactivado.", 503)
    if not info.get("available"):
        raise _error(info.get("message") or "OpenCode no está disponible.", 503)
    current = settings.load_settings()
    provider = providers.provider(current["provider"])
    if provider.requires_key and not str(current.get("api_key") or "").strip():
        raise _error(
            "Configura la API key del proveedor antes de generar una unidad.", 400
        )
    if store.count_active_jobs(user["id"]) >= config.AUTHORING_MAX_JOBS:
        raise _error(
            "Ya hay varios trabajos en marcha. Espera a que terminen antes de subir otro documento.",
            429,
        )


async def _save_uploads(job_id: str, files: list[UploadFile]) -> list[str]:
    if not files:
        raise ValueError("Sube al menos un documento.")
    if len(files) > config.AUTHORING_MAX_FILES:
        raise ValueError(
            f"Puedes subir como máximo {config.AUTHORING_MAX_FILES} documentos por unidad."
        )
    destination = runner.uploads_dir(job_id)
    max_bytes = config.AUTHORING_MAX_UPLOAD_MB * 1024 * 1024
    total_max = max_bytes * config.AUTHORING_MAX_FILES
    total = 0
    names: list[str] = []
    try:
        for index, upload in enumerate(files, start=1):
            filename = _safe_filename(upload.filename, index)
            suffix = Path(filename).suffix.lower()
            if suffix not in extract.SUPPORTED_EXTENSIONS:
                raise ValueError(
                    f"{upload.filename!r}: formato no admitido. Usa PDF, DOCX, "
                    "EPUB, ODT, Markdown, HTML o TXT."
                )
            target = destination / filename
            size = 0
            with target.open("wb") as handle:
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    total += len(chunk)
                    if size > max_bytes:
                        raise ValueError(
                            f"{upload.filename!r} supera el límite de "
                            f"{config.AUTHORING_MAX_UPLOAD_MB} MB."
                        )
                    if total > total_max:
                        raise ValueError("La subida completa es demasiado grande.")
                    handle.write(chunk)
            if size == 0:
                raise ValueError(f"{upload.filename!r} está vacío.")
            names.append(filename)
            await upload.close()
        return names
    except Exception:
        shutil.rmtree(store.job_dir(job_id), ignore_errors=True)
        raise


async def _create_job(
    *,
    user: dict,
    files: list[UploadFile],
    title: str,
    desired_slug: str,
    languages: str | list[str],
    notes: str,
    engine: str = "opencode",
) -> dict[str, Any]:
    if engine == "direct":
        _assert_ready_direct(user)
    else:
        _assert_ready(user)
    current = settings.load_settings()
    lang_list = _languages(languages)
    clean_title = (title or "").strip()[:200]
    if not clean_title and files:
        clean_title = Path(files[0].filename or "documento").stem.replace("_", " ")[:200]
    if not clean_title:
        raise _error("Pon un título a la unidad.")
    job_id = secrets.token_urlsafe(12)
    names = await _save_uploads(job_id, files)
    meta = {
        "title": clean_title,
        "slug": slugify(desired_slug) if desired_slug.strip() else slugify(clean_title),
        "languages": lang_list,
        "notes": notes.strip()[:2000],
        "source_names": names,
    }
    store.create_job(
        job_id=job_id,
        owner_id=user["id"],
        workspace_id=_ws_id(user),
        title=clean_title,
        source_names=names,
        provider=current["provider"],
        model=current["model"],
        languages=lang_list,
        engine=engine,
        job_config={k: meta[k] for k in ("title", "slug", "languages", "notes")},
    )
    runner.write_meta(job_id, meta)
    if engine == "direct":
        worker.submit(job_id, "analyze")
    else:
        runner.submit_job(job_id)
    job = store.get_job(job_id)
    return job or {"id": job_id}


# ---------------------------------------------------------------------------
# API JSON
# ---------------------------------------------------------------------------

@router.get("")
def authoring_home(user: dict = Depends(require_author)):
    return _payload(user)


@router.get("/settings")
def get_settings(user: dict = Depends(require_author)):
    return settings.public_settings()


@router.put("/settings")
def update_settings(
    body: SettingsBody,
    request: Request,
    user: dict = Depends(require_platform_admin),
):
    ensure_csrf(request, user)
    try:
        updated = settings.save_settings(
            provider=body.provider,
            model=body.model,
            base_url=body.base_url,
            api_key=body.api_key,
            clear_key=body.clear_key,
        )
    except ValueError as exc:
        raise _error(str(exc)) from exc
    return updated


@router.get("/jobs")
def list_jobs(user: dict = Depends(require_author)):
    return {"jobs": _visible_jobs(user)}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user: dict = Depends(require_author)):
    return _job_for(job_id, user)


@router.post("/jobs", status_code=202)
async def create_job(
    request: Request,
    title: str = Form(""),
    slug: str = Form(""),
    languages: list[str] = Form(["es", "en"]),
    notes: str = Form(""),
    engine: str = Form(""),
    files: list[UploadFile] = File(...),
    user: dict = Depends(require_author),
):
    ensure_csrf(request, user)
    chosen = engine if engine in {"direct", "opencode"} else config.GEN_DEFAULT_ENGINE
    try:
        return await _create_job(
            user=user,
            files=files,
            title=title,
            desired_slug=slug,
            languages=languages,
            notes=notes,
            engine=chosen,
        )
    except ValueError as exc:
        raise _error(str(exc)) from exc


@router.post("/jobs/{job_id}/cancel")
def cancel_job(
    job_id: str,
    request: Request,
    user: dict = Depends(require_author),
):
    ensure_csrf(request, user)
    job = _job_for(job_id, user)
    if job.get("engine") == "direct":
        if job["status"] in {"ready", "failed", "cancelled"}:
            raise _error("El trabajo ya ha terminado.", 409)
        store.update_job(job_id, status="cancelled", finished_at=pipeline.utcnow())
        pipeline.emit(job_id, "cancelled", "Generación cancelada.")
        return {"ok": True}
    if not runner.cancel_job(job_id):
        raise _error("El trabajo ya ha terminado.", 409)
    return {"ok": True}


@router.get("/courses")
def list_generated(user: dict = Depends(require_author)):
    return {"courses": _visible_courses(user)}


@router.get("/courses/{slug}")
def get_generated(slug: str, user: dict = Depends(require_author)):
    return _course_for(slug, user, with_package=True)


class PublishBody(BaseModel):
    visibility: Literal["workspace", "public"] = "workspace"


@router.post("/courses/{slug}/publish")
def publish_course(
    slug: str,
    request: Request,
    body: PublishBody | None = None,
    user: dict = Depends(require_author),
):
    ensure_csrf(request, user)
    course = _course_for(slug, user, with_package=True)
    visibility = (body or PublishBody()).visibility
    if visibility == "public" and not user.get("is_platform_admin"):
        # Publicar en el catálogo abierto de la plataforma requiere revisión.
        raise _error("Solo la administración de la plataforma puede publicar en abierto.", 403)
    store.set_course_visibility(slug, visibility)
    try:
        parse_package(course.get("package") or {})
    except ValueError as exc:
        raise _error(f"El paquete no es válido: {exc}") from exc
    store.set_course_status(slug, "published")
    audit.record(
        None, actor_id=user["id"], action="course.publish",
        workspace_id=course.get("workspace_id"), target=slug, request=request,
    )
    return store.get_course(slug)


@router.post("/courses/{slug}/unpublish")
def unpublish_course(
    slug: str,
    request: Request,
    user: dict = Depends(require_author),
):
    ensure_csrf(request, user)
    course = _course_for(slug, user)
    store.set_course_status(slug, "draft")
    audit.record(
        None, actor_id=user["id"], action="course.unpublish",
        workspace_id=course.get("workspace_id"), target=slug, request=request,
    )
    return store.get_course(slug)


@router.delete("/courses/{slug}")
def delete_generated(
    slug: str,
    request: Request,
    user: dict = Depends(require_author),
):
    ensure_csrf(request, user)
    course = _course_for(slug, user)
    store.delete_course(slug)
    audit.record(
        None, actor_id=user["id"], action="course.delete",
        workspace_id=course.get("workspace_id"), target=slug, request=request,
    )
    return {"ok": True}


# ---------------------------------------------------------------------------
# Motor por etapas · alcance, temario, generación y progreso
# ---------------------------------------------------------------------------

class PlanBody(BaseModel):
    scope: list[str] = Field(min_length=1, max_length=40)
    level: str = Field(default="Intermedio", max_length=60)
    lessons_per_chapter: int | None = Field(default=None, ge=2, le=12)
    minutes_per_lesson: int = Field(default=12, ge=5, le=40)
    questions_per_chapter: int = Field(default=10, ge=4, le=20)
    question_kinds: list[Literal["single", "multiple", "true_false"]] = Field(
        default_factory=lambda: ["single", "multiple", "true_false"], min_length=1
    )
    tone: str = Field(default="cercano y riguroso", max_length=120)
    code_examples: bool = False
    auto_approve: bool = False
    notes: str = Field(default="", max_length=2000)


class OutlineBody(BaseModel):
    outline: dict


class PackageBody(BaseModel):
    package: dict


class RegenerateBody(BaseModel):
    chapter: int = Field(ge=1)
    lesson: int = Field(ge=1)
    instructions: str = Field(default="", max_length=1500)


def _direct_job(job_id: str, user: dict) -> dict[str, Any]:
    job = _job_for(job_id, user)
    if job.get("engine") != "direct":
        raise _error("Este trabajo usa el motor OpenCode y no tiene etapas.", 409)
    return job


@router.get("/jobs/{job_id}/document")
def job_document(job_id: str, user: dict = Depends(require_author)):
    _direct_job(job_id, user)
    path = pipeline.job_path(job_id, "document.json")
    if not path.is_file():
        raise _error("El documento todavía se está analizando.", 409)
    return gen_document.public_outline(gen_document.load(path))


@router.post("/jobs/{job_id}/plan", status_code=202)
def plan_job(job_id: str, body: PlanBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    job = _direct_job(job_id, user)
    if job["status"] not in {"awaiting_scope", "awaiting_outline", "failed"}:
        raise _error("El trabajo no está esperando la selección de contenido.", 409)
    if not pipeline.job_path(job_id, "document.json").is_file():
        raise _error("El documento todavía no se ha analizado.", 409)
    options = {**(job.get("config") or {}), **body.model_dump()}
    if body.notes:
        options["notes"] = body.notes
    store.update_job(job_id, config_json=json.dumps(options, ensure_ascii=False), status="outlining")
    # Un temario nuevo invalida lo generado con el anterior.
    for folder in ("lessons", "assess"):
        shutil.rmtree(pipeline.job_path(job_id, folder), ignore_errors=True)
    worker.submit(job_id, "plan")
    return store.get_job(job_id, with_log=False)


@router.get("/jobs/{job_id}/outline")
def get_outline(job_id: str, user: dict = Depends(require_author)):
    _direct_job(job_id, user)
    if not pipeline.job_path(job_id, "outline.json").is_file():
        raise _error("El temario todavía no está listo.", 409)
    return pipeline.load_outline(job_id)


@router.put("/jobs/{job_id}/outline")
def put_outline(job_id: str, body: OutlineBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    job = _direct_job(job_id, user)
    if job["status"] != "awaiting_outline":
        raise _error("Solo se puede editar el temario antes de generar.", 409)
    try:
        return pipeline.save_outline(job_id, body.outline)
    except ValueError as exc:
        raise _error(str(exc)) from exc


@router.post("/jobs/{job_id}/generate", status_code=202)
def generate_job(job_id: str, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    job = _direct_job(job_id, user)
    if job["status"] not in {"awaiting_outline", "failed"}:
        raise _error("El temario no está listo para generar.", 409)
    if not pipeline.job_path(job_id, "outline.json").is_file():
        raise _error("Falta el temario.", 409)
    store.update_job(job_id, status="generating", error=None, finished_at=None)
    worker.submit(job_id, "generate")
    return store.get_job(job_id, with_log=False)


@router.post("/jobs/{job_id}/retry", status_code=202)
def retry_job(job_id: str, request: Request, user: dict = Depends(require_author)):
    """Reanuda un trabajo fallido desde la última etapa completada."""
    ensure_csrf(request, user)
    job = _direct_job(job_id, user)
    if job["status"] not in {"failed", "cancelled"}:
        raise _error("Solo se reintentan trabajos fallidos o cancelados.", 409)
    if pipeline.job_path(job_id, "outline.json").is_file():
        store.update_job(job_id, status="generating", error=None, finished_at=None)
        worker.submit(job_id, "generate")
    elif pipeline.job_path(job_id, "document.json").is_file():
        store.update_job(job_id, status="awaiting_scope", error=None, finished_at=None)
    else:
        store.update_job(job_id, status="queued", error=None, finished_at=None)
        worker.submit(job_id, "analyze")
    return store.get_job(job_id, with_log=False)


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str, request: Request, user: dict = Depends(require_author)):
    """Progreso en directo (Server-Sent Events): eventos + estado del trabajo."""
    _direct_job(job_id, user)

    async def stream():
        offset = 0
        last_status = None
        idle = 0
        while idle < 900:  # ~15 min sin cambios: el navegador reconecta solo
            if await request.is_disconnected():
                break
            events, offset_new = pipeline.read_events(job_id, offset)
            changed = bool(events)
            offset = offset_new
            for event in events:
                yield f"event: log\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
            job = store.get_job(job_id, with_log=False)
            if job is None:
                break
            status = (job["status"], json.dumps(job.get("progress"), sort_keys=True))
            if status != last_status:
                last_status = status
                changed = True
                payload = {k: job[k] for k in ("status", "status_label", "stage", "progress", "error", "course_slug", "tokens_in", "tokens_out")}
                yield f"event: job\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
            idle = 0 if changed else idle + 1
            if not changed:
                yield ": keep-alive\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/jobs/{job_id}/history")
def job_history(job_id: str, user: dict = Depends(require_author)):
    _direct_job(job_id, user)
    events, _ = pipeline.read_events(job_id)
    return {"events": events[-200:]}


@router.put("/courses/{slug}/package")
def update_package(slug: str, body: PackageBody, request: Request, user: dict = Depends(require_author)):
    """Guarda las ediciones del revisor. El paquete se valida entero."""
    ensure_csrf(request, user)
    course = _course_for(slug, user, with_package=True)
    try:
        parse_package(body.package, slug_override=slug)
    except ValueError as exc:
        raise _error(f"El paquete no es válido: {exc}") from exc
    store.save_generated_course(
        slug=slug,
        owner_id=int(course["owner_id"]),
        job_id=course.get("job_id"),
        title=course["title"],
        package=body.package,
    )
    audit.record(
        None, actor_id=user["id"], action="course.edit",
        workspace_id=course.get("workspace_id"), target=slug, request=request,
    )
    return store.get_course(slug, with_package=True)


@router.post("/courses/{slug}/regenerate", status_code=202)
def regenerate(slug: str, body: RegenerateBody, request: Request, user: dict = Depends(require_author)):
    ensure_csrf(request, user)
    course = _course_for(slug, user)
    job_id = course.get("job_id")
    job = store.get_job(job_id, with_log=False) if job_id else None
    if job is None or job.get("engine") != "direct":
        raise _error("Solo se pueden regenerar lecciones de unidades del motor por etapas.", 409)
    if not worker.submit(job_id, "regenerate", body.chapter, body.lesson, body.instructions):
        raise _error("Ya hay una tarea en marcha para esta unidad.", 409)
    return {"ok": True, "job_id": job_id}
