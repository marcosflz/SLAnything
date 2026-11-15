---
type: ADR
title: ADR-024 · Credenciales de IA por usuario y suscripción personal de Claude
description: Quien crea unidades puede usar su propia API key o su suscripción de Claude; las credenciales se resuelven siempre con quien lanza la acción y nunca se comparten.
tags: [adr, autoría, seguridad, proveedores, suscripción, perfiles]
status: stable
date: 2026-11-14
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T20:00:00Z }
sources:
  - id: credentials
    resource: ../../webapp/authoring/credentials.py
    title: Credenciales por usuario
  - id: router
    resource: ../../webapp/routers/account_ai.py
    title: /api/v1/account/ai
  - id: models
    resource: ../../webapp/generation/models.py
    title: UserEnvTransport y suscripción
---

> Ampliado por [ADR-025](/decisions/adr-025-multiple-ai-providers.md): varios proveedores a la vez
> (tabla `ai_providers`, migración v9), modelos visibles, ChatGPT, claves de academia y selector de
> modelo en el Estudio. Las reglas de este ADR siguen vigentes.

# Contexto

Con nas-adk ([ADR-023](/decisions/adr-023-nas-adk-agents.md)) se puede usar la suscripción
de Claude (Pro/Max) a través del CLI de Claude Code. Las condiciones de Anthropic no
permiten compartir una suscripción ni atender a terceros con ella, y SLAnything es
multiusuario. Se decidió que **cada usuario configure su propia credencial** y que nunca
se use para otra persona.

# Decisión

- **Dos niveles de proveedor**: el de la **plataforma** (superadmin, `/plataforma/ia`,
  `settings.json` 0600) y el **propio** de cada usuario con permiso `author`
  («Mi cuenta → Proveedor de IA», tabla `user_ai_settings`, migración v8).
  `credentials.resolve(user_id)` devuelve el propio si está completo; si no, el de la
  plataforma.
- **Siempre quien lanza la acción**: `authoring_jobs.actor_id` guarda quién lanzó la
  última etapa (crear, planificar, generar, reintentar); la reanudación usa ese actor.
  Regenerar una lección pasa el id de quien lo pide. Si un admin actúa sobre un trabajo
  ajeno, se usan **sus** credenciales o las de la plataforma, nunca las del autor.
- **Alumnado**: sin permiso `author` no ve el panel ni el Estudio (403). Leer un curso
  publicado no llama al modelo, así que la credencial de un profesor nunca se usa en
  nombre de sus alumnos.
- **Suscripción (`claude-code`)**: solo a nivel de usuario (la plataforma la rechaza).
  El usuario ejecuta `claude setup-token` en su equipo, pega el token y marca que es su
  suscripción personal (`accepted_personal_at`). Al generar, `UserEnvTransport` añade
  `CLAUDE_CODE_OAUTH_TOKEN`, `CLAUDE_CONFIG_DIR` y `HOME` propios
  (`AUTHORING_DIR/claude/<user_id>`, 0700) **solo al proceso hijo**; `env_policy="scrub"`
  quita cualquier `ANTHROPIC_*` del servidor y nas-adk exige `authMethod=oauth_token`
  y `apiKeySource=none`. Concurrencia 1 por ejecución.
- **Secretos**: cifrados con Fernet (clave derivada de `AULA_SECRET`); la API solo
  devuelve si existen y sus 4 últimos caracteres. Rotar `AULA_SECRET` los invalida
  (el usuario los vuelve a pegar; la UI avisa).
- **Sin SSRF**: los usuarios no eligen base URL; `custom`, `ollama` y `lmstudio` son
  solo de plataforma.
- Interruptores: `AULA_USER_PROVIDERS` (proveedor propio) y `AULA_SUBSCRIPTION_PROVIDER`
  (solo la suscripción). Imagen Docker con el CLI fijado (`CLAUDE_CODE_VERSION`,
  `INSTALL_CLAUDE_CODE=0` para omitirlo).

# Consecuencias

- La responsabilidad de cumplir las condiciones de Anthropic recae en cada titular; la
  plataforma solo garantiza que su suscripción no se usa para otra persona.
- Con suscripción no hay streaming y las lecciones se generan de una en una: más lento.
- La cuota mensual del espacio (`gen_monthly`) se aplica igual con credencial propia.
