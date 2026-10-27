/* Laboratorio · Plantilla de chat
   Convierte una instrucción y una respuesta en ChatML o Alpaca, resalta los
   tokens especiales y muestra qué posiciones entran en la pérdida. */

import { h } from "./common.js";

const LANG = (document.documentElement.lang || "es").toLowerCase().startsWith("en")
  ? "en"
  : "es";

const STRINGS = {
  es: {
    template: "Plantilla",
    chatml: "ChatML (tokens de turno)",
    alpaca: "Alpaca (cabeceras)",
    instruction: "Instrucción (rol user)",
    response: "Respuesta (rol assistant)",
    instructionHint: "Editable. Los saltos de línea se conservan en el texto final.",
    responseHint: "Esta zona es la que normalmente recibe la pérdida.",
    reset: "Restaurar ejemplo",
    finalText: "Texto final",
    legend: "Leyenda",
    special: "token especial",
    withLoss: "con pérdida",
    withoutLoss: "sin pérdida",
    tokens: "Tokens ≈",
    trainable: "Posiciones con pérdida",
    masked: "Posiciones enmascaradas",
    note: (
      "La máscara es una aproximación por palabras: el tokenizador real puede dividir "
      + "distinto. En Alpaca el EOS se añade al tokenizar; en ChatML el cierre del turno "
      + "forma parte del texto."
    ),
    rule: (
      "El mismo formato debe usarse al entrenar y al inferir. Si cambias los marcadores, "
      + "cambias la distribución que el modelo aprendió."
    ),
    system: "Eres un asistente breve y preciso.",
    preamble: "A continuación se describe una tarea. Escribe una respuesta que la complete.",
    instructionHeader: "### Instrucción:",
    responseHeader: "### Respuesta:",
    specialHint: "Token especial: delimita un turno o el final de la respuesta.",
    lossOn: "Esta posición contribuye a la pérdida.",
    lossOff: "Esta posición es contexto y no contribuye a la pérdida.",
    status: (total, active) => (
      `${total} tokens aproximados; ${active} posiciones con pérdida. `
      + "El texto se actualiza al editar."
    ),
  },
  en: {
    template: "Template",
    chatml: "ChatML (turn tokens)",
    alpaca: "Alpaca (headings)",
    instruction: "Instruction (user role)",
    response: "Response (assistant role)",
    instructionHint: "Editable. Line breaks are preserved in the final text.",
    responseHint: "This is the area that normally receives the loss.",
    reset: "Restore example",
    finalText: "Final text",
    legend: "Legend",
    special: "special token",
    withLoss: "with loss",
    withoutLoss: "without loss",
    tokens: "Tokens ≈",
    trainable: "Positions with loss",
    masked: "Masked positions",
    note: (
      "The mask is a word-level approximation: a real tokenizer may split differently. "
      + "In Alpaca the EOS is added during tokenization; in ChatML the turn closing is part "
      + "of the text."
    ),
    rule: (
      "Use the same format for training and inference. Changing the markers changes the "
      + "distribution the model learned."
    ),
    system: "You are a concise, precise assistant.",
    preamble: "Below is an instruction that describes a task. Write a response that completes it.",
    instructionHeader: "### Instruction:",
    responseHeader: "### Response:",
    specialHint: "Special token: it delimits a turn or the end of the response.",
    lossOn: "This position contributes to the loss.",
    lossOff: "This position is context and does not contribute to the loss.",
    status: (total, active) => (
      `${total} approximate tokens; ${active} positions with loss. `
      + "The text updates as you edit."
    ),
  },
};

const T = STRINGS[LANG];

const DEFAULTS = {
  es: {
    instruction: "Convierte a pasiva: «El chef cocina la cena cada día».",
    response: "La cena es cocinada cada día por el chef.",
  },
  en: {
    instruction: "Rewrite in the passive voice: \"The chef cooks dinner every day.\"",
    response: "Dinner is cooked every day by the chef.",
  },
};

const DEFAULT = DEFAULTS[LANG];

const STYLE_SPECIAL = (
  "background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd;border-radius:4px;"
  + "padding:0 3px;font-weight:700;"
);
const STYLE_LOSS = (
  "background:#dcfce7;color:#065f46;border-bottom:2px solid #10b981;"
);
const STYLE_MASKED = "color:#64748b;";

function statCard(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value)
  );
}

function approxTokens(segments) {
  return segments.reduce((total, segment) => {
    const text = segment.text.trim();
    if (!text) return total;
    return total + text.split(/\s+/).length;
  }, 0);
}

function legendChip(style, label) {
  return h(
    "span",
    {
      style: (
        "display:inline-flex;align-items:center;gap:6px;margin-right:14px;"
        + "font-size:13px;color:#475569;"
      ),
    },
    h("span", {
      "aria-hidden": "true",
      style: `display:inline-block;width:14px;height:14px;border-radius:3px;${style}`,
    }),
    label
  );
}

export default {
  id: "chat-template",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let template = "chatml";
    let instruction = DEFAULT.instruction;
    let response = DEFAULT.response;

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output" });
    const preview = h("pre", {
      tabindex: "0",
      "aria-label": T.finalText,
      style: (
        "margin:0;padding:14px;background:#f8fafc;border:1px solid #e2e8f0;"
        + "border-radius:10px;white-space:pre-wrap;word-break:break-word;"
        + "font-family:ui-monospace,SFMono-Regular,Consolas,monospace;"
        + "font-size:13px;line-height:1.7;color:#0f172a;max-height:340px;"
        + "overflow:auto;"
      ),
    });
    const stats = h("div", { class: "lab-stat-row mt-3" });
    const status = h("p", {
      class: "small muted mt-2",
      "aria-live": "polite",
    });

    const templateSelect = h(
      "select",
      {
        id: "chat-template-select",
        onchange: (event) => {
          template = event.currentTarget.value;
          render();
        },
      },
      h("option", { value: "chatml", selected: template === "chatml" }, T.chatml),
      h("option", { value: "alpaca", selected: template === "alpaca" }, T.alpaca)
    );

    const instructionEl = h("textarea", {
      id: "chat-template-instruction",
      rows: "4",
      spellcheck: "true",
      "aria-describedby": "chat-template-instruction-hint",
    });
    instructionEl.value = instruction;
    instructionEl.addEventListener("input", () => {
      instruction = instructionEl.value;
      render();
    });

    const responseEl = h("textarea", {
      id: "chat-template-response",
      rows: "4",
      spellcheck: "true",
      "aria-describedby": "chat-template-response-hint",
    });
    responseEl.value = response;
    responseEl.addEventListener("input", () => {
      response = responseEl.value;
      render();
    });

    const resetButton = h(
      "button",
      {
        class: "btn btn-secondary btn-sm",
        type: "button",
        onclick: () => {
          template = "chatml";
          instruction = DEFAULT.instruction;
          response = DEFAULT.response;
          templateSelect.value = template;
          instructionEl.value = instruction;
          responseEl.value = response;
          render();
        },
      },
      T.reset
    );

    controls.append(
      h(
        "div",
        { class: "field" },
        h("label", { for: "chat-template-select" }, T.template),
        templateSelect
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "chat-template-instruction" }, T.instruction),
        instructionEl,
        h("small", { id: "chat-template-instruction-hint" }, T.instructionHint)
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "chat-template-response" }, T.response),
        responseEl,
        h("small", { id: "chat-template-response-hint" }, T.responseHint)
      ),
      h("div", { class: "row" }, resetButton),
      h("p", { class: "small muted" }, T.rule)
    );

    output.append(
      h("h4", { style: "margin:0 0 8px" }, T.finalText),
      preview,
      h("div", { class: "row small muted mt-2", style: "gap:8px 0;flex-wrap:wrap" },
        h("span", { style: "font-weight:700;color:#334155;margin-right:12px" }, T.legend),
        legendChip(STYLE_SPECIAL, T.special),
        legendChip(STYLE_LOSS, T.withLoss),
        legendChip("background:#e2e8f0;", T.withoutLoss)
      ),
      stats,
      status,
      h("p", { class: "small muted mt-2" }, T.note)
    );

    body.replaceChildren(
      h(
        "div",
        {
          class: "lab-grid",
          style: "grid-template-columns:repeat(auto-fit,minmax(260px,1fr));align-items:start;",
        },
        controls,
        output
      )
    );

    function chatmlSegments() {
      return [
        { text: "<|im_start|>", special: true, trainable: false },
        { text: "system\n", special: false, trainable: false },
        { text: T.system, special: false, trainable: false },
        { text: "<|im_end|>", special: true, trainable: false },
        { text: "\n<|im_start|>", special: true, trainable: false },
        { text: "user\n", special: false, trainable: false },
        { text: instruction, special: false, trainable: false },
        { text: "<|im_end|>", special: true, trainable: false },
        { text: "\n<|im_start|>", special: true, trainable: false },
        { text: "assistant\n", special: false, trainable: false },
        { text: response, special: false, trainable: true },
        { text: "<|im_end|>", special: true, trainable: true },
      ];
    }

    function alpacaSegments() {
      return [
        {
          text: `${T.preamble}\n\n${T.instructionHeader}\n`,
          special: false,
          trainable: false,
        },
        { text: instruction, special: false, trainable: false },
        {
          text: `\n\n${T.responseHeader}\n`,
          special: false,
          trainable: false,
        },
        { text: response, special: false, trainable: true },
      ];
    }

    function segmentNode(segment) {
      if (segment.special) {
        return h(
          "span",
          {
            style: segment.trainable
              ? `${STYLE_SPECIAL}border-bottom:2px solid #10b981;`
              : STYLE_SPECIAL,
            title: segment.trainable
              ? `${T.specialHint} ${T.lossOn}`
              : T.specialHint,
          },
          segment.text
        );
      }
      if (segment.trainable) {
        return h(
          "span",
          { style: STYLE_LOSS, title: T.lossOn },
          segment.text
        );
      }
      return h(
        "span",
        { style: STYLE_MASKED, title: T.lossOff },
        segment.text
      );
    }

    function render() {
      const segments = template === "alpaca" ? alpacaSegments() : chatmlSegments();
      preview.replaceChildren(...segments.map(segmentNode));

      const total = approxTokens(segments);
      const active = approxTokens(segments.filter((segment) => segment.trainable));
      const masked = Math.max(total - active, 0);

      stats.replaceChildren(
        statCard(T.template, template === "alpaca" ? "Alpaca" : "ChatML"),
        statCard(T.tokens, String(total)),
        statCard(T.trainable, String(active)),
        statCard(T.masked, String(masked))
      );
      status.textContent = T.status(total, active);
    }

    render();
    return () => {};
  },
};
