---
type: Security
title: Seguridad de la plataforma
description: Controles de autenticación, sesión, CSRF, autorización y cabeceras, con sus límites.
tags: [seguridad, auth, csrf, sesiones, privacidad]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
sources:
  - id: security
    resource: ../../webapp/security.py
    title: Hash, tokens y rate limit
  - id: deps
    resource: ../../webapp/deps.py
    title: Autenticación y CSRF
  - id: auth
    resource: ../../webapp/routers/auth.py
    title: Login y registro
---

# Contraseñas

- `scrypt` con N=2¹⁴, r=8, p=1, sal aleatoria de 16 bytes y hash de 32 bytes.
- Formato almacenado: `scrypt$N$r$p$salt$hash`.
- Comparación con `hmac.compare_digest`.
- Longitud mínima de 8 caracteres; no hay recuperación de contraseña.

# Sesiones

- Token de 32 bytes (`secrets.token_urlsafe`); cookie `aula_session`.
- En BD solo se guarda SHA-256 del token.
- Cookie `HttpOnly`, `SameSite=Lax`, `Path=/`; `Secure` con
  `AULA_SECURE_COOKIES=1`.
- Caducidad de 14 días y renovación deslizante si quedan menos de 7.
- Logout borra la sesión de BD y la cookie.

# CSRF

- Cada sesión tiene un `csrf_token` propio.
- Todos los POST de usuario llevan `csrf_token` oculto; `ensure_csrf()` acepta
  también `X-CSRF-Token` para `fetch`.
- Login y registro no llevan CSRF porque aún no hay sesión; la cookie es
  `SameSite=Lax`.

# Autorización

- `require_user` → 401 y redirect al login con `next` interno validado.
- `require_author` → 403 para el alumnado (el Estudio es de cuentas
  individuales y profesorado).
- `require_teaching` → 403 fuera de una academia o sin rol de profesorado; una
  cuenta individual no ve analítica de curso ni panel de estudiantes.
- `require_admin` → 403 sin `manage` (admin/owner de una academia).
- `require_platform_admin` → 403 sin `users.is_platform_admin`. Un superadmin no
  puede desactivarse ni retirarse el flag, y siempre queda al menos uno.
- **Registro solo por invitación** por defecto (`AULA_OPEN_SIGNUP=0`,
  [ADR-022](/decisions/adr-022-invite-only-signup.md)): sin `invite` el alta da
  403 y crear academias o cuentas individuales exige superadmin. Las
  invitaciones de academia solo pueden ser de alumnado.
- El registro con `invite` o `join_code` valida el acceso **antes** de crear la
  cuenta; si falla, no queda usuario huérfano. Los tokens se guardan como hash
  (`invitations` y `platform_invitations`), son de un solo uso y caducan a los 14
  días.
- Los intentos de quiz se consultan filtrando `user_id`; un intento ajeno da 404.
- Las notas y marcadores se consultan siempre por `user_id`.

# Ejecución de Python

- El código de las lecciones **nunca** se ejecuta en el proceso de FastAPI.
- `execution.py` lanza `sandbox_runner.py` con `python -I`, sin heredar variables
  `PYTHON*`, en un directorio temporal.
- El runner valida el AST: imports de una lista blanca, sin clases, sin `eval`,
  `exec`, `open`, `getattr` ni atributos que empiecen por `_`.
- Después de precargar los módulos permitidos, instala un `sys.addaudithook` que
  bloquea `open` fuera del entorno Python/caché de matplotlib, red, procesos,
  `ctypes` y cambios de sistema.
- Límites: 10 s, 1 GB (best effort), 20 000 caracteres de salida, 2 ejecuciones
  simultáneas y 12 por usuario/minuto. El padre mata el subproceso con `psutil`.
- La API exige sesión y `X-CSRF-Token`. Si `AULA_EXEC_ENABLED=0`, responde 503.
- **No es un sandbox de nivel producción.** Para exponerlo a Internet, ejecuta el
  runner en un contenedor sin red y sin privilegios, o desactívalo.

# Generación con agentes nas-adk (ADR-023, ADR-024)

- Los agentes corren dentro del backend con herramientas Python que solo leen los
  fragmentos del trabajo y entregan resultados validados; sin shell, red ni rutas.
- Credenciales: la de la plataforma en `settings.json` (0600); las de cada usuario
  cifradas con Fernet (clave derivada de `AULA_SECRET`) en `user_ai_settings`.
  Ninguna se devuelve a la API (solo los 4 últimos caracteres).
- Se genera siempre con las credenciales de quien lanza la acción
  (`authoring_jobs.actor_id`); una suscripción nunca se usa para otra persona ni es
  el proveedor de la plataforma. El alumnado no tiene acceso (403).
- La suscripción de Claude se pasa solo al proceso hijo del CLI
  (`CLAUDE_CODE_OAUTH_TOKEN`, `CLAUDE_CONFIG_DIR` propio 0700), con `ANTHROPIC_*`
  eliminadas; nas-adk aísla el CLI (sin herramientas, MCP ni sesión persistente).
- Los usuarios no eligen base URL: los endpoints propios son solo de la plataforma.
- Los documentos se tratan como datos no confiables: las instrucciones que
  contengan se ignoran. El HTML resultante se sanea y el JSON se valida.
- Límites: 25 MB por archivo, 5 archivos, 300 000 caracteres, 30 minutos, un
  trabajo simultáneo y 3 activos por profesor.
- El Estudio escribe con el usuario `aula` (no root). No es un sandbox de nivel
  producción: para Internet, añade cuotas, TLS y aislamiento adicional.

# Next.js y la API

- El navegador solo habla con el origen de Next. Los rewrites proxyean
  `/api/v1/*`, `/api/ejecutar` y `/static/*` a FastAPI por loopback.
- La cookie `aula_session` sigue siendo HttpOnly y la emite FastAPI; Next la
  reenvía en las peticiones de servidor.
- Las mutaciones del cliente envían `X-CSRF-Token`; el token se obtiene de
  `/api/v1/shell` y viaja en el HTML renderizado, igual que antes en el meta tag
  de Jinja.
- Las páginas Next añaden las mismas cabeceras de seguridad que FastAPI.
- El HTML de los bloques didácticos se inserta con `dangerouslySetInnerHTML`
  solo para contenido del catálogo. El curso estático es de confianza; el
  generado pasa antes por `sanitize_html()` (lista blanca de etiquetas y
  atributos). Nunca se inserta HTML de notas, correos o formularios.
- `/api/v1/authoring` y `/estudio` exigen `require_author`; todas las mutaciones
  llevan CSRF. La API key nunca se devuelve al navegador.
- Consistencia: `get_db` se declara con `scope="function"`; con el ámbito por
  defecto FastAPI confirmaba la transacción después de responder y una
  petición inmediata podía leer datos sin confirmar (crear un grupo y añadirle
  miembros devolvía 404).

# Otras protecciones

- Rate limit de login: 5 fallos por email+IP cada 15 minutos, en memoria.
- Rate limit de ejecución: 12 runs por usuario y minuto, en memoria, más un
  semáforo global de 2 ejecuciones concurrentes.
- Redirecciones `next` solo a rutas internas que empiezan por `/` y no `//`.
- Jinja escapa la entrada de usuario; el HTML de autor se marca explícitamente.
- Cabeceras: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy`.
- `static` se sirve con `StaticFiles`, sin traversal manual.

# Límites conocidos

- Rate limit no compartido entre workers (login y ejecución).
- Sin verificación de email, OAuth ni 2FA.
- Sin política de retención ni borrado de cuenta.
- SQLite y un solo proceso recomendado.
- El panel del profesor muestra datos de progreso; en producción requiere aviso
  de privacidad y control de acceso.
- El aislamiento de Python es defensa en profundidad; un fallo de CPython o de una
  biblioteca podría escapar. No lo expongas como servicio público sin contenedor.

# Actualización 2026-11-13 · roles por espacio

- La autorización ya no usa `users.role`: `deps.require_role` comprueba el rol
  del **espacio activo** (cookie `aula_ws` o cabecera `X-Workspace`, validada
  contra `memberships`). Matriz de permisos en
  [tenancy-analytics](/architecture/tenancy-analytics.md).
- Los recursos del Estudio se filtran por espacio y por autor/admin; los
  cursos generados de otros espacios no aparecen en el catálogo.
- Cuentas desactivadas (`disabled_at`) no pueden iniciar sesión (se comprueba
  tras validar la contraseña, para no filtrar existencia).
- Invitaciones: el token solo se muestra una vez; se guarda su hash.
- Cambiar la contraseña cierra las demás sesiones; hay cierre remoto de sesiones.
- Acciones sensibles en `audit_log` (sin secretos).
- `POST /api/v1/events` acepta el CSRF en el cuerpo (necesario para
  `sendBeacon`) y solo verbos de cliente; los verbos de servidor no se pueden
  falsificar.
- Ajustes del proveedor de IA: solo `is_platform_admin`
  (`AULA_PLATFORM_ADMINS`; la profesora demo lo es con `AULA_SEED_DEMO=1`).
- Pendiente: verificación de correo, recuperación de contraseña, OAuth y 2FA.
