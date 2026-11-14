---
type: ADR
title: ADR-016 · Espacios de trabajo (tenancy)
description: Cada usuario tiene un espacio personal y las academias son espacios de organización con roles owner/admin/teacher/student.
tags: [adr, usuarios, tenancy, roles, seguridad]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: workspaces
    resource: ../../webapp/workspaces.py
    title: Espacios y roles
  - id: deps
    resource: ../../webapp/deps.py
    title: Dependencias de rol
---

# Contexto

El producto pasa a ser SaaS multi-organización con dos tipos de cuenta:
academias (profesorado y administración generan contenido) y cuentas
individuales (cualquiera sube sus documentos para sí mismo). Solo existían los
roles globales `student`/`teacher` y todos los profesores veían todo.

# Decisión

- Tablas `workspaces` (`personal` | `organization`) y `memberships` con rol
  `owner`, `admin`, `teacher` o `student`. Registrarse crea el espacio
  personal (owner). La academia demo tiene a la profesora como owner.
- Espacio activo por cookie `aula_ws` o cabecera `X-Workspace`, validado
  contra la membresía en `deps.get_current_user`; se exponen `workspace`,
  `workspaces`, `ws_role` y `permissions` al frontend.
- `require_role(min)` sustituye la comprobación de `users.role`;
  `require_teacher` = teacher+, `require_admin` = admin+,
  `require_platform_admin` = `users.is_platform_admin`.
- Cursos generados, trabajos del Estudio, analítica y panel del profesor se
  filtran por espacio. Un curso generado es visible para los miembros de su
  espacio o para todos si su `visibility` es `public` (solo la administración
  de la plataforma publica en abierto).
- Grupos, matrículas por grupo, invitaciones de un solo uso, código de clase y
  `audit_log` cuelgan del espacio.

# Consecuencias

- Los progresos no llevan `workspace_id`: el slug de curso es global y la
  pertenencia se resuelve por miembros.
- `users.role` queda como dato heredado.
