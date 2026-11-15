---
type: ADR
title: ADR-025 · Varios proveedores de IA, modelos visibles y selector en el Estudio
description: Cada persona configura varios proveedores a la vez (claves de API y suscripciones de Claude y ChatGPT), elige qué modelos ve y cuál es el predeterminado; las academias comparten claves de API con su profesorado y el Estudio elige modelo por trabajo.
tags: [adr, autoría, proveedores, suscripción, chatgpt, claude, academia, modelos]
status: stable
date: 2026-11-15
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-15T13:00:00Z }
sources:
  - id: credentials
    resource: ../../webapp/authoring/credentials.py
    title: Proveedores por ámbito, predeterminado y resolución
  - id: catalog
    resource: ../../webapp/authoring/catalog.py
    title: Catálogo de modelos por proveedor
  - id: links
    resource: ../../webapp/authoring/links.py
    title: Vinculación de Claude y ChatGPT desde la web
  - id: router
    resource: ../../webapp/routers/account_ai.py
    title: /api/v1/account/ai, /api/v1/admin/ai y /api/v1/ai/models
  - id: migration
    resource: ../../webapp/migrations.py
    title: Migración v9 (ai_providers, users.ai_default_json)
---

# Contexto

[ADR-024](/decisions/adr-024-user-ai-credentials.md) dio a cada persona **un** proveedor propio,
con el modelo escrito a mano. Hacía falta lo mismo que en Nexus: tener varios proveedores activos
a la vez, elegir qué modelos de cada uno se ven (OpenRouter ofrece cientos) y elegir modelo al
generar. También faltaban el plan de ChatGPT y que una academia pudiera dar claves a su
profesorado. nas-adk 0.4.0 añade el token de Claude por instancia, el listado de modelos de la
suscripción (sin inferencia) y el proveedor de ChatGPT («Sign in with ChatGPT»).

# Decisión

- **Tabla `ai_providers`** (migración v9): una configuración por (ámbito, proveedor), con el secreto
  cifrado, `enabled`, `models_json` (`[{id, label}]` visibles) y `default_model`.
  - Ámbito `user`: claves de API y suscripciones personales de quien tiene permiso `author`.
  - Ámbito `workspace`: **solo claves de API** que la administración de una academia (`manage`)
    comparte con su profesorado. Nunca suscripciones, nunca URL base propia.
  - `users.ai_default_json` guarda el modelo predeterminado de la persona. Las filas de
    `user_ai_settings` (v8) se copian como ámbito `user`; la tabla antigua deja de usarse.
- **Catálogo de proveedores** (`providers.py`): `kind` (`api`/`subscription`), `link`
  (`key`/`claude`/`chatgpt`) y `models_url` fija para listar modelos (sin SSRF). Nuevo proveedor
  `chatgpt` (personal, solo de usuario). Suscripciones: Claude, ChatGPT y OpenCode Go.
- **Listado de modelos**: Claude con el protocolo de control del CLI (`list_models`, añade las
  versiones conocidas del CLI fijado si el token de `setup-token` solo anuncia alias); ChatGPT con
  `GET /v1/models` del plan; el resto con la URL fija del proveedor.
- **Vinculación desde la web** (`links.py`, rutas `async`): Claude con el `claude setup-token`
  oficial en un pseudo-terminal (o pegando el token); ChatGPT con OAuth+PKCE (la redirección va a
  `127.0.0.1:1455`, la persona pega esa dirección). Exigen consentimiento de uso personal. Las
  sesiones viven en memoria, ligadas a su usuario y con caducidad.
- **ChatGPT**: el token de acceso dura 1 h y el de refresco rota en cada uso. La renovación se
  serializa por persona (bloqueo + relectura) y guarda siempre el token rotado; si OpenAI la
  rechaza, se borra la sesión y se pide volver a vincular.
- **Resolución** (`credentials.resolve(user, workspace, choice)`): el modelo elegido si esa persona
  puede usarlo → su predeterminado → su primer proveedor listo → la plataforma. Una clave de
  academia solo la usa quien es profesorado o más de esa academia; una suscripción, solo su titular.
- **Estudio**: selector agrupado (`/api/v1/ai/models`: propios, de la academia y de la plataforma)
  al crear la unidad, en las etapas del asistente y al regenerar una lección. La elección se guarda
  en `authoring_jobs.config_json.ai` y cada etapa la vuelve a resolver con quien la lanza
  (`actor_id`), como en ADR-024.

# Consecuencias

- Sigue vigente todo lo de ADR-024: secretos cifrados, quien lanza la acción, alumnado sin acceso,
  la plataforma sin suscripciones y sin URL base para usuarios.
- «Sign in with ChatGPT» está en *preview* y OpenAI lo plantea para apps open source y alojadas
  localmente: cada titular es responsable de cumplir sus condiciones, igual que con Anthropic.
- Las sesiones de vinculación en memoria exigen un único proceso de uvicorn (el despliegue actual).
- `user_ai_settings` queda como histórico; se puede borrar en una migración futura.
