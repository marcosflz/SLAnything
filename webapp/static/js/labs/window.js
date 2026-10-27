/* Laboratorio · Ventana deslizante
   Recorre una secuencia con contexto y stride ajustables. */

import { h } from "./common.js";

const EN = document.documentElement.lang.startsWith("en");

const S = EN
  ? {
      intro: "Move the sliders and watch how the same token stream is cut into training windows. Click a window to inspect its input and target.",
      contextLabel: "Context length",
      strideLabel: "Stride",
      stripLabel: "Token stream",
      windowsTitle: "Windows",
      inputLabel: "Input x",
      targetLabel: "Target y",
      formula: "windows = floor((N − L − 1) / S) + 1",
      stats: ["Windows", "Overlap", "Predictions"],
      select: "Select this window",
      summary: (start, end) => `Window from position ${start} to ${end}. The target is the same fragment shifted one token.`,
      empty: "The context is longer than the sequence.",
      note: "Every window produces one prediction per position. Overlap is shared tokens divided by context.",
    }
  : {
      intro: "Mueve los controles y observa cómo la misma secuencia se corta en ventanas de entrenamiento. Haz clic en una ventana para ver su entrada y su objetivo.",
      contextLabel: "Longitud del contexto",
      strideLabel: "Stride",
      stripLabel: "Secuencia de tokens",
      windowsTitle: "Ventanas",
      inputLabel: "Entrada x",
      targetLabel: "Objetivo y",
      formula: "ventanas = floor((N − L − 1) / S) + 1",
      stats: ["Ventanas", "Solapamiento", "Predicciones"],
      select: "Seleccionar esta ventana",
      summary: (start, end) => `Ventana desde la posición ${start} hasta la ${end}. El objetivo es el mismo fragmento desplazado un token.`,
      empty: "El contexto es más largo que la secuencia.",
      note: "Cada ventana produce una predicción por posición. El solapamiento es el cociente entre tokens compartidos y contexto.",
    };

const TOKENS = EN
  ? ["The", "cat", "sleeps", "on", "the", "sofa", "because", "it", "is", "sleepy", "and", "dreams"]
  : ["El", "gato", "duerme", "sobre", "el", "sofá", "porque", "tiene", "sueño", "y", "sueña", "."];

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, String(value))
  );
}

export default {
  id: "window",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let context = Math.min(5, TOKENS.length);
    let stride = 2;
    let selected = 0;

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output", "aria-live": "polite" });
    const strip = h("div", { class: "token-row" });
    const windowList = h("div", { class: "token-row" });
    const inputRow = h("div", { class: "token-row" });
    const targetRow = h("div", { class: "token-row" });
    const summary = h("p", { class: "small mt-2" });
    const formula = h("p", { class: "small muted" });
    const stats = h("div", { class: "lab-stat-row mt-3" });
    const contextOutput = h("output", { for: "win-context" });
    const strideOutput = h("output", { for: "win-stride" });

    const contextRange = h("input", {
      id: "win-context",
      type: "range",
      min: "3",
      max: String(TOKENS.length - 1),
      step: "1",
      value: String(context),
      oninput: (event) => {
        context = Number(event.currentTarget.value);
        selected = 0;
        render();
      },
    });

    const strideRange = h("input", {
      id: "win-stride",
      type: "range",
      min: "1",
      max: "5",
      step: "1",
      value: String(stride),
      oninput: (event) => {
        stride = Number(event.currentTarget.value);
        selected = 0;
        render();
      },
    });

    controls.append(
      h("p", { class: "small" }, S.intro),
      h(
        "div",
        { class: "field" },
        h("label", { for: "win-context" }, S.contextLabel),
        contextRange,
        contextOutput
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "win-stride" }, S.strideLabel),
        strideRange,
        strideOutput
      ),
      h("p", { class: "small muted" }, S.note)
    );

    output.append(
      h("h4", {}, S.stripLabel),
      strip,
      h("div", { class: "mt-3" }, h("h4", {}, S.windowsTitle), windowList),
      h("div", { class: "field mt-3" }, h("label", {}, S.inputLabel), inputRow),
      h("div", { class: "field mt-2" }, h("label", {}, S.targetLabel), targetRow),
      summary,
      stats,
      formula
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function startsFor() {
      const starts = [];
      if (TOKENS.length < context) return starts;
      for (let start = 0; start + context < TOKENS.length; start += stride) {
        starts.push(start);
      }
      return starts;
    }

    function renderStrip(starts) {
      strip.replaceChildren();
      const active = starts[selected];
      TOKENS.forEach((token, index) => {
        const classes = ["token-chip"];
        if (active !== undefined && index >= active && index < active + context) {
          classes.push("is-selected");
        }
        if (active !== undefined && index === active + context) classes.push("is-target");
        strip.append(
          h(
            "span",
            {
              class: classes.join(" "),
              title: `${index}: ${token}`,
            },
            `${index}·${token}`
          )
        );
      });
    }

    function render() {
      const starts = startsFor();
      if (selected >= starts.length) selected = 0;
      contextOutput.textContent = String(context);
      strideOutput.textContent = String(stride);
      renderStrip(starts);

      windowList.replaceChildren();
      if (!starts.length) {
        windowList.append(h("span", { class: "small muted" }, S.empty));
      } else {
        starts.forEach((start, index) => {
          const isActive = index === selected;
          windowList.append(
            h(
              "button",
              {
                type: "button",
                class: `token-chip${isActive ? " is-selected" : ""}`,
                "aria-pressed": isActive ? "true" : "false",
                "aria-label": `${S.select}: ${start}–${start + context - 1}`,
                onclick: () => {
                  selected = index;
                  render();
                },
              },
              `${start}–${start + context - 1}`
            )
          );
        });
      }

      const start = starts[selected];
      inputRow.replaceChildren();
      targetRow.replaceChildren();
      if (start === undefined) {
        summary.textContent = S.empty;
        stats.replaceChildren();
        return;
      }

      const input = TOKENS.slice(start, start + context);
      const target = TOKENS.slice(start + 1, start + context + 1);
      input.forEach((token) => inputRow.append(h("span", { class: "token-chip is-selected" }, token)));
      target.forEach((token, index) => {
        targetRow.append(
          h(
            "span",
            {
              class: `token-chip ${index === target.length - 1 ? "is-target" : "is-next"}`,
            },
            token
          )
        );
      });

      const overlap = context > stride ? context - stride : 0;
      const overlapPct = context > 0 ? Math.round((overlap / context) * 100) : 0;
      summary.textContent = S.summary(start, start + context - 1);
      stats.replaceChildren(
        stat(S.stats[0], starts.length),
        stat(S.stats[1], `${overlapPct} %`),
        stat(S.stats[2], starts.length * context)
      );
    }

    render();
    return () => {};
  },
};
