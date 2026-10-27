---
type: Content Model
title: Modelo de contenido didáctico
description: Cómo se definen, validan y renderizan capítulos, lecciones, quiz y glosario, y cómo añadir un capítulo.
tags: [contenido, lecciones, quiz, validacion, extension, capitulos]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: schema
    resource: ../../webapp/content/schema.py
    title: Dataclasses y helpers
  - id: course
    resource: ../../webapp/content/course.py
    title: Programa ensamblado
  - id: chapters
    resource: ../../webapp/content/chapters/
    title: Paquetes de capítulos
  - id: program
    resource: ../../webapp/content/program.py
    title: Program y validate_program
---

# Piezas

- `Lesson`: `number`, `slug`, `title`, `summary`, `minutes`, `objectives`,
  `blocks`, `key_points`, `quiz_id`.
- `Chapter`: metadatos y tupla de 8 lecciones; calcula minutos, vecinos y
  `lesson_count`.
- `Program`: agrupa los capítulos, aplana las lecciones y resuelve `lesson()`,
  `chapter_for()`, `chapter_for_quiz()` y vecinos entre capítulos.
- `Course`: unidad de producto; envuelve un `Program` y añade `slug`, libro,
  estado, nivel, color, portada y orden. Delega capítulos y lecciones.
- `Question` / `Quiz`: opciones, índice correcto, explicación y umbral.
- `GlossaryTerm`: término, definición y lección relacionada.

# Organización

- Capítulo 1: `webapp/content/lessons/` y `lessons/en/`.
- Capítulos 2-7: un paquete autocontenido por capítulo en
  `webapp/content/chapters/chNN/`:
  `chapter_es.py`, `chapter_en.py`, `lessons_es/`, `lessons_en/`, `quiz_es.py`,
  `quiz_en.py`, `glossary_es.py`, `glossary_en.py` y `labs.py`.
- `webapp/content/chapters/__init__.py` descubre los paquetes existentes en
  `MODULES`.
- `webapp/content/course.py` construye `CHAPTERS`, `PROGRAM`, `COURSE_LLM` y
  `CATALOGS`.
- `webapp/content/catalog.py` contiene `Book`, `Course` y `validate_catalog()`.
- `webapp/content/__init__.py` fusiona glosarios y quizzes, rechaza duplicados y
  construye el `ContentBundle` con el curso activo.
- `webapp/content/program.py` contiene `Program` y `validate_program()`.

# Bloques

Helpers en `schema.py`:

| Helper | Render |
|---|---|
| `lead`, `p` | Párrafo destacado / normal |
| `h2`, `h3` | Encabezados con ancla |
| `callout(tone, title, html)` | Aviso info/tip/warning/danger/success/note |
| `figure(src, alt, caption, credit, wide)` | Figura con lightbox |
| `code(lang, source, caption)` | Código con botón copiar |
| `py(source, caption)` | Python editable, ejecutable y descargable |
| `table(headers, rows, caption, note)` | Tabla responsive |
| `quote`, `bullets`, `keypoints` | Cita, lista e ideas clave |
| `lab(id)` | Laboratorio interactivo |
| `check(question, answer)` | Autochequeo desplegable |
| `divider` | Separador |

# Validación

`validate_catalog()` se ejecuta en el lifespan y, para cada idioma:

- valida cada curso con `validate_program()`, que a su vez llama a
  `validate_content()` (8 lecciones, números consecutivos, labs conocidos, quiz,
  figuras, Python y glosario);
- comprueba que los capítulos estén numerados 1..N;
- rechaza slugs de curso, lección y quiz repetidos en toda la biblioteca;
- comprueba que cada término del glosario apunte a una lección existente.

`validate_content()` comprueba además:

- labs conocidos (`config.KNOWN_LABS`);
- imágenes presentes en `webapp/static/`;
- bloques `py` con sintaxis Python válida y menos de 16 000 caracteres;
- quiz con preguntas, opciones e índices válidos;
- glosario con término y definición.

`tools/validate_all_chapters.py` añade una comprobación global de términos
repetidos, quizzes sin lección y módulos JS de laboratorio.

# Idiomas

Cada idioma tiene su propio catálogo en `CATALOGS` (`Course` con su `Program`),
además de `GLOSSARIES` y `QUIZZES_BY_LANG`. `COURSES = {"es": PROGRAM,
"en": PROGRAM_EN}` se conserva para los tests y el contenido histórico. Los
paquetes de capítulo repiten `number`, `slug`, `minutes`, `labs`, `quiz_id` y
estructura entre ES y EN. El texto de interfaz no se guarda aquí: está en
`webapp/i18n.py`.

Los tests amplían la validación: estructura pedagógica (lead, check, keypoints),
existencia de módulos JS, enlaces del glosario y paridad de los 7 capítulos.

# Contenido generado

El curso estático sigue escribiéndose en módulos Python. El Estudio produce un
`course.json` que `webapp/authoring/package.py` convierte a los mismos objetos
`Course`/`Program`/`Lesson`/`Quiz`; no se importa Python generado. Reglas
diferenciales:

- Slugs de curso, capítulo, lección y quiz con prefijo `gen-` para no colisionar.
- Sin `figure` ni `lab`; el HTML se sanea con lista blanca.
- 1–4 capítulos, 3–8 lecciones por capítulo, máximo 30 lecciones.
- Un quiz por capítulo y 6–24 términos de glosario.
- Paridad ES/EN de slugs y respuestas correctas cuando se generan ambos idiomas.
- El paquete se guarda en `generated_courses.package_json`; publicar solo cambia
  su estado y lo hace visible en `content_for`.

# Añadir un curso

1. Crea un `Program` con sus capítulos, lecciones, quizzes, glosario y labs.
2. Crea un `Course` en `webapp/content/course.py` con un slug global único,
   metadatos y el `Book` de origen.
3. Añádelo a `CATALOG` y `CATALOG_EN`; `CATALOGS` lo publica en ambos idiomas.
4. Si el curso todavía no está listo, usa `status="coming_soon"`; no aparecerá
   como curso publicado en el catálogo.
5. Ejecuta `uv run python tools/validate_all_chapters.py`, `uv run pytest -q` y
   `uv run python tools/check_okf.py`.
6. No hace falta tocar routers, API, SQLite ni la navegación: el catálogo y el
   curso activo se resuelven con `Course` y `ContentBundle`.

# Añadir una lección

1. Si es del capítulo 1: crea `webapp/content/lessons/lNN_slug.py` y su gemela
   `lessons/en/lNN_slug.py`.
2. Si es de un capítulo 2-7: crea el módulo en `lessons_es/lNN_slug.py` y
   `lessons_en/lNN_slug.py` del paquete `chNN`, y añádelo a los dos `__init__.py`.
3. Mantén el mismo `number`, `slug`, `minutes`, labs y `quiz_id` en ambos idiomas.
4. Si tiene quiz, añádelo al `quiz_es.py`/`quiz_en.py` del capítulo y enlázalo.
5. Si tiene lab, añade el ID a `config.KNOWN_LABS`, al `labs.py` del capítulo y el
   módulo JS.
6. Añade figuras a `webapp/static/img/chNN/`.
7. Ejecuta `uv run python tools/check_chapter.py chNN`,
   `uv run python tools/validate_all_chapters.py`, `uv run pytest -q` y el
   validador OKF.
8. Actualiza `okf/product/lessons.md`, `labs`, `quiz`, `status` y `log`.

# Estilo editorial

Español de España, tono cercano y riguroso, sin hype. Cada lección empieza con
`lead`, incluye al menos un `callout` y un `check`, y termina con `keypoints`.
700-1000 palabras y 6-25 bloques. Las cifras del libro se citan; las estimaciones
se marcan como tales.
