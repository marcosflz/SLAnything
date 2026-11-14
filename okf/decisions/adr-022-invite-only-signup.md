---
type: ADR
title: ADR-022 · Registro solo por invitación
description: Sin registro abierto por defecto; la superadministración invita a cuentas individuales y profesorado (academia nueva o existente) y el profesorado invita a su alumnado.
tags: [adr, usuarios, registro, invitaciones, seguridad, perfiles]
status: stable
date: 2026-11-14
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
sources:
  - id: config
    resource: ../../webapp/config.py
    title: AULA_OPEN_SIGNUP
  - id: workspaces
    resource: ../../webapp/workspaces.py
    title: describe_invitation y accept_any_invitation
  - id: platform
    resource: ../../webapp/routers/platform.py
    title: Invitaciones de plataforma
  - id: admin
    resource: ../../webapp/routers/admin.py
    title: Invitaciones de academia
---

# Contexto

Con [ADR-021](/decisions/adr-021-account-profiles.md) cualquiera podía darse de
alta como cuenta individual o crear una academia desde `/registro`, y cualquier
usuario podía crear academias o abrir su cuenta individual desde el selector de
espacio. Se pidió desactivar el registro automático: solo la superadministración
incorpora cuentas individuales y profesorado, y el profesorado invita a su
alumnado.

# Decisión

- `AULA_OPEN_SIGNUP` (por defecto `0`) controla el modo; `config.OPEN_SIGNUP` se
  lee en cada petición y se expone como `site.signup_open`.
- **Registro cerrado**: `POST /api/v1/auth/register` sin `invite` devuelve 403
  (también `account=individual|academy|join`). `POST /api/v1/workspaces`
  (crear academia) y `POST /api/v1/workspaces/personal` exigen superadmin. Unirse
  con código de clase sigue disponible para usuarios ya registrados.
- **Invitaciones de plataforma** (tabla `platform_invitations`, migración v7,
  `/api/v1/platform/invitations`, pantalla `/plataforma/invitaciones`):
  - `individual` → cuenta individual (autodidacta);
  - `teacher` con `workspace_id` → profesorado de una academia existente;
  - `teacher` sin academia → crea su academia y es su propietario
    (`academy_name` opcional; si falta, lo escribe al aceptar).
  Un solo uso, 14 días, opcionalmente ligadas a un correo, revocables.
- **Invitaciones de academia**: las crea quien tiene `teach` (profesorado,
  admin u owner). Con registro cerrado solo pueden ser de **alumnado**; el
  profesorado sin `manage` ve y revoca solo las suyas. Con registro abierto se
  mantiene lo anterior (la administración invita profesorado; el owner, admins).
- `GET /api/v1/invitations/{token}` describe ambas fuentes (`source`, `kind` =
  `member` | `individual` | `academy_owner`, `needs_academy_name`) y
  `accept` / registro con `invite` usan `workspaces.accept_any_invitation`.
- Frontend: portada y cabecera sin «Empezar gratis», `/registro` muestra el
  aviso de invitación, login sin enlace de alta, selector de espacio, «Mi
  cuenta» y `/bienvenida` sin crear academia ni cuenta individual; el
  profesorado tiene «Invitar alumnos» y en `/admin/invitaciones` solo esa
  pestaña.

# Consecuencias

- Las cuentas demo siguen sembrándose (`AULA_SEED_DEMO`); no dependen del
  registro.
- Un owner aún puede cambiar el rol de un miembro existente a profesorado desde
  `/admin/usuarios`; el registro cerrado limita las altas, no los cambios de rol.
- Sin correo saliente: los enlaces se copian y se envían por otro canal.
- La suite activa el registro abierto en `db_path` y prueba el modo por defecto
  con la fixture `closed_signup` (`test_invite_only.py`).
