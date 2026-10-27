/* Laboratorio · Mapa de atención
   Matriz 9 × 9 de pesos ilustrativos, normalizada por filas. */

import { h, bar, num, clamp } from "./common.js";
import { lang, t } from "../i18n.js";

const TOKENS =
  lang === "en"
    ? ["The", "small", "cat", "stayed", "home", "because", "it", "was", "tired"]
    : ["El", "gato", "no", "cruzó", "la", "calle", "porque", "estaba", "cansado"];

/* Puntuaciones hechas a mano para que las conexiones lingüísticas se vean:
   gato ↔ cansado, la ↔ calle, no ↔ cruzó, porque ↔ estaba/cansado. */
const RAW = [
  [9, 7, 1, 1, 1, 2, 1, 1, 1],
  [6, 8, 2, 3, 1, 2, 1, 4, 9],
  [2, 4, 9, 8, 1, 3, 1, 1, 1],
  [1, 8, 4, 6, 2, 6, 1, 2, 2],
  [1, 3, 1, 4, 8, 9, 1, 1, 1],
  [1, 3, 1, 5, 7, 8, 1, 2, 3],
  [1, 3, 2, 2, 1, 2, 6, 8, 8],
  [1, 8, 1, 2, 1, 2, 5, 6, 7],
  [1, 9, 1, 2, 1, 2, 4, 6, 6],
];

const WEIGHTS = RAW.map((row) => {
  const total = row.reduce((sum, value) => sum + value, 0);
  return row.map((value) => value / total);
});
const ROW_MAX = WEIGHTS.map((row) => Math.max(...row));

function statCard(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

export default {
  id: "attention",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let view = "matrix";
    let selected = 8;

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output" });
    const viewGroup = h("div", {
      class: "segmented",
      role: "group",
      "aria-label": t("Vista del mapa de atención"),
    });
    const picker = h("div", { class: "field" });
    const select = h("select", {
      id: "attention-token",
      onchange: (event) => {
        selected = Number(event.currentTarget.value);
        render();
      },
    });
    const title = h("h4", { "aria-live": "polite" });
    const content = h("div");
    const scaleNote = h("p", { class: "small muted mt-2" });
    const stats = h("div", { class: "lab-stat-row mt-3" });

    function selectWord(index) {
      selected = index;
      view = "single";
      render();
    }

    controls.append(
      h(
        "p",
        { class: "small" },
        t("Cada fila es la palabra que mira; cada columna, la palabra mirada. Haz clic en una fila para ver solo sus pesos.")
      ),
      h(
        "div",
        { class: "field" },
        h("label", {}, t("Vista")),
        viewGroup,
        h(
          "small",
          {},
          t("En la matriz completa puedes explorar las 81 conexiones; en una palabra, las barras.")
        )
      ),
      picker,
      h(
        "p",
        { class: "small muted" },
        t("Los pesos son ilustrativos: en un transformer real salen de comparar queries y keys (Q · K), se aprenden durante el entrenamiento y se normalizan con softmax.")
      )
    );

    picker.append(
      h("label", { for: "attention-token" }, t("Token que mira")),
      select,
      h("small", {}, t("Cambia de palabra sin volver a la matriz."))
    );

    output.append(title, content, scaleNote, stats);

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function renderViewButtons() {
      viewGroup.replaceChildren();
      [
        ["matrix", t("Ver matriz completa")],
        ["single", t("Solo una palabra")],
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

    function renderPicker() {
      picker.style.display = view === "single" ? "flex" : "none";
      select.replaceChildren();
      TOKENS.forEach((token, index) => {
        select.append(
          h(
            "option",
            { value: index, selected: index === selected },
            `${index + 1}. ${token}`
          )
        );
      });
    }

    function buildMatrix() {
      const grid = h("div", {
        class: "heatmap",
        style: `grid-template-columns:48px repeat(${TOKENS.length}, 22px);gap:1px`,
      });

      grid.append(
        h(
          "span",
          {
            class: "heatmap-label heatmap-corner",
            style: "font-size:9px;line-height:1.15;justify-self:end;text-align:right",
          },
          t("mira ↓")
        )
      );

      TOKENS.forEach((token) => {
        grid.append(
          h(
            "span",
            {
              class: "heatmap-label",
              style:
                "writing-mode:vertical-rl;transform:rotate(180deg);height:48px;font-size:9px",
            },
            token
          )
        );
      });

      WEIGHTS.forEach((row, rowIndex) => {
        const rowLabel = h(
          "button",
          {
            type: "button",
            class: "heatmap-label heatmap-row-label",
            title: t("Ver los pesos de «{token}»", { token: TOKENS[rowIndex] }),
            "aria-label": t("Ver a qué atiende «{token}»", { token: TOKENS[rowIndex] }),
            "aria-current": rowIndex === selected ? "true" : null,
            style:
              "border:0;background:transparent;padding:0 4px;font-family:inherit;" +
              "font-size:10px;cursor:pointer;",
            onclick: () => selectWord(rowIndex),
          },
          TOKENS[rowIndex]
        );
        if (rowIndex === selected) {
          rowLabel.style.color = "var(--brand)";
          rowLabel.style.fontWeight = "750";
        }
        grid.append(rowLabel);

        row.forEach((weight, columnIndex) => {
          const alpha = clamp(0.08 + 0.88 * (weight / ROW_MAX[rowIndex]), 0.08, 0.95);
          const cell = h(
            "button",
            {
              type: "button",
              tabindex: "-1",
              class: "heatmap-cell",
              title: `${TOKENS[rowIndex]} → ${TOKENS[columnIndex]}: ${num(weight * 100, 1)} %`,
              "aria-label": t("{source} atiende a {target} con {value} por ciento", {
                source: TOKENS[rowIndex],
                target: TOKENS[columnIndex],
                value: num(weight * 100, 1),
              }),
              style:
                `border:0;padding:0;width:22px;height:24px;font-size:9px;cursor:pointer;` +
                `background:rgba(37,99,235,${alpha.toFixed(3)});` +
                `color:${alpha > 0.45 ? "#fff" : "var(--text)"}`,
              onclick: () => selectWord(rowIndex),
            },
            num(weight * 100, 0)
          );
          grid.append(cell);
        });
      });

      return h("div", { class: "heatmap-wrap" }, grid);
    }

    function buildSingle() {
      const row = WEIGHTS[selected];
      const ordered = TOKENS.map((token, index) => ({
        token,
        index,
        weight: row[index],
      })).sort((a, b) => b.weight - a.weight);
      const top = ordered[0];
      const topOther = ordered.find((item) => item.index !== selected) || top;

      const tokenButtons = TOKENS.map((token, index) => {
        const classes = ["token-chip"];
        if (index === selected) classes.push("is-selected");
        else if (index === topOther.index) classes.push("is-target");
        return h(
          "button",
          {
            type: "button",
            class: classes.join(" "),
            "aria-pressed": index === selected ? "true" : "false",
            onclick: () => {
              selected = index;
              render();
            },
          },
          token
        );
      });

      const bars = ordered.map((item) =>
        bar(item.token, item.weight, top.weight, {
          format: (value) => `${num(value * 100, 1)} %`,
        })
      );

      const summary =
        top.index === selected
          ? t("La mayor parte de la atención de «{token}» se queda en sí misma ({own} %); fuera de sí, la conexión más fuerte es «{other}» ({otherValue} %).", {
              token: TOKENS[selected],
              own: num(top.weight * 100, 1),
              other: topOther.token,
              otherValue: num(topOther.weight * 100, 1),
            })
          : t("«{token}» dedica más atención a «{top}» ({value} %).", {
              token: TOKENS[selected],
              top: top.token,
              value: num(top.weight * 100, 1),
            });

      return h(
        "div",
        {},
        h("div", { class: "token-row" }, tokenButtons),
        h("div", { class: "bar-list" }, bars),
        h("p", { class: "small mt-2" }, summary)
      );
    }

    function render() {
      renderViewButtons();
      renderPicker();
      title.style.textTransform = view === "matrix" ? "" : "none";
      title.textContent =
        view === "matrix"
          ? t("Matriz de atención · {n} × {n}", { n: TOKENS.length })
          : t("¿A qué atiende «{token}»?", { token: TOKENS[selected] });
      scaleNote.textContent =
        view === "matrix"
          ? t("Cada fila suma 100 %. El color se escala al máximo de su fila y el número es el peso.")
          : t("Las barras suman 100 %. En un transformer real, estos pesos se aprenden y salen de comparar queries y keys.");
      content.replaceChildren(view === "matrix" ? buildMatrix() : buildSingle());
      const maxRow = Math.max(...WEIGHTS[selected]);
      stats.replaceChildren(
        statCard(t("Tokens"), String(TOKENS.length)),
        statCard(t("Pares"), String(TOKENS.length * TOKENS.length)),
        statCard(t("Máx. fila"), `${num(maxRow * 100, 0)} %`)
      );
    }

    render();
    return () => {};
  },
};
