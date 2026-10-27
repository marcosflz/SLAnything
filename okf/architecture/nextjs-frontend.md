---
type: Architecture
title: Frontend Next.js
description: Interfaz principal en Next.js 16 y React 19, su relación con FastAPI y la sincronización con Jinja.
tags: [nextjs, react, typescript, frontend, api]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T13:30:00Z }
sources:
  - id: package
    resource: ../../frontend/package.json
    title: Dependencias y scripts
  - id: config
    resource: ../../frontend/next.config.ts
    title: Rewrites y cabeceras
  - id: api
    resource: ../../frontend/src/lib/api.ts
    title: Cliente de API
---

# Stack

- Next.js 16.4.3 (App Router), React 19.3.1, TypeScript 7.
- Server Components por defecto; `"use client"` solo en controles interactivos.
- CSS compartido: `frontend/src/app/app.css` es copia de
  `webapp/static/css/app.css` (sincronizar con `npm run sync:assets`).
- Mensajes: `frontend/src/lib/messages.json` exportado desde `webapp/i18n.py`.

# Rutas

| Ruta | Pantalla |
|---|---|
| `/` | Landing o dashboard |
| `/entrar`, `/registro` | Auth |
| `/cursos` | Catálogo de cursos |
| `/cursos/[slug]` | Detalle de un curso |
| `/curso` | Programa del curso activo (7 capítulos) |
| `/leccion/[slug]` | Lección con bloques, labs y runner |
| `/quiz/[id]`, `/quiz/intento/[id]` | Quiz y revisión |
| `/progreso` | Progreso |
| `/glosario`, `/recursos`, `/buscar` | Glosario, recursos y búsqueda |
| `/profesor` | Panel del profesor |
| `/estudio` | Estudio de autoría (solo profesorado) |
| `/idioma/[lang]` | Cambio de idioma |
| `/manifest.webmanifest` | Manifiesto PWA |
| `/sw.js` | Service worker de estáticos |

# Comunicación con FastAPI

`next.config.ts` define rewrites:

- `/api/v1/*` → `http://127.0.0.1:8000/api/v1/*`
- `/api/ejecutar` → `http://127.0.0.1:8000/api/ejecutar`
- `/static/*` → `http://127.0.0.1:8000/static/*`
- `/salud` → `http://127.0.0.1:8000/health`

`API_INTERNAL_URL` permite cambiar el backend. Las peticiones server-side reenvían
la cookie `aula_session`; el navegador permanece en el origen de Next y no hay CORS.
En Docker se compila con `API_INTERNAL_URL=http://backend:8000` y `output:
"standalone"`. Cambiar el nombre del servicio exige reconstruir la imagen porque
los rewrites quedan en el manifiesto del build.

# Componentes

`AppShell`, `PublicShell`, `BlockRenderer`, `Lab`, `PythonRunner`, `QuizForm`,
`LessonAside`, `NoteEditor`, `ActivityBars`, `TeacherTable`, `Lightbox`,
`ThemeToggle`, `IconSprite`, `SearchShortcut`, `SidebarController`, `CourseCard`,
`ComingSoonCard`, `StudioPanel`, `PWARegister`.

- La sidebar de escritorio se puede colapsar con `[data-sidebar-collapse]`; el
  estado se guarda en `aula-sidebar-collapsed` y se aplica antes de pintar. Las
  lecciones se agrupan por capítulo y el capítulo activo se abre solo.
- El programa renderiza una sección por capítulo (`#capitulo-N`) con sus 8
  lecciones; la lección y el quiz muestran el capítulo al que pertenecen.
- El selector ES/EN usa enlaces completos (`<a>`), no `Link`, para invalidar la
  caché de RSC y que el cambio de cookie se refleje de inmediato.
- `Ring` calcula `--ring-circumference` y `--ring-value`; el `stroke-dasharray`
  usa la circunferencia real, no el tamaño en píxeles.
- El tema claro es el predeterminado; el oscuro solo se aplica si el usuario lo
  guardó en `localStorage`. No se usa `prefers-color-scheme` como fallback.
- El shell recibe `courses` para el contador del enlace «Cursos», pero el cambio
  de curso se hace siempre desde el catálogo `/cursos`; la tarjeta superior solo
  muestra el curso activo y las lecciones. El detalle vive en `/cursos/[slug]`.

# PWA

`app/manifest.ts`, `app/icon.svg`, `public/icon.svg`, `public/sw.js` y
`PWARegister` convierten la web en instalable. El service worker solo cachea
`/_next/static/`, `/static/`, el icono y el manifiesto; las páginas y `/api/`
siempre van a la red para no servir sesiones o progreso obsoletos. El registro se
omite en desarrollo y no es requisito para usar la app. La decisión completa está
en [DESKTOP](../../docs/DESKTOP.md) y [ADR-012](/decisions/adr-012-authoring-opencode.md).

# Comandos

```powershell
cd frontend
npm install
npm run dev          # http://127.0.0.1:3000
npm run typecheck
npm run build
npm start
```

El smoke test requiere backend y frontend:

```powershell
uv run python tools/smoke_next.py

# Smoke E2E de navegador
cd frontend
npx playwright install chromium
npm run e2e
```

# Relación con Jinja

- Next es la interfaz principal.
- Jinja sigue en `:8000` como fallback y referencia visual.
- Un cambio de diseño debe reflejarse en ambos CSS; `sync:assets` copia el CSS.
- Un cambio de contenido se sirve automáticamente a ambas interfaces.
- Un cambio de API debe actualizar `src/lib/types.ts` y `api.ts`.
