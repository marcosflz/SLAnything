"""Ejecución de ejemplos de Python en un proceso aislado.

La API no ejecuta código dentro del proceso de FastAPI. Cada petición lanza
`webapp/sandbox_runner.py` en un subproceso con límites de tiempo, memoria y
salida. El runner aplica además una lista blanca de imports y un hook de
auditoría.

Este módulo es la única puerta de entrada: no importes `sandbox_runner` desde
las rutas ni ejecutes `exec()` en el proceso web.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

import psutil

from webapp import config


@dataclass(frozen=True)
class ExecutionSettings:
    enabled: bool = True
    timeout_seconds: int = 10
    memory_mb: int = 1024
    max_code_chars: int = 16_000
    max_output_chars: int = 20_000
    runs_per_minute: int = 12
    max_concurrent: int = 2


settings = ExecutionSettings(
    enabled=os.environ.get("AULA_EXEC_ENABLED", "1") == "1",
    timeout_seconds=int(os.environ.get("AULA_EXEC_TIMEOUT", "10")),
    memory_mb=int(os.environ.get("AULA_EXEC_MEMORY_MB", "1024")),
    max_code_chars=int(os.environ.get("AULA_EXEC_MAX_CODE", "16000")),
    max_output_chars=int(os.environ.get("AULA_EXEC_MAX_OUTPUT", "20000")),
    runs_per_minute=int(os.environ.get("AULA_EXEC_RUNS_PER_MINUTE", "12")),
    max_concurrent=int(os.environ.get("AULA_EXEC_CONCURRENT", "2")),
)

RUNNER = Path(__file__).with_name("sandbox_runner.py")
_SEMAPHORE = threading.BoundedSemaphore(settings.max_concurrent)
_LOCK = threading.Lock()
_RUNS: dict[str, deque[float]] = defaultdict(deque)


class ExecutionError(Exception):
    """Error controlado que la API puede mostrar al alumnado."""


class RateLimitError(ExecutionError):
    """Se superó el número de ejecuciones permitidas."""


def _msg(lang: str, es: str, en: str) -> str:
    return en if lang == "en" else es


def _prune(key: str, now: float) -> None:
    window = _RUNS[key]
    while window and now - window[0] > 60:
        window.popleft()
    if not window:
        _RUNS.pop(key, None)


def reset_rate_limits() -> None:
    """Vacía el estado en memoria; útil en tests y al reiniciar."""
    with _LOCK:
        _RUNS.clear()


def check_rate_limit(user_key: str, lang: str = "es") -> None:
    now = time.monotonic()
    with _LOCK:
        _prune(user_key, now)
        window = _RUNS[user_key]
        if len(window) >= settings.runs_per_minute:
            retry = max(1, int(60 - (now - window[0])))
            raise RateLimitError(
                _msg(
                    lang,
                    f"Demasiadas ejecuciones seguidas. Espera {retry} segundos.",
                    f"Too many runs in a row. Wait {retry} seconds.",
                )
            )
        window.append(now)


def _environment(cache_dir: Path) -> dict[str, str]:
    keep = ("SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC", "PATHEXT")
    env = {key: os.environ[key] for key in keep if key in os.environ}
    env.update(
        {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(cache_dir),
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "HOME": str(cache_dir),
            "USERPROFILE": str(cache_dir),
        }
    )
    return env


def _terminate(process: subprocess.Popen) -> None:
    try:
        process.kill()
    except OSError:
        pass


def run_code(code: str, *, user_key: str = "anon", lang: str = "es") -> dict:
    """Ejecuta `code` y devuelve stdout, errores y figuras/tablas."""
    if not settings.enabled:
        raise ExecutionError(
            _msg(
                lang,
                "La ejecución remota está desactivada en este servidor.",
                "Remote execution is disabled on this server.",
            )
        )
    if not code.strip():
        raise ExecutionError(
            _msg(
                lang,
                "Escribe algo de código antes de ejecutar.",
                "Write some code before running it.",
            )
        )
    if len(code) > settings.max_code_chars:
        raise ExecutionError(
            _msg(
                lang,
                f"El código supera el límite de {settings.max_code_chars:,} caracteres.",
                f"The code exceeds the {settings.max_code_chars:,}-character limit.",
            )
        )

    check_rate_limit(user_key, lang)
    if not _SEMAPHORE.acquire(timeout=3):
        raise ExecutionError(
            _msg(
                lang,
                "El servidor está ejecutando otros ejemplos. Prueba en unos segundos.",
                "The server is running other examples. Try again in a few seconds.",
            )
        )
    try:
        return _run_in_subprocess(code, lang)
    finally:
        _SEMAPHORE.release()


def _run_in_subprocess(code: str, lang: str = "es") -> dict:
    with tempfile.TemporaryDirectory(prefix="aula-run-") as raw_dir:
        workdir = Path(raw_dir)
        result_path = workdir / "result.json"
        input_path = workdir / "input.json"
        cache_dir = Path(tempfile.gettempdir()) / "aula-mpl-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "code": code,
            "result_path": str(result_path),
            "timeout_seconds": settings.timeout_seconds,
            "memory_mb": settings.memory_mb,
            "max_output": settings.max_output_chars,
            "data_dir": str(config.STATIC_DIR / "data"),
        }
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        command = [sys.executable, "-I", str(RUNNER)]
        started = time.monotonic()
        with input_path.open("r", encoding="utf-8") as stdin:
            process = subprocess.Popen(
                command,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(workdir),
                env=_environment(cache_dir),
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        timed_out = False
        memory_exceeded = False

        deadline = started + settings.timeout_seconds
        while True:
            try:
                process.communicate(timeout=0.25)
                break
            except subprocess.TimeoutExpired:
                try:
                    rss = psutil.Process(process.pid).memory_info().rss
                except psutil.Error:
                    rss = 0
                if rss and rss > settings.memory_mb * 1024 * 1024:
                    memory_exceeded = True
                    _terminate(process)
                    process.communicate()
                    break
                if time.monotonic() >= deadline:
                    timed_out = True
                    _terminate(process)
                    process.communicate()
                    break

        if timed_out:
            return {
                "ok": False,
                "error": _msg(
                    lang,
                    f"El código ha superado el tiempo máximo de "
                    f"{settings.timeout_seconds} segundos.",
                    f"The code exceeded the maximum time of "
                    f"{settings.timeout_seconds} seconds.",
                ),
                "stdout": "",
                "outputs": [],
                "duration_ms": int((time.monotonic() - started) * 1000),
            }
        if memory_exceeded:
            return {
                "ok": False,
                "error": _msg(
                    lang,
                    f"El código ha superado el límite de memoria de "
                    f"{settings.memory_mb} MB.",
                    f"The code exceeded the {settings.memory_mb} MB memory limit.",
                ),
                "stdout": "",
                "outputs": [],
                "duration_ms": int((time.monotonic() - started) * 1000),
            }

        if result_path.is_file():
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                result = None
            if isinstance(result, dict):
                result.setdefault("duration_ms", int((time.monotonic() - started) * 1000))
                return result

        try:
            stderr = (process.stderr.read() if process.stderr else "")[-4000:]
        except (ValueError, OSError):
            stderr = ""
        return {
            "ok": False,
            "error": _msg(
                lang,
                "El proceso de ejecución no devolvió un resultado válido.",
                "The execution process did not return a valid result.",
            ),
            "stdout": "",
            "stderr": stderr,
            "outputs": [],
            "duration_ms": int((time.monotonic() - started) * 1000),
        }


def execute_for_lesson(code: str, *, user_id: int, lang: str = "es") -> dict:
    return run_code(code, user_key=f"user:{user_id}", lang=lang)
