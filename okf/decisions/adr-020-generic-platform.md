---
type: ADR
title: ADR-020 · Plataforma genérica y curso LLM como ejemplo opcional
description: La app ya no gira alrededor del curso «Construye un LLM desde cero»; funciona con la biblioteca vacía y el curso LLM es un ejemplo que se activa con AULA_SAMPLE_COURSES=1.
tags: [adr, producto, catalogo, contenido, ejemplos]
status: stable
date: 2026-11-14
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
sources:
  - id: content
    resource: ../../webapp/content/__init__.py
    title: content_for y ContentBundle
  - id: course
    resource: ../../webapp/content/course.py
    title: Curso de ejemplo
  - id: api
    resource: ../../webapp/routers/api.py
    title: API JSON
  - id: landing
    resource: ../../frontend/src/components/home/Landing.tsx
    title: Portada genérica
---

# Contexto

SLAnything nació como «Aula LLM» para un único PDF. Aunque ya existían el
catálogo multi-curso ([ADR-011](/decisions/adr-011-multi-course.md)) y el
Estudio ([ADR-012](/decisions/adr-012-authoring-opencode.md)), el curso LLM
seguía siendo el eje: curso por defecto (`DEFAULT_COURSE_SLUG`), portada sobre
ChatGPT, login con citas de LLM, recursos fijos (cuaderno, Quijote, figuras),
glosario LLM mezclado en todos los cursos y `/salud` leyendo
`CATALOGS["es"][0]`. Una instalación sin ese curso no funcionaba.

# Decisión

- El curso LLM pasa a ser **curso de ejemplo** (`Course.is_sample`). Solo
  aparece con `AULA_SAMPLE_COURSES=1` (por defecto `0`); `config.SAMPLE_COURSES`
  se lee en cada petición. `DEFAULT_COURSE_SLUG` se renombra a
  `SAMPLE_COURSE_SLUG` (sigue sirviendo para migrar datos v1).
- La plataforma **no exige curso**: `ContentBundle.course` puede ser `None` y
  las rutas de shell, inicio, progreso, glosario, recursos, búsqueda,
  profesorado y analítica devuelven `course: null`. Solo `/course`, lecciones y
  quizzes devuelven 404 si no hay curso.
- **Curso activo**: el pedido (`?course=`), luego `users.last_course_slug`
  (último curso abierto, si sigue visible) y luego el primer curso publicado.
  Los cursos del espacio van antes que los ejemplos.
- **Biblioteca por espacio activo**: los cursos generados visibles son los del
  espacio activo más los públicos, no los de todos los espacios del usuario.
- **Glosario y recursos por curso**: `ContentBundle.glossaries` va por slug; los
  recursos son `Course.resources` (ejemplo) o documentos fuente y descargas de
  código (cursos generados). `/downloads/plan` desaparece y
  `/downloads/notebook` solo responde con ejemplos activos.
- **Marca y textos genéricos**: lema «Convierte cualquier material en un
  curso», portada sobre el flujo documento → temario → curso, perfiles en
  «Para quién», login y registro neutros. Se eliminan 52 cadenas LLM huérfanas
  de `webapp/i18n.py`. Los prompts de generación dejan de suponer temas técnicos.
- Los 15 laboratorios JS siguen existiendo, pero solo los usa el curso de
  ejemplo; los cursos generados no los referencian.

# Consecuencias

- Una instalación nueva arranca con la biblioteca vacía; el Estudio es el
  camino principal para crear contenido.
- Las instalaciones previas dejan de ver el curso LLM hasta activar
  `AULA_SAMPLE_COURSES=1`; el progreso guardado no se pierde.
- La suite activa los ejemplos por defecto (fixture `db_path`) y desactiva con
  `no_samples` para probar la biblioteca vacía.
- Relacionado: [ADR-021](/decisions/adr-021-account-profiles.md) (perfiles).
