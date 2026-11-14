---
type: ADR
title: ADR-023 · Agentes propios con nas-adk en lugar de OpenCode
description: Un único motor de generación por etapas en el que cada llamada al modelo es un agente nas-adk con herramientas Python propias; se retiran el subproceso OpenCode y el cliente HTTP propio.
tags: [adr, autoría, generación, agentes, nas-adk, proveedores]
status: stable
date: 2026-11-14
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T20:00:00Z }
sources:
  - id: runtime
    resource: ../../webapp/generation/runtime.py
    title: Puente etapas → Runner de nas-adk
  - id: tools
    resource: ../../webapp/generation/tools.py
    title: Herramientas de los agentes
  - id: agents
    resource: ../../webapp/generation/agents.py
    title: Instrucciones y límites
  - id: models
    resource: ../../webapp/generation/models.py
    title: Ajustes → modelo nas-adk
  - id: providers
    resource: ../../webapp/authoring/providers.py
    title: Catálogo de proveedores
  - id: nasadk
    resource: https://github.com/marcosflz/nas-adk
    title: nas-adk (wheel v0.3.0)
---

# Contexto

El Estudio tenía dos motores: el **por etapas** ([ADR-017](/decisions/adr-017-staged-generation.md)),
con un cliente HTTP propio que pedía JSON y lo extraía con una expresión regular, y
**OpenCode** ([ADR-012](/decisions/adr-012-authoring-opencode.md)), un CLI externo como
subproceso que escribía `course.json` en una pasada. Se quería un agente propio, con
herramientas personalizadas y los proveedores de
[nas-adk](https://github.com/marcosflz/nas-adk) (OpenCode Go, OpenRouter, Anthropic,
endpoints compatibles con OpenAI y la suscripción de Claude vía Claude Code).

# Decisión

- **Un solo motor (`engine = "adk"`)** con las mismas etapas, revisión del temario,
  reanudación y regeneración de lecciones. Desaparecen el selector de motor,
  `authoring/runner.py`, `authoring/agent/AGENTS.md`, `generation/llm.py` y el binario
  OpenCode de la imagen.
- **Cuatro agentes** (`generation/agents.py`): `outline`, `course`, `lesson` y
  `assessment`. Cada uno recibe el mismo mensaje de tarea que antes (`prompts.py`,
  bloque «DATOS DE LA TAREA») y **entrega llamando a `submit_<tarea>(data)`**.
- **Herramientas** (`generation/tools.py`, `JobToolbox`): `read_fragment(chunk_id)`,
  `search_document(query)` (léxica, sobre los fragmentos de la tarea), `check_lesson`
  y las `submit_*`. Las entregas se validan con las reglas reales
  (`package.validate_lesson`, `validate_assessment`); si fallan, nas-adk devuelve el
  error al modelo y este corrige en el mismo turno. Sin shell, red ni rutas de archivo.
- **Runtime** (`generation/runtime.py`): las etapas siguen en hilos; cada agente se
  ejecuta con `asyncio.run` y un modelo nuevo (el cliente async va ligado al bucle).
  Límites por agente (llamadas, turnos, `AULA_GEN_CONTEXT_TOKENS`, `AULA_AUTHORING_TIMEOUT`),
  cancelación antes de cada llamada, un reintento si el agente no entrega, uso de
  tokens sumado al trabajo y eventos `tool` para la actividad de la UI. Los errores de
  nas-adk se traducen (credencial, cuota sin *fallback*, límite, CLI ausente).
- **Proveedores** (`authoring/providers.py`): cada id de SLAnything se traduce a un
  `ModelRouter` (`opencode`, `openrouter`, `anthropic`, `openai-compatible` con su base
  URL) o a `ClaudeCodeLlm` para la suscripción ([ADR-024](/decisions/adr-024-user-ai-credentials.md)).
- `AULA_LLM_FAKE=1` usa `FakeAgentLlm`, que llama a la `submit_*` de la tarea: los tests
  ejercitan el `Runner` real y las herramientas sin red.
- Migración v8: `engine='direct'` → `adk`; los trabajos OpenCode a medias pasan a `failed`.
  Los cursos ya generados no cambian (son paquetes JSON).

# Consecuencias

- Dependencia `nas-adk[anthropic]` fijada a la URL del *release* 0.3.0 en `uv.lock`; la
  build necesita acceso a github.com.
- Los modelos sin *tool calling* fiable pueden no llegar a `submit_*`: un reintento y
  luego error legible (ver [known-issues](/context/known-issues.md)).
- Un proveedor nuevo de nas-adk se añade con una entrada en `providers.PROVIDERS`.
- Los trabajos antiguos de OpenCode siguen listados como «motor anterior»; no tienen etapas.
