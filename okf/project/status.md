---
type: Status
title: Estado actual de SLAnything
description: Foto del proyecto a 24 de octubre de 2026 con el catálogo multi-curso, el Estudio de autoría, el curso de referencia completo y las cifras verificadas.
tags: [estado, entrega, handoff, tests, cursos, catalogo]
status: stable
stale_after: 2026-11-30T00:00:00Z
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T17:49:24Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README del proyecto
  - id: qa
    resource: ../../docs/QA.md
    title: Informe de QA
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Resumen

| Campo | Valor |
|---|---|
| Producto | SLAnything · biblioteca de cursos tipo aula virtual |
| Cursos | 1 estático + cursos generados publicables desde el Estudio |
| Curso de referencia | Construye un LLM desde cero |
| Capítulos | 7 · del 1 al 7 del libro |
| Estado | Curso completo entregado y plataforma preparada para más cursos |
| Lecciones | 56 (8 por capítulo) |
| Duración estimada | 584 minutos |
| Laboratorios | 15 |
| Quizzes | 7 · 10 preguntas cada uno · 80 % para aprobar |
| Glosario | 113 términos (ES/EN) |
| Idiomas | Español e inglés |
| Ejemplos Python | 26 ejecutables en servidor + descarga |
| Tests | 111 passed |
| Repositorio | GitHub privado · `marcosflz/SLAnything` |
| Servidor local | Next `http://127.0.0.1:3000` · FastAPI `http://127.0.0.1:8000` |
| Empaquetado | Docker Compose (`aula-llm-backend`, `aula-llm-frontend`) con OpenCode |
| Base de datos | `aula.db` (SQLite v3, ignorada por git) |
| Autoría | `/estudio` · OpenCode portable + proveedor configurable + PWA |
| Última verificación | 2026-10-24 |

# Qué está hecho

- **Estudio de autoría** (`/estudio`, solo profesorado): subida de PDF, DOCX,
  EPUB, ODT, Markdown, HTML o TXT; extracción y troceado; generación con OpenCode
  en un subproceso aislado; paquete JSON bilingüe validado y saneado; borrador,
  publicación, despublicación y borrado. Una reparación automática si el primer
  paquete no pasa el contrato.
- **OpenCode portable en la imagen Docker** (`v2.1.4`) y configuración de
  proveedor desde la web: OpenCode Go, modelos gratuitos de OpenCode, OpenAI,
  Anthropic, OpenRouter, Gemini, DeepSeek, Ollama, LM Studio o endpoint
  OpenAI-compatible. La API key vive en `authoring/settings.json` (0600).
- **Catálogo dinámico**: los cursos generados se integran en `content_for` y
  comparten catálogo, lecciones, quizzes, glosario, búsqueda, progreso y panel del
  profesor. Slugs con prefijo `gen-`.
- **PWA instalable**: manifiesto, icono, service worker de estáticos y decisión
  documentada web + PWA; Tauri queda como siguiente paso si hace falta offline.
- **Catálogo multi-curso** en Next y Jinja: `/cursos` lista la biblioteca,
  `/cursos/{slug}` abre el detalle y `/curso` se mantiene como alias del curso
  por defecto. La portada pública y la sidebar distinguen catálogo y curso actual.
- **`Course` como unidad de producto**: slug, libro, nivel, estado, color,
  portada y un `Program` propio. `CATALOGS` agrupa los cursos por idioma y
  `validate_catalog()` rechaza colisiones de slugs y quizzes.
- **Progreso aislado por curso**: `lesson_progress`, `notes`, `bookmarks` y
  `quiz_attempts` guardan `course_slug`. La migración v2 conserva los datos
  anteriores y los asigna al curso `llm-desde-cero`.
- **Siete capítulos completos** en español e inglés: entender los LLM, trabajar
  con texto, atención, arquitectura GPT, pretraining, clasificación e
  instrucciones. Cada capítulo tiene 8 lecciones, su quiz y su glosario.
- **Navegación multi-capítulo** en Next y en Jinja: portada, programa agrupado por
  capítulos, sidebar con curso activo y capítulos colapsables, lección con
  capítulo activo, siguiente/anterior entre capítulos y progreso global de 56
  lecciones por curso.
- Interfaz **Next.js 16 + React 19 + TypeScript** con landing, catálogo, registro,
  login, dashboard, curso, lecciones, quizzes, revisión, progreso, glosario,
  recursos, buscador y panel del profesor.
- **API JSON `/api/v1`** con catálogo, cursos, lecciones y quizzes; consumida por
  Server Components. Rewrites de Next para mantener cookie HttpOnly y CSRF.
- **15 laboratorios**: los 7 del capítulo 1 y 8 nuevos (`tokenizer`, `window`,
  `embedding`, `qkv`, `gpt-block`, `loss`, `classifier`, `chat-template`).
- **26 ejemplos Python** ejecutables y descargables, con validación AST y runner
  aislado.
- Contenido bilingüe con slugs compartidos: el progreso no se pierde al cambiar de
  idioma.
- **Tema claro por defecto**, tema oscuro opcional persistido en `localStorage`.
- Responsive verificado a 360, 768 y 1440 px; lightbox; accesibilidad básica.
- **Docker Compose** con dos imágenes, healthchecks, SQLite en volumen y guía.
- Documentación: README, plan, contrato de agentes, QA, migración, Docker y OKF.

# Cómo comprobarlo

```powershell
uv sync
uv run pytest -q
uv run python tools/validate_all_chapters.py
uv run python tools/check_okf.py

# Terminal 1
uv run python aula.py

# Terminal 2
cd frontend
npm install
npm run typecheck
npm run build
npm start
```

Estudio: abre `/estudio` con `profe@aulallm.local / profe1234`. En Docker,
OpenCode ya está dentro de la imagen; en local instala `@opencode/cli`. Smoke
test con ambos servidores: `uv run python tools/smoke_next.py`.
E2E de navegador: `cd frontend; npm run e2e`.
Montaje de los 15 labs: `cd frontend; npm run e2e:labs`.

Alternativa empaquetada:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Cuentas: `demo@aulallm.local / demo1234` y `profe@aulallm.local / profe1234`.

# Handoff

El curso de referencia está completo, la plataforma ya no gira alrededor de un
único libro y el Estudio permite crear unidades a partir de documentos. El
siguiente trabajo recomendado es probar el Estudio con el proveedor real del
centro, añadir el segundo curso estático si se quiere conservar el catálogo
curado, decidir si hace falta matrícula explícita y seguir con calidad
(accesibilidad, interacción profunda de labs y capturas). Antes de empezar, lee
[next-steps](/context/next-steps.md), [ADR-011](/decisions/adr-011-multi-course.md),
[ADR-012](/decisions/adr-012-authoring-opencode.md), [authoring](/architecture/authoring.md)
y [content-model](/architecture/content-model.md).

# Estado de la base de datos

`aula.db` se crea al arrancar y se siembra con demo/profesor. Es local y no se
versiona. El esquema v3 añade `authoring_jobs` y `generated_courses` al modelo v2
(progreso, notas, marcadores e intentos por curso). `init_db()` migra
automáticamente una base v1 copiando sus filas al curso por defecto. Si se borra
la base, no se pierde código ni contenido, solo progreso de pruebas y los cursos
generados; los documentos y logs viven en `authoring-data/` o en el volumen
`/data/authoring`.
