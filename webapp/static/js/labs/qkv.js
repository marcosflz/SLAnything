/* Laboratorio · Consultas, claves y valores
   Cinco tokens, embeddings de 4 dimensiones y proyecciones fijas.
   La atención se calcula en vivo; no hay dependencias ni red. */

import { h } from "./common.js";

const EMBEDDINGS = [
  [0.90, 0.20, 0.10, 0.30],
  [0.20, 0.90, 0.40, 0.10],
  [0.10, 0.40, 0.80, 0.30],
  [0.80, 0.10, 0.20, 0.40],
  [0.20, 0.30, 0.50, 0.90],
];

const W_Q = [
  [-2.0, 1.0, 2.0, -1.0],
  [-2.0, 2.0, -2.0, 1.0],
  [1.0, -2.0, -2.0, 0.0],
  [0.0, -2.0, 1.0, 2.0],
];

const W_K = [
  [2.0, -2.0, 1.0, 0.0],
  [-2.0, 1.0, 0.0, -1.0],
  [-2.0, -1.0, -2.0, -2.0],
  [-2.0, -2.0, 0.0, -1.0],
];

const W_V = [
  [0.50, 0.20, 0.00, 0.00],
  [0.00, 0.60, 0.10, 0.00],
  [0.10, 0.00, 0.70, 0.10],
  [0.00, 0.10, 0.00, 0.80],
];

const DIM = 4;

const STRINGS = {
  es: {
    intro:
      "Cada token produce una consulta (Q), una clave (K) y un valor (V). Elige una consulta y observa cómo se reparte su atención entre las claves.",
    choose: "Token que consulta",
    query: "Consulta Q del token elegido",
    queryHint: "La consulta es lo que ese token busca en los demás.",
    keysTitle: "Claves y valores",
    keysHint:
      "Cada clave se compara con la consulta; el valor es el contenido que se mezcla si recibe atención.",
    weights: "Pesos de atención",
    weightsHint:
      "Los pesos de una fila suman 100 %. Salen de softmax(QKᵀ / √d_k); aquí d_k = 4.",
    token: "Token",
    key: "Clave K",
    value: "Valor V",
    score: "puntuación",
    bars: "Barras",
    matrix: "Matriz",
    viewLabel: "Vista de los pesos",
    matrixCaption: "Matriz de atención completa: cada fila es la consulta y cada columna, la clave.",
    summary:
      "La consulta de «{token}» atiende sobre todo a «{top}» ({value} %).",
    summarySelf:
      "La consulta de «{token}» se atiende principalmente a sí misma ({value} %).",
    dims: "Dimensiones",
    tokens: "Tokens",
    topWeight: "Peso máximo",
    note:
      "Ejemplo didáctico con 4 dimensiones por cabeza y proyecciones fijas. En GPT-2 pequeño, cada cabeza trabaja con 64 dimensiones.",
  },
  en: {
    intro:
      "Each token produces a query (Q), a key (K), and a value (V). Pick a query and watch how its attention is distributed across the keys.",
    choose: "Querying token",
    query: "Query Q of the selected token",
    queryHint: "The query is what that token looks for in the others.",
    keysTitle: "Keys and values",
    keysHint:
      "Each key is compared with the query; the value is the content mixed when it receives attention.",
    weights: "Attention weights",
    weightsHint:
      "Weights in a row sum to 100%. They come from softmax(QKᵀ / √d_k); here d_k = 4.",
    token: "Token",
    key: "Key K",
    value: "Value V",
    score: "score",
    bars: "Bars",
    matrix: "Matrix",
    viewLabel: "Weight view",
    matrixCaption: "Full attention matrix: each row is the query and each column is the key.",
    summary:
      "The query of “{token}” attends mostly to “{top}” ({value}%).",
    summarySelf:
      "The query of “{token}” attends mostly to itself ({value}%).",
    dims: "Dimensions",
    tokens: "Tokens",
    topWeight: "Top weight",
    note:
      "A didactic example with 4 dimensions per head and fixed projections. In GPT-2 small, each head works with 64 dimensions.",
  },
};

function pickStrings() {
  const lang = (document.documentElement.lang || "es").toLowerCase();
  return lang.startsWith("en") ? STRINGS.en : STRINGS.es;
}

function pickTokens(lang) {
  return lang.startsWith("en")
    ? ["The", "cat", "watches", "the", "fish"]
    : ["El", "gato", "mira", "el", "pez"];
}

function project(vector, matrix) {
  return matrix[0].map((_, column) =>
    vector.reduce((sum, value, row) => sum + value * matrix[row][column], 0)
  );
}

function dot(a, b) {
  return a.reduce((sum, value, index) => sum + value * b[index], 0);
}

function softmax(row) {
  const maximum = Math.max(...row);
  const exps = row.map((value) => Math.exp(value - maximum));
  const total = exps.reduce((sum, value) => sum + value, 0);
  return exps.map((value) => value / total);
}

function fill(template, values) {
  return Object.entries(values).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    template
  );
}

const Q = EMBEDDINGS.map((vector) => project(vector, W_Q));
const K = EMBEDDINGS.map((vector) => project(vector, W_K));
const V = EMBEDDINGS.map((vector) => project(vector, W_V));
const SCORES = Q.map((query) => K.map((key) => dot(query, key) / Math.sqrt(DIM)));
const WEIGHTS = SCORES.map((row) => softmax(row));

function vectorText(values, formatter) {
  return `[${values.map(formatter).join(", ")}]`;
}

function statCard(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

export default {
  id: "qkv",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    const STR = pickStrings();
    const lang = (document.documentElement.lang || "es").toLowerCase().startsWith("en")
      ? "en"
      : "es";
    const TOKENS = pickTokens(lang);
    const numberFormat = new Intl.NumberFormat(lang === "en" ? "en" : "es", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    const format = (value) => numberFormat.format(value);
    const percent = (value) =>
      lang === "en"
        ? `${Math.round(value * 100)}%`
        : `${Math.round(value * 100)} %`;

    let selected = 1;
    let view = "bars";

    const tokenGroup = h("div", {
      class: "token-row",
      role: "group",
      "aria-label": STR.choose,
    });
    const queryPanel = h("div", {});
    const tableWrap = h("div", { class: "table-wrap" });
    const weightsTitle = h("h4", {}, STR.weights);
    const summary = h("p", {
      class: "small",
      "aria-live": "polite",
      style: "margin: 6px 0 10px",
    });
    const viewGroup = h("div", {
      class: "segmented",
      role: "group",
      "aria-label": STR.viewLabel,
    });
    const barsWrap = h("div", {});
    const matrixWrap = h("div", {});
    const stats = h("div", { class: "lab-stat-row mt-3" });

    const controls = h(
      "div",
      { class: "lab-controls" },
      h("p", { class: "small" }, STR.intro),
      tokenGroup,
      h(
        "div",
        { class: "field" },
        h("strong", { style: "font-size:12px" }, STR.query),
        queryPanel,
        h("small", {}, STR.queryHint)
      ),
      h(
        "p",
        { class: "small muted", style: "margin-top:0" },
        STR.note
      )
    );

    const output = h(
      "div",
      { class: "lab-output" },
      h("h4", {}, STR.keysTitle),
      tableWrap,
      weightsTitle,
      summary,
      h("div", { class: "row", style: "justify-content:space-between;align-items:center;gap:8px" },
        h("p", { class: "small muted", style: "margin:0" }, STR.weightsHint),
        viewGroup
      ),
      barsWrap,
      matrixWrap,
      stats
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function renderTokenGroup() {
      tokenGroup.replaceChildren();
      TOKENS.forEach((token, index) => {
        tokenGroup.append(
          h(
            "button",
            {
              type: "button",
              class: `token-chip${index === selected ? " is-selected" : ""}`,
              "aria-pressed": index === selected ? "true" : "false",
              onclick: () => {
                selected = index;
                render();
              },
            },
            token
          )
        );
      });
    }

    function renderQuery() {
      queryPanel.replaceChildren(
        h(
          "div",
          {
            class: "row",
            style: "gap:8px;font-family:var(--mono);font-size:12px;margin:6px 0 4px;align-items:center",
          },
          h("span", { class: "badge badge-brand" }, TOKENS[selected]),
          h("span", {}, vectorText(Q[selected], format))
        )
      );
    }

    function renderKvTable() {
      const head = h(
        "tr",
        {},
        h("th", { scope: "col" }, STR.token),
        h("th", { scope: "col" }, STR.key),
        h("th", { scope: "col" }, STR.value)
      );
      const rows = TOKENS.map((token, index) =>
        h(
          "tr",
          {
            style: index === selected
              ? "background:var(--brand-soft)"
              : null,
          },
          h("th", { scope: "row", style: "text-transform:none;letter-spacing:0;font-size:12px;color:var(--text)" }, token),
          h("td", { style: "font-family:var(--mono);font-size:11px;white-space:nowrap" }, vectorText(K[index], format)),
          h("td", { style: "font-family:var(--mono);font-size:11px;white-space:nowrap" }, vectorText(V[index], format))
        )
      );
      tableWrap.replaceChildren(
        h(
          "table",
          {},
          h("caption", {}, STR.keysHint),
          h("thead", {}, head),
          h("tbody", {}, rows)
        )
      );
    }

    function renderBars() {
      const row = WEIGHTS[selected];
      const top = TOKENS.reduce(
        (best, token, index) => (row[index] > row[best.index] ? { token, index } : best),
        { token: TOKENS[0], index: 0 }
      );
      summary.textContent = fill(
        top.index === selected ? STR.summarySelf : STR.summary,
        {
          token: TOKENS[selected],
          top: top.token,
          value: Math.round(row[top.index] * 100),
        }
      );

      barsWrap.replaceChildren(
        h(
          "div",
          { class: "bar-list", style: "margin-top:10px" },
          TOKENS.map((token, index) => {
            const weight = row[index];
            return h(
              "div",
              {
                class: "bar-row",
                title: `${TOKENS[selected]} → ${token}: ${percent(weight)} (${STR.score} ${format(
                  SCORES[selected][index]
                )})`,
              },
              h("span", { class: "bar-label" }, `${index + 1}. ${token}`),
              h(
                "div",
                { class: "bar-track" },
                h("span", {
                  style: `width:${(weight * 100).toFixed(1)}%;background:linear-gradient(90deg,#d97706,#fbbf24)`,
                })
              ),
              h("span", { class: "bar-value" }, percent(weight))
            );
          })
        )
      );
    }

    function renderMatrix() {
      const head = h(
        "tr",
        {},
        h("th", { scope: "col" }, `${TOKENS[selected]} ↓ / →`),
        ...TOKENS.map((token) => h("th", { scope: "col", style: "text-align:center" }, token))
      );
      const rows = TOKENS.map((token, rowIndex) => {
        const rowMaximum = Math.max(...WEIGHTS[rowIndex]);
        return h(
          "tr",
          {},
          h(
            "th",
            {
              scope: "row",
              style: "text-transform:none;letter-spacing:0;font-size:11px;color:var(--text)",
            },
            token
          ),
          ...WEIGHTS[rowIndex].map((weight) => {
            const alpha = 0.08 + 0.82 * (weight / Math.max(rowMaximum, 0.0001));
            return h(
              "td",
              {
                style:
                  `text-align:center;font-family:var(--mono);font-size:10px;` +
                  `background:rgba(217,119,6,${alpha.toFixed(3)});` +
                  `color:${alpha > 0.55 ? "#fff" : "var(--text)"}`,
              },
              percent(weight)
            );
          })
        );
      });
      matrixWrap.replaceChildren(
        h(
          "div",
          { class: "table-wrap", style: "margin-top:10px" },
          h(
            "table",
            {},
            h("caption", {}, STR.matrixCaption),
            h("thead", {}, head),
            h("tbody", {}, rows)
          )
        )
      );
    }

    function renderViewButtons() {
      viewGroup.replaceChildren();
      [
        ["bars", STR.bars],
        ["matrix", STR.matrix],
      ].forEach(([key, label]) => {
        viewGroup.append(
          h(
            "button",
            {
              type: "button",
              class: key === view ? "is-active" : "",
              "aria-pressed": key === view ? "true" : "false",
              onclick: () => {
                view = key;
                render();
              },
            },
            label
          )
        );
      });
    }

    function renderStats() {
      const row = WEIGHTS[selected];
      const top = Math.max(...row);
      stats.replaceChildren(
        statCard(STR.dims, String(DIM)),
        statCard(STR.tokens, String(TOKENS.length)),
        statCard(STR.topWeight, percent(top))
      );
    }

    function render() {
      renderTokenGroup();
      renderQuery();
      renderKvTable();
      renderViewButtons();
      renderBars();
      if (view === "matrix") renderMatrix();
      barsWrap.style.display = view === "bars" ? "block" : "none";
      matrixWrap.style.display = view === "matrix" ? "block" : "none";
      renderStats();
    }

    render();
    return () => {};
  },
};
