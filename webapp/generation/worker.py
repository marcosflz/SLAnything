"""Cola de generación persistente (ADR-019).

El estado de cada trabajo vive en ``authoring_jobs`` (estado + etapa) y sus
artefactos en disco, así que la cola sobrevive a reinicios:

- Por defecto un *pool* dentro del proceso web ejecuta las etapas
  (``AULA_GEN_WORKERS`` hilos). Al arrancar, ``resume_pending()`` vuelve a
  encolar lo que quedó a medias y cada etapa salta lo ya hecho.
- Con ``AULA_GEN_INPROCESS=0`` la web solo encola y un proceso aparte hace el
  trabajo: ``uv run python -m webapp.generation.worker``.
"""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from webapp import config
from webapp.authoring import store
from webapp.generation import pipeline

logger = logging.getLogger("aula.generation.worker")

STAGES = {
    "analyze": pipeline.analyze,
    "plan": pipeline.plan,
    "generate": pipeline.generate,
}

# Estado → etapa que lo continúa al reanudar.
RESUME = {
    "queued": "analyze",
    "extracting": "analyze",
    "outlining": "plan",
    "generating": "generate",
    "validating": "generate",
}

_lock = threading.Lock()
_pool: ThreadPoolExecutor | None = None
_running: set[str] = set()


def _executor() -> ThreadPoolExecutor:
    global _pool
    with _lock:
        if _pool is None:
            _pool = ThreadPoolExecutor(
                max_workers=max(1, config.GEN_WORKERS), thread_name_prefix="gen"
            )
        return _pool


def _run(job_id: str, stage: str, *args) -> None:
    try:
        if stage == "regenerate":
            pipeline.regenerate_lesson(job_id, *args)
        else:
            STAGES[stage](job_id)
    finally:
        with _lock:
            _running.discard(job_id)


def submit(job_id: str, stage: str, *args) -> bool:
    """Encola una etapa. Devuelve False si el trabajo ya tiene una en marcha."""
    if not config.GEN_INPROCESS:
        # El proceso worker la recogerá por su estado en la base de datos.
        return True
    with _lock:
        if job_id in _running:
            return False
        _running.add(job_id)
    _executor().submit(_run, job_id, stage, *args)
    return True


def is_running(job_id: str) -> bool:
    with _lock:
        return job_id in _running


def resume_pending() -> int:
    jobs = store.resumable_jobs()
    for job in jobs:
        stage = RESUME.get(job["status"])
        if stage:
            pipeline.emit(job["id"], "stage", "Reanudando tras un reinicio del servidor…")
            submit(job["id"], stage)
    return len(jobs)


def shutdown() -> None:
    global _pool
    with _lock:
        pool, _pool = _pool, None
    if pool is not None:
        pool.shutdown(wait=False, cancel_futures=True)


def main() -> None:  # pragma: no cover - proceso de larga duración
    """Worker independiente: recoge trabajos pendientes cada pocos segundos."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from webapp.db import init_db

    init_db()
    config.GEN_INPROCESS = True  # en este proceso sí se ejecuta
    logger.info("Worker de generación listo (%s hilos)", config.GEN_WORKERS)
    while True:
        for job in store.resumable_jobs():
            stage = RESUME.get(job["status"])
            if stage and not is_running(job["id"]):
                submit(job["id"], stage)
        time.sleep(3)


if __name__ == "__main__":  # pragma: no cover
    main()
