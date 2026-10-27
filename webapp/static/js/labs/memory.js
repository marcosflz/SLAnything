/* Laboratorio · Explorador de memoria: pesos, caché KV y entrenamiento. */

import { h, num, bar, option } from "./common.js";
import { t } from "../i18n.js";

const MODELS = [
  { id: "gpt2-small", label: "GPT-2 small · 124 M", params: 124e6, layers: 12, dim: 768 },
  { id: "gpt2-xl", label: "GPT-2 XL · 1,5 B", params: 1.5e9, layers: 48, dim: 1600 },
  { id: "llama-8b", label: "Llama 3.1 8B", params: 8e9, layers: 32, dim: 4096 },
  { id: "llama-70b", label: "Llama 3.1 70B", params: 70e9, layers: 80, dim: 8192 },
  { id: "gpt3", label: "GPT-3 · 175 B", params: 175e9, layers: 96, dim: 12288 },
];

const PRECISIONS = [
  { bits: 4, bytes: 0.5 },
  { bits: 8, bytes: 1 },
  { bits: 16, bytes: 2 },
  { bits: 32, bytes: 4 },
];

const LAPTOP_GB = 16;
const GPU_GB = 80;
const TRAINING_BYTES_PER_PARAM = 16;
const INITIAL_CONTEXT_TOKENS = 8192;

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

function memoryLabel(value) {
  if (value >= 1000) return `${num(value / 1000, 1)} TB`;
  const digits = value >= 100 ? 0 : value >= 10 ? 1 : 2;
  return `${num(value, digits)} GB`;
}

export default {
  id: "memory",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");

    let modelId = "gpt2-small";
    let precision = PRECISIONS[2];

    /* ----------------------------- Controles ----------------------------- */
    const modelSelect = h(
      "select",
      { id: "memory-model" },
      MODELS.map((model) => option(model.id, model.label, model.id === modelId))
    );

    const precisionGroup = h("div", {
      class: "segmented",
      role: "group",
      "aria-label": t("Precisión de inferencia"),
    });
    const precisionButtons = PRECISIONS.map((item) => {
      const button = h(
        "button",
        { type: "button", class: item === precision ? "is-active" : "" },
        `${item.bits} bits`
      );
      button.addEventListener("click", () => {
        precision = item;
        precisionButtons.forEach((other) => {
          other.classList.toggle("is-active", other === button);
        });
        render();
      });
      precisionGroup.append(button);
      return button;
    });

    const contextOutput = h(
      "output",
      { for: "memory-context" },
      `${num(INITIAL_CONTEXT_TOKENS, 0)} tokens`
    );
    const contextInput = h("input", {
      id: "memory-context",
      type: "range",
      min: "1024",
      max: "131072",
      step: "1024",
      value: String(INITIAL_CONTEXT_TOKENS),
    });

    const precisionHint = h("small", {});

    const controls = h(
      "div",
      { class: "lab-controls" },
      h(
        "div",
        { class: "field" },
        h("label", { for: "memory-model" }, t("Modelo")),
        modelSelect,
        h("small", {}, t("Capas y dimensión son valores aproximados de cada arquitectura."))
      ),
      h(
        "div",
        { class: "field" },
        h("label", {}, t("Precisión de inferencia")),
        precisionGroup,
        precisionHint
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "memory-context" }, t("Ventana de contexto"), contextOutput),
        contextInput,
        h("small", {}, t("Tokens que el modelo puede atender a la vez."))
      ),
      h(
        "div",
        { class: "lab-note" },
        h("strong", {}, t("Cómo leerlo")),
        h(
          "p",
          {},
          t("Los pesos crecen con los parámetros y la precisión. La caché KV crece con el contexto: por eso una ventana de 128k tokens puede costar más que el propio modelo en modelos pequeños. El entrenamiento añade gradientes y estados del optimizador.")
        )
      )
    );

    /* ------------------------------ Salida ------------------------------- */
    const statsRow = h("div", { class: "lab-stat-row" });
    const bars = h("div", { class: "bar-list" });
    const inferenceLine = h("p", { class: "small mt-2" });
    const notes = h(
      "div",
      { class: "mt-3" },
      h(
        "p",
        { class: "small muted" },
        t("Entrenar no es solo guardar los pesos: con Adam en fp32 hacen falta pesos, gradientes y dos estados del optimizador (≈16 bytes por parámetro). Las activaciones, los gradientes y los lotes añaden todavía más memoria.")
      ),
      h(
        "p",
        { class: "small muted" },
        t("La caché KV se estima como 2 · capas · dimensión · tokens · bytes. Es una simplificación: técnicas como GQA reducen la caché real en algunos modelos.")
      ),
      h(
        "p",
        { class: "small muted" },
        t("Cifras aproximadas: el tamaño real depende de la arquitectura, la implementación y del hardware. La precisión de inferencia no cambia la estimación de entrenamiento.")
      )
    );

    const output = h(
      "div",
      { class: "lab-output" },
      h("h4", {}, t("Memoria estimada")),
      statsRow,
      inferenceLine,
      h("h4", { class: "mt-3" }, t("Comparación con el hardware")),
      bars,
      notes
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    /* ---------------------------- Lógica -------------------------------- */
    function render() {
      const model = MODELS.find((item) => item.id === modelId) || MODELS[0];
      const contextTokens = Number(contextInput.value);
      const bytes = precision.bytes;

      const weights = (model.params * bytes) / 1e9;
      const kvCache = (2 * model.layers * model.dim * contextTokens * bytes) / 1e9;
      const training = (model.params * TRAINING_BYTES_PER_PARAM) / 1e9;
      const inference = weights + kvCache;

      contextOutput.textContent = `${num(contextTokens, 0)} tokens`;
      precisionHint.textContent = t("{n} {unit} por parámetro en pesos y caché.", {
        n: num(bytes, 1),
        unit: bytes === 1 ? t("byte") : t("bytes"),
      });

      statsRow.replaceChildren(
        stat(t("Pesos"), memoryLabel(weights)),
        stat(t("Caché KV"), memoryLabel(kvCache)),
        stat(t("Entrenamiento aprox."), memoryLabel(training))
      );

      const rows = [
        { label: t("Pesos"), value: weights, tone: "" },
        { label: t("Caché KV"), value: kvCache, tone: "amber" },
        { label: t("Entrenamiento"), value: training, tone: "danger" },
        { label: t("Portátil 16 GB"), value: LAPTOP_GB, tone: "success" },
        { label: t("GPU 80 GB"), value: GPU_GB, tone: "success" },
      ];
      const maxValue = Math.max(...rows.map((row) => row.value), 1);
      bars.replaceChildren(
        ...rows.map((row) =>
          bar(row.label, row.value, maxValue, {
            tone: row.tone,
            format: (value) => memoryLabel(value),
          })
        )
      );

      const fits = [];
      if (inference <= LAPTOP_GB) fits.push(t("un portátil de 16 GB"));
      if (inference <= GPU_GB) fits.push(t("una GPU de 80 GB"));

      let fitText;
      if (fits.length === 2) {
        fitText = t("Cabe en {first} y en {second}.", { first: fits[0], second: fits[1] });
      } else if (fits.length === 1) {
        fitText = t("No cabe en un portátil de 16 GB, pero sí en {device}.", { device: fits[0] });
      } else {
        fitText = t("No cabe completo ni en un portátil de 16 GB ni en una GPU de 80 GB.");
      }
      inferenceLine.textContent =
        t("Inferencia (pesos + caché KV) ≈ {memory}. {fit}", {
          memory: memoryLabel(inference),
          fit: fitText,
        });
    }

    modelSelect.addEventListener("change", () => {
      modelId = modelSelect.value;
      render();
    });
    contextInput.addEventListener("input", render);

    render();
    return () => {};
  },
};
