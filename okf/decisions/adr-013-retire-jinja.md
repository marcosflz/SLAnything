---
type: ADR
title: ADR-013 · Retirar la interfaz Jinja
description: Next.js pasa a ser la única interfaz; FastAPI solo expone la API JSON, la ejecución y los estáticos.
tags: [adr, frontend, jinja, nextjs]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: api
    resource: ../../webapp/routers/api.py
    title: API JSON
  - id: main
    resource: ../../webapp/main.py
    title: App FastAPI
---

> Relación: supersedes parte de ADR-001.

# Contexto

Mantener dos interfaces (Jinja en `:8000` y Next.js en `:3000`) obligaba a
duplicar cada cambio de UI y a sincronizar dos copias de `app.css`, que ya se
habían desincronizado. El rediseño hacia un LMS moderno multiplicaba ese coste.

# Decisión

- Se borran `webapp/templates/`, `webapp/templating.py`, las rutas HTML
  (`routers/auth.py`, `course.py`, `glossary.py`, `language.py`,
  `progress.py`, `quiz.py`, `resources.py`, `search.py`, `teacher.py` y la
  parte HTML de `authoring.py`), `webapp/static/css/app.css`,
  `webapp/static/js/app.js` y `tools/sync_frontend_assets.py`.
- FastAPI sirve `/api/v1/*`, `/api/ejecutar`, `/static/*` (imágenes, datos y
  módulos JS de los labs) y `/salud`/`/health`. Los errores siempre son JSON.
- Los helpers de descarga de código pasan a `webapp/downloads.py`.
- Los tests de páginas se reescribieron contra la API.

# Consecuencias

- Un solo sitio para la UI y un solo CSS (`frontend/src/app/app.css`, ahora
  en la capa `legacy`; ver [ADR-014](/decisions/adr-014-design-system.md)).
- El puerto 8000 deja de ser navegable; para depurar se usa la API o `/docs`.
