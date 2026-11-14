---
type: Architecture
title: Espacios, usuarios y analítica
description: Tenancy por espacios de trabajo, roles, grupos, invitaciones, auditoría, cuenta y eventos de aprendizaje con sus KPIs.
tags: [usuarios, roles, tenancy, analítica, kpis, auditoría]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: workspaces
    resource: ../../webapp/workspaces.py
    title: Espacios y roles
  - id: admin
    resource: ../../webapp/routers/admin.py
    title: Administración y cuenta
  - id: analytics
    resource: ../../webapp/analytics.py
    title: Eventos y KPIs
  - id: migrations
    resource: ../../webapp/migrations.py
    title: Migraciones v4/v5
---

# Modelo

- `workspaces` (`personal`/`organization`, `plan`, `seat_limit`,
  `join_code`), `memberships` (rol `owner|admin|teacher|student`).
- `groups`, `group_members`, `enrollments` (curso por grupo o usuario, con
  `due_at`), `invitations` (token guardado como hash, 14 días, un solo uso,
  opcionalmente ligado a un correo y a un grupo), `audit_log`.
- `users` añade `is_platform_admin`, `last_login_at`, `disabled_at`, `locale`.
- `learning_events` para la analítica.

Decisiones: [ADR-016](/decisions/adr-016-workspaces.md) y
[ADR-018](/decisions/adr-018-learning-events.md). Esquema completo en
[data-model](/architecture/data-model.md).

# Permisos

| Acción | Rol mínimo en el espacio activo |
|---|---|
| Aprender, progreso, cuenta | cualquier miembro |
| Estudio, analítica de curso, panel de estudiantes | `teacher` (en el espacio personal el usuario es `owner`) |
| Miembros, grupos, invitaciones, auditoría, métricas | `admin` |
| Asignar o retirar la propiedad, invitar admins | `owner` |
| Proveedor de IA, publicar en el catálogo abierto | administración de la plataforma |

# API

- `/api/v1/workspaces`: listar, `switch`, crear academia, `join` por código.
- `/api/v1/admin/*`: `members` (rol, expulsar), `join-code`, `groups`
  (+ `members`, `enrollments`), `invitations`, `audit`, `metrics`.
- `/api/v1/invitations/{token}` (pública) y `/accept`.
- `/api/v1/account`: perfil, `password` (cierra otras sesiones),
  `sessions/revoke-others`.
- `/api/v1/events`, `/api/v1/analytics/me`, `/api/v1/analytics/course`
  (+ `.csv`, filtro `group` y `days`).

# KPIs

- **Alumno**: minutos de estudio (latidos), objetivo semanal, racha de
  aprendizaje, fecha estimada de fin, dominio por capítulo (40 % lecciones +
  60 % mejor nota), evolución de notas, preguntas a repasar, práctica.
- **Profesorado**: activos, progreso medio, tasa de aprobados, en riesgo
  (inactivo ≥ 7 días, nota < 50 o sin empezar), embudo y abandono, mapa de
  calor, distribución del tiempo, análisis de ítems (p, discriminación,
  distractor).
- **Administración**: DAU/WAU, plazas, unidades, éxito y duración de las
  generaciones.

# UI

`/` (dashboard), `/analitica`, `/admin`, `/admin/usuarios`, `/admin/grupos`,
`/admin/invitaciones`, `/admin/auditoria`, `/cuenta`, `/invitacion/[token]`.
