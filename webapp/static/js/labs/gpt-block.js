/* Laboratorio · Bloque GPT interactivo
   Flujo Pre-LN con componentes activables y formas de tensor siempre visibles. */

import { h } from "./common.js";

const LANG = (document.documentElement.lang || "es")
  .toLowerCase()
  .startsWith("en")
  ? "en"
  : "es";

const TEXT = {
  es: {
    intro:
      "Activa o desactiva piezas del bloque y observa qué cambia. La forma del tensor se conserva; lo que cambia es el cálculo y el contenido.",
    batch: "Lote",
    tokens: "Tokens por secuencia",
    components: "Componentes",
    reset: "Restablecer",
    flowTitle: "Flujo del bloque Pre-LN",
    input: "Entrada x",
    inputNote: "Vectores que salen de los embeddings y la posición.",
    output: "Salida x′",
    outputNote: "Misma forma, contenido contextualizado.",
    ln1: "LayerNorm 1",
    ln1Note: "Centra y escala cada token antes de la atención.",
    attn: "Atención multi-head",
    attnNote: "12 cabezas mezclan información entre las posiciones de la secuencia.",
    res1: "Residual 1",
    res1Note: "Suma la entrada de la atención a su salida.",
    ln2: "LayerNorm 2",
    ln2Note: "Prepara la entrada de la red feed-forward.",
    ffn: "Feed-forward + GELU",
    ffnNote: "Expande a 3072, aplica GELU y vuelve a 768.",
    res2: "Residual 2",
    res2Note: "Suma la entrada de la FFN a su salida.",
    active: "activo",
    skipped: "omitido",
    shape: "Forma",
    internal: "interna",
    stats: {
      active: "Componentes activos",
      shape: "Forma de salida",
      params: "Parámetros del bloque",
      memory: "Pesos fp32",
    },
    statusAll:
      "Bloque completo: atención, FFN y residuales activos. La atención mezcla tokens, la FFN transforma cada posición y los residuales mantienen el camino directo. La forma no cambia.",
    statusSkipped: "Omitidos:",
    noAttention: "Sin atención no hay mezcla entre tokens.",
    noFFN: "Sin FFN se pierde la transformación no lineal por token.",
    noNorm: "Sin LayerNorm las activaciones pueden descontrolarse.",
    noResidual: "Sin residual se pierde el camino de identidad que ayuda al gradiente.",
    noSubLayer: "Sin subcapa, la suma residual equivale a la identidad.",
    disclaimer:
      "Desactivar una pieza no produce un GPT válido: es una herramienta para ver qué aporta cada componente. Las cifras de parámetros son las de GPT-2 small.",
    expandNote: "Expansión interna de la FFN:",
    sameShape: "[B, T, 768]",
    inputShape: "[B, T]",
    hiddenShape: "[B, T, 3072]",
    paramsNote:
      "La atención aporta 2,36 M, la FFN 4,72 M y cada LayerNorm 1 536 parámetros. Los residuales no tienen parámetros.",
  },
  en: {
    intro:
      "Turn block components on and off and watch what changes. The tensor shape is preserved; the computation and, above all, the content change.",
    batch: "Batch",
    tokens: "Tokens per sequence",
    components: "Components",
    reset: "Reset",
    flowTitle: "Pre-LN block flow",
    input: "Input x",
    inputNote: "Vectors coming from token and positional embeddings.",
    output: "Output x′",
    outputNote: "Same shape, contextualized content.",
    ln1: "LayerNorm 1",
    ln1Note: "Centers and scales each token before attention.",
    attn: "Multi-head attention",
    attnNote: "12 heads mix information across sequence positions.",
    res1: "Residual 1",
    res1Note: "Adds the attention input to its output.",
    ln2: "LayerNorm 2",
    ln2Note: "Prepares the feed-forward input.",
    ffn: "Feed-forward + GELU",
    ffnNote: "Expands to 3072, applies GELU, and returns to 768.",
    res2: "Residual 2",
    res2Note: "Adds the FFN input to its output.",
    active: "on",
    skipped: "skipped",
    shape: "Shape",
    internal: "internal",
    stats: {
      active: "Active components",
      shape: "Output shape",
      params: "Block parameters",
      memory: "fp32 weights",
    },
    statusAll:
      "Complete block: attention, FFN, and residuals are on. Attention mixes tokens, the FFN transforms each position, and residuals keep the direct path. The shape does not change.",
    statusSkipped: "Skipped:",
    noAttention: "Without attention there is no mixing across tokens.",
    noFFN: "Without the FFN, the per-token non-linear transformation is lost.",
    noNorm: "Without LayerNorm, activations can drift out of control.",
    noResidual: "Without residuals, the identity path that helps gradients is lost.",
    noSubLayer: "Without a sublayer, the residual sum is equivalent to the identity.",
    disclaimer:
      "Turning a piece off does not produce a valid GPT: it is a tool for seeing what each component contributes. Parameter figures are those of GPT-2 small.",
    expandNote: "Internal FFN expansion:",
    sameShape: "[B, T, 768]",
    inputShape: "[B, T]",
    hiddenShape: "[B, T, 3072]",
    paramsNote:
      "Attention contributes 2.36 M, the FFN 4.72 M, and each LayerNorm 1,536 parameters. Residuals have no parameters.",
  },
}[LANG];

const EMB = 768;
const ATTN_PARAMS = 4 * EMB * EMB + EMB; // 2,360,064
const FFN_PARAMS = 2 * EMB * (4 * EMB) + 4 * EMB + EMB; // 4,722,432
const LN_PARAMS = 2 * EMB; // 1,536

const COMPONENTS = [
  { id: "ln1", title: TEXT.ln1, note: TEXT.ln1Note, type: "norm", symbol: "LN" },
  { id: "attn", title: TEXT.attn, note: TEXT.attnNote, type: "attn", symbol: "A" },
  { id: "res1", title: TEXT.res1, note: TEXT.res1Note, type: "res", symbol: "+" },
  { id: "ln2", title: TEXT.ln2, note: TEXT.ln2Note, type: "norm", symbol: "LN" },
  { id: "ffn", title: TEXT.ffn, note: TEXT.ffnNote, type: "ffn", symbol: "F" },
  { id: "res2", title: TEXT.res2, note: TEXT.res2Note, type: "res", symbol: "+" },
];

const numberFmt = new Intl.NumberFormat(LANG === "es" ? "es-ES" : "en-US", {
  maximumFractionDigits: 2,
});

function fmtParams(value) {
  if (value >= 1e6) return `${numberFmt.format(value / 1e6)} M`;
  if (value >= 1e3) return `${numberFmt.format(value / 1e3)} mil`;
  return numberFmt.format(value);
}

function fmtMb(value) {
  return `${numberFmt.format(value)} MB`;
}

function chip(text, active = true) {
  return h(
    "span",
    {
      class: active ? "badge badge-violet" : "badge",
      style: "white-space:nowrap;font-variant-numeric:tabular-nums",
    },
    text
  );
}

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", { style: "font-size:15px" }, value)
  );
}

export default {
  id: "gpt-block",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    const state = {
      ln1: true,
      attn: true,
      res1: true,
      ln2: true,
      ffn: true,
      res2: true,
      batch: 2,
      tokens: 4,
    };

    const batchSelect = h(
      "select",
      {
        id: "gpt-block-batch",
        onchange: (event) => {
          state.batch = Number(event.currentTarget.value);
          render();
        },
      },
      [1, 2, 4].map((value) =>
        h("option", { value, selected: value === state.batch }, String(value))
      )
    );

    const tokenSelect = h(
      "select",
      {
        id: "gpt-block-tokens",
        onchange: (event) => {
          state.tokens = Number(event.currentTarget.value);
          render();
        },
      },
      [2, 4, 8].map((value) =>
        h("option", { value, selected: value === state.tokens }, String(value))
      )
    );

    const toggleGroup = h("div", {
      role: "group",
      "aria-label": TEXT.components,
      style: "display:grid;gap:6px",
    });

    const resetButton = h(
      "button",
      {
        type: "button",
        class: "btn btn-secondary btn-sm",
        onclick: () => {
          Object.assign(state, {
            ln1: true,
            attn: true,
            res1: true,
            ln2: true,
            ffn: true,
            res2: true,
            batch: 2,
            tokens: 4,
          });
          batchSelect.value = "2";
          tokenSelect.value = "4";
          render();
        },
      },
      TEXT.reset
    );

    const controls = h(
      "div",
      { class: "lab-controls" },
      h("p", { class: "small" }, TEXT.intro),
      h(
        "div",
        { class: "row", style: "align-items:flex-start;gap:12px" },
        h(
          "div",
          { class: "field", style: "flex:1 1 120px" },
          h("label", { for: "gpt-block-batch" }, TEXT.batch),
          batchSelect
        ),
        h(
          "div",
          { class: "field", style: "flex:1 1 150px" },
          h("label", { for: "gpt-block-tokens" }, TEXT.tokens),
          tokenSelect
        )
      ),
      h("div", { class: "field" }, h("label", {}, TEXT.components), toggleGroup),
      h("div", { class: "row" }, resetButton),
      h("p", { class: "small muted" }, TEXT.paramsNote)
    );

    const flowList = h("div", {
      role: "list",
      "aria-label": TEXT.flowTitle,
      style: "display:grid;gap:6px",
    });
    const status = h("p", {
      class: "small mt-2",
      "aria-live": "polite",
      style: "margin-bottom:0",
    });
    const stats = h("div", { class: "lab-stat-row mt-3" });
    const memory = h("p", { class: "small muted", style: "margin:8px 0 0" });
    const output = h(
      "div",
      { class: "lab-output" },
      h("h4", {}, TEXT.flowTitle),
      flowList,
      status,
      stats,
      memory,
      h("p", { class: "small muted", style: "margin:10px 0 0" }, TEXT.disclaimer)
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function isOn(id) {
      return Boolean(state[id]);
    }

    function params() {
      return (
        (isOn("ln1") ? LN_PARAMS : 0) +
        (isOn("attn") ? ATTN_PARAMS : 0) +
        (isOn("ln2") ? LN_PARAMS : 0) +
        (isOn("ffn") ? FFN_PARAMS : 0)
      );
    }

    function flowShape() {
      return `[${state.batch}, ${state.tokens}, ${EMB}]`;
    }

    function toggleButton(item) {
      const on = isOn(item.id);
      return h(
        "button",
        {
          type: "button",
          "data-component": item.id,
          "aria-pressed": on ? "true" : "false",
          "aria-label": `${item.title}: ${on ? TEXT.active : TEXT.skipped}`,
          onclick: () => {
            state[item.id] = !state[item.id];
            render();
            const next = toggleGroup.querySelector(
              `[data-component="${item.id}"]`
            );
            if (next) next.focus();
          },
          style: [
            "display:flex",
            "align-items:center",
            "justify-content:space-between",
            "gap:8px",
            "width:100%",
            "padding:8px 10px",
            "border-radius:8px",
            "font:inherit",
            "font-size:12px",
            "text-align:left",
            "cursor:pointer",
            `border:1px solid ${on ? "var(--violet, #7c3aed)" : "var(--border, #e2e8f0)"}`,
            `background:${on ? "var(--violet-soft, #ede9fe)" : "var(--surface, #fff)"}`,
            `color:${on ? "var(--violet, #6d28d9)" : "var(--text-soft, #475569)"}`,
            on ? "font-weight:700" : "font-weight:600",
          ].join(";"),
        },
        h("span", {}, `${on ? "✓" : "○"} ${item.title}`),
        h(
          "span",
          {
            class: "small",
            style: `color:${on ? "var(--violet, #6d28d9)" : "var(--muted, #64748b)"}`,
          },
          on ? TEXT.active : TEXT.skipped
        )
      );
    }

    function stageCard(item, index, shape) {
      const on = isOn(item.id);
      const isResidual = item.type === "res";
      let note = item.note;
      if (isResidual && on) {
        const sublayer = item.id === "res1" ? "attn" : "ffn";
        if (!isOn(sublayer)) note = `${item.note} ${TEXT.noSubLayer}`;
      }

      return h(
        "div",
        {
          role: "listitem",
          style: [
            "display:grid",
            "grid-template-columns:28px minmax(0,1fr)",
            "gap:10px",
            "align-items:start",
            "padding:9px 11px",
            "border-radius:9px",
            `border:1px solid ${on ? "var(--border, #e2e8f0)" : "var(--border, #e2e8f0)"}`,
            `background:${on ? "var(--surface, #fff)" : "var(--surface-2, #f8fafc)"}`,
            on ? "opacity:1" : "opacity:0.62",
          ].join(";"),
        },
        h(
          "span",
          {
            "aria-hidden": "true",
            style: [
              "display:grid",
              "place-items:center",
              "width:26px",
              "height:26px",
              "border-radius:50%",
              "font-size:11px",
              "font-weight:800",
              `background:${on ? "var(--violet-soft, #ede9fe)" : "var(--surface-3, #e2e8f0)"}`,
              `color:${on ? "var(--violet, #6d28d9)" : "var(--muted, #64748b)"}`,
            ].join(";"),
          },
          item.symbol
        ),
        h(
          "div",
          { style: "min-width:0" },
          h(
            "div",
            {
              class: "row",
              style: "justify-content:space-between;gap:8px;flex-wrap:wrap",
            },
            h(
              "span",
              {},
              h(
                "strong",
                { style: "font-size:12.5px" },
                `${index}. ${item.title}`
              ),
              on
                ? null
                : h(
                    "span",
                    { class: "small muted" },
                    ` · ${TEXT.skipped}`
                  )
            ),
            chip(shape, on)
          ),
          h(
            "div",
            {
              class: "small muted",
              style: "margin-top:2px;line-height:1.45",
            },
            note
          ),
          item.id === "ffn" && on
            ? h(
                "div",
                { class: "small muted", style: "margin-top:3px" },
                `${TEXT.expandNote} ${TEXT.hiddenShape}`
              )
            : null
        )
      );
    }

    function arrow() {
      return h(
        "div",
        {
          "aria-hidden": "true",
          style:
            "text-align:center;color:var(--muted, #64748b);font-size:12px;line-height:1;margin:1px 0",
        },
        "↓"
      );
    }

    function renderFlow() {
      const shape = flowShape();
      const nodes = [];
      nodes.push(
        h(
          "div",
          {
            role: "listitem",
            style:
              "display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;" +
              "padding:8px 11px;border-radius:9px;border:1px dashed var(--border-strong, #cbd5e1);" +
              "background:var(--surface-2, #f8fafc)",
          },
          h(
            "div",
            {},
            h("strong", { style: "font-size:12.5px" }, TEXT.input),
            h("div", { class: "small muted" }, TEXT.inputNote)
          ),
          chip(`${TEXT.inputShape} → ${shape}`, true)
        )
      );
      COMPONENTS.forEach((item, index) => {
        nodes.push(arrow());
        nodes.push(stageCard(item, index + 1, shape));
      });
      nodes.push(arrow());
      nodes.push(
        h(
          "div",
          {
            role: "listitem",
            style:
              "display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;" +
              "padding:8px 11px;border-radius:9px;border:1px solid var(--success, #059669);" +
              "background:var(--success-soft, #ecfdf5)",
          },
          h(
            "div",
            {},
            h("strong", { style: "font-size:12.5px" }, TEXT.output),
            h("div", { class: "small muted" }, TEXT.outputNote)
          ),
          chip(shape, true)
        )
      );
      flowList.replaceChildren(...nodes);
    }

    function renderStatus() {
      const skipped = COMPONENTS.filter((item) => !isOn(item.id));
      if (!skipped.length) {
        status.textContent = TEXT.statusAll;
        return;
      }
      const reasons = [];
      if (!isOn("attn")) reasons.push(TEXT.noAttention);
      if (!isOn("ffn")) reasons.push(TEXT.noFFN);
      if (!isOn("ln1") || !isOn("ln2")) reasons.push(TEXT.noNorm);
      if (!isOn("res1") || !isOn("res2")) reasons.push(TEXT.noResidual);
      status.textContent = `${TEXT.statusSkipped} ${skipped
        .map((item) => item.title)
        .join(", ")}. ${reasons.join(" ")}`.trim();
    }

    function renderStats() {
      const activeCount = COMPONENTS.filter((item) => isOn(item.id)).length;
      const parameterCount = params();
      stats.replaceChildren(
        stat(TEXT.stats.active, `${activeCount} / ${COMPONENTS.length}`),
        stat(TEXT.stats.shape, flowShape()),
        stat(TEXT.stats.params, fmtParams(parameterCount))
      );
      memory.textContent = `${TEXT.stats.memory}: ${fmtMb(
        (parameterCount * 4) / (1024 * 1024)
      )}`;
    }

    function renderToggles() {
      toggleGroup.replaceChildren(...COMPONENTS.map(toggleButton));
    }

    function render() {
      renderToggles();
      renderFlow();
      renderStatus();
      renderStats();
    }

    render();
    return () => {};
  },
};
