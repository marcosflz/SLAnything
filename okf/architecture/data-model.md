---
type: Data Model
title: Modelo de datos SQLite
description: Tablas, columnas y relaciones que sostienen usuarios, progreso y evaluación.
tags: [datos, sqlite, esquema, progreso, quiz]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
sources:
  - id: db
    resource: ../../webapp/db.py
    title: Esquema y conexión SQLite
  - id: repos
    resource: ../../webapp/repositories.py
    title: Consultas y reglas de negocio
---

# Tablas

| Tabla | Clave | Propósito |
|---|---|---|
| `users` | `id` | Cuentas; email único, rol `student`/`teacher` |
| `sessions` | `id` (hash) | Sesiones con CSRF y caducidad |
| `lesson_progress` | `(user_id, course_slug, lesson_slug)` | Completadas, visitas y fechas |
| `quiz_attempts` | `id` | Curso, puntuación, total y respuestas JSON |
| `notes` | `(user_id, course_slug, lesson_slug)` | Apuntes privados |
| `bookmarks` | `(user_id, course_slug, lesson_slug)` | Marcadores |
| `activity` | `(user_id, day, kind)` | Racha y actividad diaria |
| `authoring_jobs` | `id` | Trabajos del Estudio: estado, proveedor, modelo, idiomas, error y fechas |
| `generated_courses` | `slug` | Paquete JSON generado, estado `draft`/`published`, autor, job, `workspace_id`, `visibility` (`workspace`/`public`) y `report_json` |
| `workspaces` | `id` | Espacio `personal` u `organization`; plan, plazas, código de clase |
| `memberships` | `(workspace_id, user_id)` | Rol `owner`/`admin`/`teacher`/`student` |
| `groups`, `group_members` | `id`, `(group_id, user_id)` | Clases o cohortes del espacio |
| `enrollments` | `id` | Curso asignado a un grupo o usuario, con `due_at` |
| `invitations` | `id` | Invitación de un solo uso (hash del token, rol, grupo, caducidad) |
| `audit_log` | `id` | Acciones sensibles por espacio |
| `learning_events` | `id` | Eventos de aprendizaje (ADR-018) |

# Relaciones

- `sessions`, `lesson_progress`, `quiz_attempts`, `notes`, `bookmarks` y `activity`
  referencian `users.id` con `ON DELETE CASCADE`.
- Los cursos y las lecciones viven en código, no en una tabla. `course_slug`
  identifica el curso y `lesson_slug` la lección dentro de él. La combinación es
  única; el progreso de dos cursos nunca se mezcla.
- Los slugs de curso, lección y quiz son únicos en toda la plataforma para
  mantener las URLs históricas `/leccion/{slug}` y `/quiz/{id}`.
- `quiz_attempts` guarda `course_slug` y el `quiz_id` global
  (`quiz-capitulo-N`), no el idioma.
- `quiz_attempts.answers_json` guarda `{question_id: selected_index|null}`.
- `authoring_jobs.owner_id` y `generated_courses.owner_id` referencian
  `users.id`. Los trabajos guardan `languages` y `source_names` como JSON.
- `generated_courses.package_json` es el `course.json` original normalizado. El
  catálogo lo valida al cargarlo; si deja de validar, se ignora y se registra.
- Los cursos generados llevan slugs `gen-*`; el resto sigue viviendo en código.

# Migración v2 → v3

`init_db()` detecta tablas del esquema de un solo curso, las renombra a
`*_legacy`, crea el esquema nuevo y copia las filas asignándolas a
`config.SAMPLE_COURSE_SLUG` (`llm-desde-cero`). Después elimina las tablas
antiguas y fija `PRAGMA user_version = 3`. La v3 solo añade
`authoring_jobs` y `generated_courses` con `CREATE TABLE IF NOT EXISTS`, así que
una base v2 se actualiza sin tocar sus datos. La operación es idempotente.

# Reglas

- Email en minúsculas; `users.email` es `UNIQUE`.
- Sesión: token en claro solo en cookie; en BD se guarda SHA-256.
- `lesson_progress.completed` es 0/1; `completed_at` se actualiza al completar.
- `activity` incrementa un contador por usuario/día/tipo.
- Racha: días consecutivos con actividad, contando desde hoy o ayer.
- SQLite en WAL, `foreign_keys=ON`, `busy_timeout=5000`, una conexión por petición.

# Operación

- `aula.db`, `aula.db-wal` y `aula.db-shm` están en `.gitignore`.
- `init_db()` crea el esquema, aplica las migraciones y, con `AULA_SEED_DEMO=1`,
  siembra las cuatro cuentas demo (una por perfil) y la Academia Demo.
- Los cambios de esquema se añaden como migración numerada en
  `webapp/migrations.py`.
- Copia de seguridad: parar el servidor y copiar `aula.db` (o usar `sqlite3 .backup`).

# Migraciones versionadas (v4 a v8)

Desde 2026-11-13 el esquema evoluciona con `webapp/migrations.py`
([ADR-015](/decisions/adr-015-versioned-migrations.md)). v4 añade espacios,
membresías, grupos, matrículas, invitaciones, auditoría, `learning_events` y
columnas nuevas en `users`, `authoring_jobs` y `generated_courses`; además crea
un espacio personal por usuario. v5 reconstruye `authoring_jobs` sin el CHECK de
estados y añade `engine`, `stage`, `progress_json`, `config_json`, tokens y
`generated_courses.report_json`. `activity.day` pasa a UTC. v6
([ADR-021](/decisions/adr-021-account-profiles.md)) añade
`users.last_course_slug` (curso activo por defecto), borra el espacio personal
vacío de quien solo es alumno, crea la cuenta individual de usuarios sin
espacio y renombra las cuentas demo `@aulallm.local`. `workspaces.settings_json`
guarda `gen_monthly` (cuota fijada por la superadministración). v7
([ADR-022](/decisions/adr-022-invite-only-signup.md)) añade
`platform_invitations` (`kind` individual|teacher, `email`, `workspace_id`,
`academy_name`, `token_hash`, fechas de creación, caducidad, aceptación y
revocación). v8 ([ADR-023](/decisions/adr-023-nas-adk-agents.md),
[ADR-024](/decisions/adr-024-user-ai-credentials.md)) añade `user_ai_settings`
(`user_id` PK, `provider`, `model`, `secret_enc` cifrado, `secret_hint`,
`accepted_personal_at`, `updated_at`) y `authoring_jobs.actor_id` (quién lanzó la
última etapa; se rellena con `owner_id`), pasa `engine='direct'` a `adk` y cierra
como fallidos los trabajos OpenCode a medias. v9
([ADR-025](/decisions/adr-025-multiple-ai-providers.md)) añade `ai_providers`
(`scope_kind` user|workspace, `scope_id`, `provider`, `secret_enc`, `secret_hint`,
`enabled`, `models_json` con los modelos visibles, `default_model`,
`accepted_personal_at`, `updated_by`, `updated_at`; único por ámbito y proveedor) y
`users.ai_default_json` (modelo predeterminado), y copia ahí las filas de
`user_ai_settings`, que deja de usarse. La elección de modelo de cada trabajo va en
`authoring_jobs.config_json.ai`. Detalle de uso
en [tenancy-analytics](/architecture/tenancy-analytics.md).
