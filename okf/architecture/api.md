---
type: Architecture
title: API JSON v1
description: Contrato entre FastAPI y Next.js para sesión, curso, progreso, quiz, recursos y profesor.
tags: [api, json, nextjs, fastapi, contrato]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T13:30:00Z }
sources:
  - id: api
    resource: ../../webapp/routers/api.py
    title: Router API v1
  - id: types
    resource: ../../frontend/src/lib/types.ts
    title: Tipos del frontend
---

# Prefijo

Todas las rutas JSON viven bajo `/api/v1` (`webapp/routers/api.py`). Next.js las
consume mediante rewrites; el navegador no habla directamente con FastAPI.

# Rutas

| Método | Ruta | Auth | Devuelve |
|---|---|---|---|
| GET | `/api/v1/session` | opcional | Usuario, CSRF y idioma |
| GET | `/api/v1/public` | no | Landing, curso destacado, catálogo y sitio |
| GET | `/api/v1/catalog` | opcional | Catálogo con progreso si hay sesión |
| GET | `/api/v1/courses/{slug}` | opcional | Detalle de curso, progreso y siguiente lección |
| GET | `/api/v1/shell` | sí | Usuario, curso activo, catálogo, progreso, sitio y stats |
| POST | `/api/v1/auth/login` | no | Sesión + cookie |
| POST | `/api/v1/auth/register` | no | Alta + sesión + cookie |
| POST | `/api/v1/auth/logout` | sí | Borra sesión |
| GET | `/api/v1/dashboard` | sí | Stats, siguiente lección, actividad e intentos |
| GET | `/api/v1/course` | sí | Programa, capítulos y progreso |
| GET | `/api/v1/lessons/{slug}` | sí | Lección completa, capítulo, nota y marcador |
| POST | `/api/v1/lessons/{slug}/complete` | sí | Alterna completada |
| POST | `/api/v1/lessons/{slug}/note` | sí | Guarda apuntes |
| POST | `/api/v1/lessons/{slug}/bookmark` | sí | Alterna marcador |
| GET | `/api/v1/quiz/{id}` | sí | Preguntas sin respuestas y capítulo |
| POST | `/api/v1/quiz/{id}` | sí | Corrige y crea intento |
| GET | `/api/v1/quiz/attempts/{id}` | sí | Revisión privada |
| GET | `/api/v1/progress` | sí | Progreso, actividad e intentos |
| GET | `/api/v1/glossary` | sí | Grupos por letra |
| GET | `/api/v1/resources` | sí | Recursos |
| GET | `/api/v1/search?q=` | sí | Resultados |
| GET | `/api/v1/teacher` | teacher | Tabla de estudiantes |
| GET | `/api/v1/authoring` | teacher | Ajustes, trabajos, unidades y límites |
| GET/PUT | `/api/v1/authoring/settings` | teacher | Proveedor, modelo y estado de la key |
| GET | `/api/v1/authoring/jobs` | teacher | Trabajos recientes |
| POST | `/api/v1/authoring/jobs` | teacher | Sube documentos y crea un trabajo |
| GET | `/api/v1/authoring/jobs/{id}` | teacher | Estado y cola del log |
| POST | `/api/v1/authoring/jobs/{id}/cancel` | teacher | Cancela la generación |
| GET | `/api/v1/authoring/courses` | teacher | Unidades generadas |
| GET | `/api/v1/authoring/courses/{slug}` | teacher | Paquete JSON completo |
| POST | `/api/v1/authoring/courses/{slug}/publish` | teacher | Publica en el catálogo |
| POST | `/api/v1/authoring/courses/{slug}/unpublish` | teacher | Retira del catálogo |
| DELETE | `/api/v1/authoring/courses/{slug}` | teacher | Elimina la unidad |
| GET | `/api/v1/downloads/...` | sí | Cuaderno, plan y código |

Además existe `POST /api/ejecutar` para el runner de Python, fuera del prefijo v1
por compatibilidad con el frontend. Los cursos generados publicados aparecen en
`/api/v1/catalog`, `/api/v1/courses/{slug}`, `/api/v1/lessons/{slug}` y
`/api/v1/quiz/{id}` sin cambios de contrato.

# Forma del curso

La clave `course` representa el **curso activo**, no un capítulo. El catálogo se
devuelve aparte en `courses` cuando la pantalla lo necesita.

```json
{
  "slug": "llm-desde-cero",
  "title": "Construye un LLM desde cero",
  "status": "published",
  "book": {"title": "Build a Large Language Model (From Scratch)", "author": "Sebastian Raschka"},
  "chapter_count": 7,
  "lesson_count": 56,
  "lab_count": 15,
  "total_minutes": 584,
  "chapters": [
    {
      "number": 2,
      "slug": "capitulo-2",
      "title": "Trabajar con texto",
      "lesson_count": 8,
      "total_minutes": 83,
      "lessons": [{"number": 1, "slug": "tokens-y-vocabulario", "chapter_number": 2, "course_slug": "llm-desde-cero"}]
    }
  ],
  "lessons": ["...lecciones aplanadas..."]
}
```

El catálogo (`/api/v1/catalog`, `/api/v1/public` y la clave `courses` de otras
respuestas) devuelve resúmenes con `slug`, `book`, `stats`, `next_lesson` y
metadatos, sin duplicar el contenido completo.

`/api/v1/lessons/{slug}` y `/api/v1/quiz/{id}` incluyen además `chapter` y
`course`. `next_lesson` y `prev_lesson` viajan entre capítulos y llevan
`chapter_number`, `chapter_title`, `course_slug` y `course_title`.

# Contrato

- Errores: `{"detail": "..."}` con el código HTTP real.
- 401 en API devuelve JSON, no redirect (a diferencia de las rutas HTML).
- La sesión se comparte con Jinja: cookie `aula_session` HttpOnly.
- El idioma se negocia con `?lang=es|en` y cookie `aula_lang`.
- El quiz nunca expone `correct` ni `explanation` antes de enviar.
- Los intentos y notas se filtran por `user_id` y `course_slug`.
- El progreso se indexa por `(user_id, course_slug, lesson_slug)`; los slugs de
  curso, lección y quiz son únicos en toda la plataforma.
- `?course=slug` fija el curso activo; sin parámetro se usa el curso por defecto.
- Los tipos TypeScript espejo están en `frontend/src/lib/types.ts`.

# Cambios

Al añadir o modificar una ruta:

1. Actualiza `webapp/routers/api.py`.
2. Actualiza los tipos de `frontend/src/lib/types.ts` y el cliente `api.ts`.
3. Añade tests en `webapp/tests/test_api.py`.
4. Actualiza este concepto, [nextjs-frontend](/architecture/nextjs-frontend.md),
   [testing](/operations/testing.md) y [log](/log.md).
