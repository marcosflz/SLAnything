---
type: ADR
title: ADR-017 · Generación por etapas con salida JSON
description: Ingesta estructurada, temario editable, lecciones en paralelo con citas, banco de preguntas y verificación; OpenCode queda como motor opcional.
tags: [adr, autoría, llm, generación, citas]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: pipeline
    resource: ../../webapp/generation/pipeline.py
    title: Pipeline
  - id: document
    resource: ../../webapp/generation/document.py
    title: Ingesta
  - id: llm
    resource: ../../webapp/generation/llm.py
    title: Cliente LLM
---

> Relación: supersede en parte ADR-012.

# Contexto

El motor de [ADR-012](/decisions/adr-012-authoring-opencode.md) era una sola
sesión de OpenCode que escribía todo `course.json`: recortaba a 300 000
caracteres, producía 1–2 capítulos sin importar el tamaño del libro, no
verificaba citas y solo admitía preguntas de opción única.

# Decisión

Motor `direct` por etapas (`webapp/generation/`), con artefactos en el
directorio del trabajo:

1. **Ingesta** (`document.py`): secciones nivel 1/2 por marcadores de PDF,
   estilos DOCX, *spine* de EPUB, `#` de Markdown, `h1/h2` de HTML o patrones
   de línea; fragmentos de ~1 500 caracteres con id `dN:pPÁG:cN`.
2. **Alcance**: el usuario marca secciones y opciones (nivel, lecciones,
   tipos de pregunta…).
3. **Temario** por capítulo + ficha del curso; editable antes de generar.
4. **Lecciones** en paralelo (`AULA_GEN_CONCURRENCY`) con `sources` por bloque.
5. **Evaluación**: quiz (única, múltiple, verdadero/falso) y glosario.
6. **Verificación** (`verify.py`): citas existentes y respaldo léxico; marca
   `unsupported`; reparación dirigida de la lección que no valida.

Las llamadas usan `llm.py` (HTTP directo, dialectos OpenAI-compatible y
Anthropic, reintentos con *backoff*, conteo de tokens). `FakeLLM` sirve a los
tests (`AULA_LLM_FAKE=1`). El contrato admite `schema_version` 2, hasta 40
capítulos/300 lecciones, `sources` en bloques y `kind`/`correct` múltiple en
preguntas. OpenCode sigue disponible como motor `opencode`.

# Consecuencias

- La revisión edita el paquete (`PUT /courses/{slug}/package`) y puede
  regenerar una lección conservando las ediciones del resto.
- El respaldo es léxico, no semántico: detecta desvíos, no prueba verdad.
- Las URLs base de OpenCode Zen/Go en modo directo deben confirmarse; se
  pueden sobrescribir con `base_url`.
