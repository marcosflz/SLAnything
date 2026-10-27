---
type: ADR
title: "ADR-011 · Catálogo multi-curso y progreso por curso"
description: Cómo pasa SLAnything de un programa único a una biblioteca de cursos con metadatos editoriales y progreso aislado por curso.
tags: [adr, cursos, catalogo, progreso, sqlite, modularidad]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T22:00:00Z }
sources:
  - id: catalog
    resource: ../../webapp/content/catalog.py
    title: Modelo Course y validate_catalog
  - id: db
    resource: ../../webapp/db.py
    title: Esquema v2 y migración
  - id: api
    resource: ../../webapp/routers/api.py
    title: Catálogo y curso activo en la API
---

# Contexto

`Program` resolvió la navegación entre los 7 capítulos del libro, pero seguía
siendo el único curso del producto. La portada, `/curso`, el dashboard, el
progreso, la búsqueda y el panel del profesor asumían un programa global. Añadir
un segundo libro habría exigido duplicar rutas o mezclar el progreso de cursos
distintos.

# Decisión

1. **`Course` es la unidad de producto.** Vive en
   `webapp/content/catalog.py`, envuelve un `Program` y añade slug, título,
   subtítulo, descripción, nivel, libro de origen, estado (`published` o
   `coming_soon`), color, portada y orden.
2. **`CATALOGS` agrupa los cursos por idioma.** `content_for(lang, course_slug)`
   devuelve un `ContentBundle` con el curso activo, el catálogo completo,
   glosario y quizzes. `ContentBundle.select()` cambia de curso sin reconstruir
   el contenido.
3. **La API expone la biblioteca.** `GET /api/v1/catalog` y
   `GET /api/v1/courses/{slug}` son públicos; el resto de endpoints aceptan
   `?course=` para fijar el curso activo. Lección, quiz y progreso incluyen el
   curso al que pertenecen.
4. **Rutas de producto:** `/cursos` es el catálogo, `/cursos/{slug}` el detalle
   del curso y `/curso` se mantiene como alias autenticado del curso por defecto
   para no romper enlaces ni el E2E existente.
5. **Progreso aislado en SQLite.** `lesson_progress`, `notes`, `bookmarks` y
   `quiz_attempts` incorporan `course_slug`. La migración v2 copia los datos
   existentes al curso `llm-desde-cero` antes de cambiar las claves primarias.
6. **Slugs globales.** Cursos, lecciones y quizzes siguen siendo únicos en toda
   la plataforma. Simplifica las URLs `/leccion/{slug}` y `/quiz/{id}` y evita
   colisiones en el glosario y el buscador. `validate_catalog()` falla al arrancar
   si dos cursos chocan.

# Consecuencias

- La portada, el catálogo, el dashboard y la sidebar muestran cursos, no un
  único libro.
- Cambiar de curso no mezcla progreso, notas, marcadores ni intentos.
- Añadir un libro nuevo requiere un `Program` y una entrada en `CATALOGS`; no
  toca routers ni el esquema.
- El curso de referencia sigue siendo el primero y el que se abre en `/curso`.
- La API conserva `course` como clave del curso activo para no romper a los
  consumidores existentes.

# Alternativas descartadas

- **Duplicar la aplicación por curso:** multiplica mantenimiento y rompe la
  biblioteca única.
- **Mantener un programa global y solo cambiar textos:** no permite progreso
  independiente ni catálogo real.
- **Slugs por curso en la base de datos sin migración:** habría perdido el
  progreso existente o exigido reescribir URLs históricas.
- **Matrícula explícita ahora:** se deja como siguiente paso; el acceso actual es
  abierto para usuarios autenticados y el catálogo ya distingue cursos.
