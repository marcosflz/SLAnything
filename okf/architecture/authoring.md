---
type: Architecture
title: Estudio de autoría y generación con OpenCode
description: Cómo se convierten documentos en unidades didácticas validadas y cómo se integran en el catálogo dinámico.
tags: [autoría, opencode, documentos, generación, catálogo, seguridad]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T21:40:00Z }
sources:
  - id: authoring
    resource: ../../docs/AUTHORING.md
    title: Guía del Estudio
  - id: package
    resource: ../../webapp/authoring/package.py
    title: Contrato y validación
  - id: runner
    resource: ../../webapp/authoring/runner.py
    title: Runner de OpenCode
  - id: store
    resource: ../../webapp/authoring/store.py
    title: Persistencia y catálogo dinámico
  - id: router
    resource: ../../webapp/routers/authoring.py
    title: API y rutas Jinja
---

# Piezas

| Módulo | Responsabilidad |
|---|---|
| `webapp/authoring/settings.py` | Proveedor, modelo y API key en `authoring/settings.json` (0600). |
| `webapp/authoring/providers.py` | Proveedores de OpenCode, `opencode.json` del agente y variables de entorno. |
| `webapp/authoring/extract.py` | Texto de PDF, DOCX, EPUB, ODT, Markdown, HTML y TXT; troceado. |
| `webapp/authoring/package.py` | Contrato JSON, saneado HTML y conversión a `Course`/`Program`. |
| `webapp/authoring/store.py` | `authoring_jobs`, `generated_courses`, caché de publicados y logs. |
| `webapp/authoring/runner.py` | Subproceso de OpenCode, timeout, cancelación, reparación y validación. |
| `webapp/authoring/agent/AGENTS.md` | Instrucciones editoriales y esquema que lee el agente. |
| `webapp/routers/authoring.py` | API `/api/v1/authoring` y fallback Jinja `/estudio`. |
| `frontend/src/app/estudio/` | Página Next y panel cliente. |

# Flujo

1. El profesorado guarda proveedor y key en `/estudio`.
2. Sube hasta 5 documentos. Se guardan en `authoring/jobs/<id>/uploads/`.
3. El runner extrae texto, lo trocea en `source/source-NN.md` y escribe `meta.json`.
4. Genera `opencode.json` con el agente `slanything-author` y ejecuta
   `opencode run --standalone --format json --auto`.
5. El agente lee `AGENTS.md`, `meta.json` y `source/`; escribe `course.json`.
6. `parse_package()` valida, sanea y construye cursos. Si falla, hay **una
   reparación automática** con el error exacto.
7. El paquete queda en `generated_courses` como `draft`. Publicar lo mete en el
   catálogo dinámico.

# Catálogo dinámico

`content_for(lang, course_slug)` combina `CATALOGS` con los paquetes publicados
de `generated_courses`. Los slugs generados llevan prefijo `gen-`; las lecciones
y quizzes también se prefijan para no chocar con el curso estático. La caché de
`store.dynamic_content()` se invalida al guardar, publicar, despublicar o borrar.

Los cursos generados usan el mismo `Course`, `Program`, `Chapter`, `Lesson` y
`Quiz` que el curso de referencia, así que catálogo, lección, quiz, progreso,
glosario, búsqueda y panel del profesor funcionan sin rutas paralelas. El
progreso se aísla por `course_slug` como cualquier otro curso.

# Contrato y calidad

- `schema_version: 1`; 1–4 capítulos; 3–8 lecciones por capítulo; máximo 30.
- Un quiz por capítulo (4–10 preguntas) y 6–24 términos de glosario.
- Cada lección empieza por `lead`, termina en `keypoints` y contiene `callout` y
  `check`; mínimo 220 palabras (el agente apunta a 650–900).
- Bloques permitidos: `lead`, `p`, `h2`, `h3`, `callout`, `table`, `quote`,
  `list`, `keypoints`, `check`, `divider`, `code`, `python`. Sin `figure` ni `lab`.
- El HTML se limpia con lista blanca; se eliminan scripts, estilos, `iframe`,
  atributos `on*` y enlaces `javascript:`.
- Los bloques `python` se compilan antes de guardar; luego los ejecuta el sandbox
  existente, nunca OpenCode.
- Si el idioma es ES+EN, la estructura de slugs y las respuestas correctas deben
  coincidir.

# Aislamiento

OpenCode corre como subproceso con `cwd` en el directorio del trabajo, `HOME` y
`XDG_*` bajo `authoring/opencode-home`, variables de proveedor propias y
`--standalone`. El agente tiene permitido `read`, `edit`, `glob`, `grep` y
`list`; se deniegan `shell`, `webfetch`, `websearch`, `task`,
`external_directory` y `question`. La API key no se escribe en `opencode.json`:
se inyecta como variable de entorno y se redacta del log.

# Operación

- Un trabajo simultáneo (`ThreadPoolExecutor(max_workers=1)`).
- Timeout de 30 minutos; cancelación termina el proceso.
- Al arrancar, los trabajos `extracting/generating/validating` se marcan como
  fallidos para no quedar colgados.
- Log en `authoring/jobs/<id>/run.log`, recortado a 2 MB y visible en `/estudio`.
- Si OpenCode cierra con código 1 pero `course.json` existe, se valida igual: el
  proveedor puede haber tenido un error transitorio y el agente haberlo resuelto.

# Pruebas

`webapp/tests/test_authoring.py` cubre saneado, contrato, tonos, extracción,
ajustes, API, permisos, publicación en catálogo, reparación y flujo del runner
con OpenCode simulado. La prueba manual con el modelo gratuito de OpenCode dentro
de Docker generó una unidad de 4 lecciones, la publicó y la sirvió en `/cursos`.
