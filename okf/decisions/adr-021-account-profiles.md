---
type: ADR
title: ADR-021 · Perfiles de cuenta - individual, academia y superadmin
description: Dos altas (cuenta individual o academia) más invitación o código; matriz de permisos learn/author/teach/manage/platform; el alumnado solo consume; superadmin con panel /plataforma.
tags: [adr, usuarios, roles, permisos, tenancy, seguridad]
status: stable
date: 2026-11-14
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
sources:
  - id: deps
    resource: ../../webapp/deps.py
    title: permissions_for y dependencias
  - id: workspaces
    resource: ../../webapp/workspaces.py
    title: Espacios, invitaciones y código de clase
  - id: platform
    resource: ../../webapp/routers/platform.py
    title: Superadministración
  - id: migrations
    resource: ../../webapp/migrations.py
    title: Migración v6
---

# Contexto

[ADR-016](/decisions/adr-016-workspaces.md) daba a **todo** usuario un espacio
personal donde era `owner`, así que cualquier alumno podía usar el Estudio y la
API de profesorado (`require_teacher` dejaba pasar al owner personal a
`/teacher` y `/analytics/course`). No existía un panel para la
superadministración y la profesora demo era superadmin. Se pidieron cuatro
perfiles: admin, profesor, alumno y *self-learner* (genera unidades como un
profesor pero sin gestión de aula).

# Decisión

**Altas.** O se crea una cuenta individual o se crea una academia:

| Alta | Resultado | Perfil |
|---|---|---|
| Cuenta individual | espacio `personal`, rol `owner` | autodidacta (`self_learner`) |
| Crear academia | espacio `organization`, rol `owner` | administración de la academia |
| Invitación o código de clase | membresía con el rol invitado (o `student`) | alumno, profesorado o admin; **sin espacio personal** |

`POST /api/v1/auth/register` acepta `account` (`individual` · `academy` ·
`join`), `academy_name`, `join_code` e `invite`, y valida el acceso antes de
crear la cuenta. Un alumno puede abrir después su cuenta individual con
`POST /api/v1/workspaces/personal`; en la academia sigue siendo alumno.

**Permisos** (única fuente, `deps.permissions_for(role, kind, platform)`):

| Permiso | Individual (owner) | Alumno | Profesorado | Admin/owner academia |
|---|---|---|---|---|
| `learn` | ✔ | ✔ | ✔ | ✔ |
| `author` (Estudio) | ✔ | ✘ | ✔ | ✔ |
| `teach` (analítica, estudiantes) | ✘ | ✘ | ✔ | ✔ |
| `manage` (miembros, grupos, invitaciones, auditoría) | ✘ | ✘ | ✘ | ✔ |
| `platform` | según `users.is_platform_admin` | | | |

`permissions.admin` se mantiene como alias de `manage`. Dependencias:
`require_author`, `require_teaching`, `require_admin` (manage) y
`require_platform_admin`. `deps.profile_for` da el perfil de presentación
(`self_learner`, `student`, `teacher`, `academy_admin`).

**Superadmin.** Flag global `users.is_platform_admin` (por
`AULA_PLATFORM_ADMINS` o desde el panel). Router `/api/v1/platform/*`:
resumen, usuarios (desactivar, dar o quitar superadmin; nunca el último),
espacios (plan, plazas y cuota mensual `settings.gen_monthly`), cursos
generados (visibilidad abierta, despublicar) y proveedor de IA. Frontend
`/plataforma/*`.

**Matrículas aplicadas.** El catálogo marca `assigned` y `due_at` cruzando
`enrollments` con los grupos del usuario y pone los asignados primero.

**Migración v6.** `users.last_course_slug`; borra el espacio personal vacío de
quien solo es alumno en academias; crea la cuenta individual de usuarios sin
espacio (bases v3); renombra las cuentas demo `@aulallm.local` a
`@slanything.local` y retira la superadmin a la profesora.

**Cuentas demo** (con `AULA_SEED_DEMO=1`): `alumno@` (alumno de la Academia
Demo), `profe@` (propietaria de la academia), `autodidacta@` (individual) y
`admin@` (superadmin), todas en `slanything.local`.

# Consecuencias

- `users.role` deja de leerse; se conserva en el esquema.
- Un usuario sin ningún espacio va a `/bienvenida` (unirse, cuenta individual o
  academia).
- Corrección asociada: `get_db` se usa con `Depends(get_db, scope="function")`
  para confirmar antes de responder (ver [security](/architecture/security.md)).
- Matiza [ADR-016](/decisions/adr-016-workspaces.md): el espacio personal ya
  no es universal.
