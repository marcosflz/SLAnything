/* Laboratorio · Dentro del transformer
   Mapa conceptual de seis etapas, con variantes de encoder y decoder. */

import { h, bar, num } from "./common.js";
import { lang, t } from "../i18n.js";

const STEPS_ES = [
  { title: "Tokenización", sub: "texto → IDs", focus: "texto" },
  { title: "Embeddings", sub: "IDs → vectores", focus: "vectores" },
  { title: "Self-attention", sub: "contexto entre tokens", focus: "contexto" },
  { title: "Feed-forward", sub: "transformación por token", focus: "por token" },
  { title: "Capas + residual", sub: "profundidad estable", focus: "profundidad" },
  { title: "Salida", sub: "probabilidades", focus: "predicción" },
];

const STEPS_EN = [
  { title: "Tokenization", sub: "text → IDs", focus: "text" },
  { title: "Embeddings", sub: "IDs → vectors", focus: "vectors" },
  { title: "Self-attention", sub: "context across tokens", focus: "context" },
  { title: "Feed-forward", sub: "per-token transformation", focus: "per token" },
  { title: "Layers + residual", sub: "stable depth", focus: "depth" },
  { title: "Output", sub: "probabilities", focus: "prediction" },
];

const MODES_ES = {
  encoder: {
    label: "Encoder",
    note: "Ve toda la secuencia en ambas direcciones.",
  },
  decoder: {
    label: "Decoder",
    note: "Usa máscara causal y genera de izquierda a derecha.",
  },
};

const MODES_EN = {
  encoder: {
    label: "Encoder",
    note: "Sees the whole sequence in both directions.",
  },
  decoder: {
    label: "Decoder",
    note: "Uses a causal mask and generates from left to right.",
  },
};

const DETAILS_ES = {
  encoder: [
    {
      text:
        "El texto se divide en tokens y cada token se convierte en un ID del vocabulario. " +
        "El encoder recibe la frase completa de una vez, sin generar todavía ninguna palabra.",
      input: "frase",
      output: "IDs",
    },
    {
      text:
        "Cada ID se busca en la tabla de embeddings y se le suma información de posición. " +
        "Así cada token empieza como un vector distinto que la atención podrá comparar.",
      input: "IDs",
      output: "vectores",
    },
    {
      text:
        "Cada token compara su query con las keys de todos los tokens, también los de la derecha. " +
        "El softmax reparte pesos que suman 1 y mezcla los values.",
      input: "vectores",
      output: "contexto",
    },
    {
      text:
        "Cada vector pasa por la misma red feed-forward, posición a posición. " +
        "Es una transformación no lineal que no mezcla tokens entre sí; eso ya lo hizo la atención.",
      input: "vector",
      output: "vector",
    },
    {
      text:
        "Cada subcapa se envuelve en una conexión residual y una normalización. " +
        "La suma x + Sublayer(x) facilita que el gradiente fluya en pilas profundas.",
      input: "vector",
      output: "bloque",
    },
    {
      text:
        "La pila del encoder devuelve un vector contextual por token. " +
        "Según la tarea, se conecta a una cabeza de clasificación o se usa como representación de la frase.",
      input: "vectores",
      output: "etiquetas",
    },
  ],
  decoder: [
    {
      text:
        "El decoder recibe la secuencia que ya existe: el prompt y lo generado hasta ahora. " +
        "También se tokeniza igual, pero la secuencia crece a cada paso de generación.",
      input: "texto conocido",
      output: "IDs",
    },
    {
      text:
        "Cada ID se convierte en un vector y se le suma su posición. " +
        "En generación, la representación del último token es la que suele disparar la siguiente predicción.",
      input: "IDs",
      output: "vectores",
    },
    {
      text:
        "La atención funciona igual, pero con máscara causal: un token solo puede mirar hacia atrás. " +
        "La posición que se está generando no puede ver el futuro porque aún no existe.",
      input: "vectores",
      output: "contexto",
    },
    {
      text:
        "La red feed-forward se aplica a cada posición de forma independiente. " +
        "No introduce información de otros tokens: esa mezcla ya la hizo la atención.",
      input: "vector",
      output: "vector",
    },
    {
      text:
        "El bloque del decoder añade una segunda atención sobre la salida del encoder. " +
        "Residuales y normalización mantienen estable la pila mientras la generación avanza.",
      input: "vector",
      output: "bloque",
    },
    {
      text:
        "La última representación se proyecta al tamaño del vocabulario y un softmax da probabilidades. " +
        "Se elige un token, se añade a la secuencia y el proceso se repite.",
      input: "vector",
      output: "probabilidades",
    },
  ],
};

const DETAILS_EN = {
  encoder: [
    {
      text:
        "The text is split into tokens and each token becomes a vocabulary ID. " +
        "The encoder receives the complete sentence at once, without generating any word yet.",
      input: "sentence",
      output: "IDs",
    },
    {
      text:
        "Each ID is looked up in the embedding table and position information is added. " +
        "That way each token starts as a distinct vector that attention can compare.",
      input: "IDs",
      output: "vectors",
    },
    {
      text:
        "Each token compares its query with the keys of all tokens, including those on the right. " +
        "Softmax distributes weights that sum to 1 and mixes the values.",
      input: "vectors",
      output: "context",
    },
    {
      text:
        "Each vector goes through the same feed-forward network, position by position. " +
        "It is a non-linear transformation that does not mix tokens; attention already did that.",
      input: "vector",
      output: "vector",
    },
    {
      text:
        "Each sublayer is wrapped in a residual connection and normalization. " +
        "The sum x + Sublayer(x) helps gradients flow in deep stacks.",
      input: "vector",
      output: "block",
    },
    {
      text:
        "The encoder stack returns a contextual vector per token. " +
        "Depending on the task, it is connected to a classification head or used as a sentence representation.",
      input: "vectors",
      output: "labels",
    },
  ],
  decoder: [
    {
      text:
        "The decoder receives the sequence that already exists: the prompt and what has been generated so far. " +
        "It is tokenized the same way, but the sequence grows at every generation step.",
      input: "known text",
      output: "IDs",
    },
    {
      text:
        "Each ID becomes a vector and its position is added. " +
        "During generation, the last token's representation usually drives the next prediction.",
      input: "IDs",
      output: "vectors",
    },
    {
      text:
        "Attention works the same way, but with a causal mask: a token can only look backwards. " +
        "The position being generated cannot see the future because it does not exist yet.",
      input: "vectors",
      output: "context",
    },
    {
      text:
        "The feed-forward network is applied to each position independently. " +
        "It does not introduce information from other tokens: attention already did that mixing.",
      input: "vector",
      output: "vector",
    },
    {
      text:
        "The decoder block adds a second attention over the encoder output. " +
        "Residuals and normalization keep the stack stable as generation advances.",
      input: "vector",
      output: "block",
    },
    {
      text:
        "The last representation is projected to the vocabulary size and a softmax gives probabilities. " +
        "A token is chosen, appended to the sequence, and the process repeats.",
      input: "vector",
      output: "probabilities",
    },
  ],
};

const STEPS = lang === "en" ? STEPS_EN : STEPS_ES;
const MODES = lang === "en" ? MODES_EN : MODES_ES;
const DETAILS = lang === "en" ? DETAILS_EN : DETAILS_ES;
const EXAMPLE_TOKENS =
  lang === "en"
    ? ["The", "cat", "sleeps", "on", "the", "sofa"]
    : ["El", "gato", "duerme", "sobre", "el", "sofá"];

function statCard(label, value, compact = false) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", { style: compact ? "font-size:13px" : null }, value)
  );
}

function chip(text, className = "") {
  return h("span", { class: `token-chip ${className}`.trim() }, text);
}

export default {
  id: "transformer",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let step = 0;
    let mode = "encoder";
    let modeJustChanged = false;

    const modeGroup = h("div", {
      class: "segmented",
      role: "group",
      "aria-label": t("Modo del transformer"),
    });
    const note = h("p", {
      class: "small muted",
      "aria-live": "polite",
      style: "margin:10px 0 0",
    });
    const pipeline = h("div", { class: "pipeline" });
    const detail = h("div", { class: "step-detail" });
    const example = h("div");
    const stats = h("div", { class: "lab-stat-row mt-3" });

    const prevButton = h(
      "button",
      { class: "btn btn-secondary btn-sm", type: "button" },
      t("← Anterior")
    );
    const nextButton = h(
      "button",
      { class: "btn btn-primary btn-sm", type: "button" },
      t("Siguiente →")
    );

    prevButton.addEventListener("click", () => {
      if (step > 0) {
        step -= 1;
        modeJustChanged = false;
        render();
      }
    });

    nextButton.addEventListener("click", () => {
      if (step < STEPS.length - 1) {
        step += 1;
        modeJustChanged = false;
        render();
      }
    });

    const top = h(
      "div",
      {
        class: "row",
        style: "justify-content:space-between;align-items:center;gap:12px",
      },
      modeGroup,
      h("div", { class: "row" }, prevButton, nextButton)
    );

    const grid = h(
      "div",
      { class: "lab-grid mt-3" },
      h(
        "div",
        { class: "lab-controls" },
        detail,
        h(
          "p",
          { class: "small muted" },
          t("Mapa conceptual: no es una implementación real ni ejecuta un modelo. Al cambiar de modo se conserva el paso para que compares la misma etapa.")
        )
      ),
      h(
        "div",
        { class: "lab-output" },
        h("h4", {}, t("Qué ocurre con los datos")),
        example,
        stats
      )
    );

    body.replaceChildren(top, note, pipeline, grid);

    function renderModeButtons() {
      modeGroup.replaceChildren();
      Object.entries(MODES).forEach(([key, value]) => {
        modeGroup.append(
          h(
            "button",
            {
              type: "button",
              class: key === mode ? "is-active" : "",
              "aria-pressed": key === mode ? "true" : "false",
              onclick: () => {
                if (mode !== key) {
                  mode = key;
                  modeJustChanged = true;
                  render();
                }
              },
            },
            value.label
          )
        );
      });
    }

    function renderPipeline() {
      pipeline.replaceChildren();
      STEPS.forEach((item, index) => {
        if (index > 0) {
          pipeline.append(
            h(
              "span",
              { class: "pipeline-arrow", "aria-hidden": "true", style: "width:10px" },
              "→"
            )
          );
        }
        pipeline.append(
          h(
            "button",
            {
              type: "button",
              class: `pipeline-step${index === step ? " is-active" : ""}`,
              "aria-current": index === step ? "step" : null,
              "aria-label": t("Paso {n}: {title}", { n: index + 1, title: item.title }),
              style: "font:inherit;cursor:pointer;min-width:78px;padding:9px 6px",
              onclick: () => {
                step = index;
                modeJustChanged = false;
                render();
              },
            },
            h("small", {}, t("Paso {n}", { n: index + 1 })),
            h("strong", {}, item.title),
            h("small", {}, item.sub)
          )
        );
      });
    }

    function renderDetail() {
      const data = DETAILS[mode][step];
      detail.replaceChildren(
        h(
          "div",
          { class: "row" },
          h("span", { class: "badge badge-brand" }, t("Paso {n} de {total}", { n: step + 1, total: STEPS.length })),
          h("span", { class: "badge" }, MODES[mode].label)
        ),
        h(
          "strong",
          { style: "display:block;margin-top:8px;font-size:14px" },
          STEPS[step].title
        ),
        h("p", { style: "margin:6px 0 10px" }, data.text),
        h(
          "div",
          { class: "row" },
          h("span", { class: "badge badge-success" }, t("Entra: {value}", { value: data.input })),
          h("span", { class: "badge badge-violet" }, t("Sale: {value}", { value: data.output }))
        )
      );
    }

    function renderExample() {
      const children = [];

      if (step === 0) {
        children.push(
          h("p", { class: "small muted" }, t("Frase de ejemplo, ya dividida en tokens:")),
          h(
            "div",
            { class: "token-row" },
            EXAMPLE_TOKENS.map((token, index) =>
              h(
                "span",
                { class: "token-chip" },
                token,
                h("span", { class: "prob" }, `#${101 + index * 37}`)
              )
            )
          ),
          h(
            "p",
            { class: "small muted" },
            mode === "encoder"
              ? t("El encoder recibe la frase completa. Los IDs son ilustrativos.")
              : t("El decoder recibe el prompt y lo que ya ha generado. Los IDs son ilustrativos.")
          )
        );
      } else if (step === 1) {
        const vectors = [
          [EXAMPLE_TOKENS[0], [0.21, -0.08, 0.44, 0.03]],
          [EXAMPLE_TOKENS[1], [-0.12, 0.35, 0.18, -0.27]],
          [EXAMPLE_TOKENS[2], [0.09, 0.12, -0.31, 0.4]],
        ];
        children.push(
          h(
            "p",
            { class: "small muted" },
            t("Cada ID se convierte en un vector. Aquí solo mostramos cuatro dimensiones.")
          ),
          ...vectors.map(([token, values]) =>
            h(
              "div",
              { class: "row", style: "margin:6px 0" },
              h("span", { class: "token-chip" }, token),
              h(
                "span",
                { class: "small", style: "font-family:var(--mono)" },
                `[${values.join(", ")}]`
              )
            )
          ),
          h(
            "p",
            { class: "small muted" },
            t("A cada vector se le suma una señal de posición para conservar el orden.")
          )
        );
      } else if (step === 2) {
        if (mode === "encoder") {
          const weights = [
            [EXAMPLE_TOKENS[0], 0.18],
            [EXAMPLE_TOKENS[1], 0.27],
            [EXAMPLE_TOKENS[2], 0.22],
            [EXAMPLE_TOKENS[3], 0.11],
            [EXAMPLE_TOKENS[4], 0.1],
            [EXAMPLE_TOKENS[5], 0.12],
          ];
          children.push(
            h(
              "p",
              { class: "small muted" },
              t("«{token}» puede mirar toda la frase, incluidos los tokens de la derecha:", { token: EXAMPLE_TOKENS[1] })
            ),
            h(
              "div",
              { class: "bar-list" },
              weights.map(([token, weight]) =>
                bar(token, weight, 1, {
                  format: (value) => `${num(value * 100, 0)} %`,
                })
              )
            )
          );
        } else {
          children.push(
            h(
              "p",
              { class: "small muted" },
              t("«{token}» solo puede mirar su pasado. Los tokens futuros están enmascarados:", { token: EXAMPLE_TOKENS[2] })
            ),
            h(
              "div",
              { class: "token-row" },
              chip(EXAMPLE_TOKENS[0]),
              chip(EXAMPLE_TOKENS[1]),
              chip(EXAMPLE_TOKENS[2]),
              chip(EXAMPLE_TOKENS[3], "is-masked"),
              chip(EXAMPLE_TOKENS[4], "is-masked"),
              chip(EXAMPLE_TOKENS[5], "is-masked")
            ),
            h(
              "div",
              { class: "bar-list" },
              [
                [EXAMPLE_TOKENS[0], 0.3],
                [EXAMPLE_TOKENS[1], 0.45],
                [EXAMPLE_TOKENS[2], 0.25],
              ].map(([token, weight]) =>
                bar(token, weight, 1, {
                  format: (value) => `${num(value * 100, 0)} %`,
                })
              )
            )
          );
        }
      } else if (step === 3) {
        children.push(
          h(
            "p",
            { class: "small muted" },
            t("La misma red se aplica a cada posición, sin mezclar tokens:")
          ),
          h(
            "div",
            { class: "output-text", style: "font-family:var(--mono);font-size:12px" },
            h("div", {}, t("vector")),
            h("div", { class: "muted" }, t("↓ capa intermedia (más ancha)")),
            h("div", {}, t("vector transformado")),
            h("div", { class: "muted" }, t("↓ proyección de vuelta")),
            h("div", {}, t("mismo tamaño que la entrada"))
          ),
          h(
            "p",
            { class: "small muted" },
            t("No hay atención aquí: cada token se transforma por separado.")
          )
        );
      } else if (step === 4) {
        children.push(
          h(
            "p",
            { class: "small muted" },
            t("Cada subcapa suma su entrada original antes de pasar a la siguiente:")
          ),
          h(
            "div",
            { class: "output-text", style: "font-family:var(--mono);font-size:12px" },
            h("div", {}, "x"),
            h("div", { class: "muted" }, "↓ self-attention"),
            h("div", {}, t("x + atención(x)")),
            h("div", { class: "muted" }, "↓ feed-forward"),
            h("div", {}, "x + feed-forward(x)"),
            h("div", { class: "muted" }, t("↓ se repite en N bloques"))
          ),
          h(
            "p",
            { class: "small muted" },
            mode === "encoder"
              ? t("El bloque del encoder solo tiene una atención; el del decoder, dos.")
              : t("El bloque del decoder añade atención sobre la representación del encoder.")
          )
        );
      } else {
        if (mode === "decoder") {
          children.push(
            h(
              "p",
              { class: "small muted" },
              t("Después de «{prompt}», el modelo reparte probabilidad:", {
                prompt: EXAMPLE_TOKENS.slice(0, 5).join(" "),
              })
            ),
            h(
              "div",
              { class: "bar-list" },
              (lang === "en"
                ? [
                    ["sofa", 0.34],
                    ["mattress", 0.18],
                    ["floor", 0.12],
                    ["there", 0.09],
                    ["sleep", 0.07],
                    ["others", 0.2],
                  ]
                : [
                    ["sofá", 0.34],
                    ["colchón", 0.18],
                    ["suelo", 0.12],
                    ["allí", 0.09],
                    ["dormir", 0.07],
                    ["otros", 0.2],
                  ]
              ).map(([token, weight]) =>
                bar(token, weight, 1, {
                  format: (value) => `${num(value * 100, 0)} %`,
                })
              )
            ),
            h(
              "p",
              { class: "small muted" },
              t("Se elige un token, se añade a la secuencia y se vuelve a empezar.")
            )
          );
        } else {
          children.push(
            h(
              "p",
              { class: "small muted" },
              t("La representación final puede alimentar una cabeza de clasificación:")
            ),
            h(
              "div",
              { class: "bar-list" },
              (lang === "en"
                ? [
                    ["positive", 0.71],
                    ["neutral", 0.19],
                    ["negative", 0.1],
                  ]
                : [
                    ["positivo", 0.71],
                    ["neutro", 0.19],
                    ["negativo", 0.1],
                  ]
              ).map(([token, weight]) =>
                bar(token, weight, 1, {
                  format: (value) => `${num(value * 100, 0)} %`,
                })
              )
            ),
            h(
              "p",
              { class: "small muted" },
              t("El ejemplo es ilustrativo: la tarea concreta la define la cabeza de salida.")
            )
          );
        }
      }

      example.replaceChildren(...children);
    }

    function render() {
      renderModeButtons();
      renderPipeline();
      renderDetail();
      renderExample();

      prevButton.disabled = step === 0;
      nextButton.disabled = step === STEPS.length - 1;
      const stepPhrase = modeJustChanged ? t("mantienes el paso") : t("paso");
      note.textContent = `${MODES[mode].label} · ${stepPhrase} ${step + 1} ${t("de")} ${STEPS.length}. ${MODES[mode].note}`;

      stats.replaceChildren(
        statCard(t("Paso"), `${step + 1} / ${STEPS.length}`),
        statCard(t("Modo"), MODES[mode].label),
        statCard(t("Foco"), STEPS[step].focus, true)
      );
    }

    render();
    return () => {};
  },
};
