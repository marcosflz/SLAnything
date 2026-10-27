---
type: Security
title: Seguridad de la plataforma
description: Controles de autenticación, sesión, CSRF, autorización y cabeceras, con sus límites.
tags: [seguridad, auth, csrf, sesiones, privacidad]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
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
- `require_teacher` → 403 para estudiantes.
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

# Generación con OpenCode

- OpenCode corre como subproceso del backend, nunca dentro del proceso FastAPI.
- `cwd` es el directorio del trabajo; `HOME`, `XDG_CONFIG_HOME`,
  `XDG_DATA_HOME` y `TMPDIR` apuntan a `authoring/opencode-home` o al propio
  trabajo. Se eliminan `OPENCODE_DB`, `OPENCODE_CONFIG` y credenciales del host.
- El agente solo puede `read`, `edit`, `glob`, `grep` y `list`. Se deniegan
  `shell`, `webfetch`, `websearch`, `task`, `external_directory` y `question`.
- La API key se inyecta como variable de entorno; nunca se escribe en
  `opencode.json` y los logs se redactan.
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
- `/api/v1/authoring` y `/estudio` exigen `require_teacher`; todas las mutaciones
  llevan CSRF. La API key nunca se devuelve al navegador.

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
