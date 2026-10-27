---
type: Architecture
title: Frontend Next.js y legado Jinja
description: Interfaz React 19 con Next.js 16 sobre la API FastAPI, sistema visual heredado y carga de laboratorios.
tags: [frontend, nextjs, react, typescript, css, javascript, accesibilidad]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: frontend
    resource: ../../frontend/
    title: Aplicación Next.js
  - id: api
    resource: ../../webapp/routers/api.py
    title: API JSON
  - id: css
    resource: ../../webapp/static/css/app.css
    title: Sistema de diseño compartido
---

# Conceptos relacionados

- [Frontend Next.js](/architecture/nextjs-frontend.md): rutas, componentes y build.
- [API JSON](/architecture/api.md): contrato con FastAPI.
- [Internacionalización](/architecture/i18n.md): cadenas ES/EN.
- [Ejecución Python](/architecture/execution.md): editor y sandbox.

# Estado

La interfaz principal es **Next.js 16 (App Router, React 19, TypeScript)** en
`frontend/`. FastAPI sigue sirviendo la API JSON, el contenido, la sesión y la
ejecución de Python. Las rutas Jinja de `webapp/templates/` se mantienen como
fallback reversible en el puerto 8000 hasta cerrar la paridad.

# Rutas Next.js

| Ruta | Componente | Datos |
|---|---|---|
| `/` | landing o dashboard | `getSession`, `getPublic`, `/api/v1/dashboard` |
| `/entrar`, `/registro` | autenticación | `getSession`, `getPublic`, `/api/v1/auth/*` |
| `/cursos` | catálogo de cursos | `/api/v1/catalog` |
| `/cursos/[slug]` | detalle de un curso | `/api/v1/courses/{slug}` |
| `/curso` | programa del curso activo (alias) | `/api/v1/course` |
| `/leccion/[slug]` | lección | `/api/v1/lessons/{slug}` |
| `/quiz/[id]` | quiz | `/api/v1/quiz/{id}` |
| `/quiz/intento/[id]` | revisión | `/api/v1/quiz/attempts/{id}` |
| `/progreso` | progreso | `/api/v1/progress` |
| `/glosario` | glosario | `/api/v1/glossary` |
| `/recursos` | recursos | `/api/v1/resources` |
| `/buscar` | buscador | `/api/v1/search?q=` |
| `/profesor` | panel docente | `/api/v1/teacher` |
| `/estudio` | Estudio de autoría (docente) | `/api/v1/authoring` |
| `/idioma/[lang]` | cambio de idioma | cookie `aula_lang` |
| `/salud` | health | rewrite a FastAPI |

# Shell

- `components/AppShell.tsx`: sidebar colapsable en escritorio, topbar, buscador,
  selector ES/EN, tema, menú de usuario, footer, barra de lectura y lightbox. La
  sidebar agrupa las lecciones por capítulo con `<details>`; el capítulo activo se
  abre automáticamente. La tarjeta superior muestra el curso activo y el cambio
  de curso se hace desde el enlace genérico «Cursos» (`/cursos`); no hay enlaces
  duplicados «Curso actual» ni «Cambiar de curso». El estado de la sidebar se
  guarda en `localStorage`.
- `components/home/Landing.tsx` muestra el catálogo de cursos; `app/cursos/page.tsx`
  lista la biblioteca y `app/cursos/[slug]/page.tsx` el detalle. `app/curso/page.tsx`
  agrupa las 56 lecciones en secciones `#capitulo-N`; la lección y el quiz
  muestran su capítulo.
- El selector ES/EN usa `<a>` (navegación completa) para que el cambio de cookie
  invalide la caché de RSC de Next.
- `components/PublicShell.tsx`: navegación pública, tema, idioma y footer.
- `components/ui.tsx`: `Icon`, `Badge`, `ProgressBar`, `Ring`, `Stat`,
  `LessonStatus`.
- `components/ThemeScript.tsx` evita el destello de tema: si no hay preferencia
  guardada, aplica **claro**. `ThemeToggle` lo cambia y lo persiste en
  `localStorage`.

# Contenido y bloques

`components/BlockRenderer.tsx` traduce los bloques del backend a React:
`p`, `lead`, `h2`, `h3`, `callout`, `figure`, `code`, `python`, `table`,
`quote`, `list`, `lab`, `keypoints`, `check` y `divider`.

- El HTML de los bloques es contenido estático del repositorio y se inserta con
  `dangerouslySetInnerHTML`.
- `Figure` abre el lightbox global.
- `CodeBlock` copia al portapapeles.
- `PythonRunner` reproduce el editor, la numeración, Tab, Ctrl+Enter, ejecución
  contra `/api/ejecutar`, salida, tablas, imágenes y descarga.
- `Lab` monta los 15 módulos JS existentes desde `/static/js/labs/*.js` con
  `IntersectionObserver` e `import()` en tiempo de ejecución.

# Datos y sesión

- Las páginas son Server Components y llaman a `lib/api.ts` con `cache:
  "no-store"`.
- La cookie `aula_session` se reenvía a FastAPI en el servidor.
- El navegador usa el mismo origen de Next: `next.config.ts` reescribe
  `/api/v1/*`, `/api/ejecutar` y `/static/*` a FastAPI.
- Las mutaciones de cliente usan `lib/client.ts` y envían `X-CSRF-Token`.
- `getShell()` redirige a `/entrar?next=` si la sesión no es válida.

# i18n

- FastAPI sigue siendo la fuente de las cadenas de interfaz (`webapp/i18n.py`).
- `tools/export_messages.py` genera `frontend/src/lib/messages.json`.
- `lib/messages.ts` expone `t(lang, clave, variables)` y `pick(lang, es, en)`.
- El idioma se guarda en `aula_lang`; `/idioma/[lang]` la actualiza y redirige.
- Los slugs de lección no cambian entre idiomas: el progreso es compartido.

# CSS

`frontend/src/app/app.css` es una copia sincronizada de
`webapp/static/css/app.css` mediante `tools/sync_frontend_assets.py`. Se mantiene
el mismo sistema de variables, componentes, responsive (1180, 1024, 820 y
600 px), impresión, `prefers-reduced-motion` y foco visible. `next.css` solo
contiene ajustes de integración.

# Accesibilidad

- `lang` dinámico, landmarks, skip link y foco visible.
- Formularios con `label`, radios dentro de `label`, botones con `aria-label`.
- `aria-live` en salidas de laboratorios cuando aplica.
- Lightbox con `dialog`, figuras con `alt` y contraste AA en ambos temas.
