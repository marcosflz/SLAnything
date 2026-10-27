---
type: ADR
title: "ADR-010 · Programa multi-capítulo con paquetes autocontenidos"
description: Cómo se incorporaron los capítulos 2-7 sin tocar routers ni esquema y cómo se mantiene el progreso global.
tags: [adr, capitulos, contenido, programa, slugs, arquitectura]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: course
    resource: ../../webapp/content/course.py
    title: Ensamblado del programa
  - id: program
    resource: ../../webapp/content/program.py
    title: Program y validación global
  - id: chapters
    resource: ../../webapp/content/chapters/
    title: Paquetes de capítulos
---

# Contexto

El producto nació como un curso de un solo capítulo: `COURSES` mapeaba cada idioma
a un `Chapter` de 8 lecciones y todos los routers, la API, las plantillas Jinja y
el frontend asumían `course.lessons`. Completar los capítulos 2-7 exigía agrupar
lecciones sin duplicar progreso, quizzes ni navegación, y sin convertir cada
capítulo en un curso independiente.

# Decisión

1. **`Chapter` sigue siendo la unidad editorial** de 8 lecciones y un quiz.
2. Se añade **`Program`** (`webapp/content/program.py`) como unidad de navegación:
   agrupa capítulos, aplana lecciones, resuelve `lesson()`, `chapter_for()`,
   `chapter_for_quiz()` y vecinos entre capítulos.
3. Los capítulos 2-7 viven en **paquetes autocontenidos**
   `webapp/content/chapters/chNN/` con exports estables: `CHAPTER_ES`,
   `CHAPTER_EN`, `QUIZZES_ES`, `QUIZZES_EN`, `GLOSSARY_ES`, `GLOSSARY_EN`,
   `LAB_META_ES`, `LAB_META_EN` y `LAB_IDS`.
4. `webapp/content/chapters/__init__.py` descubre los paquetes existentes y
   `course.py` construye `PROGRAM`/`PROGRAM_EN` y `COURSES`.
5. **Los slugs son globales y únicos**. El progreso, las notas, los marcadores y
   los intentos siguen indexándose por `lesson_slug`; no hay migración de esquema.
6. La API mantiene la clave `course` pero devuelve el **programa completo**, con
   `chapters`, `lesson_count`, `chapter_count` y `lab_count`. Lección y quiz
   incluyen su `chapter`.
7. La validación se eleva a `validate_program()`: valida cada capítulo con
   `validate_content()` y añade comprobaciones de capítulos consecutivos, slugs y
   quizzes únicos, y enlaces del glosario.

# Consecuencias

- Añadir un capítulo no toca routers ni SQLite: se crea el paquete y se exporta.
- El progreso es único por slug; cambiar de idioma o de capítulo no lo duplica.
- Los quizzes y el glosario se fusionan con detección de duplicados al arrancar.
- La navegación puede fluir entre capítulos (siguiente/anterior) y el programa
  agrupa las lecciones por capítulo.
- El frontend y Jinja comparten `course.chapters`; el shell muestra capítulos
  colapsables.
- Los agentes de contenido pueden trabajar en paralelo en paquetes aislados sin
  editar archivos compartidos.

# Alternativas descartadas

- **Un `COURSE` gigante con 56 lecciones planas:** rompe la semántica de capítulo,
  la navegación y los quizzes por capítulo.
- **Un curso por capítulo:** duplica matrículas, progreso y navegación; el
  producto es un único curso.
- **Slugs con prefijo de capítulo:** habría exigido migrar progreso y enlaces
  existentes; se prefirió reservar slugs descriptivos únicos.
- **Tablas nuevas para capítulos:** el contenido es código versionado; no hacía
  falta persistir metadatos editoriales en SQLite.
