"""Ejecución aislada de OpenCode para convertir documentos en unidades.

OpenCode corre como subproceso con un ``opencode.json`` propio, un HOME privado y
permisos que le impiden usar shell, web o directorios externos. El resultado se
valida con ``package.parse_package`` antes de tocar el catálogo.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from webapp import config
from webapp.authoring import extract, providers, settings, store
from webapp.authoring.package import parse_package

logger = logging.getLogger("aula.authoring.runner")

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="authoring")
_active: dict[str, subprocess.Popen] = {}
_cancel: dict[str, threading.Event] = {}
_timed_out: set[str] = set()
_lock = threading.Lock()
MAX_LOG_BYTES = 2_000_000
_PROVIDER_ENV_VARS = {
    "OPENCODE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENROUTER_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GENERATIVE_AI_API_KEY",
    "GEMINI_API_KEY",
    "DEEPSEEK_API_KEY",
    "SLANYTHING_LLM_KEY",
    # No dejes que un OpenCode del host aporte su base de datos, su servicio o
    # credenciales guardadas al subproceso del Estudio.
    "OPENCODE_DB",
    "OPENCODE_CONFIG",
    "OPENCODE_CONFIG_CONTENT",
    "OPENCODE_PASSWORD",
    "OPENCODE_SERVER_PASSWORD",
}
_SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,})")


def _redact(value: str, key: str) -> str:
    if key:
        value = value.replace(key, "***")
    return _SECRET_RE.sub("sk-***", value)


def _log(job_id: str, message: str, key: str = "") -> None:
    path = store.log_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = _redact(message.rstrip() + "\n", key)
    try:
        if path.is_file() and path.stat().st_size > MAX_LOG_BYTES:
            return
        with path.open("a", encoding="utf-8") as handle:
            handle.write(safe)
    except OSError:
        logger.exception("No se pudo escribir el log del trabajo %s", job_id)


def uploads_dir(job_id: str) -> Path:
    path = store.job_dir(job_id) / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_meta(job_id: str, meta: dict[str, Any]) -> None:
    path = store.job_dir(job_id) / "meta.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def submit_job(job_id: str) -> None:
    with _lock:
        _cancel[job_id] = threading.Event()
        _timed_out.discard(job_id)
    _executor.submit(run_job, job_id)


def cancel_job(job_id: str) -> bool:
    with _lock:
        event = _cancel.get(job_id)
        process = _active.get(job_id)
        if event:
            event.set()
    if process and process.poll() is None:
        try:
            process.terminate()
        except OSError:
            pass
        return True
    if event:
        store.update_job(
            job_id,
            status="cancelled",
            finished_at=store.utcnow(),
            error="Generación cancelada.",
        )
        return True
    return False


def _terminate(process: subprocess.Popen, job_id: str, timed_out: bool = False) -> None:
    if timed_out:
        with _lock:
            _timed_out.add(job_id)
    try:
        process.terminate()
    except OSError:
        pass


def _minimal_env(extra: dict[str, str], job_id: str) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key not in _PROVIDER_ENV_VARS}
    home = config.AUTHORING_HOME
    home.mkdir(parents=True, exist_ok=True)
    data = home / ".local" / "share"
    conf = home / ".config"
    cache = home / ".cache"
    tmp = store.job_dir(job_id) / "tmp"
    for path in (data, conf, cache, tmp):
        path.mkdir(parents=True, exist_ok=True)
    env.update(
        {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "XDG_DATA_HOME": str(data),
            "XDG_CONFIG_HOME": str(conf),
            "XDG_CACHE_HOME": str(cache),
            "TMPDIR": str(tmp),
            "TEMP": str(tmp),
            "TMP": str(tmp),
            "OPENCODE_DISABLE_AUTOUPDATE": "1",
            "NO_COLOR": "1",
            "CI": "1",
        }
    )
    env.update(extra)
    binary = config.AUTHORING_OPENCODE_BIN
    resolved = shutil.which(binary)
    if resolved:
        env["PATH"] = str(Path(resolved).parent) + os.pathsep + env.get("PATH", "")
    return env


def _resolve_binary() -> str:
    binary = config.AUTHORING_OPENCODE_BIN
    resolved = shutil.which(binary)
    if resolved:
        return resolved
    if Path(binary).is_file():
        return str(Path(binary))
    raise RuntimeError(
        "No se encontró OpenCode. Instala `@opencode/cli` o usa la imagen Docker, "
        "que ya lo incluye."
    )


def _combine_sources(job_id: str) -> tuple[str, list[str], bool]:
    uploads = uploads_dir(job_id)
    names = sorted(
        (path for path in uploads.iterdir() if path.is_file()),
        key=lambda path: path.name.casefold(),
    )
    if not names:
        raise ValueError("No hay documentos subidos para este trabajo.")
    parts: list[str] = []
    truncated = False
    for path in names:
        text = extract.extract_text(path)
        parts.append(f"\n\n# Documento: {path.name}\n\n{text}")
    combined = "".join(parts)
    if len(combined) > config.AUTHORING_MAX_CHARS:
        truncated = True
    metadata = extract.write_source_parts(
        combined, store.job_dir(job_id) / "source", config.AUTHORING_MAX_CHARS
    )
    truncated = truncated or bool(metadata.get("truncated"))
    return combined, [path.name for path in names], truncated


def _prompt(meta: dict[str, Any]) -> str:
    languages = ", ".join(meta.get("languages") or ["es"])
    notes = str(meta.get("notes") or "").strip()
    extra = f"\nNotas del profesorado: {notes}" if notes else ""
    return (
        "Lee AGENTS.md, meta.json y todos los archivos source/source-*.md. "
        f"Genera una unidad didáctica en {languages} y escribe course.json. "
        "No pidas confirmación. Cuando termines, responde con una sola línea "
        "OK con el número de lecciones."
        f"{extra}"
    )


def _read_course(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError("OpenCode terminó sin crear course.json.")
    if path.stat().st_size > 3_000_000:
        raise RuntimeError("course.json supera el tamaño máximo permitido (3 MB).")
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"course.json no es JSON válido (línea {exc.lineno}): {exc.msg}."
        ) from exc
    if not isinstance(package, dict):
        raise ValueError("course.json debe contener un objeto JSON.")
    return package


def _ensure_requested_languages(parsed, meta: dict[str, Any]) -> None:
    requested = [lang for lang in (meta.get("languages") or ["es"]) if lang]
    missing = [lang for lang in requested if lang not in parsed.languages]
    if missing:
        raise ValueError(
            "faltan los idiomas solicitados: " + ", ".join(missing)
        )


def _check_abort(job_id: str) -> bool:
    with _lock:
        cancelled = _cancel.get(job_id, threading.Event()).is_set()
        timed_out = job_id in _timed_out
    if cancelled:
        store.update_job(
            job_id,
            status="cancelled",
            finished_at=store.utcnow(),
            error="Generación cancelada por el usuario.",
        )
        _log(job_id, f"[{store.utcnow()}] Cancelada.")
        return True
    if timed_out:
        raise RuntimeError(
            f"OpenCode superó el tiempo máximo de {config.AUTHORING_TIMEOUT} segundos."
        )
    return False


def _run_opencode(
    job_id: str,
    run_dir: Path,
    config_data: dict[str, Any],
    env_extra: dict[str, str],
    model_ref: str,
    meta: dict[str, Any],
    key: str,
    *,
    prompt: str | None = None,
    continue_session: bool = False,
) -> int:
    (run_dir / "opencode.json").write_text(
        json.dumps(config_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    agent_source = Path(__file__).with_name("agent") / "AGENTS.md"
    shutil.copyfile(agent_source, run_dir / "AGENTS.md")

    binary = _resolve_binary()
    command = [
        binary,
        "run",
        "--standalone",
        "--format",
        "json",
        "--agent",
        providers.AUTHORING_AGENT,
        "--model",
        model_ref,
        "--auto",
    ]
    if continue_session:
        command.append("--continue")
    command.append(prompt or _prompt(meta))
    env = _minimal_env(env_extra, job_id)
    _log(job_id, f"$ {' '.join(command[:8])} …", key)
    process = subprocess.Popen(
        command,
        cwd=str(run_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
    )
    with _lock:
        _active[job_id] = process
    timeout = max(60, config.AUTHORING_TIMEOUT)
    timer = threading.Timer(timeout, _terminate, args=(process, job_id, True))
    timer.daemon = True
    timer.start()
    try:
        if process.stdout is not None:
            for line in process.stdout:
                _log(job_id, line, key)
                with _lock:
                    cancelled = _cancel.get(job_id, threading.Event()).is_set()
                if cancelled and process.poll() is None:
                    process.terminate()
        return process.wait()
    finally:
        timer.cancel()
        with _lock:
            _active.pop(job_id, None)


def run_job(job_id: str) -> None:
    job = store.get_job(job_id)
    if job is None:
        return
    with _lock:
        if _cancel.get(job_id, threading.Event()).is_set():
            store.update_job(
                job_id,
                status="cancelled",
                finished_at=store.utcnow(),
                error="Generación cancelada antes de empezar.",
            )
            return
    run_dir = store.job_dir(job_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    key = ""
    try:
        store.update_job(job_id, status="extracting", started_at=store.utcnow())
        _log(job_id, f"[{store.utcnow()}] Extrayendo texto de {len(job['source_names'])} documento(s)…")
        combined, names, truncated = _combine_sources(job_id)
        meta_path = run_dir / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        meta.update(
            {
                "source_names": names,
                "characters": len(combined),
                "truncated": truncated,
                "languages": job.get("languages") or ["es"],
            }
        )
        if truncated:
            meta["warning"] = (
                "El documento superaba el límite y se ha recortado; cita solo lo "
                "que aparece en source/."
            )
        write_meta(job_id, meta)
        _log(
            job_id,
            f"[{store.utcnow()}] Texto listo: {len(combined)} caracteres"
            + (" (recortado)." if truncated else "."),
        )

        current = settings.load_settings()
        key = str(current.get("api_key") or "")
        current["provider"] = job["provider"]
        current["model"] = job["model"]
        config_data, env_extra, model_ref = providers.build_config(current)
        store.update_job(job_id, status="generating")
        _log(job_id, f"[{store.utcnow()}] OpenCode · {model_ref}")
        code = _run_opencode(job_id, run_dir, config_data, env_extra, model_ref, meta, key)
        if _check_abort(job_id):
            return
        course_path = run_dir / "course.json"
        if code != 0:
            # OpenCode puede cerrar con código 1 después de recuperarse de un
            # error transitorio del proveedor (por ejemplo, un stream cortado)
            # y aun así dejar un course.json completo. La validación manda: si
            # el archivo existe y pasa el contrato, la unidad es utilizable.
            if not course_path.is_file():
                raise RuntimeError(f"OpenCode terminó con código {code}. Revisa el log.")
            _log(
                job_id,
                f"[{store.utcnow()}] Aviso: OpenCode cerró con código {code}, "
                "pero course.json existe; se valida igualmente.",
            )
        store.update_job(job_id, status="validating")
        _log(job_id, f"[{store.utcnow()}] Validando el paquete…")
        desired = str(meta.get("slug") or "").strip() or None
        try:
            package = _read_course(course_path)
            parsed = parse_package(package, slug_override=desired)
            _ensure_requested_languages(parsed, meta)
        except (ValueError, TypeError, KeyError) as first_error:
            _log(job_id, f"[{store.utcnow()}] Validación fallida: {first_error}")
            _log(job_id, f"[{store.utcnow()}] Pidiendo una reparación a OpenCode…")
            repair_prompt = (
                "El validador de SLAnything ha rechazado course.json. Corrige "
                "ÚNICAMENTE lo necesario y vuelve a escribir el archivo completo. "
                f"Error exacto: {first_error}\n"
                "No cambies el resto del contenido ni el alcance. Cuando termines, "
                "responde OK."
            )
            repair_code = _run_opencode(
                job_id,
                run_dir,
                config_data,
                env_extra,
                model_ref,
                meta,
                key,
                prompt=repair_prompt,
                continue_session=True,
            )
            if _check_abort(job_id):
                return
            if repair_code != 0 and not course_path.is_file():
                raise RuntimeError(
                    f"El paquete no pasó la validación ({first_error}) y la "
                    f"reparación terminó con código {repair_code}."
                ) from first_error
            package = _read_course(course_path)
            try:
                parsed = parse_package(package, slug_override=desired)
                _ensure_requested_languages(parsed, meta)
            except (ValueError, TypeError, KeyError) as second_error:
                raise RuntimeError(
                    f"El paquete no pasó la validación: {first_error}. "
                    f"La reparación automática tampoco lo resolvió: {second_error}."
                ) from second_error
            _log(job_id, f"[{store.utcnow()}] Reparación validada.")
        unique = store.unique_course_slug(parsed.slug)
        if unique != parsed.slug:
            package["slug"] = unique
            parsed = parse_package(package)
        else:
            package["slug"] = parsed.slug
        title = parsed.summary["titles"].get(parsed.languages[0], parsed.slug)
        store.save_generated_course(
            slug=parsed.slug,
            owner_id=int(job.get("owner_id") or 0)
            if "owner_id" in job
            else _owner_for_job(job_id),
            job_id=job_id,
            title=title,
            package=package,
            status="draft",
        )
        store.update_job(
            job_id,
            status="ready",
            course_slug=parsed.slug,
            finished_at=store.utcnow(),
            error=None,
        )
        _log(
            job_id,
            f"[{store.utcnow()}] Lista: {parsed.slug} · "
            f"{parsed.summary['lesson_count']} lecciones · "
            f"{parsed.summary['quiz_count']} quiz.",
        )
    except Exception as exc:  # noqa: BLE001 - el trabajo debe terminar con estado legible
        logger.exception("Fallo generando la unidad %s", job_id)
        store.update_job(
            job_id,
            status="failed",
            finished_at=store.utcnow(),
            error=str(exc)[:4000],
        )
        _log(job_id, f"[{store.utcnow()}] ERROR: {exc}")
        _log(job_id, traceback.format_exc()[-6000:], key)


def _owner_for_job(job_id: str) -> int:
    from webapp.db import connect

    conn = connect()
    try:
        row = conn.execute(
            "SELECT owner_id FROM authoring_jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return int(row["owner_id"]) if row else 0
    finally:
        conn.close()


def shutdown() -> None:
    """Termina los procesos vivos sin destruir el executor global.

    El lifespan de FastAPI se ejecuta también en cada ``TestClient``; apagar el
    pool aquí lo dejaría inservible para el resto del proceso. Los hilos son
    cortos y el sistema operativo recoge el pool al salir.
    """
    with _lock:
        for process in list(_active.values()):
            if process.poll() is None:
                try:
                    process.terminate()
                except OSError:
                    pass
        _active.clear()
