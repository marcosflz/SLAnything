/* Laboratorio · Mapa de embeddings
   Vectores 2D ilustrativos, similitud coseno y vecinos editables. */

import { h } from "./common.js";

const EN = document.documentElement.lang.startsWith("en");

const S = EN
  ? {
      intro: "Pick a word and move its vector. The ranking on the right recomputes the cosine similarity against every other word.",
      mapTitle: "Map (2D projection)",
      selectLabel: "Word",
      coordsLabel: "Coordinates of the selected vector",
      rankingTitle: "Cosine similarity",
      stats: ["Closest", "Max cosine", "Norm"],
      reset: "Reset vectors",
      note: "The coordinates are illustrative. In a trained model they are learned in many dimensions; cosine compares directions, not lengths.",
      summary: (word, neighbour, value) => `“${word}” is closest to “${neighbour}” with cosine ${value}.`,
      axisX: "dimension 1",
      axisY: "dimension 2",
      xLabel: "x₁",
      yLabel: "x₂",
    }
  : {
      intro: "Elige una palabra y mueve su vector. La lista de la derecha recalcula la similitud coseno con todas las demás.",
      mapTitle: "Mapa (proyección 2D)",
      selectLabel: "Palabra",
      coordsLabel: "Coordenadas del vector seleccionado",
      rankingTitle: "Similitud coseno",
      stats: ["Más cercano", "Coseno máximo", "Norma"],
      reset: "Restablecer vectores",
      note: "Las coordenadas son ilustrativas. En un modelo entrenado se aprenden en muchas dimensiones; el coseno compara direcciones, no longitudes.",
      summary: (word, neighbour, value) => `«${word}» es la palabra más cercana a «${neighbour}» con coseno ${value}.`,
      axisX: "dimensión 1",
      axisY: "dimensión 2",
      xLabel: "x₁",
      yLabel: "x₂",
    };

const DATA = EN
  ? [
      { word: "cat", vector: [0.9, 0.3] },
      { word: "dog", vector: [0.85, 0.4] },
      { word: "car", vector: [0.2, 0.9] },
      { word: "bus", vector: [0.28, 0.84] },
      { word: "pizza", vector: [0.72, 0.18] },
      { word: "paella", vector: [0.68, 0.24] },
    ]
  : [
      { word: "gato", vector: [0.9, 0.3] },
      { word: "perro", vector: [0.85, 0.4] },
      { word: "coche", vector: [0.2, 0.9] },
      { word: "autobús", vector: [0.28, 0.84] },
      { word: "pizza", vector: [0.72, 0.18] },
      { word: "paella", vector: [0.68, 0.24] },
    ];

const ORIGINAL = DATA.map((item) => ({ word: item.word, vector: [...item.vector] }));

function cosine(a, b) {
  const dot = a[0] * b[0] + a[1] * b[1];
  const normA = Math.hypot(a[0], a[1]);
  const normB = Math.hypot(b[0], b[1]);
  if (!normA || !normB) return 0;
  return dot / (normA * normB);
}

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

export default {
  id: "embedding",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let vectors = ORIGINAL.map((item) => ({ word: item.word, vector: [...item.vector] }));
    let selected = 0;

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output", "aria-live": "polite" });
    const wordRow = h("div", { class: "token-row" });
    const map = h("div", {
      role: "group",
      "aria-label": S.mapTitle,
      style:
        "position:relative;height:230px;border:1px solid var(--border);border-radius:10px;" +
        "background:linear-gradient(var(--border) 1px, transparent 1px) 0 0/25% 25%," +
        "linear-gradient(90deg, var(--border) 1px, transparent 1px) 0 0/25% 25%," +
        "var(--surface);overflow:hidden",
    });
    const axisX = h("span", {
      class: "small muted",
      style: "position:absolute;right:6px;bottom:4px",
    }, S.axisX);
    const axisY = h("span", {
      class: "small muted",
      style: "position:absolute;left:6px;top:4px",
    }, S.axisY);
    const ranking = h("div", { class: "bar-list", "aria-live": "polite" });
    const summary = h("p", { class: "small mt-2" });
    const stats = h("div", { class: "lab-stat-row mt-3" });
    const xOutput = h("output", { for: "emb-x" });
    const yOutput = h("output", { for: "emb-y" });

    const xRange = h("input", {
      id: "emb-x",
      type: "range",
      min: "-1",
      max: "1",
      step: "0.05",
      value: String(vectors[selected].vector[0]),
      oninput: (event) => {
        vectors[selected].vector[0] = Number(event.currentTarget.value);
        render(false);
      },
    });

    const yRange = h("input", {
      id: "emb-y",
      type: "range",
      min: "-1",
      max: "1",
      step: "0.05",
      value: String(vectors[selected].vector[1]),
      oninput: (event) => {
        vectors[selected].vector[1] = Number(event.currentTarget.value);
        render(false);
      },
    });

    const resetButton = h(
      "button",
      {
        type: "button",
        class: "btn btn-secondary btn-sm",
        onclick: () => {
          vectors = ORIGINAL.map((item) => ({ word: item.word, vector: [...item.vector] }));
          selected = 0;
          syncControls();
          render(true);
        },
      },
      S.reset
    );

    controls.append(
      h("p", { class: "small" }, S.intro),
      h(
        "div",
        { class: "field" },
        h("label", {}, S.selectLabel),
        wordRow
      ),
      h(
        "div",
        { class: "field" },
        h("label", {}, S.coordsLabel),
        h("div", { class: "row" }, h("label", { for: "emb-x", class: "small" }, S.xLabel), xRange, xOutput),
        h("div", { class: "row" }, h("label", { for: "emb-y", class: "small" }, S.yLabel), yRange, yOutput)
      ),
      h("div", { class: "row" }, resetButton),
      h("p", { class: "small muted" }, S.note)
    );

    output.append(
      h("h4", {}, S.mapTitle),
      map,
      h("div", { class: "mt-3" }, h("h4", {}, S.rankingTitle), ranking),
      summary,
      stats
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function syncControls() {
      const [x, y] = vectors[selected].vector;
      xRange.value = String(x);
      yRange.value = String(y);
      xOutput.textContent = x.toFixed(2);
      yOutput.textContent = y.toFixed(2);
    }

    function renderMap() {
      map.replaceChildren(axisX, axisY);
      vectors.forEach((item, index) => {
        const [x, y] = item.vector;
        const left = `${((x + 1) / 2) * 100}%`;
        const bottom = `${((y + 1) / 2) * 100}%`;
        const active = index === selected;
        map.append(
          h(
            "button",
            {
              type: "button",
              class: `token-chip${active ? " is-selected" : ""}`,
              "aria-pressed": active ? "true" : "false",
              title: `${item.word} (${x.toFixed(2)}, ${y.toFixed(2)})`,
              style:
                `position:absolute;left:${left};bottom:${bottom};transform:translate(-50%,50%);` +
                `font-size:10.5px;padding:4px 7px;z-index:${active ? 2 : 1}`,
              onclick: () => {
                selected = index;
                syncControls();
                render(true);
              },
            },
            item.word
          )
        );
      });
    }

    function renderRanking() {
      const base = vectors[selected];
      const ranked = vectors
        .map((item, index) => ({ ...item, index, score: index === selected ? null : cosine(base.vector, item.vector) }))
        .filter((item) => item.score !== null)
        .sort((a, b) => b.score - a.score);

      ranking.replaceChildren();
      ranked.forEach((item) => {
        const width = Math.max(0, Math.min(1, item.score)) * 100;
        ranking.append(
          h(
            "div",
            { class: "bar-row" },
            h("span", { class: "bar-label" }, item.word),
            h(
              "div",
              { class: "bar-track" },
              h("span", { style: `width:${width}%` })
            ),
            h("span", { class: "bar-value" }, item.score.toFixed(3))
          )
        );
      });

      const top = ranked[0];
      const norm = Math.hypot(base.vector[0], base.vector[1]);
      stats.replaceChildren(
        stat(S.stats[0], top ? top.word : "—"),
        stat(S.stats[1], top ? top.score.toFixed(3) : "—"),
        stat(S.stats[2], norm.toFixed(3))
      );
      summary.textContent = top
        ? S.summary(base.word, top.word, top.score.toFixed(3))
        : "";
    }

    function render(refreshControls) {
      wordRow.replaceChildren();
      vectors.forEach((item, index) => {
        const active = index === selected;
        wordRow.append(
          h(
            "button",
            {
              type: "button",
              class: `token-chip${active ? " is-selected" : ""}`,
              "aria-pressed": active ? "true" : "false",
              onclick: () => {
                selected = index;
                syncControls();
                render(true);
              },
            },
            item.word
          )
        );
      });
      if (refreshControls) syncControls();
      else {
        xOutput.textContent = Number(xRange.value).toFixed(2);
        yOutput.textContent = Number(yRange.value).toFixed(2);
      }
      renderMap();
      renderRanking();
    }

    render(true);
    return () => {};
  },
};
