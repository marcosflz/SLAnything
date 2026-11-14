---
type: Architecture
title: Generación por etapas con agentes nas-adk
description: Cómo un documento se convierte en una unidad didáctica revisable (ingesta, temario, lecciones, evaluación, verificación, cola y SSE), con un agente nas-adk por llamada al modelo.
tags: [autoría, generación, agentes, nas-adk, citas, cola, sse]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T20:00:00Z }
sources:
  - id: pipeline
    resource: ../../webapp/generation/pipeline.py
    title: Etapas
  - id: document
    resource: ../../webapp/generation/document.py
    title: Ingesta estructurada
  - id: router
    resource: ../../webapp/routers/authoring.py
    title: API del Estudio
  - id: runtime
    resource: ../../webapp/generation/runtime.py
    title: Runner de nas-adk
  - id: tools
    resource: ../../webapp/generation/tools.py
    title: Herramientas de los agentes
  - id: tests
    resource: ../../webapp/tests/test_generation.py
    title: Tests de extremo a extremo
---

# Flujo

```
subida → extracting → awaiting_scope → outlining → awaiting_outline
       → generating → validating → ready | failed | cancelled
```

| Etapa | Código | Artefacto en `authoring-data/jobs/<id>/` |
|---|---|---|
| Ingesta | `document.build_document` | `document.json` (secciones + fragmentos `dN:pPÁG:cN`) |
| Alcance | `POST /jobs/{id}/plan` | `config_json` del trabajo |
| Temario | `pipeline.plan` | `outline.json` (editable con `PUT /jobs/{id}/outline`) |
| Lecciones | `pipeline.generate` (paralelo) | `lessons/cN-lM.json` |
| Evaluación | `pipeline.generate` | `assess/cN.json` (quiz + glosario) |
| Ensamblado | `pipeline.assemble` | `course.json`, `report.json` → borrador en `generated_courses` |

Decisiones: [ADR-017](/decisions/adr-017-staged-generation.md) (etapas),
[ADR-019](/decisions/adr-019-generation-queue.md) (cola) y
[ADR-023](/decisions/adr-023-nas-adk-agents.md) (agentes nas-adk; el motor OpenCode se
retiró). Credenciales: [ADR-024](/decisions/adr-024-user-ai-credentials.md).

# Agentes

Cada llamada al modelo es un agente nas-adk (`runtime.run_agent`) con su `JobToolbox`:

| Agente | Herramientas | Entrega |
|---|---|---|
| `outline` (una sección) | `read_fragment`, `search_document` | `submit_outline` |
| `course` (ficha) | — | `submit_course` |
| `lesson` | `read_fragment`, `search_document`, `check_lesson` | `submit_lesson` (valida con `package.validate_lesson`) |
| `assessment` (quiz + glosario) | `read_fragment`, `search_document` | `submit_assessment` (`validate_assessment`) |

- El mensaje de tarea (`prompts.py`) incluye ya los fragmentos asignados; las
  herramientas amplían contexto. Una entrega inválida devuelve el error al modelo, que
  corrige en el mismo turno; si el agente termina sin entregar hay un reintento.
- Límites (`agents.py`): 4–12 llamadas al modelo por agente, `AULA_GEN_CONTEXT_TOKENS`
  (60 000) y `AULA_AUTHORING_TIMEOUT` por ejecución.
- `_JobCallback` cancela antes de cada llamada si el trabajo se canceló y emite eventos
  `tool` («Consultando un fragmento…») que la página del trabajo muestra en «Actividad».
- Tokens: `metrics.total_usage` del `Runner` se suma a `tokens_in/out` del trabajo.
- Con la suscripción de Claude las lecciones van de una en una (CLI local).

# Endpoints (`/api/v1/authoring`)

- `POST /jobs` (siempre `engine = "adk"`; ya no hay selector de motor).
- `GET /jobs/{id}/document`, `POST /jobs/{id}/plan`, `GET|PUT /jobs/{id}/outline`,
  `POST /jobs/{id}/generate`, `POST /jobs/{id}/retry`, `POST /jobs/{id}/cancel`.
- `GET /jobs/{id}/events` (SSE: eventos `log` y `job`) y `GET /jobs/{id}/history`.
- `PUT /courses/{slug}/package` (edición validada), `POST /courses/{slug}/regenerate`
  (una lección, con instrucciones; conserva el resto del borrador),
  `POST /courses/{slug}/publish` con `visibility` `workspace|public`.
- `PUT /settings` solo para administración de la plataforma.

# Contrato v2

`schema_version` 1 o 2. Novedades: `sources` (ids de fragmento) y
`unsupported` en bloques; preguntas con `kind` `single|multiple|true_false`,
`correct` entero o lista, `difficulty` y `source`; hasta 40 capítulos, 2–12
lecciones por capítulo, 300 lecciones y 20 preguntas por quiz.
`Question.normalize/is_correct` corrigen en servidor.

# Verificación

`verify.verify_package` comprueba que cada cita existe y que el bloque comparte
vocabulario con sus fragmentos (umbral 0,22). El informe guarda `cited_pct`,
bloques `unsupported` y referencias inválidas; la revisión los resalta.

# Configuración

`AULA_GEN_WORKERS`, `AULA_GEN_CONCURRENCY`, `AULA_GEN_INPROCESS`,
`AULA_GEN_MAX_CHARS`, `AULA_GEN_CONTEXT_TOKENS`, `AULA_GEN_MONTHLY_PERSONAL`,
`AULA_GEN_MONTHLY_ORG`, `AULA_LLM_FAKE` (usa `models.FakeAgentLlm`). Detalle en [run](/operations/run.md).

# UI

`/estudio` (subida con arrastrar y soltar, proyectos, unidades, proveedor),
`/estudio/trabajos/[id]` (asistente con pasos, selección de secciones, editor
del temario, progreso en directo) y `/estudio/cursos/[slug]` (revisión con
vista previa real, edición de bloques, quiz y glosario, regeneración y
publicación).

# Actualización 2026-11-14

- Los prompts (`generation/prompts.py`) ya no suponen temas técnicos: piden adaptar
  tono y bloques a la materia y usar `code`/`python` solo en programación,
  datos o cálculo.
- El Estudio exige `require_author` (cuenta individual o profesorado); el
  alumnado recibe 403 ([ADR-021](/decisions/adr-021-account-profiles.md)).
- La cuota mensual del espacio puede fijarla la superadministración
  (`workspaces.settings_json.gen_monthly`); si no, se usan
  `AULA_GEN_MONTHLY_PERSONAL` / `_ORG`.
- Al publicar, la unidad pasa a ser curso activo de quien la abre (último curso
  visitado) y sus documentos fuente aparecen en `/recursos`.
