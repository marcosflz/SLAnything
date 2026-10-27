/* Laboratorio · Calculadora de coste de preentrenamiento. */

import { h, num, option } from "./common.js";
import { lang, t } from "../i18n.js";

const MODELS = [
  {
    id: "124m",
    label: lang === "en" ? "Book model · 124 M" : "Modelo del libro · 124 M",
    params: 124e6,
  },
  { id: "1_5b", label: "GPT-2 XL · 1.5 B", params: 1.5e9 },
  { id: "8b", label: "Llama 3.1 · 8 B", params: 8e9 },
  { id: "70b", label: "Llama 3.1 · 70 B", params: 70e9 },
  { id: "175b", label: "GPT-3 · 175 B", params: 175e9 },
];

const BOOK_PARAMS = 124e6;
const DEFAULT_TFLOPS = 40; // A100 ≈ 40 TFLOPS efectivos (no pico teórico)
const INITIAL = {
  modelId: "175b",
  tokensB: 300,
  gpus: 1024,
  price: 2,
  tflops: DEFAULT_TFLOPS,
};

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

function sci(value) {
  if (!Number.isFinite(value) || value <= 0) return "0";
  const exponent = Math.floor(Math.log10(value));
  const mantissa = value / 10 ** exponent;
  return `${num(mantissa, 2)} × 10^${exponent}`;
}

function money(value) {
  const digits = value >= 100 ? 0 : 2;
  return `$${num(value, digits)}`;
}

function hoursLabel(value) {
  return num(value, value >= 100 ? 0 : 1);
}

function memoryLabel(value) {
  if (value >= 1000) return `${num(value / 1000, 1)} TB`;
  const digits = value >= 100 ? 0 : 1;
  return `${num(value, digits)} GB`;
}

function durationLabel(days) {
  const seconds = days * 86400;
  if (seconds >= 86400) return `${num(days, days >= 100 ? 0 : 1)} ${t("días")}`;
  if (seconds >= 3600) return `${num(seconds / 3600, 1)} h`;
  if (seconds >= 60) return `${num(seconds / 60, 1)} min`;
  return `${num(seconds, 0)} s`;
}

function tokensLabel(tokensB) {
  if (tokensB >= 1000) return `${num(tokensB / 1000, 1)} ${t("billones")}`;
  return `${num(tokensB, 0)} ${t("mil millones")}`;
}

export default {
  id: "cost",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");

    let modelId = INITIAL.modelId;
    let tokensB = INITIAL.tokensB;
    let gpus = INITIAL.gpus;
    let price = INITIAL.price;
    let tflops = INITIAL.tflops;

    /* ----------------------------- Controles ----------------------------- */
    const modelSelect = h(
      "select",
      { id: "cost-model" },
      MODELS.map((model) => option(model.id, model.label, model.id === modelId))
    );

    const tokensOutput = h("output", { for: "cost-tokens" });
    const tokensInput = h("input", {
      id: "cost-tokens",
      type: "range",
      min: "1",
      max: "2000",
      step: "1",
      value: String(tokensB),
    });

    const gpusOutput = h("output", { for: "cost-gpus" });
    const gpusInput = h("input", {
      id: "cost-gpus",
      type: "range",
      min: "1",
      max: "4096",
      step: "1",
      value: String(gpus),
    });

    const priceOutput = h("output", { for: "cost-price" });
    const priceInput = h("input", {
      id: "cost-price",
      type: "range",
      min: "0.5",
      max: "10",
      step: "0.1",
      value: String(price),
    });

    const tflopsOutput = h("output", { for: "cost-tflops" });
    const tflopsInput = h("input", {
      id: "cost-tflops",
      type: "range",
      min: "5",
      max: "150",
      step: "5",
      value: String(tflops),
    });

    const controls = h(
      "div",
      { class: "lab-controls" },
      h(
        "div",
        { class: "field" },
        h("label", { for: "cost-model" }, t("Modelo")),
        modelSelect
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "cost-tokens" }, t("Tokens de entrenamiento"), tokensOutput),
        tokensInput,
        h("small", {}, t("D en la fórmula FLOPs ≈ 6 · N · D."))
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "cost-gpus" }, t("GPUs"), gpusOutput),
        gpusInput,
        h("small", {}, t("Número de GPUs que trabajan en paralelo."))
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "cost-price" }, t("Precio por GPU-hora"), priceOutput),
        priceInput,
        h("small", {}, t("Incluye solo el alquiler del hardware; no la energía ni la red."))
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "cost-tflops" }, t("Rendimiento efectivo"), tflopsOutput),
        tflopsInput,
        h("small", {}, t("A100 ≈ 40 TFLOPS efectivos; H100 ≈ 150. Es velocidad sostenida, no el pico teórico."))
      ),
      h(
        "div",
        { class: "lab-note" },
        h("strong", {}, t("Qué mueve el coste")),
        h(
          "p",
          {},
          t("Duplicar parámetros o tokens duplica los FLOPs. Más GPUs reparten el trabajo, pero no reducen el coste total si el precio por hora es el mismo. El rendimiento efectivo es la palanca más realista: pasar de 40 a 60 TFLOPS recorta un tercio las GPU-horas.")
        )
      )
    );

    /* ------------------------------ Salida ------------------------------- */
    const statsPrimary = h("div", { class: "lab-stat-row" });
    const statsSecondary = h("div", { class: "lab-stat-row mt-2" });
    const comparison = h("div", { class: "callout callout-note mt-2" });
    const notes = h(
      "div",
      { class: "mt-3" },
      h(
        "p",
        { class: "small muted" },
        t("GPU-h = FLOPs / (TFLOPS · 10^12 · 3600); días = GPU-h / GPUs / 24; coste = GPU-h × precio. La memoria de entrenamiento usa 16 bytes por parámetro.")
      ),
      h(
        "p",
        { class: "small muted" },
        t("La memoria de entrenamiento solo cuenta pesos, gradientes y estados del optimizador; las activaciones y los lotes añaden más.")
      ),
      h(
        "p",
        { class: "small muted" },
        t("Estimación de orden de magnitud; el coste real depende del hardware, la eficiencia y el precio de la energía.")
      )
    );

    const output = h(
      "div",
      { class: "lab-output" },
      h("h4", {}, t("Resultados")),
      statsPrimary,
      statsSecondary,
      h("h4", { class: "mt-3" }, t("Comparación con el modelo del libro")),
      comparison,
      notes
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    /* ---------------------------- Lógica -------------------------------- */
    function render() {
      const model = MODELS.find((item) => item.id === modelId) || MODELS[0];
      const params = model.params;
      const datasetTokens = tokensB * 1e9;

      const flops = 6 * params * datasetTokens;
      const gpuHours = flops / (tflops * 1e12 * 3600);
      const wallHours = gpuHours / gpus;
      const days = wallHours / 24;
      const cost = gpuHours * price;
      const trainingMemory = (params * 16) / 1e9;

      const bookGpuHours = (6 * BOOK_PARAMS * datasetTokens) / (tflops * 1e12 * 3600);
      const bookDays = bookGpuHours / gpus / 24;
      const bookCost = bookGpuHours * price;
      const ratio = params / BOOK_PARAMS;

      const refGpuHours = (6 * BOOK_PARAMS * 1e9) / (30e12 * 3600);
      const refCost = refGpuHours * 0.5;

      tokensOutput.textContent = tokensLabel(tokensB);
      gpusOutput.textContent = num(gpus, 0);
      priceOutput.textContent = `${num(price, 1)} USD`;
      tflopsOutput.textContent = `${num(tflops, 0)} TFLOPS`;

      statsPrimary.replaceChildren(
        stat(t("GPU-horas"), hoursLabel(gpuHours)),
        stat(t("Tiempo en el cluster"), durationLabel(days)),
        stat(t("Coste estimado"), money(cost))
      );

      statsSecondary.replaceChildren(
        stat(t("FLOPs (6 · N · D)"), sci(flops)),
        stat(t("Memoria de entrenamiento"), memoryLabel(trainingMemory)),
        stat(t("Vs. modelo del libro"), `${num(ratio, ratio >= 100 ? 0 : 1)}×`)
      );

      comparison.replaceChildren(
        h("div", { class: "callout-icon", "aria-hidden": "true" }, "i"),
        h(
          "div",
          { class: "callout-body" },
          h("strong", { class: "callout-title" }, t("Dos escalas para comparar")),
          h(
            "div",
            { class: "callout-text" },
            model.params === BOOK_PARAMS
              ? h(
                  "p",
                  {},
                  `${t("Estás calculando el modelo del libro (124 M).")} `,
                  t("Con estos ajustes necesitaría ≈ {hours} GPU-h, ≈ {time} y {cost}.", {
                    hours: hoursLabel(gpuHours),
                    time: durationLabel(days),
                    cost: money(cost),
                  })
                )
              : h(
                  "p",
                  {},
                  t("Con los mismos tokens, GPUs, precio y rendimiento, el modelo del libro (124 M) necesitaría ≈ {hours} GPU-h, ≈ {time} y {cost}. Este modelo es {ratio}× mayor.", {
                    hours: hoursLabel(bookGpuHours),
                    time: durationLabel(bookDays),
                    cost: money(bookCost),
                    ratio: num(ratio, ratio >= 100 ? 0 : 1),
                  })
                ),
            h(
              "p",
              {},
              t("Escenario del libro: 124 M · 1 B tokens · 30 TFLOPS efectivos · 0,5 USD/GPU-h ≈ {hours} GPU-h y {cost}.", {
                hours: hoursLabel(refGpuHours),
                cost: money(refCost),
              })
            )
          )
        )
      );
    }

    modelSelect.addEventListener("change", () => {
      modelId = modelSelect.value;
      render();
    });
    tokensInput.addEventListener("input", () => {
      tokensB = Number(tokensInput.value);
      render();
    });
    gpusInput.addEventListener("input", () => {
      gpus = Number(gpusInput.value);
      render();
    });
    priceInput.addEventListener("input", () => {
      price = Number(priceInput.value);
      render();
    });
    tflopsInput.addEventListener("input", () => {
      tflops = Number(tflopsInput.value);
      render();
    });

    render();
    return () => {};
  },
};
