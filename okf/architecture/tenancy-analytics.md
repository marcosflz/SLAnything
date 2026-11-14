---
type: Architecture
title: Espacios, usuarios y analítica
description: Perfiles de cuenta, tenancy por espacios, matriz de permisos, superadmin, grupos, matrículas, invitaciones, auditoría y eventos de aprendizaje con sus KPIs.
tags: [usuarios, roles, perfiles, tenancy, analítica, kpis, auditoría, superadmin]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
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
    title: Migraciones v4/v5/v6
  - id: platform
    resource: ../../webapp/routers/platform.py
    title: Superadministración
  - id: deps
    resource: ../../webapp/deps.py
    title: permissions_for, profile_for y dependencias
---

# Perfiles (ADR-021) y altas (ADR-022)

Por defecto **no hay registro abierto** (`AULA_OPEN_SIGNUP=0`,
[ADR-022](/decisions/adr-022-invite-only-signup.md)): la superadministración
invita a cuentas individuales y a profesorado (academia nueva o existente) desde
`/plataforma/invitaciones`, y el profesorado invita a su alumnado desde
`/admin/invitaciones`. Con `AULA_OPEN_SIGNUP=1` vuelve el alta libre como
cuenta individual, academia o código de clase.

| Perfil | Cómo se obtiene | Espacio activo |
|---|---|---|
| Autodidacta (`self_learner`) | invitación de plataforma `individual` | `personal`, rol `owner` |
| Alumno (`student`) | invitación del profesorado (o código, ya registrado) | academia, rol `student` (sin espacio personal) |
| Profesorado (`teacher`) | invitación de plataforma `teacher` a una academia existente | academia, rol `teacher` |
| Administración de la academia (`academy_admin`) | invitación de plataforma `teacher` con academia nueva (owner), o rol `admin` | academia |
| Superadmin | `users.is_platform_admin` | cualquiera; añade el panel `/plataforma` |

`deps.profile_for(role, kind)` calcula el perfil de presentación. Un alumno
puede abrir su cuenta individual (`POST /api/v1/workspaces/personal`) sin dejar
de ser alumno en su academia (con registro cerrado, solo el superadmin crea
espacios fuera de una invitación). Sin ningún espacio, la UI lleva a
`/bienvenida`.

| Invitación | Quién la crea | Resultado |
|---|---|---|
| Plataforma · `individual` | superadmin | cuenta individual |
| Plataforma · `teacher` + academia | superadmin | profesorado de esa academia |
| Plataforma · `teacher` sin academia | superadmin | academia nueva con el invitado como owner |
| Academia · `student` | profesorado, admin u owner (`teach`) | alumno de la academia |
| Academia · `teacher` / `admin` | admin / owner, **solo con registro abierto** | rol en la academia |

El profesorado sin `manage` ve y revoca solo sus invitaciones.


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

`deps.permissions_for(role, kind, platform)` es la única fuente; la API la
aplica con `require_author`, `require_teaching`, `require_admin` (= `manage`) y
`require_platform_admin`, y el frontend la usa para la navegación.

| Permiso | Individual | Alumno | Profesorado | Admin/owner academia |
|---|---|---|---|---|
| `learn` · aprender, progreso, cuenta | ✔ | ✔ | ✔ | ✔ |
| `author` · Estudio | ✔ | ✘ | ✔ | ✔ |
| `teach` · analítica de curso, estudiantes | ✘ | ✘ | ✔ | ✔ |
| `manage` · miembros, grupos, invitaciones, auditoría, métricas | ✘ | ✘ | ✘ | ✔ |
| `owner` · propiedad, invitar admins | ✔ (propio) | ✘ | ✘ | solo owner |
| `platform` · panel `/plataforma`, proveedor de IA, catálogo abierto | superadmin | | | |

`permissions.admin` sigue existiendo como alias de `manage`.

# Matrículas

`repositories.assigned_courses` cruza `enrollments` (por grupo o usuario) con
los grupos del usuario; el catálogo devuelve `assigned` y `due_at` y pone los
cursos asignados primero (por fecha límite). El alumnado sigue viendo el resto
de cursos publicados en su academia debajo.

# API

- `/api/v1/auth/register`: con registro cerrado exige `invite` (403 sin ella);
  con registro abierto, `account` = `individual` | `academy` | `join`.
  `academy_name` acompaña a las invitaciones de academia nueva.
- `/api/v1/invitations/{token}` (`source`, `kind`, `needs_academy_name`) y
  `/accept` (`academy_name` opcional), para invitaciones de academia y de
  plataforma.
- `/api/v1/admin/invitations`: `teach`; devuelve `roles` invitables.
- `/api/v1/workspaces`: listar, `switch`, crear academia, `join` por código,
  `personal` (abrir la cuenta individual).
- `/api/v1/platform/*` (superadmin): `overview`, `users` (+`PATCH`),
  `workspaces` (+`PATCH` plan, plazas y cuota `gen_monthly`; `DELETE` academias
  sin cursos), `courses` (+`visibility`, `unpublish`), `ai`, `invitations`
  (+`POST`, `DELETE`).
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
- **Administración de la academia**: DAU/WAU, plazas, unidades, éxito y
  duración de las generaciones.
- **Plataforma**: usuarios (activos semanales, desactivados), espacios por tipo,
  cursos publicados/abiertos/borradores y generaciones del mes.

# UI

`/` (dashboard por perfil), `/analitica`, `/admin`, `/admin/usuarios`,
`/admin/grupos`, `/admin/invitaciones`, `/admin/auditoria`, `/plataforma`,
`/plataforma/usuarios`, `/plataforma/invitaciones`, `/plataforma/espacios`, `/plataforma/cursos`,
`/plataforma/ia`, `/cuenta`, `/bienvenida`, `/invitacion/[token]`.
