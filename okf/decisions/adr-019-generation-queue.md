---
type: ADR
title: ADR-019 · Cola de generación persistente y reanudable
description: Estado en authoring_jobs y artefactos en disco; pool en proceso con reanudación al arrancar y worker opcional aparte.
tags: [adr, autoría, cola, worker, sse]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: worker
    resource: ../../webapp/generation/worker.py
    title: Worker
---

# Contexto

El Estudio tenía un único hilo en memoria: los trabajos de todos los profesores
iban en serie y un reinicio los marcaba como fallidos.

# Decisión

- El estado vive en `authoring_jobs` (`status`, `stage`, `progress_json`,
  `config_json`, tokens) y los artefactos en disco; cada etapa salta lo ya
  hecho, así que reanudar es volver a encolar.
- Por defecto, pool en el proceso web (`AULA_GEN_WORKERS`, 2 hilos);
  `resume_pending()` reanuda al arrancar. Con `AULA_GEN_INPROCESS=0`, un
  proceso aparte (`python -m webapp.generation.worker`) recoge el trabajo.
- Progreso en directo por **SSE** (`GET /jobs/{id}/events`) leyendo
  `events.jsonl`; la UI cae a *polling* si la conexión falla.
- Cuotas mensuales por espacio (`AULA_GEN_MONTHLY_PERSONAL`,
  `AULA_GEN_MONTHLY_ORG`).

# Consecuencias

- Sin Redis. Con PostgreSQL, el reparto entre varios workers usará
  `FOR UPDATE SKIP LOCKED` ([ADR-015](/decisions/adr-015-versioned-migrations.md)).
