/* Laboratorio · Generador de n-gramas entrenado con un fragmento de El Quijote. */

import {
  h,
  num,
  pct,
  bar,
  tokenize,
  buildNGramModel,
  nextDistribution,
  sampleNext,
  mulberry32,
  detokenize,
  loadText,
} from "./common.js";
import { t } from "../i18n.js";

const CORPUS_URL = "/static/data/quijote_fragmento.txt";
const MAX_ORDER = 4;
const INITIAL_CONTEXT = "El caballero";
const INITIAL_SEED = 7;
const CLOSING = new Set([".", ",", ";", ":", "!", "?", ")", "]", "}"]);

/* El corpus y el modelo se cargan una sola vez por página. */
let corpusCache = null;
let corpusPromise = null;

/*
 * `buildNGramModel` guarda cada distribución bajo el orden del n-grama
 * (por ejemplo, "4:contexto de 3 tokens"), mientras que `nextDistribution`
 * indexa por el número de tokens del contexto ("3:contexto"). Según la
 * versión de common.js, una de las dos convenciones funciona. Construimos
 * una copia reindexada y comprobamos con un 4-grama real cuál responde.
 */
function prepareModel(raw) {
  const shiftedCounts = new Map();
  for (const [key, bucket] of raw.counts) {
    const separator = key.indexOf(":");
    const order = Number(key.slice(0, separator));
    const context = key.slice(separator + 1);
    const queryKey = order > 1 ? `${order - 1}:${context}` : key;
    if (!shiftedCounts.has(queryKey)) shiftedCounts.set(queryKey, bucket);
  }
  const shifted = { ...raw, counts: shiftedCounts };

  let probes = 0;
  for (const [key, bucket] of raw.counts) {
    if (!key.startsWith("4:") || bucket.size < 2) continue;
    if (++probes > 12) break;
    let token = null;
    let count = 0;
    let total = 0;
    for (const [candidate, value] of bucket) {
      total += value;
      if (value > count) {
        token = candidate;
        count = value;
      }
    }
    if (!token || !total) continue;

    const context = key.slice(2).split(" ");
    const expectedProb = count / total;
    const matches = (model) => {
      const top = nextDistribution(model, context, 1)[0];
      return (
        top !== undefined &&
        top.token === token &&
        Math.abs(top.prob - expectedProb) < 1e-9
      );
    };

    if (matches(raw)) return raw;
    if (matches(shifted)) return shifted;
  }
  return shifted;
}

function loadCorpus() {
  if (corpusCache) return Promise.resolve(corpusCache);
  if (!corpusPromise) {
    corpusPromise = (async () => {
      try {
        const text = await loadText(CORPUS_URL);
        // Deja que el navegador pinte el aviso de carga antes de contar n-gramas.
        await new Promise((resolve) => setTimeout(resolve, 30));
        const tokens = tokenize(text);
        const model = prepareModel(buildNGramModel(tokens, MAX_ORDER));
        corpusCache = { tokens, model };
        return corpusCache;
      } catch (error) {
        corpusPromise = null;
        throw error;
      }
    })();
  }
  return corpusPromise;
}

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

function sliderField(id, labelText, attrs, output) {
  const input = h("input", {
    id,
    type: "range",
    ...attrs,
  });
  return {
    input,
    node: h(
      "div",
      { class: "field" },
      h("label", { for: id }, labelText, output),
      input
    ),
  };
}

export default {
  id: "ngram",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    let disposed = false;

    const showLoading = () => {
      body.replaceChildren(
        h(
          "div",
          { class: "lab-loading" },
          h("span", { class: "spinner", "aria-hidden": "true" }),
          ` ${t("Entrenando modelo…")}`
        )
      );
    };

    const showError = (error) => {
      if (disposed) return;
      body.replaceChildren(
        h(
          "div",
          { class: "callout callout-danger" },
          h("div", { class: "callout-icon", "aria-hidden": "true" }, "!"),
          h(
            "div",
            { class: "callout-body" },
            h("strong", { class: "callout-title" }, t("No se pudo cargar el corpus")),
            h(
              "div",
              { class: "callout-text" },
              h(
                "p",
                {},
                `${t("El laboratorio necesita descargar")} `,
                h("code", {}, "quijote_fragmento.txt"),
                `. ${t("Revisa la conexión y vuelve a intentarlo.")}`
              ),
              h("p", { class: "small muted" }, error?.message || String(error)),
              h(
                "button",
                {
                  class: "btn btn-secondary btn-sm",
                  type: "button",
                  onclick: () => start(),
                },
                t("Reintentar")
              )
            )
          )
        )
      );
    };

    const start = () => {
      if (disposed) return;
      showLoading();
      loadCorpus()
        .then(({ tokens, model }) => {
          if (disposed) return;
          buildLab(body, tokens, model);
        })
        .catch(showError);
    };

    start();
    return () => {
      disposed = true;
    };
  },
};

function buildLab(body, corpusTokens, model) {
  const fallbackTokens = corpusTokens.slice(0, 3);

  let seed = INITIAL_SEED;

  /* ----------------------------- Controles ----------------------------- */
  const contextInput = h("input", {
    id: "ngram-context",
    type: "text",
    value: INITIAL_CONTEXT,
    placeholder: t("Escribe un comienzo…"),
    autocomplete: "off",
    spellcheck: "false",
  });

  const tempOutput = h("output", { for: "ngram-temperature" }, "0,8");
  const temp = sliderField(
    "ngram-temperature",
    t("Temperatura"),
    { min: "0.1", max: "1.5", step: "0.1", value: "0.8" },
    tempOutput
  );

  const topKOutput = h("output", { for: "ngram-topk" }, "40");
  const topK = sliderField(
    "ngram-topk",
    "Top-k",
    { min: "1", max: "50", step: "1", value: "40" },
    topKOutput
  );

  const lengthOutput = h("output", { for: "ngram-length" }, "18");
  const length = sliderField(
    "ngram-length",
    t("Longitud"),
    { min: "5", max: "40", step: "1", value: "18" },
    lengthOutput
  );

  const seedOutput = h("span", {}, num(seed, 0));
  const generateButton = h(
    "button",
    { class: "btn btn-primary", type: "button" },
    t("Generar texto")
  );
  const seedButton = h(
    "button",
    { class: "btn btn-secondary", type: "button" },
    t("Nueva semilla")
  );

  const controls = h(
    "div",
    { class: "lab-controls" },
    h(
      "div",
      { class: "field" },
      h("label", { for: "ngram-context" }, t("Contexto")),
      contextInput,
      h("small", {}, t("El modelo mira como mucho los tres últimos tokens."))
    ),
    temp.node,
    topK.node,
    length.node,
    h(
      "div",
      { class: "row" },
      generateButton,
      seedButton,
      h("span", { class: "badge" }, `${t("Semilla")} `, seedOutput)
    ),
    h(
      "p",
      { class: "small muted" },
      t("Modelo de n-gramas: no es GPT, pero comparte la idea de predecir el siguiente token.")
    )
  );

  /* ------------------------------ Salida ------------------------------- */
  const outputText = h("div", {
    class: "output-text",
    "aria-live": "polite",
  });
  const statusLine = h("p", { class: "small muted" });
  const topHint = h("p", { class: "small muted" });
  const topList = h("div", { class: "bar-list" });
  const stats = h(
    "div",
    { class: "lab-stat-row mt-3" },
    stat(t("Tokens del corpus"), num(model.totalTokens, 0)),
    stat(t("Vocabulario"), num(model.vocab, 0)),
    stat(t("Contextos de 3 tokens"), num(model.contexts, 0))
  );

  const output = h(
    "div",
    { class: "lab-output" },
    h("h4", {}, t("Texto generado")),
    outputText,
    statusLine,
    h("h4", { class: "mt-3" }, t("Siguientes tokens más probables")),
    topHint,
    topList,
    stats
  );

  body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

  /* ---------------------------- Lógica -------------------------------- */
  const currentPrompt = () => {
    const typed = tokenize(contextInput.value);
    if (typed.length) return { tokens: typed, fallback: false };
    return { tokens: fallbackTokens.slice(), fallback: true };
  };

  const renderDistribution = (promptTokens, fallback) => {
    const distribution = nextDistribution(model, promptTokens, 10);
    topList.replaceChildren();

    if (!distribution.length) {
      topList.append(
        h("p", { class: "small muted" }, t("No hay continuaciones para este contexto."))
      );
      return;
    }

    const maxProb = distribution[0].prob || 1;
    distribution.forEach((item) => {
      topList.append(
        bar(item.token, item.prob, maxProb, {
          format: (value) => pct(value, 1),
        })
      );
    });

    topHint.textContent = fallback
      ? t("Contexto vacío: se usa el inicio del corpus. Barras relativas al candidato más probable.")
      : t("Barras relativas al candidato más probable. Se usa el contexto más largo que existe en el corpus.");
  };

  const render = () => {
    const temperature = Number(temp.input.value);
    const topKValue = Number(topK.input.value);
    const lengthValue = Number(length.input.value);
    const { tokens: promptTokens, fallback } = currentPrompt();

    const random = mulberry32(seed);
    const context = promptTokens.slice();
    const generated = [];

    for (let i = 0; i < lengthValue; i += 1) {
      const distribution = nextDistribution(model, context, Math.max(10, topKValue));
      if (!distribution.length) break;
      const next = sampleNext(distribution, temperature, topKValue, random);
      if (next === null || next === undefined) break;
      generated.push(next);
      context.push(next);
    }

    outputText.replaceChildren();
    const promptText = detokenize(promptTokens);
    const generatedText = detokenize(generated);
    if (promptText) outputText.append(h("span", { class: "muted" }, promptText));
    if (promptText && generatedText) {
      outputText.append(CLOSING.has(generated[0]) ? "" : " ");
    }
    if (generatedText) {
      outputText.append(h("span", { class: "generated" }, generatedText));
    }
    outputText.append(h("span", { class: "muted" }, " …"));

    statusLine.textContent = [
      fallback ? t("contexto de inicio del corpus") : t("contexto escrito"),
      t("semilla {n}", { n: num(seed, 0) }),
      t("{n} tokens", { n: num(lengthValue, 0) }),
      `T = ${num(temperature, 1)}`,
      `top-k ${num(topKValue, 0)}`,
    ].join(" · ");

    renderDistribution(promptTokens, fallback);
  };

  const syncLabels = () => {
    tempOutput.textContent = num(Number(temp.input.value), 1);
    topKOutput.textContent = num(Number(topK.input.value), 0);
    lengthOutput.textContent = num(Number(length.input.value), 0);
    seedOutput.textContent = num(seed, 0);
  };

  contextInput.addEventListener("input", render);
  temp.input.addEventListener("input", () => {
    syncLabels();
    render();
  });
  topK.input.addEventListener("input", () => {
    syncLabels();
    render();
  });
  length.input.addEventListener("input", () => {
    syncLabels();
    render();
  });
  generateButton.addEventListener("click", render);
  seedButton.addEventListener("click", () => {
    let candidate = Math.floor(Math.random() * 10000);
    if (candidate === seed) candidate = (candidate + 1) % 10000;
    seed = candidate;
    syncLabels();
    render();
  });

  syncLabels();
  render();
}
