---
type: Status
title: Estado actual de SLAnything
description: Foto del proyecto a 14 de noviembre de 2026 - plataforma genérica sin curso obligatorio, perfiles individual/academia/superadmin, curso LLM como ejemplo opcional y cifras verificadas.
tags: [estado, entrega, handoff, tests, cursos, catalogo]
status: stable
stale_after: 2026-12-15T00:00:00Z
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
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
| Producto | SLAnything · aula virtual genérica: cualquier material → curso |
| Perfiles | Cuenta individual (autodidacta), alumno, profesorado, administración de academia, superadmin |
| Cursos | Generados desde el Estudio; biblioteca vacía al instalar |
| Curso de ejemplo | Construye un LLM desde cero (`AULA_SAMPLE_COURSES=1`): 7 capítulos, 56 lecciones, 15 labs, 7 quizzes, 113 términos, 26 ejemplos Python |
| Idiomas | Español e inglés |
| Acceso | Registro solo por invitación (`AULA_OPEN_SIGNUP=0`, ADR-022) |
| Tests | 224 passed |
| E2E | `npm run e2e` (perfiles) y `npm run e2e:labs` en verde con y sin ejemplos |
| Repositorio | GitHub privado · `marcosflz/SLAnything` |
| Servidor local | Next `http://127.0.0.1:3000` · FastAPI `http://127.0.0.1:8000` |
| Empaquetado | Docker Compose (`slanything-backend`, `slanything-frontend`; volumen histórico `aula-llm-data`) con agentes nas-adk y CLI de Claude Code |
| Base de datos | `aula.db` (SQLite v3, ignorada por git) |
| Autoría | `/estudio` · agentes nas-adk 0.4 (ADR-023) + proveedor de plataforma, varios propios por usuario (claves de API y suscripciones de Claude y ChatGPT) y claves compartidas por la academia, con selector de modelo (ADR-024, ADR-025) + PWA |
| Última verificación | 2026-11-14 |

# Qué está hecho

**Registro por invitación (2026-11-14, tarde):** sin registro abierto por
defecto; la superadministración invita a cuentas individuales y profesorado
(academia nueva o existente) desde `/plataforma/invitaciones` y el profesorado
invita a su alumnado ([ADR-022](/decisions/adr-022-invite-only-signup.md)).
Migración v7 (`platform_invitations`).

**Plataforma genérica y perfiles (2026-11-14):** la app funciona con la
biblioteca vacía y el curso LLM pasa a ser ejemplo opcional
([ADR-020](/decisions/adr-020-generic-platform.md)); curso activo por último
abierto, biblioteca por espacio activo, glosario y recursos por curso; portada,
login y registro genéricos. Perfiles ([ADR-021](/decisions/adr-021-account-profiles.md)):
alta como cuenta individual o academia, invitación o código de clase sin espacio
personal, matriz `learn/author/teach/manage/platform`, alumnado sin Estudio,
cuenta individual sin gestión de aula, panel de superadmin `/plataforma`,
matrículas visibles con fecha límite, `/bienvenida` y migración v6. Corregida
una carrera de lectura tras escritura (`get_db` con `scope="function"`).

**Evolución 2026-11-13 (SLAnything 2.0, en curso):** interfaz Jinja retirada;
espacios de trabajo con roles (cuentas personales y academias), grupos,
invitaciones, auditoría y cuenta; eventos de aprendizaje y paneles de KPIs
(alumno, profesorado, administración); generación por etapas con citas,
temario editable, quiz de varios tipos, verificación, cola reanudable y SSE;
sistema de diseño Tailwind con shell nuevo. Ver
[generation](/architecture/generation.md),
[tenancy-analytics](/architecture/tenancy-analytics.md) y ADR-013 a ADR-019.


- **Estudio de autoría** (`/estudio`, solo profesorado): subida de PDF, DOCX,
  EPUB, ODT, Markdown, HTML o TXT; generación por etapas con agentes nas-adk que
  entregan con herramientas validadas; paquete JSON bilingüe validado y saneado;
  borrador, publicación, despublicación y borrado.
- **Proveedores vía nas-adk**: OpenCode Go, OpenCode Zen gratuitos, OpenAI,
  Anthropic, OpenRouter, Gemini, DeepSeek, Ollama, LM Studio o endpoint
  OpenAI-compatible para la plataforma (`authoring/settings.json`, 0600); cada
  usuario con autoría puede usar su API key o su suscripción de Claude desde
  «Mi cuenta» (cifrada, nunca compartida).
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

Estudio: abre `/estudio` con `autodidacta@slanything.local / auto1234` o
`profe@slanything.local / profe1234`. Sin red: `AULA_LLM_FAKE=1`. Los agentes son
nas-adk (dependencia Python); la suscripción de Claude necesita el CLI `claude`
(incluido en la imagen Docker). Smoke
test con ambos servidores: `uv run python tools/smoke_next.py`.
E2E de navegador: `cd frontend; npm run e2e`.
Montaje de los 15 labs: `cd frontend; npm run e2e:labs`.

Alternativa empaquetada:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Cuentas demo (`AULA_SEED_DEMO=1`): `alumno@slanything.local / alumno1234`,
`profe@slanything.local / profe1234`, `autodidacta@slanything.local / auto1234`
y `admin@slanything.local / admin1234` (superadmin). Curso de ejemplo:
`AULA_SAMPLE_COURSES=1`.

# Handoff

La plataforma ya es genérica: arranca sin cursos, cada perfil ve solo lo que le
corresponde y el curso LLM es un ejemplo que se activa por variable de entorno.
El siguiente trabajo recomendado es probar el Estudio con un proveedor real y
documentos de materias no técnicas, automatizar en Playwright el asistente del
Estudio, migrar las páginas heredadas (lección, quiz, progreso, glosario) al
sistema de diseño nuevo y añadir correo (invitaciones y recuperación de
contraseña). Antes de empezar, lee [next-steps](/context/next-steps.md),
[ADR-020](/decisions/adr-020-generic-platform.md),
[ADR-021](/decisions/adr-021-account-profiles.md) y
[tenancy-analytics](/architecture/tenancy-analytics.md).

# Estado de la base de datos

`aula.db` se crea al arrancar y, con `AULA_SEED_DEMO=1`, se siembra con las
cuatro cuentas demo y la Academia Demo. Es local y no se versiona. El esquema va
por la **v6** (`webapp/migrations.py`): espacios, membresías, grupos,
matrículas, invitaciones, auditoría, eventos, generación por etapas y perfiles.
`init_db()` migra automáticamente bases antiguas (v1 copia sus filas al curso de
ejemplo). Si se borra
la base, no se pierde código ni contenido, solo progreso de pruebas y los cursos
generados; los documentos y logs viven en `authoring-data/` o en el volumen
`/data/authoring`.
