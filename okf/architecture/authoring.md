---
type: Architecture
title: Estudio de autoría · agentes nas-adk, proveedores y credenciales
description: Piezas del Estudio que convierten documentos en unidades validadas, cómo se eligen proveedor y credenciales y cómo se integran los cursos generados en el catálogo.
tags: [autoría, nas-adk, agentes, proveedores, credenciales, documentos, catálogo, seguridad]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T20:00:00Z }
sources:
  - id: authoring
    resource: ../../docs/AUTHORING.md
    title: Guía del Estudio
  - id: package
    resource: ../../webapp/authoring/package.py
    title: Contrato y validación
  - id: providers
    resource: ../../webapp/authoring/providers.py
    title: Proveedores → nas-adk
  - id: credentials
    resource: ../../webapp/authoring/credentials.py
    title: Credenciales por usuario
  - id: store
    resource: ../../webapp/authoring/store.py
    title: Persistencia y catálogo dinámico
  - id: router
    resource: ../../webapp/routers/authoring.py
    title: API del Estudio
---

# Piezas

| Módulo | Responsabilidad |
|---|---|
| `webapp/authoring/settings.py` | Proveedor de la **plataforma** en `authoring/settings.json` (0600); estado del motor (versión de nas-adk) y del CLI `claude`. |
| `webapp/authoring/credentials.py` | Proveedor **propio** de cada usuario (`user_ai_settings`, secreto cifrado) y `resolve(user_id)`. |
| `webapp/authoring/providers.py` | Catálogo de proveedores y su traducción a `ModelRouter` de nas-adk (`router_kwargs`). |
| `webapp/authoring/extract.py` | Texto de PDF, DOCX, EPUB, ODT, Markdown, HTML y TXT. |
| `webapp/authoring/package.py` | Contrato JSON, saneado HTML, `validate_lesson`/`validate_assessment` y conversión a `Course`/`Program`. |
| `webapp/authoring/store.py` | `authoring_jobs` (con `actor_id`), `generated_courses`, subidas, `meta.json` y caché de publicados. |
| `webapp/generation/` | Etapas y agentes nas-adk: ver [generation](/architecture/generation.md). |
| `webapp/routers/authoring.py` | API `/api/v1/authoring`. |
| `webapp/routers/account_ai.py` | API `/api/v1/account/ai` (proveedor propio). |
| `frontend/src/app/estudio/`, `components/studio/`, `components/account/UserAiPanel.tsx` | Estudio, asistente, revisión y panel «Proveedor de IA» de «Mi cuenta». |

Decisiones: [ADR-023](/decisions/adr-023-nas-adk-agents.md) (agentes nas-adk; sustituye a
[ADR-012](/decisions/adr-012-authoring-opencode.md)) y
[ADR-024](/decisions/adr-024-user-ai-credentials.md) (credenciales por usuario).

# Proveedores

| Id | nas-adk | Nivel |
|---|---|---|
| `opencode-go` | `opencode` | plataforma y usuario |
| `opencode` (Zen gratuitos) | `openai-compatible` + `https://opencode.ai/zen/v1` | ambos |
| `anthropic` | `anthropic` (API de pago) | ambos |
| `openrouter` | `openrouter` | ambos |
| `openai`, `google`, `deepseek` | `openai-compatible` con su URL fija | ambos |
| `custom`, `ollama`, `lmstudio` | `openai-compatible` con base URL editable | solo plataforma |
| `claude-code` | `ClaudeCodeLlm` (suscripción personal) | solo usuario |

# Con qué se genera

`credentials.resolve(actor)` → proveedor propio del actor si está completo (y, para la
suscripción, con el consentimiento marcado); si no, el de la plataforma. El **actor** es
quien lanza la acción: crear el trabajo, planificar, generar, reintentar o regenerar una
lección (`authoring_jobs.actor_id`; la reanudación tras reinicio usa el último). El
Estudio muestra «Generarás con…» (`/api/v1/authoring` → `ai`). El alumnado no tiene
`author`: no configura proveedor ni genera.

# Catálogo dinámico

`content_for(lang, course_slug)` combina los cursos de ejemplo (si están activos) con los
paquetes publicados de `generated_courses`. Los slugs generados llevan prefijo `gen-`;
lecciones y quizzes también. La caché de `store.dynamic_content()` se invalida al guardar,
publicar, despublicar o borrar. Los cursos generados usan los mismos `Course`, `Program`,
`Chapter`, `Lesson` y `Quiz` que el ejemplo.

# Contrato y calidad

- `schema_version` 1 o 2; hasta 40 capítulos, 2–12 lecciones por capítulo, 300 lecciones.
- Un quiz por capítulo (4–20 preguntas `single|multiple|true_false`) y 6–24 términos.
- Cada lección empieza por `lead`, termina en `keypoints` y tiene `callout` y `check`;
  mínimo 220 palabras.
- Bloques: `lead`, `p`, `h2`, `h3`, `callout`, `table`, `quote`, `list`, `keypoints`,
  `check`, `divider`, `code`, `python`. HTML con lista blanca.
- Los bloques `python` se compilan antes de guardar y solo los ejecuta el sandbox.
- ES+EN: misma estructura de slugs y mismas respuestas correctas.

# Seguridad

- Los agentes solo tienen herramientas Python sobre los fragmentos del trabajo; sin shell,
  red ni rutas. Los documentos se tratan como datos no confiables.
- Secretos de plataforma en `settings.json` (0600); los de usuario cifrados con Fernet
  (clave derivada de `AULA_SECRET`). Ninguno se devuelve a la API.
- La suscripción solo entra en el entorno del proceso hijo del CLI (`UserEnvTransport`),
  con `CLAUDE_CONFIG_DIR` propio por usuario y `env_policy="scrub"`.
- Los usuarios no fijan base URL (sin SSRF); solo la plataforma usa endpoints propios.

# Pruebas

`test_authoring.py` (contrato, saneado, ajustes, mapeo de proveedores, API, publicación),
`test_generation.py` (flujo completo con `FakeAgentLlm`), `test_adk_agents.py`
(herramientas, runtime, errores, cancelación, transporte de la suscripción) y
`test_ai_credentials.py` (cifrado, alumnado 403, consentimiento, aislamiento entre
usuarios, plataforma sin suscripción, rotación del secreto).
