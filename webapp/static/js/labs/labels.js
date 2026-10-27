/* Laboratorio · Fábrica de etiquetas
   Convierte una frase fija en pares entrada → objetivo para el pretraining. */

import { h } from "./common.js";
import { lang, t } from "../i18n.js";

const SENTENCE =
  lang === "en"
    ? ["The", "cat", "sleeps", "on", "the", "sofa", "because", "it", "is", "sleepy", "."]
    : ["El", "gato", "duerme", "sobre", "el", "sofá", "porque", "tiene", "sueño", "."];
const DEFAULT_POSITION = 5;
const LAST_TARGET = SENTENCE.length - 1;

function statCard(label, value, unit = "") {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value, unit ? h("small", {}, ` ${unit}`) : null)
  );
}

function shorten(tokens) {
  if (tokens.length <= 5) return tokens.join(" ");
  return `${tokens.slice(0, 3).join(" ")} … ${tokens.slice(-2).join(" ")}`;
}

export default {
  id: "labels",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let position = DEFAULT_POSITION;

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output" });
    const tokenRow = h("div", { class: "token-row", "aria-label": t("Frase tokenizada") });
    const inputRow = h("div", { class: "token-row" });
    const targetRow = h("div", { class: "token-row" });
    const pairPreview = h("p", { class: "output-text mt-3", "aria-live": "polite" });
    const tableBody = h("tbody");
    const stats = h("div", { class: "lab-stat-row" });
    const positionLabel = h("output", {});
    const inputCount = h("output", {});

    const nextButton = h(
      "button",
      { class: "btn btn-primary btn-sm", type: "button" },
      t("Siguiente posición")
    );
    const resetButton = h(
      "button",
      { class: "btn btn-secondary btn-sm", type: "button" },
      t("Reiniciar")
    );

    function selectPosition(index) {
      position = Math.min(Math.max(index, 1), LAST_TARGET);
      render();
    }

    nextButton.addEventListener("click", () => {
      position = position >= LAST_TARGET ? 1 : position + 1;
      render();
    });

    resetButton.addEventListener("click", () => {
      position = DEFAULT_POSITION;
      render();
    });

    const legend = h(
      "div",
      { class: "row small muted" },
      h("span", {}, t("Leyenda:")),
      h("span", { class: "token-chip is-selected" }, t("entrada")),
      h("span", { class: "token-chip is-target" }, t("objetivo")),
      h("span", { class: "token-chip is-next" }, t("próximo")),
      h("span", {}, t("Haz clic en un token para mover el corte."))
    );

    controls.append(
      h(
        "p",
        { class: "small" },
        t("El texto se corta en dos: todo lo anterior es la entrada y el token siguiente es el objetivo. En el entrenamiento real se usan todos los cortes a la vez.")
      ),
      h(
        "p",
        { class: "small muted" },
        t("La etiqueta no la escribe un humano: sale del propio texto. Eso es autosupervisión.")
      ),
      h(
        "div",
        { class: "field" },
        h("label", {}, t("Posición de corte"), positionLabel),
        tokenRow,
        h("small", {}, t("El primer token siempre forma parte de la entrada."))
      ),
      legend,
      h("div", { class: "row" }, nextButton, resetButton),
      stats
    );

    const tableWrap = h(
      "div",
      { class: "table-wrap", style: "margin:0" },
      h(
        "table",
        {},
        h(
          "caption",
          {},
          lang === "en"
            ? `The ${LAST_TARGET} pairs that come from the same sentence`
            : "Los nueve pares que salen de la misma frase"
        ),
        h(
          "thead",
          {},
          h(
            "tr",
            {},
            h("th", { scope: "col" }, t("Posición")),
            h("th", { scope: "col" }, t("Entrada (x)")),
            h("th", { scope: "col" }, t("Objetivo (y)"))
          )
        ),
        tableBody
      )
    );

    output.append(
      h("h4", {}, t("Par de entrenamiento")),
      h(
        "div",
        { class: "field" },
        h("label", {}, t("Entrada (x)"), inputCount),
        inputRow
      ),
      h(
        "div",
        { class: "field mt-3" },
        h("label", {}, t("Objetivo (y)")),
        targetRow
      ),
      pairPreview
    );

    body.replaceChildren(
      h(
        "div",
        { class: "stack" },
        h("div", { class: "lab-grid" }, controls, output),
        tableWrap
      )
    );

    function render() {
      positionLabel.textContent = `${position} / ${LAST_TARGET}`;
      inputCount.textContent = position === 1 ? t("{n} token", { n: position }) : t("{n} tokens", { n: position });

      tokenRow.replaceChildren();
      SENTENCE.forEach((token, index) => {
        const classes = ["token-chip"];
        if (index < position) classes.push("is-selected");
        if (index === position) classes.push("is-target");
        if (index === position + 1) classes.push("is-next");

        let chip;
        if (index === 0) {
          chip = h(
            "span",
            {
              class: classes.join(" "),
              title: t("El primer token siempre forma parte de la entrada."),
            },
            token
          );
        } else {
          chip = h(
            "button",
            {
              class: classes.join(" "),
              type: "button",
              title: index === 1
                ? t("Usar «{token}» como objetivo y cortar tras {n} token.", { token, n: index })
                : t("Usar «{token}» como objetivo y cortar tras {n} tokens.", { token, n: index }),
              "aria-label": t("Cortar antes de «{token}» y usarlo como objetivo.", { token }),
              onclick: () => selectPosition(index),
            },
            token
          );
        }
        if (index > position + 1) chip.style.opacity = "0.32";
        tokenRow.append(chip);
      });

      inputRow.replaceChildren();
      const inputTokens = SENTENCE.slice(0, position);
      inputTokens.forEach((token) => {
        inputRow.append(h("span", { class: "token-chip is-selected" }, token));
      });

      targetRow.replaceChildren(
        h("span", { class: "token-chip is-target" }, SENTENCE[position]),
        h("span", { class: "small muted" }, t("← el siguiente token de la frase"))
      );

      pairPreview.replaceChildren(
        h("strong", {}, `${t("Entrada")}: `),
        document.createTextNode(inputTokens.join(" ")),
        h("br"),
        h("strong", {}, `${t("Objetivo")}: `),
        h("span", { class: "generated" }, SENTENCE[position])
      );

      stats.replaceChildren(
        statCard(t("Posición"), `${position} / ${LAST_TARGET}`),
        statCard(t("Entrada"), String(position), position === 1 ? t("token") : t("tokens")),
        statCard(t("Objetivo"), SENTENCE[position])
      );

      tableBody.replaceChildren();
      for (let target = 1; target <= LAST_TARGET; target += 1) {
        const input = SENTENCE.slice(0, target);
        const active = target === position;
        const row = h(
          "tr",
          {
            class: active ? "is-selected" : "",
            tabindex: "0",
            "aria-label": t("Posición {n}: predecir «{token}».", { n: target, token: SENTENCE[target] }),
            onclick: () => selectPosition(target),
            onkeydown: (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                selectPosition(target);
              }
            },
          },
          h("td", {}, h("strong", {}, String(target))),
          h(
            "td",
            { class: "small", title: input.join(" ") },
            shorten(input)
          ),
          h("td", {}, h("span", { class: "token-chip is-target" }, SENTENCE[target]))
        );
        if (active) row.style.background = "var(--brand-soft)";
        row.style.cursor = "pointer";
        tableBody.append(row);
      }
    }

    render();
    return () => {};
  },
};
