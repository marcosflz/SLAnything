---
type: Lab Catalog
title: Laboratorios interactivos
description: Los 15 laboratorios JS, su contrato, archivos y comportamiento esperado.
tags: [laboratorios, javascript, interactividad, labs]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: labsmeta
    resource: ../../webapp/labs.py
    title: Metadatos de laboratorios
  - id: chapters
    resource: ../../webapp/content/chapters/
    title: Metadatos por capítulo
  - id: appjs
    resource: ../../webapp/static/js/app.js
    title: Carga diferida
  - id: common
    resource: ../../webapp/static/js/labs/common.js
    title: Utilidades compartidas
---

# Catálogo

| ID | Título | Cap. | Archivo | Qué hace |
|---|---|---|---|---|
| `memory` | Explorador de memoria | 1, 4 | `labs/memory.js` | Pesos, cuantización, KV cache y entrenamiento |
| `labels` | Fábrica de etiquetas | 1, 2 | `labs/labels.js` | Pares entrada→objetivo señalando tokens |
| `transformer` | Dentro del transformer | 1, 3 | `labs/transformer.js` | Stepper encoder/decoder |
| `attention` | Mapa de atención | 1, 3 | `labs/attention.js` | Heatmap y pesos por palabra |
| `ngram` | Generador de n-gramas | 1 | `labs/ngram.js` | Corpus de El Quijote, temperatura y top-k |
| `prompt` | Constructor de prompts | 1 | `labs/prompt.js` | Zero/one/few-shot y copia |
| `cost` | Calculadora de entrenamiento | 1, 5 | `labs/cost.js` | FLOPs, GPU-h, coste y memoria |
| `tokenizer` | Tokenizador BPE | 2 | `labs/tokenizer.js` | Entrena un BPE en miniatura y tokeniza palabras |
| `window` | Ventana deslizante | 2 | `labs/window.js` | Ajusta contexto/stride y cuenta ventanas |
| `embedding` | Mapa de embeddings | 2 | `labs/embedding.js` | Mueve vectores y compara similitud coseno |
| `qkv` | Consultas, claves y valores | 3 | `labs/qkv.js` | Visualiza Q/K/V y los pesos de atención |
| `gpt-block` | Bloque GPT interactivo | 4 | `labs/gpt-block.js` | Activa LN, atención, FFN y residuales |
| `loss` | Laboratorio de pérdida | 5 | `labs/loss.js` | Entropía cruzada, perplejidad y batches |
| `classifier` | Clasificador interactivo | 6 | `labs/classifier.js` | Umbral, matriz de confusión y métricas |
| `chat-template` | Plantilla de chat | 7 | `labs/chat-template.js` | Roles, tokens especiales y máscara de pérdida |

# Contrato

```js
export default {
  id: "memory",
  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    // UI + eventos
    return () => {};
  }
};
```

- `root` es `<section class="lab" data-lab="...">`.
- `body` existe vacío; el módulo lo rellena.
- Sin librerías externas; helpers en `labs/common.js`.
- Carga con `IntersectionObserver` e `import()` dinámico.
- En Next lo monta `frontend/src/components/Lab.tsx`; en Jinja, `static/js/app.js`.
- Si el módulo falla, la interfaz muestra un aviso dentro del lab.
- Los módulos nuevos del capítulo 2 en adelante usan un diccionario local
  `ES/EN` basado en `document.documentElement.lang`; no editan `i18n.js`.

# Detalles relevantes

- **ngram** carga `/static/data/quijote_fragmento.txt` (417 KB), tokeniza y
  construye un modelo de orden 4 una sola vez; usa backoff y semilla determinista.
- **memory** estima pesos = N × bytes, KV cache = 2 · capas · dim · tokens · bytes
  y entrenamiento = N × 16 B.
- **cost** usa FLOPs ≈ 6·N·D, GPU-h = FLOPs / (TFLOPS·10¹²·3600) y precio por
  GPU-hora; por defecto 40 TFLOPS efectivos.
- **attention**, **qkv** y **transformer** son visualizaciones didácticas, no
  pesos entrenados; se indica en la UI.
- **tokenizer** entrena un BPE simplificado sobre un corpus de juguete.
- **window** muestra el número de ventanas y el solapamiento para L y stride.
- **embedding** usa vectores 2D y coseno para comparar vecinos.
- **gpt-block** conserva la forma de los tensores al activar/desactivar piezas.
- **loss** relaciona probabilidad del token correcto con entropía y perplejidad.
- **classifier** recalcula TP/FP/FN/TN, precisión, recall y F1 al mover el umbral.
- **chat-template** muestra el texto final y qué posiciones entran en la pérdida.

# Idiomas

`webapp/labs.py` mantiene `LAB_META` (español) y `LAB_META_EN` (inglés), y fusiona
los metadatos de cada capítulo desde `webapp/content/chapters/chNN/labs.py`. Los
módulos del capítulo 1 usan `t()` de `static/js/i18n.js`; los nuevos usan su
diccionario local bilingüe para no acoplar cada capítulo a un archivo compartido.

# Verificación

- Los 15 labs montan sin errores de consola en Chrome headless
  (`frontend/e2e-labs.mjs`, `npm run e2e:labs`).
- `tokenizer` se verificó además en Jinja con Playwright.
- Los módulos nuevos se validaron con `node --check`, DOM simulado y Playwright.
- Sin overflow horizontal a 360 px.
- Queda pendiente automatizar la interacción profunda de cada control; se anota
  en [known-issues](/context/known-issues.md).
