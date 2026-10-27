/* Laboratorio · Clasificador interactivo
   Mueve el umbral y observa la matriz de confusión y las métricas. */

import { h } from "./common.js";

const COPY = {
  es: {
    intro: "Un clasificador devuelve una probabilidad. El umbral decide cuándo esa probabilidad se convierte en una alerta de spam.",
    threshold: "Umbral de decisión",
    thresholdHelp: "Si la probabilidad de spam es mayor o igual que el umbral, el mensaje se marca como spam.",
    how: "Cómo leerlo",
    howText: "Bajar el umbral detecta más spam, pero también bloquea más mensajes legítimos. Subirlo hace lo contrario. La accuracy puede cambiar poco mientras la precisión y el recall se mueven en direcciones opuestas.",
    metrics: "Métricas en este umbral",
    accuracy: "Accuracy",
    precision: "Precisión",
    recall: "Recall",
    f1: "F1",
    matrix: "Matriz de confusión",
    matrixCaption: "Recuento de los 14 mensajes de ejemplo con el umbral actual.",
    actualVsPredicted: "Real ↓ / Predicho →",
    predictedSpam: "Predicho spam",
    predictedHam: "Predicho ham",
    actualSpam: "Real spam",
    actualHam: "Real ham",
    truePositive: "Verdadero positivo",
    falseNegative: "Falso negativo",
    falsePositive: "Falso positivo",
    trueNegative: "Verdadero negativo",
    messages: "Mensajes de ejemplo",
    message: "Mensaje",
    spamProbability: "Prob. spam",
    actual: "Real",
    prediction: "Predicción",
    spam: "spam",
    ham: "ham",
    note: "Datos ficticios con puntuaciones fijas. El objetivo es ver cómo una misma lista de mensajes produce matrices distintas al mover el umbral.",
    dataset: "Conjunto de ejemplo",
    datasetText: "14 mensajes: 6 spam y 8 ham. Las puntuaciones son la probabilidad estimada de spam.",
    reset: "Restaurar 50 %",
  },
  en: {
    intro: "A classifier returns a probability. The threshold decides when that probability becomes a spam alert.",
    threshold: "Decision threshold",
    thresholdHelp: "If the spam probability is greater than or equal to the threshold, the message is marked as spam.",
    how: "How to read it",
    howText: "Lowering the threshold catches more spam, but also blocks more legitimate messages. Raising it does the opposite. Accuracy may change little while precision and recall move in opposite directions.",
    metrics: "Metrics at this threshold",
    accuracy: "Accuracy",
    precision: "Precision",
    recall: "Recall",
    f1: "F1",
    matrix: "Confusion matrix",
    matrixCaption: "Counts for the 14 example messages at the current threshold.",
    actualVsPredicted: "Actual ↓ / Predicted →",
    predictedSpam: "Predicted spam",
    predictedHam: "Predicted ham",
    actualSpam: "Actual spam",
    actualHam: "Actual ham",
    truePositive: "True positive",
    falseNegative: "False negative",
    falsePositive: "False positive",
    trueNegative: "True negative",
    messages: "Example messages",
    message: "Message",
    spamProbability: "Spam prob.",
    actual: "Actual",
    prediction: "Prediction",
    spam: "spam",
    ham: "ham",
    note: "Fictional data with fixed scores. The point is to see how the same messages produce different matrices as the threshold moves.",
    dataset: "Example dataset",
    datasetText: "14 messages: 6 spam and 8 ham. The scores are the estimated spam probability.",
    reset: "Reset to 50%",
  },
};

const MESSAGES = [
  {
    es: "¡Felicidades! Has ganado un premio de 1.000 €. Reclámalo hoy.",
    en: "Congratulations! You have won a €1,000 prize. Claim it today.",
    score: 0.96,
    label: 1,
  },
  {
    es: "Reclama tu premio antes de que caduque. Solo necesitamos tus datos.",
    en: "Claim your prize before it expires. We only need your details.",
    score: 0.91,
    label: 1,
  },
  {
    es: "Última oportunidad: tu cuenta será suspendida si no verificas ahora.",
    en: "Last chance: your account will be suspended unless you verify now.",
    score: 0.87,
    label: 1,
  },
  {
    es: "Tu cuenta será suspendida. Confirma la contraseña en este enlace.",
    en: "Your account will be suspended. Confirm your password at this link.",
    score: 0.72,
    label: 1,
  },
  {
    es: "Gana dinero desde casa con solo dos horas al día.",
    en: "Earn money from home with just two hours a day.",
    score: 0.66,
    label: 1,
  },
  {
    es: "Premio disponible para los primeros diez usuarios que respondan.",
    en: "Prize available to the first ten users who reply.",
    score: 0.54,
    label: 1,
  },
  {
    es: "Nos vemos mañana a las ocho en la puerta del teatro.",
    en: "See you tomorrow at eight at the theatre entrance.",
    score: 0.61,
    label: 0,
  },
  {
    es: "Te envío el informe revisado para que lo leas antes de la reunión.",
    en: "I am sending you the revised report so you can read it before the meeting.",
    score: 0.43,
    label: 0,
  },
  {
    es: "¿Comemos el jueves? Me apetece probar el sitio nuevo.",
    en: "Shall we have lunch on Thursday? I would like to try the new place.",
    score: 0.35,
    label: 0,
  },
  {
    es: "La reunión empieza a las diez; lleva el borrador impreso.",
    en: "The meeting starts at ten; bring the printed draft.",
    score: 0.28,
    label: 0,
  },
  {
    es: "Gracias por tu ayuda con la mudanza, ha sido un día largo.",
    en: "Thanks for your help with the move, it has been a long day.",
    score: 0.19,
    label: 0,
  },
  {
    es: "He comprado pan y leche; no hace falta que pases por el supermercado.",
    en: "I bought bread and milk; you do not need to stop at the supermarket.",
    score: 0.12,
    label: 0,
  },
  {
    es: "Llámame cuando llegues a casa, así me quedo tranquila.",
    en: "Call me when you get home so I know you are safe.",
    score: 0.08,
    label: 0,
  },
  {
    es: "El paquete llega el martes por la tarde, según la empresa de reparto.",
    en: "The parcel arrives on Tuesday afternoon, according to the courier.",
    score: 0.05,
    label: 0,
  },
];

function percentFormatter(maximumFractionDigits) {
  return new Intl.NumberFormat(
    document.documentElement.lang === "en" ? "en-GB" : "es-ES",
    { style: "percent", maximumFractionDigits }
  );
}

export default {
  id: "classifier",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    const lang = document.documentElement.lang === "en" ? "en" : "es";
    const copy = COPY[lang];
    const formatPercent = percentFormatter(1);
    const formatThreshold = percentFormatter(0);

    let threshold = 0.5;

    const thresholdOutput = h("output", { for: "classifier-threshold" });
    const thresholdHelp = h("small", { id: "classifier-threshold-help" }, copy.thresholdHelp);
    const slider = h("input", {
      id: "classifier-threshold",
      type: "range",
      min: "0",
      max: "1",
      step: "0.05",
      value: String(threshold),
      "aria-describedby": "classifier-threshold-help",
    });

    const resetButton = h(
      "button",
      { class: "btn btn-secondary btn-sm", type: "button" },
      copy.reset
    );

    const controls = h(
      "div",
      { class: "lab-controls" },
      h(
        "div",
        { class: "field" },
        h("label", { for: "classifier-threshold" }, copy.threshold, thresholdOutput),
        slider,
        thresholdHelp
      ),
      h(
        "div",
        { class: "lab-note" },
        h("strong", {}, copy.how),
        h("p", {}, copy.howText)
      ),
      h(
        "div",
        { class: "field" },
        h("label", {}, copy.dataset),
        h("p", { class: "small muted" }, copy.datasetText)
      ),
      h("div", { class: "row" }, resetButton)
    );

    const stats = h("div", {
      role: "status",
      "aria-live": "polite",
      style: "display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px",
    });
    const matrix = h("div");
    const messageTable = h("div", { class: "mt-3" });
    const output = h(
      "div",
      { class: "lab-output" },
      h("h4", {}, copy.metrics),
      stats,
      h("h4", { class: "mt-3" }, copy.matrix),
      matrix,
      h("p", { class: "small muted mt-2" }, copy.note)
    );

    body.replaceChildren(
      h("div", { class: "lab-grid" }, controls, output),
      messageTable
    );

    function evaluate() {
      let tp = 0;
      let fp = 0;
      let fn = 0;
      let tn = 0;

      for (const message of MESSAGES) {
        const predicted = message.score >= threshold ? 1 : 0;
        if (message.label === 1 && predicted === 1) tp += 1;
        else if (message.label === 0 && predicted === 1) fp += 1;
        else if (message.label === 1 && predicted === 0) fn += 1;
        else tn += 1;
      }

      const total = MESSAGES.length;
      return {
        tp,
        fp,
        fn,
        tn,
        accuracy: (tp + tn) / total,
        precision: tp + fp ? tp / (tp + fp) : 0,
        recall: tp + fn ? tp / (tp + fn) : 0,
        f1:
          tp + fp && tp + fn
            ? (2 * (tp / (tp + fp)) * (tp / (tp + fn))) /
              (tp / (tp + fp) + tp / (tp + fn))
            : 0,
      };
    }

    function stat(label, value) {
      return h(
        "div",
        { class: "lab-stat" },
        h("span", {}, label),
        h("strong", {}, value)
      );
    }

    function cell(label, count, tone) {
      const palette = {
        good: ["#dcfce7", "#16a34a", "#166534"],
        bad: ["#fef3c7", "#d97706", "#92400e"],
      };
      const [background, border, color] = palette[tone];
      return h(
        "td",
        {
          style: `background:${background};border:1px solid ${border};border-radius:8px;padding:12px;text-align:center;color:${color};vertical-align:middle`,
        },
        h("strong", { style: "display:block;font-size:26px;line-height:1.1" }, String(count)),
        h("small", { style: "display:block;margin-top:4px;font-size:10.5px" }, label)
      );
    }

    function renderMatrix(result) {
      const table = h(
        "table",
        { style: "width:100%;border-collapse:separate;border-spacing:6px" },
        h("caption", { style: "caption-side:top;text-align:left;font-size:11px;color:#64748b;padding-bottom:6px" }, copy.matrixCaption),
        h(
          "thead",
          {},
          h(
            "tr",
            {},
            h("th", { scope: "col", style: "font-size:10px;color:#64748b;text-align:left;padding:2px" }, copy.actualVsPredicted),
            h("th", { scope: "col", style: "font-size:10px;color:#64748b;text-align:center;padding:2px" }, copy.predictedSpam),
            h("th", { scope: "col", style: "font-size:10px;color:#64748b;text-align:center;padding:2px" }, copy.predictedHam)
          )
        ),
        h(
          "tbody",
          {},
          h(
            "tr",
            {},
            h("th", { scope: "row", style: "font-size:10.5px;color:#475569;text-align:left;padding:2px" }, copy.actualSpam),
            cell(copy.truePositive, result.tp, "good"),
            cell(copy.falseNegative, result.fn, "bad")
          ),
          h(
            "tr",
            {},
            h("th", { scope: "row", style: "font-size:10.5px;color:#475569;text-align:left;padding:2px" }, copy.actualHam),
            cell(copy.falsePositive, result.fp, "bad"),
            cell(copy.trueNegative, result.tn, "good")
          )
        )
      );
      matrix.replaceChildren(h("div", { class: "table-wrap", style: "margin:0" }, table));
    }

    function badge(value) {
      const isSpam = value === 1;
      return h(
        "span",
        {
          style: `display:inline-block;padding:2px 8px;border-radius:999px;font-size:10px;font-weight:700;background:${
            isSpam ? "#fef3c7" : "#e2e8f0"
          };color:${isSpam ? "#92400e" : "#475569"}`,
        },
        isSpam ? copy.spam : copy.ham
      );
    }

    function renderMessages() {
      const rows = [...MESSAGES]
        .sort((a, b) => b.score - a.score)
        .map((message) => {
          const predicted = message.score >= threshold ? 1 : 0;
          return h(
            "tr",
            {},
            h("td", { style: "min-width:220px" }, message[lang]),
            h("td", { style: "white-space:nowrap;font-variant-numeric:tabular-nums" }, formatPercent.format(message.score)),
            h("td", {}, badge(message.label)),
            h("td", {}, badge(predicted))
          );
        });

      const table = h(
        "table",
        {},
        h("caption", {}, copy.messages),
        h(
          "thead",
          {},
          h(
            "tr",
            {},
            h("th", { scope: "col" }, copy.message),
            h("th", { scope: "col" }, copy.spamProbability),
            h("th", { scope: "col" }, copy.actual),
            h("th", { scope: "col" }, copy.prediction)
          )
        ),
        h("tbody", {}, rows)
      );

      messageTable.replaceChildren(h("div", { class: "table-wrap" }, table));
    }

    function render() {
      const result = evaluate();
      thresholdOutput.textContent = formatThreshold.format(threshold);
      slider.setAttribute("aria-valuetext", formatThreshold.format(threshold));

      stats.replaceChildren(
        stat(copy.accuracy, formatPercent.format(result.accuracy)),
        stat(copy.precision, formatPercent.format(result.precision)),
        stat(copy.recall, formatPercent.format(result.recall)),
        stat(copy.f1, formatPercent.format(result.f1))
      );

      renderMatrix(result);
      renderMessages();
    }

    slider.addEventListener("input", () => {
      threshold = Number(slider.value);
      render();
    });

    resetButton.addEventListener("click", () => {
      threshold = 0.5;
      slider.value = "0.5";
      render();
    });

    render();

    return () => {};
  },
};
