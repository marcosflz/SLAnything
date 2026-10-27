---
type: ADR
title: "ADR-008 · Frontend Next.js sobre API FastAPI"
description: Migración de la interfaz a Next.js App Router manteniendo FastAPI como backend y fuente de contenido.
tags: [adr, nextjs, react, fastapi, migracion, frontend]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: plan
    resource: ../../docs/MIGRATION_NEXTJS.md
    title: Plan de migración a Next.js
  - id: api
    resource: ../../webapp/routers/api.py
    title: API JSON /api/v1
---

# Contexto

La interfaz original se renderiza con Jinja2 desde FastAPI. El producto ha
crecido hasta 14 páginas, 8 lecciones bilingües, 7 laboratorios y un runner de
Python. Mantener toda la interactividad en JavaScript global y plantillas hace
cada vez más difícil componer estados, reutilizar UI y evolucionar el producto.

# Decisión

Migrar la interfaz a **Next.js 16 (App Router, React 19, TypeScript)** y
mantener **FastAPI** como backend:

- FastAPI conserva SQLite, autenticación, CSRF, contenido, ejecución de Python y
  validación.
- Se añade una API JSON versionada en `/api/v1`.
- Next.js renderiza en servidor y consume la API con la cookie del usuario.
- El navegador habla solo con el origen de Next; los *rewrites* proxyean
  `/api/v1/*`, `/api/ejecutar` y `/static/*` a FastAPI. Esto evita CORS y
  mantiene la cookie `aula_session` HttpOnly.
- Se reutiliza el sistema visual `app.css` y los 7 laboratorios JS existentes.
- Las rutas Jinja se mantienen temporalmente como red de seguridad hasta
  verificar la paridad.

# Consecuencias

- Dos runtimes en desarrollo (`uv` en 8000 y Node en 3000) y un build adicional.
- La API JSON pasa a ser un contrato estable que hay que testear.
- El frontend puede evolucionar con componentes, estados y tipado sin reescribir
  el backend.
- La migración es reversible: la app Jinja sigue funcionando en el puerto 8000.
- Cuando la paridad esté cerrada, se podrán retirar `webapp/templates/` y
  `webapp/templating.py`, y ADR-001 quedará completamente superseded.

# Alternativas descartadas

- **SPA con Vite**: menos estructura de servidor, pero obliga a CORS, a mover
  auth al cliente y a rehacer el SEO.
- **Reescribir el backend en Node**: duplica el coste y pierde el runner Python,
  el contenido y los tests existentes.
- **Mantener Jinja y añadir islas React**: no resuelve la composición de páginas
  ni la navegación, y perpetúa dos modelos mentales.
