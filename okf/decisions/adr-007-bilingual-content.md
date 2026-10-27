---
type: Decision
title: ADR-007 · Contenido bilingüe con módulos por idioma
description: Separar el contenido didáctico en módulos español/inglés y resolver el idioma con cookie, sin duplicar plantillas.
tags: [adr, i18n, idiomas, contenido, jinja]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T17:00:00Z }
sources:
  - id: i18n
    resource: ../../webapp/i18n.py
    title: Traducciones de interfaz
  - id: content
    resource: ../../webapp/content/__init__.py
    title: Bundles por idioma
  - id: en
    resource: ../../webapp/content/lessons/en/
    title: Lecciones en inglés
---

# Contexto

El curso nació en español. Se pidió añadir inglés sin romper URLs, slugs,
progreso ni intentos de quiz ya guardados. Traducir solo la interfaz habría dejado
las lecciones en español; duplicar plantillas habría multiplicado el mantenimiento.

# Decisión

- El contenido vive en módulos paralelos: `webapp/content/lessons/` (español) y
  `webapp/content/lessons/en/` (inglés), con los mismos `slug`, `number` y
  `quiz_id`. Glosario y quiz tienen su propio módulo inglés.
- `content_for(lang)` devuelve `ContentBundle` con curso, glosario y quizzes.
- La interfaz usa `t("texto en español")` con un diccionario español→inglés en
  `webapp/i18n.py`; si falta una traducción, se muestra el español.
- El idioma se guarda en la cookie `aula_lang`; `/idioma/{lang}` la cambia y
  redirige a una URL interna segura. `?lang=en` permite enlaces directos.
- Las plantillas son únicas; `render()` inyecta `lang`, `t`, `course`, `lab_meta`
  y los textos de cabecera del idioma activo.
- El progreso se guarda por slug, así que es compartido entre idiomas. Los
  intentos de quiz usan el mismo ID y se revisan con las preguntas del idioma
  activo.

# Consecuencias

- Añadir un idioma exige traducir contenido, glosario, quiz y diccionario de UI.
- Los slugs internos siguen en español para no invalidar enlaces ni progreso.
- El HTML declara `lang` correcto y los lectores de pantalla reciben el idioma
  activo.
- La traducción de los textos largos de algunos laboratorios JS puede quedar
  pendiente; se anota en [known-issues](/context/known-issues.md).

# Alternativas descartadas

- **Gettext con catálogos .po:** buena para equipos grandes, pero añade archivos
  binarios/compilados y no resuelve el contenido didáctico.
- **Traducción automática en tiempo de petición:** dependencia externa, coste y
  resultados inconsistentes.
- **Duplicar plantillas por idioma:** doble mantenimiento de HTML y CSS.
