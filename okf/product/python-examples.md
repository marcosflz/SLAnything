---
type: Lab Catalog
title: Ejemplos de Python ejecutables
description: Los 26 ejemplos del curso que se pueden editar, ejecutar en servidor y descargar.
tags: [python, ejemplos, ejecucion, sandbox, lecciones]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: schema
    resource: ../../webapp/content/schema.py
    title: Helper py()
  - id: execution
    resource: ../../webapp/execution.py
    title: Runner
  - id: chapters
    resource: ../../webapp/content/chapters/
    title: Ejemplos por capítulo
---

# Catálogo

| Capítulo | Ejemplos | Qué demuestran |
|---|---|---|
| 1 · Entender los LLM | 7 | Memoria, pares, atención, corpus, autorregresión, prompts y coste |
| 2 · Trabajar con texto | 3 | BPE en miniatura, ventanas/pares y similitud coseno |
| 3 · Atención | 3 | Self-attention, producto escalado y máscara causal |
| 4 · Arquitectura GPT | 4 | Conteo de parámetros, LayerNorm/GELU, residuales y logits |
| 5 · Pretraining | 3 | Entropía/perplejidad, paso de entrenamiento y FLOPs |
| 6 · Clasificación | 3 | Cabeza/softmax, matriz de confusión y umbrales |
| 7 · Instrucciones | 3 | Plantilla de chat, máscara de pérdida y evaluación |

Los ejemplos del capítulo 1 están en `webapp/content/lessons/` y su gemelo
`lessons/en/`; los de los capítulos 2-7, en
`webapp/content/chapters/chNN/lessons_es/` y `lessons_en/`.

# Cómo funciona

- El bloque se crea con `py(source, caption)` en `webapp/content/schema.py`.
- Se valida al arrancar con `compile()` y límite de 16 000 caracteres.
- La UI permite editar, ejecutar, ver stdout/tablas/figuras y descargar.
- `POST /api/ejecutar` exige sesión, CSRF y rate limit.
- Descargas: `/api/v1/downloads/lessons/{slug}/code` y `.../code/{index}`.
- Cada ejemplo es autocontenido; no comparte variables entre ejecuciones.

# Seguridad

El runner está en `webapp/sandbox_runner.py` y se lanza con `python -I` en un
subproceso. Usa AST, imports permitidos, hook de auditoría y límites. No es un
sandbox de nivel producción; ver [ejecución](/architecture/execution.md) y
[seguridad](/architecture/security.md).

# Añadir un ejemplo

1. Añade `py(...)` a la lección en ES y EN.
2. Mantén el código corto y sin imports fuera de la lista permitida.
3. Ejecuta `uv run pytest -q`; el contenido se valida al arrancar.
4. Actualiza este concepto, [lecciones](/product/lessons.md),
   [status](/project/status.md) y [log](/log.md).
