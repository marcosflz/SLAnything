/* Laboratorio · Pérdida, perplejidad y contribución al lote. */

import { h } from "./common.js";

const isEnglish = (document.documentElement.lang || "es")
  .toLowerCase()
  .startsWith("en");

const copy = isEnglish
  ? {
      title: "The loss account",
      intro:
        "Each row is a position in the batch. Move the probability that the model gives to the correct token and watch how its loss and the batch mean change.",
      reset: "Reset example",
      contributions: "Contribution to the batch",
      batchLoss: "Batch cross-entropy",
      perplexity: "Perplexity",
      sum: "Sum of contributions",
      formula: "The mean loss is the sum of the contributions.",
      note: "Each row is a separate next-token distribution, so the four probabilities do not need to add up to 1. Perplexity is exp(batch loss).",
      tokens: ["The → sky", "sky → is", "is → cloudy", "cloudy → ."],
      tokenTargets: ["sky", "is", "cloudy", "."],
      lossLabel: "loss",
      contributionLabel: "contribution",
      sentence: "Example: “The sky is cloudy.”",
    }
  : {
      title: "La cuenta de la pérdida",
      intro:
        "Cada fila es una posición del lote. Mueve la probabilidad que el modelo asigna al token correcto y observa cómo cambian su pérdida y la media del lote.",
      reset: "Restablecer ejemplo",
      contributions: "Contribución al lote",
      batchLoss: "Entropía cruzada del lote",
      perplexity: "Perplejidad",
      sum: "Suma de aportes",
      formula: "La pérdida media es la suma de las contribuciones.",
      note: "Cada fila es una distribución del siguiente token distinta, así que las cuatro probabilidades no tienen que sumar 1. La perplejidad es exp(pérdida del lote).",
      tokens: ["El → cielo", "cielo → está", "está → nublado", "nublado → ."],
      tokenTargets: ["cielo", "está", "nublado", "."],
      lossLabel: "pérdida",
      contributionLabel: "aporte",
      sentence: "Ejemplo: «El cielo está nublado.»",
    };

const DEFAULTS = [0.8, 0.1, 0.6, 0.4];

function locale() {
  return isEnglish ? "en-GB" : "es-ES";
}

function number(value, digits = 2) {
  return new Intl.NumberFormat(locale(), {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

function compact(value) {
  if (value >= 100) return number(value, 0);
  if (value >= 10) return number(value, 1);
  return number(value, 2);
}

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

function barRow(label, value, max, display) {
  const width = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
  return h(
    "div",
    { class: "bar-row" },
    h("span", { class: "bar-label", title: label }, label),
    h(
      "div",
      { class: "bar-track" },
      h("span", { style: `width:${width}%` })
    ),
    h("span", { class: "bar-value" }, display)
  );
}

export default {
  id: "loss",

  mount(root) {
    const body = root.querySelector("[data-lab-body]") || root;
    const state = DEFAULTS.slice();
    const controls = [];

    const batchLoss = h("strong", {}, "—");
    const perplexity = h("strong", {}, "—");
    const sumContributions = h("strong", {}, "—");
    const stats = h(
      "div",
      { class: "lab-stat-row" },
      stat(copy.batchLoss, batchLoss),
      stat(copy.perplexity, perplexity),
      stat(copy.sum, sumContributions)
    );

    const bars = h("div", { class: "bar-list" });
    const formula = h("p", { class: "small muted" });
    const live = h("div", { class: "small muted", "aria-live": "polite" });
    const reset = h(
      "button",
      { type: "button", class: "btn btn-secondary btn-sm" },
      copy.reset
    );

    const controlBox = h(
      "div",
      { class: "lab-controls" },
      h("p", { class: "small muted" }, copy.sentence),
      h("p", { class: "small" }, copy.intro)
    );

    for (let index = 0; index < copy.tokens.length; index += 1) {
      const id = `loss-p-${index}`;
      const output = h("output", { for: id }, `${number(state[index], 2)}`);
      const detail = h("small", {}, "");
      const input = h("input", {
        id,
        type: "range",
        min: "0.01",
        max: "1",
        step: "0.01",
        value: String(state[index]),
      });

      input.addEventListener("input", () => {
        state[index] = Number(input.value);
        render();
      });

      controlBox.append(
        h(
          "div",
          { class: "field" },
          h("label", { for: id }, copy.tokens[index], output),
          input,
          detail
        )
      );
      controls.push({ input, output, detail });
    }

    controlBox.append(reset);

    reset.addEventListener("click", () => {
      for (let index = 0; index < state.length; index += 1) {
        state[index] = DEFAULTS[index];
        controls[index].input.value = String(DEFAULTS[index]);
      }
      render();
    });

    const output = h(
      "div",
      { class: "lab-output" },
      h("h4", {}, copy.title),
      stats,
      h("h4", { class: "mt-3" }, copy.contributions),
      bars,
      formula,
      h("p", { class: "small muted mt-2" }, copy.note),
      live
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controlBox, output));

    function render() {
      const losses = state.map((probability) =>
        -Math.log(Math.max(probability, 0.000001))
      );
      const mean = losses.reduce((sum, value) => sum + value, 0) / losses.length;
      const perplexityValue = Math.exp(mean);
      const contributions = losses.map((value) => value / losses.length);
      const total = contributions.reduce((sum, value) => sum + value, 0);
      const maxContribution = Math.max(...contributions, 0.000001);

      batchLoss.textContent = number(mean, 3);
      perplexity.textContent = compact(perplexityValue);
      sumContributions.textContent = number(total, 3);

      bars.replaceChildren(
        ...contributions.map((value, index) =>
          barRow(
            copy.tokenTargets[index],
            value,
            maxContribution,
            number(value, 3)
          )
        )
      );

      formula.textContent = `${copy.formula} ${contributions
        .map((value) => number(value, 3))
        .join(" + ")} = ${number(total, 3)}.`;

      let worstIndex = 0;
      for (let index = 1; index < losses.length; index += 1) {
        if (losses[index] > losses[worstIndex]) worstIndex = index;
      }

      live.textContent = isEnglish
        ? `The lowest probability is ${number(
            state[worstIndex],
            2
          )} and contributes ${number(
            contributions[worstIndex],
            3
          )}. Batch cross-entropy ${number(mean, 3)}; perplexity ${compact(
            perplexityValue
          )}.`
        : `La probabilidad más baja es ${number(
            state[worstIndex],
            2
          )} y aporta ${number(
            contributions[worstIndex],
            3
          )}. Entropía cruzada del lote ${number(mean, 3)}; perplejidad ${compact(
            perplexityValue
          )}.`;

      controls.forEach((control, index) => {
        const p = state[index];
        const loss = losses[index];
        control.output.textContent = number(p, 2);
        control.input.setAttribute(
          "aria-valuetext",
          `${number(p, 2)} · ${copy.lossLabel} ${number(loss, 3)}`
        );
        control.detail.textContent = `${copy.lossLabel} ${number(
          loss,
          3
        )} · ${copy.contributionLabel} ${number(contributions[index], 3)}`;
      });
    }

    render();
    return () => {};
  },
};
