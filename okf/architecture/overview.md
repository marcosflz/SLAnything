---
type: Architecture
title: Visión general de la arquitectura
description: Stack, flujo de una petición y mapa de carpetas de SLAnything con Next.js y FastAPI.
tags: [arquitectura, nextjs, fastapi, sqlite, react]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: main
    resource: ../../webapp/main.py
    title: Punto de entrada FastAPI
  - id: api
    resource: ../../webapp/routers/api.py
    title: API JSON
  - id: frontend
    resource: ../../frontend/
    title: Aplicación Next.js
  - id: readme
    resource: ../../README.md
    title: README del proyecto
---

# Stack

| Capa | Tecnología | Papel |
|---|---|---|
| Interfaz | Next.js 16 + React 19 + TypeScript | App Router, Server Components y controles cliente |
| API | FastAPI + Uvicorn | JSON `/api/v1`, sesión, CSRF, ejecución |
| Plantillas legado | Jinja2 | Fallback reversible en el puerto 8000 |
| Datos | SQLite (`sqlite3` stdlib) | Usuarios, progreso, quiz, notas |
| Estilos | CSS propio con variables | Diseño, responsive, modo oscuro |
| Interacción | Módulos JS existentes | 15 laboratorios, lightbox, runner |
| Contenido | Módulos Python | 7 capítulos, lecciones, quizzes y glosario (ES/EN) |
| Ejecución | Subproceso Python aislado | Ejemplos editables con límites |
| Empaquetado | Docker + Compose | Dos imágenes y SQLite en volumen |

# Flujo de una petición

1. El navegador pide una ruta a Next.js (`http://127.0.0.1:3000`).
2. El Server Component lee la cookie `aula_session` y llama a la API JSON de
   FastAPI con `cache: "no-store"`.
3. `get_current_user()` valida la sesión; `get_db()` abre una conexión SQLite por
   petición.
4. El router `/api/v1` serializa curso, lección, progreso o quiz.
5. Next renderiza el shell y los bloques; los componentes cliente hidratan tema,
   notas, quiz, Python y laboratorios.
6. Las mutaciones del navegador van al mismo origen de Next; los *rewrites* las
   proxyean a FastAPI con cookie y `X-CSRF-Token`.
7. Los laboratorios se cargan desde `/static/js/labs/*.js` y el runner hace
   `POST /api/ejecutar`, también proxeado.

# Estructura

```text
frontend/                # interfaz principal Next.js
  src/app/               # rutas App Router
  src/components/        # shell, bloques, labs, quiz y UI
  src/lib/               # API, tipos, mensajes y cliente HTTP
  next.config.ts         # rewrites a FastAPI y cabeceras
webapp/                  # backend FastAPI y legado Jinja
  main.py                # app, middleware, errores, health
  config.py              # rutas, cookie, lab registry, cuentas demo
  db.py                  # esquema, conexión, seed
  security.py            # scrypt, tokens, CSRF, rate limit
  deps.py                # usuario actual, require_user, require_teacher, CSRF
  repositories.py        # SQL
  routers/api.py         # API JSON versionada
  routers/authoring.py   # API del Estudio y /estudio
  routers/*.py           # rutas HTML legado
  authoring/             # settings, providers, extract, package, store y runner
  content/               # schema, Program, Course/Catalog, lecciones, quizzes, glosario
  content/chapters/      # paquetes autocontenidos de los capítulos 2-7
  templates/             # Jinja2 legado
  static/                # css, js, img (ch01..ch07), data
  tests/                 # 111 tests
docs/AUTHORING.md        # flujo de documentos a unidades
docs/DESKTOP.md          # web + PWA y ruta a Tauri
```

# Decisiones clave

- **Next.js sobre API FastAPI**: se conserva el backend, el contenido y los
  tests; la interfaz gana componentes, tipado y composición.
- **Mismo origen con rewrites**: la cookie HttpOnly y el CSRF siguen siendo
  responsabilidad de FastAPI, sin CORS.
- **Contenido en Python**: versionado, tipado y validable; la API lo serializa.
- **Labs en JS vanilla**: se reutilizan sin reescribirlos en React.
- **Python ejecutable en servidor** con subproceso aislado y descarga local.
- **Contenido bilingüe** con slugs compartidos: el progreso no se pierde al
  cambiar de idioma.
- **Estudio de autoría** con OpenCode en Docker y paquetes JSON validados; el
  catálogo mezcla cursos estáticos y generados sin rutas paralelas.
- **Web + PWA** como superficie única; Tauri queda documentado como siguiente
  paso si hace falta offline o integración nativa.
- **Catálogo multi-curso** con `Course`/`CATALOGS`: un curso envuelve un
  `Program` y añade libro, estado, color y orden; el progreso se aísla por
  `course_slug`.
- **SQLite** en lugar de PostgreSQL: cero infraestructura para el MVP.

# Puntos de extensión

- Nueva página Next: `frontend/src/app/<ruta>/page.tsx` + endpoint si necesita
  datos nuevos.
- Nueva lección: módulo en `content/lessons/` (capítulo 1) o en
  `content/chapters/chNN/lessons_es|en/` (capítulos 2-7) y su `__init__.py`.
- Nuevo capítulo: crear un paquete en `content/chapters/chNN/` con los exports
  acordados; `content/chapters/__init__.py` lo descubre y `course.py` lo
  ensambla. La navegación del shell se adapta sola a `course.chapters`.
- Nuevo curso: crear un `Program`, envolverlo en `Course` con `Book` y
  registrarlo en `CATALOGS`; `validate_catalog()` comprueba colisiones. No hacen
  falta cambios en routers ni SQLite.
- Nuevo lab: `config.KNOWN_LABS`, `labs.py` (o el `labs.py` del capítulo),
  `static/js/labs/<id>.js` y el componente `Lab` lo carga sin cambios.
