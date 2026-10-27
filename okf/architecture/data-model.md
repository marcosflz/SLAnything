---
type: Data Model
title: Modelo de datos SQLite
description: Tablas, columnas y relaciones que sostienen usuarios, progreso y evaluación.
tags: [datos, sqlite, esquema, progreso, quiz]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
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
| `generated_courses` | `slug` | Paquete JSON generado, estado `draft`/`published`, autor y job |

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
`config.DEFAULT_COURSE_SLUG` (`llm-desde-cero`). Después elimina las tablas
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
- `init_db()` crea el esquema y siembra demo/profesor con `INSERT OR IGNORE`.
- No hay migraciones versionadas todavía. Para un cambio de columna, añade una
  migración idempotente en `init_db()` o un script en `tools/`.
- Copia de seguridad: parar el servidor y copiar `aula.db` (o usar `sqlite3 .backup`).
