"""Estudio de autoría: ajustes, subida de documentos y publicación.

La API JSON es la que consume Next.js. Las rutas ``/estudio`` son el fallback
Jinja y usan los mismos servicios, para que las dos interfaces no diverjan.
"""

from __future__ import annotations

import secrets
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from webapp import config
from webapp.authoring import extract, providers, runner, settings, store
from webapp.authoring.package import parse_package, slugify
from webapp.deps import ensure_csrf, require_teacher
from webapp.i18n import request_lang, translate
from webapp.templating import render

router = APIRouter(prefix="/api/v1/authoring", tags=["authoring"])
pages = APIRouter()


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


def _payload() -> dict[str, Any]:
    return {
        "settings": settings.public_settings(),
        "jobs": store.list_jobs(),
        "courses": store.list_courses(),
        "limits": {
            "max_upload_mb": config.AUTHORING_MAX_UPLOAD_MB,
            "max_files": config.AUTHORING_MAX_FILES,
            "max_chars": config.AUTHORING_MAX_CHARS,
            "timeout_seconds": config.AUTHORING_TIMEOUT,
            "max_active_jobs": config.AUTHORING_MAX_JOBS,
        },
    }


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
) -> dict[str, Any]:
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
        title=clean_title,
        source_names=names,
        provider=current["provider"],
        model=current["model"],
        languages=lang_list,
    )
    runner.write_meta(job_id, meta)
    runner.submit_job(job_id)
    job = store.get_job(job_id)
    return job or {"id": job_id}


# ---------------------------------------------------------------------------
# API JSON
# ---------------------------------------------------------------------------

@router.get("")
def authoring_home(user: dict = Depends(require_teacher)):
    return _payload()


@router.get("/settings")
def get_settings(user: dict = Depends(require_teacher)):
    return settings.public_settings()


@router.put("/settings")
def update_settings(
    body: SettingsBody,
    request: Request,
    user: dict = Depends(require_teacher),
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
def list_jobs(user: dict = Depends(require_teacher)):
    return {"jobs": store.list_jobs()}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user: dict = Depends(require_teacher)):
    job = store.get_job(job_id)
    if job is None:
        raise _error("Trabajo no encontrado.", 404)
    return job


@router.post("/jobs", status_code=202)
async def create_job(
    request: Request,
    title: str = Form(""),
    slug: str = Form(""),
    languages: list[str] = Form(["es", "en"]),
    notes: str = Form(""),
    files: list[UploadFile] = File(...),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user)
    try:
        return await _create_job(
            user=user,
            files=files,
            title=title,
            desired_slug=slug,
            languages=languages,
            notes=notes,
        )
    except ValueError as exc:
        raise _error(str(exc)) from exc


@router.post("/jobs/{job_id}/cancel")
def cancel_job(
    job_id: str,
    request: Request,
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user)
    if store.get_job(job_id) is None:
        raise _error("Trabajo no encontrado.", 404)
    if not runner.cancel_job(job_id):
        raise _error("El trabajo ya ha terminado.", 409)
    return {"ok": True}


@router.get("/courses")
def list_generated(user: dict = Depends(require_teacher)):
    return {"courses": store.list_courses()}


@router.get("/courses/{slug}")
def get_generated(slug: str, user: dict = Depends(require_teacher)):
    course = store.get_course(slug, with_package=True)
    if course is None:
        raise _error("Curso generado no encontrado.", 404)
    return course


@router.post("/courses/{slug}/publish")
def publish_course(
    slug: str,
    request: Request,
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user)
    course = store.get_course(slug, with_package=True)
    if course is None:
        raise _error("Curso generado no encontrado.", 404)
    try:
        parsed = parse_package(course.get("package") or {})
    except ValueError as exc:
        raise _error(f"El paquete no es válido: {exc}") from exc
    store.set_course_status(slug, "published")
    return store.get_course(slug)


@router.post("/courses/{slug}/unpublish")
def unpublish_course(
    slug: str,
    request: Request,
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user)
    if not store.set_course_status(slug, "draft"):
        raise _error("Curso generado no encontrado.", 404)
    return store.get_course(slug)


@router.delete("/courses/{slug}")
def delete_generated(
    slug: str,
    request: Request,
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user)
    if not store.delete_course(slug):
        raise _error("Curso generado no encontrado.", 404)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Fallback Jinja · /estudio
# ---------------------------------------------------------------------------

@pages.get("/estudio")
def studio_page(
    request: Request,
    user: dict = Depends(require_teacher),
):
    payload = _payload()
    active_jobs = [job for job in payload["jobs"] if job.get("active")]
    return render(
        request,
        "pages/studio.html",
        settings=payload["settings"],
        jobs=payload["jobs"],
        courses=payload["courses"],
        engine=payload["settings"]["engine"],
        providers=payload["settings"]["providers"],
        active_jobs=active_jobs,
        limits=payload["limits"],
        sidebar_progress={},
    )


@pages.post("/estudio/settings")
def studio_save_settings(
    request: Request,
    csrf_token: str = Form(""),
    provider: str = Form("opencode-go"),
    model: str = Form(""),
    base_url: str = Form(""),
    api_key: str = Form(""),
    clear_key: str = Form("0"),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user, csrf_token)
    try:
        settings.save_settings(
            provider=provider,
            model=model,
            base_url=base_url,
            api_key=api_key or None,
            clear_key=clear_key == "1",
        )
        message = translate("Configuración guardada.", request_lang(request))
        return RedirectResponse(f"/estudio?ok={quote(message)}", status_code=303)
    except ValueError as exc:
        return RedirectResponse(f"/estudio?error={quote(str(exc))}", status_code=303)


@pages.post("/estudio/jobs")
async def studio_create_job(
    request: Request,
    csrf_token: str = Form(""),
    title: str = Form(""),
    slug: str = Form(""),
    languages: list[str] = Form(["es", "en"]),
    notes: str = Form(""),
    files: list[UploadFile] = File(...),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user, csrf_token)
    try:
        job = await _create_job(
            user=user,
            files=files,
            title=title,
            desired_slug=slug,
            languages=languages,
            notes=notes,
        )
        message = translate(
            "Trabajo creado. La unidad se generará en segundo plano.",
            request_lang(request),
        )
        return RedirectResponse(
            f"/estudio?ok={quote(message)}&job={quote(str(job.get('id', '')))}",
            status_code=303,
        )
    except (ValueError, HTTPException) as exc:
        detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
        return RedirectResponse(f"/estudio?error={quote(str(detail))}", status_code=303)


@pages.post("/estudio/jobs/{job_id}/cancelar")
def studio_cancel_job(
    job_id: str,
    request: Request,
    csrf_token: str = Form(""),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user, csrf_token)
    runner.cancel_job(job_id)
    message = translate("Generación cancelada.", request_lang(request))
    return RedirectResponse(f"/estudio?ok={quote(message)}", status_code=303)


@pages.post("/estudio/courses/{slug}/publicar")
def studio_publish(
    slug: str,
    request: Request,
    csrf_token: str = Form(""),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user, csrf_token)
    course = store.get_course(slug, with_package=True)
    if course is None:
        return RedirectResponse("/estudio?error=Curso%20no%20encontrado", status_code=303)
    try:
        parse_package(course.get("package") or {})
        store.set_course_status(slug, "published")
        message = translate("Unidad publicada en el catálogo.", request_lang(request))
        return RedirectResponse(f"/estudio?ok={quote(message)}", status_code=303)
    except ValueError as exc:
        return RedirectResponse(f"/estudio?error={quote(str(exc))}", status_code=303)


@pages.post("/estudio/courses/{slug}/despublicar")
def studio_unpublish(
    slug: str,
    request: Request,
    csrf_token: str = Form(""),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user, csrf_token)
    store.set_course_status(slug, "draft")
    message = translate("Unidad retirada del catálogo.", request_lang(request))
    return RedirectResponse(f"/estudio?ok={quote(message)}", status_code=303)


@pages.post("/estudio/courses/{slug}/eliminar")
def studio_delete(
    slug: str,
    request: Request,
    csrf_token: str = Form(""),
    user: dict = Depends(require_teacher),
):
    ensure_csrf(request, user, csrf_token)
    store.delete_course(slug)
    message = translate("Unidad eliminada.", request_lang(request))
    return RedirectResponse(f"/estudio?ok={quote(message)}", status_code=303)
