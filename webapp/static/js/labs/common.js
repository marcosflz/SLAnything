/* Utilidades compartidas por los laboratorios. */

import { locale, t } from "../i18n.js";

export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

export function h(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key === "text") node.textContent = value;
    else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (key === "checked" || key === "disabled" || key === "selected") {
      node[key] = Boolean(value);
    } else {
      node.setAttribute(key, String(value));
    }
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export function num(value, digits = 2) {
  return new Intl.NumberFormat(locale(), {
    maximumFractionDigits: digits,
    minimumFractionDigits: 0,
  }).format(value);
}

export function fmt(value, digits = 1) {
  const abs = Math.abs(value);
  if (abs >= 1e12) return `${num(value / 1e12, digits)} ${t("B")}`;
  if (abs >= 1e9) return `${num(value / 1e9, digits)} ${t("mil M")}`;
  if (abs >= 1e6) return `${num(value / 1e6, digits)} ${t("M")}`;
  if (abs >= 1e3) return `${num(value / 1e3, digits)} ${t("mil")}`;
  return num(value, digits);
}

export function pct(value, digits = 1) {
  return `${num(value * 100, digits)} %`;
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function debounce(fn, wait = 120) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

export function mulberry32(seed) {
  let state = seed >>> 0;
  return function random() {
    state |= 0;
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* --------------------------------------------------------------------------
   Tokenización y modelo de n-gramas (didáctico, no production-grade)
   -------------------------------------------------------------------------- */

const TOKEN_RE = /[\p{L}\p{N}]+|[^\s\p{L}\p{N}]/gu;

export function tokenize(text) {
  return (text.toLowerCase().match(TOKEN_RE) || []);
}

export function detokenize(tokens) {
  const closing = new Set([".", ",", ";", ":", "!", "?", ")", "]", "}"]);
  const opening = new Set(["¿", "¡", "(", "[", "{"]);
  let output = "";
  tokens.forEach((token, index) => {
    if (index === 0) {
      output = token;
      return;
    }
    if (closing.has(token)) output += token;
    else if (opening.has(token)) output += ` ${token}`;
    else output += ` ${token}`;
  });
  return output;
}

export function buildNGramModel(tokens, maxOrder = 4) {
  const counts = new Map();
  for (let i = 0; i < tokens.length; i += 1) {
    for (let n = 1; n <= maxOrder; n += 1) {
      if (i < n - 1) continue;
      const context = tokens.slice(i - n + 1, i).join(" ");
      const key = `${n}:${context}`;
      let bucket = counts.get(key);
      if (!bucket) {
        bucket = new Map();
        counts.set(key, bucket);
      }
      bucket.set(tokens[i], (bucket.get(tokens[i]) || 0) + 1);
    }
  }
  return {
    counts,
    maxOrder,
    totalTokens: tokens.length,
    vocab: new Set(tokens).size,
    contexts: [...counts.keys()].filter((key) => key.startsWith(`${maxOrder}:`)).length,
  };
}

export function nextDistribution(model, contextTokens, limit = 12) {
  const maxContext = model.maxOrder - 1;
  for (let n = Math.min(maxContext, contextTokens.length); n >= 1; n -= 1) {
    const key = `${n}:${contextTokens.slice(-n).join(" ")}`;
    const bucket = model.counts.get(key);
    if (bucket && bucket.size) {
      const total = [...bucket.values()].reduce((sum, value) => sum + value, 0);
      return [...bucket.entries()]
        .map(([token, count]) => ({ token, count, prob: count / total }))
        .sort((a, b) => b.count - a.count)
        .slice(0, limit);
    }
  }
  const unigram = model.counts.get("1:");
  if (!unigram) return [];
  const total = [...unigram.values()].reduce((sum, value) => sum + value, 0);
  return [...unigram.entries()]
    .map(([token, count]) => ({ token, count, prob: count / total }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}

export function sampleNext(items, temperature = 0.8, topK = 40, random = Math.random) {
  if (!items.length) return null;
  const candidates = items.slice(0, Math.max(1, topK));
  if (temperature <= 0.05) return candidates[0].token;
  const weights = candidates.map((item) => Math.pow(item.count, 1 / temperature));
  const total = weights.reduce((sum, value) => sum + value, 0);
  let ticket = random() * total;
  for (let i = 0; i < candidates.length; i += 1) {
    ticket -= weights[i];
    if (ticket <= 0) return candidates[i].token;
  }
  return candidates[candidates.length - 1].token;
}

export async function loadText(url) {
  const response = await fetch(url, { cache: "force-cache" });
  if (!response.ok) throw new Error(`No se pudo cargar ${url} (${response.status})`);
  return response.text();
}

export async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    if (button) {
      const previous = button.textContent;
      button.textContent = t("Copiado");
      setTimeout(() => { button.textContent = previous; }, 1500);
    }
    return true;
  } catch (error) {
    return false;
  }
}

export function bar(label, value, max, options = {}) {
  const width = max > 0 ? clamp((value / max) * 100, 0, 100) : 0;
  return h(
    "div",
    { class: "bar-row" },
    h("span", { class: "bar-label" }, label),
    h("div", { class: "bar-track" }, h("span", {
      style: `width:${width}%`,
      class: options.tone ? `bar-${options.tone}` : "",
    })),
    h("span", { class: "bar-value" }, options.format ? options.format(value) : num(value, 2))
  );
}

export function stat(label, value, unit = "") {
  return h(
    "div",
    { class: "lab-stat" },
    h("span", {}, label),
    h("strong", {}, value, unit ? h("small", {}, ` ${unit}`) : null)
  );
}

export function option(value, label, selected = false) {
  return h("option", { value, selected }, label);
}
