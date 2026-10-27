---
type: Repository Map
title: Mapa del repositorio
description: Qué contiene cada carpeta y dónde tocar cada tipo de cambio.
tags: [repositorio, estructura, archivos, mantenimiento]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T17:49:24Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README
---

# Árbol

```text
AGENTS.md                  # obligaciones del agente y arranque de sesión
aula.py                    # arranque local (uv run python aula.py)
Dockerfile                 # imagen del backend FastAPI
compose.yaml               # backend + frontend + volumen SQLite/Estudio
.env.example               # variables de Docker Compose
okf/                       # bundle OKF: memoria persistente
docs/                      # plan, migración, Docker, contrato de agentes, QA y capturas
notebooks/                 # cuaderno del capítulo 1, figuras y corpus
tools/                     # generadores, export de i18n, smoke test y validador OKF
frontend/                  # interfaz principal Next.js 16
  src/app/                 # rutas App Router
  src/components/          # shell, bloques, labs, quiz y UI
  src/lib/                 # API, tipos, mensajes y cliente HTTP
  next.config.ts           # rewrites a FastAPI y cabeceras
  Dockerfile               # imagen standalone del frontend
webapp/
  main.py                  # app FastAPI
  config.py                # configuración
  db.py                    # SQLite
  security.py              # scrypt, sesiones, CSRF, rate limit
  deps.py                  # auth y permisos
  repositories.py          # SQL
  templating.py            # Jinja, locale y filtros de fecha
  i18n.py                  # diccionario ES→EN de interfaz
  execution.py             # límites, rate limit y subproceso de ejecución
  sandbox_runner.py        # runner aislado (se ejecuta con -I)
  routers/api.py           # API JSON /api/v1 para Next
  routers/authoring.py     # API del Estudio y /estudio
  routers/                 # rutas HTML legado, /api/ejecutar e /idioma
  authoring/               # settings, providers, extract, package, store, runner y agente
  content/                 # schema, Program, Course/Catalog, lecciones, quiz y glosario
  content/chapters/        # paquetes autocontenidos ch02…ch07 (ES/EN, quiz, labs)
  templates/               # base, componentes, páginas
  static/                  # CSS, JS (i18n, runner), imágenes ch01…ch07, corpus
  tests/                   # pytest (111 tests)
```

# Dónde tocar

| Quiero… | Voy a… |
|---|---|
| Cambiar una lección del capítulo 1 | `webapp/content/lessons/lNN_*.py` y su gemela en `lessons/en/` |
| Cambiar una lección de los capítulos 2-7 | `webapp/content/chapters/chNN/lessons_es/` y `lessons_en/` |
| Añadir un quiz | `webapp/content/quizzes.py`/`quizzes_en.py` (cap. 1) o `chapters/chNN/quiz_*.py` |
| Añadir un capítulo | crear `webapp/content/chapters/chNN/` y exportar `CHAPTER_ES/EN`, quizzes, glosario y labs |
| Añadir un curso | crear un `Program`, envolverlo en `Course` y registrarlo en `CATALOGS` (`webapp/content/course.py`) o publicarlo desde `/estudio` |
| Tocar el Estudio | `webapp/authoring/`, `webapp/routers/authoring.py`, `frontend/src/app/estudio/` |
| Cambiar las instrucciones del agente | `webapp/authoring/agent/AGENTS.md` y `webapp/authoring/providers.py` |
| Añadir un proveedor LLM | `webapp/authoring/providers.py` y `docs/AUTHORING.md` |
| Cambiar el catálogo | `webapp/content/catalog.py`, `routers/course.py`, `frontend/src/app/cursos/` |
| Cambiar textos de interfaz | `webapp/i18n.py` (fuente) y `frontend/src/lib/messages.json` (export) |
| Tocar la ejecución Python | `webapp/execution.py`, `sandbox_runner.py` y `routers/execution.py` |
| Añadir un lab | `webapp/static/js/labs/`, `webapp/labs.py` o `chapters/chNN/labs.py`, `config.KNOWN_LABS` |
| Validar contenido | `tools/check_chapter.py chNN` y `tools/validate_all_chapters.py` |
| Cambiar estilos | `webapp/static/css/app.css` y sincronizar con `tools/sync_frontend_assets.py` |
| Cambiar navegación o shell | `frontend/src/components/AppShell.tsx` / `PublicShell.tsx` |
| Añadir una ruta | `frontend/src/app/` y, si necesita datos, `webapp/routers/api.py` |
| Cambiar la API JSON | `webapp/routers/api.py` y `webapp/tests/test_api.py` |
| Cambiar el esquema | `webapp/db.py` y `repositories.py` |
| Cambiar auth/CSRF | `security.py`, `deps.py`, `routers/auth.py` |
| Cambiar tests | `webapp/tests/` |
| Actualizar contexto | `okf/` y `okf/log.md` |

# Remoto

- `origin` → <https://github.com/marcosflz/SLAnything.git>. El repositorio de
  GitHub es privado y sustituye al antiguo nombre `LLMScratch`.
- `main` es la rama publicada y sigue a `origin/main`. El primer commit
  (2026-10-27) versiona el proyecto completo; no hay historial anterior.

# Secretos y artefactos locales

- Ningún `.env` real se versiona: solo `.env.example` y `frontend/.env.example`
  con placeholders.
- La API key del Estudio vive en `authoring/settings.json` (fuera de Git) y se
  configura desde `/estudio`.
- `AULA_SECRET` tiene un valor de desarrollo por defecto; en Docker se inyecta
  desde `${AULA_SECRET:-...}` y debe cambiarse en cualquier despliegue real.

# Archivos que no se versionan

- `aula.db*`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.openchamber/`.
- PDF del libro y `book_extract/`.
- `docs/capturas/_tmp*`.

# Regla

Si añades una carpeta nueva con conocimiento del proyecto, añádela a este mapa y
crea su `index.md` OKF si contiene conceptos.
