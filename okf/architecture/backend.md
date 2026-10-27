---
type: Architecture
title: Backend FastAPI
description: Routers, dependencias, repositorios y convenciones del backend de SLAnything.
tags: [backend, fastapi, routers, sqlite]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: main
    resource: ../../webapp/main.py
    title: app factory y rutas base
  - id: deps
    resource: ../../webapp/deps.py
    title: Dependencias de autenticación
  - id: repos
    resource: ../../webapp/repositories.py
    title: Consultas SQL
---

# Punto de entrada

`webapp/main.py` crea la app, monta `/static`, incluye los routers, añade cabeceras
de seguridad, define `/salud` y `/health`, y registra handlers 401/403/404/Exception.
El `lifespan` llama a `init_db()` y `validate_content()` antes de aceptar tráfico.

# Routers

| Router | Rutas principales |
|---|---|
| `language.py` | `/idioma/{lang}`, `/language/{lang}` |
| `auth.py` | `GET/POST /entrar`, `GET/POST /registro`, `POST /salir` |
| `course.py` | `/`, `/cursos`, `/cursos/{slug}`, `/curso`, `/leccion/{slug}`, completar, nota, marcador, descargas de código |
| `execution.py` | `POST /api/ejecutar` (sesión + CSRF + rate limit) |
| `quiz.py` | `/quiz/{id}`, `POST /quiz/{id}`, `/quiz/intento/{id}` |
| `progress.py` | `/progreso` |
| `glossary.py` | `/glosario` |
| `resources.py` | `/recursos`, `/recursos/cuaderno`, `/recursos/plan` |
| `search.py` | `/buscar?q=` |
| `teacher.py` | `/profesor` (solo rol teacher) |
| `authoring.py` | `/api/v1/authoring/*` y `/estudio` (solo rol teacher) |
| `api.py` | `/api/v1/*` · API JSON para Next.js |

# API JSON

`webapp/routers/api.py` expone la frontera que consume el frontend Next.js:

- `GET /api/v1/session`, `/public`, `/catalog`, `/courses/{slug}`, `/shell` para
  arranque, sesión y biblioteca.
- `GET /api/v1/dashboard`, `/course`, `/lessons/{slug}`, `/progress`,
  `/glossary`, `/resources`, `/search`, `/teacher`; aceptan `?course=` cuando
  aplica para fijar el curso activo.
- `POST /api/v1/auth/login`, `/auth/register`, `/auth/logout`.
- `POST /api/v1/lessons/{slug}/complete`, `/note`, `/bookmark`.
- `GET/POST /api/v1/quiz/{id}` y `GET /api/v1/quiz/attempts/{id}`.
- `GET /api/v1/downloads/...` para código, cuaderno y plan.

La API reutiliza `repositories.py`, `deps.py`, `security.py` y los
serializadores del router. Las mutaciones exigen `X-CSRF-Token`; el login y el
registro emiten la misma cookie `aula_session`. El quiz nunca devuelve
`correct` ni `explanation` en el GET. Las respuestas incluyen `course` (curso
activo) y `courses` (resumen del catálogo) en las pantallas que lo necesitan.

# Estudio de autoría

`webapp/authoring/` implementa el flujo documento → unidad. El router
`authoring.py` valida permisos y CSRF, guarda las subidas, crea el trabajo y lo
envía al executor. El runner construye un `opencode.json` por trabajo, ejecuta el
agente `slanything-author` y valida el `course.json` resultante con
`package.parse_package()`. La API y `/estudio` comparten los mismos servicios para
que Next y Jinja no diverjan. Los detalles están en
[authoring](/architecture/authoring.md).

# Idioma y contenido

`webapp/i18n.py` resuelve el idioma desde `?lang=`, la cookie `aula_lang` o el
valor por defecto (`es`). `render()` inyecta `lang`, `t()`, `course`, `lab_meta` y
las etiquetas de cabecera del bundle activo. `content_for(lang)` selecciona
`Course`, glosario y quiz en español o inglés. Los slugs no cambian entre idiomas,
así que el progreso y los intentos siguen siendo válidos al cambiar de lengua.

# Ejecución de Python

`POST /api/ejecutar` recibe `{code, lesson?}` y llama a
`webapp.execution.execute_for_lesson()`, que lanza `webapp/sandbox_runner.py` en
un subproceso con `python -I`. El endpoint exige usuario, `X-CSRF-Token` y aplica
un rate limit por usuario (12/minuto por defecto) y un límite de dos ejecuciones
concurrentes. Los errores de código se devuelven como JSON (`ok: false`) para que
el navegador los muestre sin romper la página.

# Dependencias

- `get_db()`: conexión SQLite por petición, commit/rollback y cierre.
- `get_current_user()`: cookie → sesión → usuario; renueva la sesión si quedan
  menos de 7 días.
- `require_user()`: lanza 401; el handler redirige a `/entrar?next=...`.
- `require_teacher()`: lanza 403 si el rol no es `teacher`.
- `ensure_csrf()`: valida el token de formulario o `X-CSRF-Token`.

# Repositorios

`repositories.py` concentra el SQL:

- usuarios y sesiones;
- progreso y estadísticas filtradas por `course_slug`;
- progreso agrupado por curso para el catálogo y el dashboard;
- notas y marcadores por curso;
- actividad, racha y últimos días;
- intentos de quiz por curso, mejor intento y media;
- panel del profesor global.

Los routers no escriben SQL salvo el quiz POST, que lee el formulario con
`await request.form()`.

# Convenciones

- Endpoints síncronos (`def`) para SQLite; FastAPI los ejecuta en threadpool.
- `from __future__ import annotations` en todos los módulos.
- Respuestas HTML con `render()`; redirecciones 303 tras POST.
- Mensajes de éxito/error por query string (`?ok=`, `?error=`) escapados por Jinja.
- Nunca se revela la respuesta correcta en el GET del quiz.
- Los mensajes de interfaz se traducen con `t(request, "texto")`; los textos
  didácticos vienen del bundle de contenido, no del diccionario de UI.
- Las descargas de código responden con `text/x-python` y un nombre ASCII estable.

# Errores y salud

- 401 → redirect al login con `next` seguro.
- 403/404/500 → `pages/error.html` con el código HTTP real.
- `/salud` y `/health` → `{"status": "ok", "lecciones": 8}`.
