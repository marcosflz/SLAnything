"""Persistencia de trabajos del Estudio y cursos generados.

La tabla guarda el paquete JSON tal cual lo produjo OpenCode, no objetos Python.
Así se puede auditar, exportar o volver a validar sin ejecutar nada del modelo.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Any

from webapp import config
from webapp.authoring.package import ParsedPackage, parse_package
from webapp.db import connect, utcnow

logger = logging.getLogger("aula.authoring")

ACTIVE_STATUSES = {"queued", "extracting", "generating", "validating"}
STATUS_LABELS = {
    "queued": "En cola",
    "extracting": "Extrayendo texto",
    "generating": "Generando unidad",
    "validating": "Validando",
    "ready": "Lista para revisar",
    "failed": "Error",
    "cancelled": "Cancelada",
}

_cache_lock = threading.Lock()
_parsed_cache: dict[str, tuple[str, list[ParsedPackage]]] = {}


def reset_cache() -> None:
    with _cache_lock:
        _parsed_cache.clear()


def ensure_dir() -> Path:
    config.AUTHORING_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config.AUTHORING_DIR.chmod(0o700)
    except OSError:
        pass
    return config.AUTHORING_DIR


def job_dir(job_id: str) -> Path:
    safe = "".join(char for char in job_id if char.isalnum() or char in "-_")
    return ensure_dir() / "jobs" / safe


def log_path(job_id: str) -> Path:
    return job_dir(job_id) / "run.log"


def _row_to_job(row: sqlite3.Row, with_log: bool = True) -> dict[str, Any]:
    try:
        source_names = json.loads(row["source_names"])
    except (TypeError, json.JSONDecodeError):
        source_names = []
    try:
        languages = json.loads(row["languages"])
    except (TypeError, json.JSONDecodeError):
        languages = ["es"]
    payload = {
        "id": row["id"],
        "title": row["title"],
        "source_names": source_names,
        "status": row["status"],
        "status_label": STATUS_LABELS.get(row["status"], row["status"]),
        "provider": row["provider"],
        "model": row["model"],
        "languages": languages,
        "course_slug": row["course_slug"],
        "error": row["error"],
        "created_at": row["created_at"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "active": row["status"] in ACTIVE_STATUSES,
        "log": tail_log(row["id"]) if with_log else "",
    }
    return payload


def _row_to_course(row: sqlite3.Row, with_package: bool = False) -> dict[str, Any]:
    package = json.loads(row["package_json"])
    try:
        parsed = parse_package(package)
        summary = parsed.summary
    except ValueError as exc:
        logger.warning("Curso generado inválido %s: %s", row["slug"], exc)
        summary = {
            "slug": row["slug"],
            "languages": [],
            "titles": {"es": row["title"]},
            "chapter_count": 0,
            "lesson_count": 0,
            "quiz_count": 0,
            "glossary_count": 0,
            "tags": [],
            "book": None,
        }
    payload = {
        "slug": row["slug"],
        "title": row["title"],
        "status": row["status"],
        "job_id": row["job_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "summary": summary,
    }
    if with_package:
        payload["package"] = package
    return payload


def create_job(
    *,
    job_id: str,
    owner_id: int,
    title: str,
    source_names: list[str],
    provider: str,
    model: str,
    languages: list[str],
) -> None:
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO authoring_jobs
                   (id, owner_id, title, source_names, status, provider, model,
                    languages, created_at)
               VALUES (?, ?, ?, ?, 'queued', ?, ?, ?, ?)""",
            (
                job_id,
                owner_id,
                title[:200],
                json.dumps(source_names, ensure_ascii=False),
                provider,
                model,
                json.dumps(languages),
                utcnow(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def update_job(job_id: str, **fields: Any) -> None:
    allowed = {
        "status",
        "course_slug",
        "error",
        "started_at",
        "finished_at",
        "provider",
        "model",
    }
    updates = {key: value for key, value in fields.items() if key in allowed}
    if not updates:
        return
    conn = connect()
    try:
        assignments = ", ".join(f"{key} = ?" for key in updates)
        conn.execute(
            f"UPDATE authoring_jobs SET {assignments} WHERE id = ?",
            [*updates.values(), job_id],
        )
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: str) -> dict[str, Any] | None:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM authoring_jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return _row_to_job(row) if row else None
    finally:
        conn.close()


def list_jobs(
    owner_id: int | None = None,
    limit: int = 30,
    with_log: bool = True,
) -> list[dict[str, Any]]:
    conn = connect()
    try:
        if owner_id is None:
            rows = conn.execute(
                "SELECT * FROM authoring_jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM authoring_jobs
                   WHERE owner_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (owner_id, limit),
            ).fetchall()
        return [_row_to_job(row, with_log=with_log) for row in rows]
    finally:
        conn.close()


def count_active_jobs(owner_id: int) -> int:
    conn = connect()
    try:
        row = conn.execute(
            """SELECT COUNT(*) AS n FROM authoring_jobs
               WHERE owner_id = ? AND status IN
                     ('queued', 'extracting', 'generating', 'validating')""",
            (owner_id,),
        ).fetchone()
        return int(row["n"]) if row else 0
    finally:
        conn.close()


def mark_interrupted_jobs() -> int:
    conn = connect()
    try:
        cursor = conn.execute(
            """UPDATE authoring_jobs
               SET status = 'failed',
                   error = 'El servidor se reinició mientras la unidad se generaba. Vuelve a intentarlo.',
                   finished_at = ?
               WHERE status IN ('queued', 'extracting', 'generating', 'validating')""",
            (utcnow(),),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def save_generated_course(
    *,
    slug: str,
    owner_id: int,
    job_id: str | None,
    title: str,
    package: dict[str, Any],
    status: str = "draft",
) -> None:
    now = utcnow()
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO generated_courses
                   (slug, owner_id, job_id, title, status, package_json,
                    created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(slug) DO UPDATE SET
                   title = excluded.title,
                   package_json = excluded.package_json,
                   updated_at = excluded.updated_at""",
            (
                slug,
                owner_id,
                job_id,
                title[:200],
                status,
                json.dumps(package, ensure_ascii=False),
                now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    reset_cache()


def unique_course_slug(base_slug: str) -> str:
    conn = connect()
    try:
        candidate = base_slug
        suffix = 2
        while conn.execute(
            "SELECT 1 FROM generated_courses WHERE slug = ?", (candidate,)
        ).fetchone():
            candidate = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate
    finally:
        conn.close()


def get_course(slug: str, with_package: bool = False) -> dict[str, Any] | None:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT * FROM generated_courses WHERE slug = ?", (slug,)
        ).fetchone()
        return _row_to_course(row, with_package) if row else None
    finally:
        conn.close()


def list_courses(status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    conn = connect()
    try:
        if status is None:
            rows = conn.execute(
                "SELECT * FROM generated_courses ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM generated_courses
                   WHERE status = ? ORDER BY updated_at DESC LIMIT ?""",
                (status, limit),
            ).fetchall()
        return [_row_to_course(row) for row in rows]
    finally:
        conn.close()


def set_course_status(slug: str, status: str) -> bool:
    if status not in {"draft", "published"}:
        raise ValueError("Estado de curso no válido.")
    conn = connect()
    try:
        cursor = conn.execute(
            "UPDATE generated_courses SET status = ?, updated_at = ? WHERE slug = ?",
            (status, utcnow(), slug),
        )
        conn.commit()
        changed = cursor.rowcount > 0
    finally:
        conn.close()
    reset_cache()
    return changed


def delete_course(slug: str) -> bool:
    conn = connect()
    try:
        cursor = conn.execute("DELETE FROM generated_courses WHERE slug = ?", (slug,))
        conn.commit()
        changed = cursor.rowcount > 0
    finally:
        conn.close()
    reset_cache()
    return changed


def _published_rows(lang: str) -> list[sqlite3.Row]:
    conn = connect()
    try:
        return conn.execute(
            """SELECT * FROM generated_courses
               WHERE status = 'published'
               ORDER BY created_at ASC"""
        ).fetchall()
    finally:
        conn.close()


def dynamic_content(lang: str) -> tuple[list[Any], dict[str, Any], tuple[Any, ...]]:
    """Cursos, quizzes y glosario publicados para un idioma.

    Se cachea por ``(slug, updated_at)``; publicar o despublicar invalida la
    entrada. Si un paquete guardado deja de validar se ignora y se registra.
    """
    try:
        rows = _published_rows(lang)
    except sqlite3.OperationalError:
        return [], {}, ()
    if not rows:
        with _cache_lock:
            _parsed_cache.pop(f"{lang}:{config.DB_PATH}", None)
        return [], {}, ()
    version = "|".join(f"{row['slug']}:{row['updated_at']}" for row in rows)
    cache_key = f"{lang}:{config.DB_PATH}"
    with _cache_lock:
        cached = _parsed_cache.get(cache_key)
        parsed_packages = list(cached[1]) if cached and cached[0] == version else []
    if not parsed_packages:
        parsed_packages = []
        for row in rows:
            try:
                parsed_packages.append(
                    parse_package(json.loads(row["package_json"]))
                )
            except (ValueError, json.JSONDecodeError) as exc:
                logger.warning("Se ignora el curso generado %s: %s", row["slug"], exc)
        with _cache_lock:
            _parsed_cache[cache_key] = (version, list(parsed_packages))

    courses = []
    quizzes: dict[str, Any] = {}
    glossary: list[Any] = []
    for parsed in parsed_packages:
        course = parsed.course_for(lang)
        if course is None:
            continue
        courses.append(course)
        quizzes.update(parsed.quizzes.get(lang, {}))
        glossary.extend(parsed.glossaries.get(lang, ()))
    return courses, quizzes, tuple(glossary)


def tail_log(job_id: str, limit: int = 14_000) -> str:
    path = log_path(job_id)
    if not path.is_file():
        return ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(max(0, size - limit))
            return handle.read()
    except OSError:
        return ""
