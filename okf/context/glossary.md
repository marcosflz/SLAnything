---
type: Glossary
title: Glosario del proyecto
description: Vocabulario interno de SLAnything, OKF y la plataforma web.
tags: [glosario, contexto, okf]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README del proyecto
---

# OKF

- **OKF**: Open Knowledge Format v0.2, bundle de markdown con frontmatter YAML.
- **Bundle**: directorio `okf/` que contiene los conceptos y sus índices.
- **Concepto**: documento `.md` con frontmatter y un `type` no vacío.
- **Índice**: `index.md` que enumera conceptos para divulgación progresiva.
- **Log**: `log.md` con el historial newest-first.
- **Actor**: identidad en `generated.by` o `verified.by`, por ejemplo
  `opencode/deepseek-v4.1-flash` o `human:marco`.

# Producto

- **Lección**: unidad de contenido con objetivos, bloques, ideas clave y,
  opcionalmente, quiz.
- **Bloque**: elemento de una lección (`p`, `h2`, `figure`, `lab`, `py`, `check`…).
- **Bloque `py`**: ejemplo Python editable, ejecutable y descargable.
- **Laboratorio (lab)**: módulo JavaScript interactivo montado dentro de una lección.
- **Intento**: registro de un envío de quiz con puntuación y respuestas.
- **Progreso**: estado por usuario y lección (`completed`, visitas, fechas).
- **Racha**: días consecutivos con actividad registrada.
- **Apuntes**: nota privada por usuario y lección.
- **Marcador**: lección guardada por un usuario.
- **Capítulo**: agrupación de 8 lecciones con su quiz; el curso de referencia
  tiene 7.
- **Programa (`Program`)**: agrupación de capítulos; resuelve lecciones,
  capítulos y vecinos entre capítulos.
- **Curso (`Course`)**: unidad de producto del catálogo; envuelve un `Program` y
  añade slug, libro, nivel, estado y presentación.
- **Catálogo (`CATALOGS`)**: biblioteca de cursos publicados por idioma.
- **Curso activo**: curso que resuelve el `ContentBundle` de una petición.
- **Paquete de capítulo**: directorio `webapp/content/chapters/chNN/` con
  lecciones, quiz, glosario y labs de un capítulo.
- **ContentBundle**: curso activo, catálogo, glosario y quizzes resueltos para un
  idioma.
- **Estudio**: sección `/estudio` donde el profesorado sube documentos y revisa
  unidades generadas.
- **Unidad generada**: curso creado desde un `course.json`; vive en
  `generated_courses` y se publica como cualquier otro curso.
- **Paquete (`course.json`)**: JSON bilingüe con curso, capítulos, lecciones,
  quiz y glosario que produce el agente.
- **Agente de autoría**: `slanything-author`, configuración de OpenCode con
  permisos restringidos y las instrucciones de `agent/AGENTS.md`.
- **Job**: trabajo de generación con estado, proveedor, modelo, documentos y log.
- **PWA**: web instalable con manifiesto y service worker; no sustituye al
  backend.

# Plataforma

- **Aula**: prefijo interno histórico (`aula.db`, `aula_session`, `aula_lang`,
  volumen `aula-llm-data`); el producto visible es SLAnything.
- **Demo**: cuenta `demo@aulallm.local` con contraseña `demo1234`.
- **Profesor**: rol con acceso a `/profesor`; cuenta `profe@aulallm.local`.
- **CSRF**: token por sesión que protege los POST.
- **Sesión**: fila en `sessions`; cookie `aula_session` con token hasheado en BD.
- **Render**: helper de `webapp/templating.py` que añade contexto común a Jinja.
- **Lab registry**: `app.js` detecta `[data-lab]` y carga el módulo con `import()`.
- **Next.js**: interfaz principal en `frontend/`, puerto 3000.
- **Jinja**: interfaz fallback en `webapp/templates/`, puerto 8000.
- **API v1**: contrato JSON `/api/v1` que consume Next.
- **i18n**: soporte ES/EN de interfaz y contenido.
- **Sandbox**: runner `webapp/sandbox_runner.py` para Python de usuario.
- **Runner**: subproceso `python -I` con AST, auditoría y límites.
- **messages.json**: traducciones exportadas a Next desde `webapp/i18n.py`.
