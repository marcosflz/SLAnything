/* Laboratorio · Tokenizador BPE
   Entrena un BPE en miniatura sobre un corpus y permite tokenizar palabras nuevas. */

import { h } from "./common.js";

const EN = document.documentElement.lang.startsWith("en");

const S = EN
  ? {
      intro: "Watch BPE learn merges from a small corpus. Increase the number of merges and see how words break into fewer pieces.",
      corpusLabel: "Training corpus",
      mergesLabel: "Number of merges",
      wordLabel: "Word to tokenize",
      wordPlaceholder: "Type a word",
      examplesLabel: "Try one",
      mergesTitle: "Learned merges",
      vocabTitle: "Vocabulary pieces",
      resultTitle: "Tokenization",
      stats: ["Base symbols", "Merges", "Tokens"],
      empty: "Type a word to see its subword pieces.",
      noRules: "No merges yet: the word is split into characters.",
      end: "end marker",
      merge: "merge",
      reset: "Reset",
      hint: "Each merge joins the most frequent adjacent pair. The end marker · closes the word.",
      unknown: "The word was not in the corpus, but BPE still represents it with known pieces.",
      known: "This word appears in the corpus. The merges learned from it also apply to new words.",
      ruleLine: (a, b, result, count) => `${a} + ${b} → ${result} (${count}×)`,
    }
  : {
      intro: "Observa cómo BPE aprende fusiones de un corpus pequeño. Aumenta el número de fusiones y comprueba cómo las palabras se dividen en menos piezas.",
      corpusLabel: "Corpus de entrenamiento",
      mergesLabel: "Número de fusiones",
      wordLabel: "Palabra para tokenizar",
      wordPlaceholder: "Escribe una palabra",
      examplesLabel: "Prueba una",
      mergesTitle: "Fusiones aprendidas",
      vocabTitle: "Piezas del vocabulario",
      resultTitle: "Tokenización",
      stats: ["Símbolos base", "Fusiones", "Tokens"],
      empty: "Escribe una palabra para ver sus piezas.",
      noRules: "Todavía no hay fusiones: la palabra se divide en caracteres.",
      end: "marca de final",
      merge: "fusión",
      reset: "Reiniciar",
      hint: "Cada fusión une el par adyacente más frecuente. La marca · cierra la palabra.",
      unknown: "La palabra no estaba en el corpus, pero BPE la representa con piezas conocidas.",
      known: "La palabra aparece en el corpus. Las fusiones aprendidas también se aplican a palabras nuevas.",
      ruleLine: (a, b, result, count) => `${a} + ${b} → ${result} (${count}×)`,
    };

const CORPUS = EN
  ? ["low", "low", "lower", "lowest", "new", "newer", "newest", "wide"]
  : ["bajo", "bajo", "baja", "bajas", "casa", "casas", "casero", "paso"];
const EXAMPLES = EN ? ["lowly", "newest", "wider"] : ["bajito", "casero", "pasillo"];
const END = "·";
const MAX_MERGES = 9;

function countPairs(words) {
  const counts = new Map();
  for (const tokens of words) {
    for (let i = 0; i < tokens.length - 1; i += 1) {
      const key = `${tokens[i]}\u0000${tokens[i + 1]}`;
      const entry = counts.get(key);
      if (entry) entry.count += 1;
      else counts.set(key, { a: tokens[i], b: tokens[i + 1], count: 1 });
    }
  }
  return counts;
}

function mergePair(tokens, a, b) {
  const output = [];
  let i = 0;
  while (i < tokens.length) {
    if (i + 1 < tokens.length && tokens[i] === a && tokens[i + 1] === b) {
      output.push(a + b);
      i += 2;
    } else {
      output.push(tokens[i]);
      i += 1;
    }
  }
  return output;
}

function train(words, limit) {
  let vocabulary = words.map((word) => [...word, END]);
  const rules = [];
  for (let step = 0; step < limit; step += 1) {
    const counts = countPairs(vocabulary);
    let best = null;
    for (const entry of counts.values()) {
      if (entry.count < 2) continue;
      if (
        !best ||
        entry.count > best.count ||
        (entry.count === best.count && `${entry.a}${entry.b}` < `${best.a}${best.b}`)
      ) {
        best = entry;
      }
    }
    if (!best) break;
    vocabulary = vocabulary.map((tokens) => mergePair(tokens, best.a, best.b));
    rules.push({ a: best.a, b: best.b, result: best.a + best.b, count: best.count });
  }
  return rules;
}

function tokenize(word, rules) {
  let tokens = [...word, END];
  for (const rule of rules) tokens = mergePair(tokens, rule.a, rule.b);
  return tokens;
}

function stat(label, value) {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, String(value))
  );
}

export default {
  id: "tokenizer",

  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    if (!body) return () => {};

    const rules = train(CORPUS, MAX_MERGES);
    let mergeCount = Math.min(4, rules.length);
    let word = EXAMPLES[0];

    const controls = h("div", { class: "lab-controls" });
    const output = h("div", { class: "lab-output", "aria-live": "polite" });
    const mergeOutput = h("output", { for: "bpe-merges" });
    const mergeList = h("ol", { class: "small", style: "margin:6px 0 0 18px;padding:0" });
    const vocabRow = h("div", { class: "token-row" });
    const tokenRow = h("div", { class: "token-row" });
    const resultNote = h("p", { class: "small muted mt-2" });
    const stats = h("div", { class: "lab-stat-row mt-3" });

    const range = h("input", {
      id: "bpe-merges",
      type: "range",
      min: "0",
      max: String(rules.length),
      step: "1",
      value: String(mergeCount),
      oninput: (event) => {
        mergeCount = Number(event.currentTarget.value);
        render();
      },
    });

    const wordInput = h("input", {
      id: "bpe-word",
      type: "text",
      value: word,
      placeholder: S.wordPlaceholder,
      autocomplete: "off",
      oninput: (event) => {
        word = event.currentTarget.value;
        render();
      },
    });

    const resetButton = h(
      "button",
      {
        type: "button",
        class: "btn btn-secondary btn-sm",
        onclick: () => {
          mergeCount = Math.min(4, rules.length);
          word = EXAMPLES[0];
          range.value = String(mergeCount);
          wordInput.value = word;
          render();
        },
      },
      S.reset
    );

    const exampleRow = h("div", { class: "token-row" });
    EXAMPLES.forEach((example) => {
      exampleRow.append(
        h(
          "button",
          {
            type: "button",
            class: "token-chip",
            onclick: () => {
              word = example;
              wordInput.value = example;
              render();
            },
          },
          example
        )
      );
    });

    controls.append(
      h("p", { class: "small" }, S.intro),
      h(
        "div",
        { class: "field" },
        h("label", {}, S.corpusLabel),
        h(
          "p",
          { class: "small", style: "margin:0;font-family:ui-monospace,monospace" },
          CORPUS.join(" · ")
        ),
        h("small", {}, S.hint)
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "bpe-merges" }, S.mergesLabel),
        range,
        mergeOutput
      ),
      h(
        "div",
        { class: "field" },
        h("label", { for: "bpe-word" }, S.wordLabel),
        wordInput,
        h("small", {}, S.examplesLabel),
        exampleRow
      ),
      h("div", { class: "row" }, resetButton)
    );

    output.append(
      h("h4", {}, S.resultTitle),
      tokenRow,
      resultNote,
      stats,
      h("div", { class: "mt-3" }, h("h4", {}, S.vocabTitle), vocabRow),
      h("div", { class: "mt-3" }, h("h4", {}, S.mergesTitle), mergeList)
    );

    body.replaceChildren(h("div", { class: "lab-grid" }, controls, output));

    function render() {
      const active = rules.slice(0, mergeCount);
      const pieces = word.trim() ? tokenize(word.trim(), active) : [];
      const known = CORPUS.includes(word.trim());
      mergeOutput.textContent = `${mergeCount} / ${rules.length}`;

      mergeList.replaceChildren();
      if (!active.length) {
        mergeList.append(h("li", {}, S.noRules));
      } else {
        active.forEach((rule) => {
          mergeList.append(h("li", {}, S.ruleLine(rule.a, rule.b, rule.result, rule.count)));
        });
      }

      const base = new Set();
      CORPUS.forEach((item) => {
        [...item, END].forEach((symbol) => base.add(symbol));
      });
      active.forEach((rule) => base.add(rule.result));
      vocabRow.replaceChildren();
      [...base].forEach((symbol) => {
        vocabRow.append(
          h(
            "span",
            {
              class: symbol === END ? "token-chip is-next" : "token-chip",
              title: symbol === END ? S.end : S.merge,
            },
            symbol
          )
        );
      });

      tokenRow.replaceChildren();
      if (!pieces.length) {
        tokenRow.append(h("span", { class: "small muted" }, S.empty));
      } else {
        pieces.forEach((piece) => {
          tokenRow.append(
            h(
              "span",
              {
                class: piece === END ? "token-chip is-next" : "token-chip is-selected",
                title: piece === END ? S.end : S.merge,
              },
              piece
            )
          );
        });
      }

      resultNote.textContent = pieces.length
        ? `${word.trim()} → ${pieces.map((piece) => (piece === END ? "·" : piece)).join(" | ")}. ${known ? S.known : S.unknown}`
        : S.empty;

      stats.replaceChildren(
        stat(S.stats[0], base.size - active.length),
        stat(S.stats[1], active.length),
        stat(S.stats[2], pieces.length)
      );
    }

    render();
    return () => {};
  },
};
