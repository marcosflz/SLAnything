/* Laboratorio · Constructor de prompts
   Zero-shot, one-shot y few-shot con instrucción, ejemplos y consulta. */

import { h, copyText, tokenize } from "./common.js";
import { lang, t } from "../i18n.js";

const TASKS_ES = {
  translate: {
    label: "Traducir al inglés",
    instruction: "Traduce el texto al inglés.",
    input: "¿Dónde está la biblioteca?",
    examples: [
      ["Buenos días.", "Good morning."],
      ["¿Dónde está la estación?", "Where is the station?"],
      ["Me gustaría un café.", "I would like a coffee."],
    ],
  },
  sentiment: {
    label: "Analizar sentimiento",
    instruction: "Clasifica el sentimiento como positivo, negativo o neutro.",
    input: "El envío fue rápido, pero la caja llegó rota.",
    examples: [
      ["Me encanta este producto.", "positivo"],
      ["No funciona y llegó tarde.", "negativo"],
      ["Es un producto normal.", "neutro"],
    ],
  },
  summary: {
    label: "Resumir",
    instruction: "Resume el texto en una sola frase.",
    input: "El gobierno presentó un plan para reducir emisiones y crear empleo verde.",
    examples: [
      [
        "La empresa anunció pérdidas récord y el consejero delegado dimitió.",
        "La empresa atraviesa una crisis tras las pérdidas y la dimisión.",
      ],
      [
        "El equipo ganó el partido en el último minuto y celebró el título.",
        "El equipo se llevó el título con un gol en el último minuto.",
      ],
      [
        "La ciudad invertirá en transporte público durante los próximos cinco años.",
        "La ciudad ampliará el transporte público durante cinco años.",
      ],
    ],
  },
};

const TASKS_EN = {
  translate: {
    label: "Translate into Spanish",
    instruction: "Translate the text into Spanish.",
    input: "Where is the library?",
    examples: [
      ["Good morning.", "Buenos días."],
      ["Where is the station?", "¿Dónde está la estación?"],
      ["I would like a coffee.", "Me gustaría un café."],
    ],
  },
  sentiment: {
    label: "Analyze sentiment",
    instruction: "Classify the sentiment as positive, negative, or neutral.",
    input: "Shipping was fast, but the box arrived broken.",
    examples: [
      ["I love this product.", "positive"],
      ["It does not work and arrived late.", "negative"],
      ["It is a normal product.", "neutral"],
    ],
  },
  summary: {
    label: "Summarize",
    instruction: "Summarize the text in one sentence.",
    input: "The government presented a plan to reduce emissions and create green jobs.",
    examples: [
      [
        "The company announced record losses and the CEO resigned.",
        "The company is in crisis after the losses and the resignation.",
      ],
      [
        "The team won the match in the last minute and celebrated the title.",
        "The team took the title with a last-minute goal.",
      ],
      [
        "The city will invest in public transport over the next five years.",
        "The city will expand public transport for five years.",
      ],
    ],
  },
};

const TASKS = lang === "en" ? TASKS_EN : TASKS_ES;

const MODES = [
  { id: "zero", label: "Zero-shot", count: 0 },
  { id: "one", label: "One-shot", count: 1 },
  { id: "few", label: "Few-shot", count: 3 },
];

function statCard(label, value, compact = false) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", { style: compact ? "font-size:13px;white-space:nowrap" : null }, value)
  );
}

export default {
  id: "prompt",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    let taskKey = "translate";
    let modeId = "zero";
    let currentPrompt = "";

    const inputs = Object.fromEntries(
      Object.entries(TASKS).map(([key, task]) => [key, task.input])
    );

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output" });
    const modeGroup = h("div", {
      class: "segmented",
      role: "group",
      "aria-label": t("Modalidad del prompt"),
    });
    const promptBox = h("div", { class: "prompt-box mt-2" });
    const stats = h("div", { class: "lab-stat-row mt-3" });

    const taskSelect = h(
      "select",
      {
        id: "prompt-task",
        onchange: (event) => {
          taskKey = event.currentTarget.value;
          inputEl.value = inputs[taskKey];
          render();
        },
      },
      Object.entries(TASKS).map(([key, task]) =>
        h("option", { value: key, selected: key === taskKey }, task.label)
      )
    );

    const inputEl = h("textarea", {
      id: "prompt-input",
      rows: "3",
      spellcheck: "true",
      placeholder: t("Escribe aquí la entrada que quieres procesar…"),
    });
    inputEl.value = inputs[taskKey];
    inputEl.addEventListener("input", () => {
      inputs[taskKey] = inputEl.value;
      render();
    });

    const resetButton = h(
      "button",
      { class: "btn btn-secondary btn-sm", type: "button" },
      t("Restaurar ejemplo")
    );
    resetButton.addEventListener("click", () => {
      inputs[taskKey] = TASKS[taskKey].input;
      inputEl.value = inputs[taskKey];
      render();
    });

    const copyButton = h(
      "button",
      { class: "btn btn-primary btn-sm", type: "button" },
      t("Copiar prompt")
    );
    let copyTimer;
    copyButton.addEventListener("click", async () => {
      const copied = await copyText(currentPrompt);
      clearTimeout(copyTimer);
      copyButton.textContent = copied ? t("Copiado") : t("No disponible");
      copyTimer = setTimeout(() => {
        copyButton.textContent = t("Copiar prompt");
      }, 1500);
    });

    controls.append(
      h(
        "div",
        { class: "field" },
        h("label", { for: "prompt-task" }, t("Tarea")),
        taskSelect
      ),
      h(
        "div",
        { class: "field" },
        h("label", {}, t("Modalidad")),
        modeGroup,
        h("small", {}, t("Zero-shot: sin ejemplos · One-shot: 1 ejemplo · Few-shot: 3 ejemplos."))
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "prompt-input" }, t("Texto de entrada")),
        inputEl,
        h("small", {}, t("Editable: el prompt y el contador se actualizan al instante."))
      ),
      h("div", { class: "row" }, resetButton),
      h(
        "p",
        { class: "small muted" },
        t("Los ejemplos no cambian los pesos; solo condicionan la generación.")
      )
    );

    output.append(
      h(
        "div",
        {
          class: "row",
          style: "justify-content:space-between;align-items:center;gap:12px",
        },
        h("h4", { style: "margin:0" }, t("Prompt completo")),
        copyButton
      ),
      promptBox,
      stats,
      h(
        "p",
        { class: "small muted mt-2" },
        t("El contador es aproximado: separa por espacios y signos. Un tokenizador real puede dividir distinto.")
      )
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function renderModeButtons() {
      modeGroup.replaceChildren();
      MODES.forEach((mode) => {
        modeGroup.append(
          h(
            "button",
            {
              type: "button",
              class: mode.id === modeId ? "is-active" : "",
              "aria-pressed": mode.id === modeId ? "true" : "false",
              onclick: () => {
                modeId = mode.id;
                render();
              },
            },
            mode.label
          )
        );
      });
    }

    function renderPrompt() {
      const task = TASKS[taskKey];
      const mode = MODES.find((item) => item.id === modeId) || MODES[0];
      const examples = task.examples.slice(0, mode.count);
      const input = inputs[taskKey];
      const nodes = [];

      nodes.push(h("span", { class: "prompt-label" }, `${t("Instrucción")}: `));
      nodes.push(document.createTextNode(`${task.instruction}\n`));

      examples.forEach(([source, target], index) => {
        nodes.push(h("span", { class: "prompt-label" }, `\n${t("Ejemplo")} ${index + 1}:\n`));
        nodes.push(
          h(
            "span",
            { class: "prompt-example" },
            `${t("Entrada")}: ${source}\n${t("Salida")}: ${target}\n`
          )
        );
      });

      nodes.push(h("span", { class: "prompt-label" }, `\n${t("Entrada")}: `));
      if (input) nodes.push(h("span", { class: "prompt-query" }, input));
      nodes.push(h("span", { class: "prompt-label" }, `\n${t("Salida")}:`));

      promptBox.replaceChildren(...nodes);
      currentPrompt = promptBox.textContent;

      const tokenCount = tokenize(currentPrompt).length;
      stats.replaceChildren(
        statCard(t("Modo"), mode.label, true),
        statCard(t("Ejemplos"), String(examples.length)),
        statCard(t("Tokens ≈"), String(tokenCount))
      );
    }

    function render() {
      renderModeButtons();
      renderPrompt();
    }

    render();
    return () => {};
  },
};
