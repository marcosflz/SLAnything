---
type: Architecture
title: Generación por etapas
description: Cómo un documento se convierte en una unidad didáctica revisable con el motor direct (ingesta, temario, lecciones, evaluación, verificación, cola y SSE).
tags: [autoría, generación, llm, citas, cola, sse]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
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

Decisión: [ADR-017](/decisions/adr-017-staged-generation.md). Cola:
[ADR-019](/decisions/adr-019-generation-queue.md). El motor `opencode`
original sigue documentado en [authoring](/architecture/authoring.md).

# Endpoints (`/api/v1/authoring`)

- `POST /jobs` con `engine=direct` (por defecto `AULA_GEN_ENGINE`).
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
`AULA_GEN_MAX_CHARS`, `AULA_GEN_MONTHLY_PERSONAL`, `AULA_GEN_MONTHLY_ORG`,
`AULA_LLM_FAKE`. Detalle en [run](/operations/run.md).

# UI

`/estudio` (subida con arrastrar y soltar, proyectos, unidades, proveedor),
`/estudio/trabajos/[id]` (asistente con pasos, selección de secciones, editor
del temario, progreso en directo) y `/estudio/cursos/[slug]` (revisión con
vista previa real, edición de bloques, quiz y glosario, regeneración y
publicación).

# Actualización 2026-11-14

- Los prompts (`generation/prompts.py`) y el agente de OpenCode
  (`authoring/agent/AGENTS.md`) ya no suponen temas técnicos: piden adaptar
  tono y bloques a la materia y usar `code`/`python` solo en programación,
  datos o cálculo.
- El Estudio exige `require_author` (cuenta individual o profesorado); el
  alumnado recibe 403 ([ADR-021](/decisions/adr-021-account-profiles.md)).
- La cuota mensual del espacio puede fijarla la superadministración
  (`workspaces.settings_json.gen_monthly`); si no, se usan
  `AULA_GEN_MONTHLY_PERSONAL` / `_ORG`.
- Al publicar, la unidad pasa a ser curso activo de quien la abre (último curso
  visitado) y sus documentos fuente aparecen en `/recursos`.
