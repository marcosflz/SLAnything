---
type: Syllabus
title: Lecciones del curso de referencia
description: Los 7 capítulos y sus 56 lecciones del curso `llm-desde-cero`, con slug, duración, laboratorios y objetivo principal.
tags: [lecciones, contenido, syllabus, capitulos]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: course
    resource: ../../webapp/content/course.py
    title: Programa ensamblado
  - id: chapters
    resource: ../../webapp/content/chapters/
    title: Paquetes de los capítulos 2-7
  - id: lessons
    resource: ../../webapp/content/lessons/
    title: Lecciones del capítulo 1
---

# Capítulo 1 · Entender los LLM

| # | Slug | Título | Min | Labs | Figuras |
|---|---|---|---|---|---|
| 1 | `que-es-un-llm` | ¿Qué es un LLM? | 10 | `memory` | 1.1, 1.2 |
| 2 | `pretraining-y-finetuning` | Las dos etapas | 10 | `labels` | 1.3 |
| 3 | `transformer-y-atencion` | Transformer y atención | 12 | `transformer`, `attention` | 1.4, 1.5 |
| 4 | `escala-de-datos` | La escala de los datos | 8 | — | Tabla 1.1 |
| 5 | `predecir-la-siguiente-palabra` | Predecir la siguiente palabra | 15 | `ngram` | 1.7, 1.8 |
| 6 | `zero-shot-y-few-shot` | Zero-shot y few-shot | 10 | `prompt` | 1.6 |
| 7 | `como-se-construye` | Cómo se construye un LLM | 8 | `cost` | 1.9 |
| 8 | `repaso` | Repaso y autoevaluación | 10 | — | Quiz |

# Capítulo 2 · Trabajar con texto

| # | Slug | Título | Min | Labs |
|---|---|---|---|---|
| 1 | `tokens-y-vocabulario` | Tokens y vocabulario | 10 | — |
| 2 | `tokens-especiales` | Tokens especiales y decodificación | 9 | — |
| 3 | `byte-pair-encoding` | BPE paso a paso | 12 | `tokenizer` |
| 4 | `vocabulario-y-embeddings` | Del token al vector | 11 | — |
| 5 | `ventana-deslizante` | La ventana deslizante | 10 | `window` |
| 6 | `pares-entrada-objetivo` | Pares entrada → objetivo | 10 | `labels` |
| 7 | `embeddings-y-significado` | Embeddings y significado | 11 | `embedding` |
| 8 | `repaso-texto` | Repaso y autoevaluación | 10 | Quiz |

# Capítulo 3 · Atención

| # | Slug | Título | Min | Labs |
|---|---|---|---|---|
| 1 | `por-que-atencion` | El problema de la memoria fija | 10 | — |
| 2 | `self-attention` | Self-attention paso a paso | 12 | `attention` |
| 3 | `consultas-claves-valores` | Consultas, claves y valores | 12 | `qkv` |
| 4 | `producto-escalado` | Producto escalado y softmax | 10 | — |
| 5 | `mascara-causal` | La máscara causal | 10 | — |
| 6 | `multi-head-attention` | Multi-head attention | 11 | — |
| 7 | `atencion-en-gpt` | La atención dentro de GPT | 10 | `transformer` |
| 8 | `repaso-atencion` | Repaso y autoevaluación | 10 | Quiz |

# Capítulo 4 · Arquitectura GPT

| # | Slug | Título | Min | Labs |
|---|---|---|---|---|
| 1 | `configuracion-gpt` | Configurar un GPT pequeño | 10 | — |
| 2 | `layer-normalization` | Layer normalization | 10 | — |
| 3 | `gelu` | GELU y activaciones | 9 | — |
| 4 | `feed-forward` | La red feed-forward | 10 | — |
| 5 | `bloque-transformer` | El bloque transformer | 12 | `gpt-block` |
| 6 | `conexiones-residuales` | Conexiones residuales | 10 | — |
| 7 | `cabeza-de-salida` | De vectores a tokens | 10 | `memory` |
| 8 | `repaso-gpt` | Repaso y autoevaluación | 10 | Quiz |

# Capítulo 5 · Pretraining

| # | Slug | Título | Min | Labs |
|---|---|---|---|---|
| 1 | `perdida-siguiente-token` | La pérdida del siguiente token | 11 | — |
| 2 | `entropia-cruzada` | Entropía cruzada y perplejidad | 11 | `loss` |
| 3 | `bucle-de-entrenamiento` | El bucle de entrenamiento | 12 | — |
| 4 | `optimizador-y-lr` | AdamW y el learning rate | 10 | — |
| 5 | `carga-de-datos` | Data loaders y batches | 9 | — |
| 6 | `evaluacion-y-generacion` | Evaluar y generar | 11 | — |
| 7 | `escala-y-coste` | Escala, FLOPs y coste | 9 | `cost` |
| 8 | `repaso-pretraining` | Repaso y autoevaluación | 10 | Quiz |

# Capítulo 6 · Clasificación

| # | Slug | Título | Min | Labs |
|---|---|---|---|---|
| 1 | `finetuning-clasificacion` | Del modelo base al clasificador | 10 | — |
| 2 | `datos-etiquetados` | Datos, etiquetas y splits | 10 | — |
| 3 | `cabeza-clasificacion` | La cabeza de clasificación | 11 | `classifier` |
| 4 | `perdida-clasificacion` | Pérdida y desbalance | 10 | — |
| 5 | `entrenamiento-clasificador` | Entrenar sin romper el modelo | 11 | — |
| 6 | `metricas` | Accuracy, precisión y recall | 11 | — |
| 7 | `inferencia-clasificador` | Inferencia y umbrales | 10 | — |
| 8 | `repaso-clasificacion` | Repaso y autoevaluación | 10 | Quiz |

# Capítulo 7 · Instrucciones

| # | Slug | Título | Min | Labs |
|---|---|---|---|---|
| 1 | `instrucciones-y-sft` | Instrucciones y SFT | 11 | — |
| 2 | `datos-de-instrucciones` | Construir un dataset | 10 | — |
| 3 | `plantillas-chat` | Plantillas de chat | 12 | `chat-template` |
| 4 | `mascara-de-perdida` | Enmascarar la pérdida | 11 | — |
| 5 | `entrenamiento-instrucciones` | Entrenar instrucciones | 11 | — |
| 6 | `evaluar-instrucciones` | Evaluar respuestas | 10 | — |
| 7 | `preferencias-y-seguridad` | Preferencias, RLHF y seguridad | 11 | — |
| 8 | `repaso-instrucciones` | Repaso y autoevaluación | 10 | Quiz |

# Estado editorial

- 7 capítulos, 56 lecciones, 584 minutos.
- Cada capítulo tiene 8 lecciones numeradas 1-8, quiz propio y glosario.
- Todas las lecciones empiezan con `lead`, incluyen `callout`, `check` y cierran
  con `keypoints`.
- Versión inglesa completa en `webapp/content/lessons/en/` y en
  `webapp/content/chapters/chNN/lessons_en/`. Los slugs, minutos y labs son
  idénticos entre idiomas.
- 26 ejemplos Python ejecutables (ES) y sus equivalentes EN.
- Las figuras 1.1-1.9 del libro se usan en el capítulo 1; los capítulos 2-7 usan
  diagramas SVG propios en `webapp/static/img/chNN/`.

# Añadir o cambiar una lección

Ver [modelo de contenido](/architecture/content-model.md). Después actualiza este
concepto, [status](/project/status.md) y [log](/log.md).
