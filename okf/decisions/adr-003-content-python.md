---
type: Decision
title: ADR-003 · Contenido en módulos Python
description: Modelar lecciones, quiz y glosario como módulos Python versionados en lugar de una base de datos o un CMS.
tags: [adr, contenido, python, cms, versionado]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: schema
    resource: ../../webapp/content/schema.py
    title: Esquema de contenido
  - id: course
    resource: ../../webapp/content/course.py
    title: Curso
---

# Contexto

El contenido es didáctico, cambia con el libro y debe revisarse como código. Se
quiere validar al arrancar y mantener el historial en git.

# Decisión

Cada lección es un módulo Python que exporta `LESSON`; el curso se ensambla en
`course.py`. Los bloques son dicts creados con helpers tipados. El quiz y el
glosario también son estructuras Python.

# Consecuencias

- Contenido revisable en PR, diffeable y testeable.
- Validación de slugs, labs, quizzes e imágenes al arrancar.
- Sin editor visual ni edición desde el navegador.
- Añadir contenido requiere escribir Python, no solo Markdown.
- Para autores no técnicos, en el futuro se podría generar desde Markdown/OKF.

# Alternativas descartadas

- Base de datos + CMS: más flexible, pero necesita panel, migraciones y backup.
- Markdown plano: cómodo, pero menos validación y peor tipado.
