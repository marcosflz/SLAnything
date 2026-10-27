/* Aula LLM · comportamiento global. Sin dependencias. */

import { t } from "./i18n.js";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

/* --------------------------------------------------------------------------
   Tema claro / oscuro
   -------------------------------------------------------------------------- */
function initTheme() {
  const root = document.documentElement;
  const buttons = $$("[data-theme-toggle]");
  const apply = (theme) => {
    root.dataset.theme = theme;
    try { localStorage.setItem("aula-theme", theme); } catch (e) {}
    buttons.forEach((button) => {
      button.setAttribute(
        "aria-label",
        theme === "dark" ? t("Cambiar a tema claro") : t("Cambiar a tema oscuro")
      );
    });
  };
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      apply(root.dataset.theme === "dark" ? "light" : "dark");
    });
  });
}

/* --------------------------------------------------------------------------
   Navegación móvil
   -------------------------------------------------------------------------- */
function initSidebar() {
  const sidebar = $("#sidebar");
  const backdrop = $(".sidebar-backdrop");
  if (!sidebar) return;
  const open = () => {
    sidebar.classList.add("is-open");
    backdrop?.classList.add("is-open");
    document.body.classList.add("no-scroll");
  };
  const close = () => {
    sidebar.classList.remove("is-open");
    backdrop?.classList.remove("is-open");
    document.body.classList.remove("no-scroll");
  };
  $$("[data-sidebar-open]").forEach((button) => button.addEventListener("click", open));
  $$("[data-sidebar-close]").forEach((button) => button.addEventListener("click", close));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });
}

/* --------------------------------------------------------------------------
   Detalles de interfaz
   -------------------------------------------------------------------------- */
function initFlash() {
  $$("[data-dismiss]").forEach((button) => {
    button.addEventListener("click", () => button.closest(".flash")?.remove());
  });
}

function initCopyButtons() {
  $$("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.innerText);
        const previous = button.textContent;
        button.textContent = t("Copiado");
        setTimeout(() => { button.textContent = previous; }, 1600);
      } catch (error) {
        button.textContent = t("No disponible");
      }
    });
  });
}

function initLightbox() {
  const dialog = $("#lightbox");
  if (!dialog) return;
  const image = $("img", dialog);
  $$("[data-lightbox]").forEach((button) => {
    button.addEventListener("click", () => {
      image.src = button.dataset.lightbox;
      image.alt = button.querySelector("img")?.alt || "Figura ampliada";
      if (typeof dialog.showModal === "function") dialog.showModal();
    });
  });
  $("[data-lightbox-close]", dialog)?.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
}

function initReadingProgress() {
  const bar = $("[data-reading-progress]");
  const prose = $(".prose");
  if (!bar || !prose) return;
  const update = () => {
    const rect = prose.getBoundingClientRect();
    const total = rect.height - window.innerHeight * 0.55;
    const read = Math.min(Math.max(-rect.top + 120, 0), Math.max(total, 1));
    bar.style.width = `${Math.min(100, (read / Math.max(total, 1)) * 100)}%`;
  };
  update();
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
}

function initSearchShortcut() {
  const input = $("#busqueda");
  if (!input) return;
  document.addEventListener("keydown", (event) => {
    const tag = document.activeElement?.tagName?.toLowerCase();
    const typing = tag === "input" || tag === "textarea" || tag === "select" || document.activeElement?.isContentEditable;
    if (event.key === "/" && !typing) {
      event.preventDefault();
      input.focus();
    }
  });
}

function initNotes() {
  const textarea = $("[data-note]");
  const counter = $("[data-note-count]");
  if (!textarea || !counter) return;
  const template = textarea.dataset.noteLabel || "{n} caracteres";
  const update = () => {
    counter.textContent = template.replace("{n}", textarea.value.length);
  };
  update();
  textarea.addEventListener("input", update);
}

function initConfirmations() {
  $$("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
}

function initGlossary() {
  const input = $("[data-glossary-search]");
  const grid = $("[data-glossary-grid]");
  const empty = $("[data-glossary-empty]");
  if (!input || !grid) return;
  const cards = $$("[data-term-card]", grid);
  const letters = $$("[data-glossary-letter]", grid);
  const filter = () => {
    const query = input.value.trim().toLocaleLowerCase("es");
    let visible = 0;
    cards.forEach((card) => {
      const match = !query || card.dataset.term.includes(query);
      card.hidden = !match;
      if (match) visible += 1;
    });
    letters.forEach((letter) => {
      let sibling = letter.nextElementSibling;
      let hasVisible = false;
      while (sibling && !sibling.matches("[data-glossary-letter]")) {
        if (sibling.matches("[data-term-card]") && !sibling.hidden) hasVisible = true;
        sibling = sibling.nextElementSibling;
      }
      letter.hidden = !hasVisible;
    });
    if (empty) empty.hidden = visible !== 0;
  };
  input.addEventListener("input", filter);
  filter();
}

/* --------------------------------------------------------------------------
   Laboratorios con carga diferida
   -------------------------------------------------------------------------- */
function initLabs() {
  const sections = $$("[data-lab]");
  if (!sections.length) return;

  const mount = async (section) => {
    if (section.dataset.loaded === "true") return;
    section.dataset.loaded = "true";
    const id = section.dataset.lab;
    const body = $("[data-lab-body]", section);
    try {
      const module = await import(`/static/js/labs/${id}.js`);
      if (!module.default || typeof module.default.mount !== "function") {
        throw new Error(t("El laboratorio {id} no exporta mount()", { id }));
      }
      body.innerHTML = "";
      await module.default.mount(section);
      section.classList.add("is-ready");
    } catch (error) {
      console.error(t("No se pudo cargar el laboratorio {id}", { id }), error);
      body.innerHTML = `
        <div class="lab-error">
          <strong></strong>
          <p></p>
        </div>`;
      const box = $(".lab-error", body);
      if (box) {
        $("strong", box).textContent = t("No se pudo cargar este laboratorio.");
        $("p", box).textContent = t("Recarga la página o revisa la consola del navegador.");
      }
    }
  };

  if (!("IntersectionObserver" in window)) {
    sections.forEach(mount);
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          observer.unobserve(entry.target);
          mount(entry.target);
        }
      });
    },
    { rootMargin: "320px 0px" }
  );
  sections.forEach((section) => observer.observe(section));
}

/* --------------------------------------------------------------------------
   Quiz
   -------------------------------------------------------------------------- */
function initQuiz() {
  const form = $(".quiz-form");
  if (!form) return;
  const cards = $$(".quiz-card", form);
  const counter = $("[data-quiz-answered]");
  const bar = $("[data-quiz-bar]");
  const total = cards.length;

  const update = () => {
    let answered = 0;
    cards.forEach((card) => {
      const checked = card.querySelector("input[type=radio]:checked");
      card.classList.toggle("is-answered", Boolean(checked));
      if (checked) answered += 1;
    });
    if (counter) {
      const template = counter.dataset.quizLabel || "{n} de {total} respondidas";
      counter.textContent = template.replace("{n}", answered).replace("{total}", total);
    }
    if (bar) {
      bar.style.width = `${total ? (answered / total) * 100 : 0}%`;
      bar.parentElement?.setAttribute("aria-valuenow", String(total ? Math.round((answered / total) * 100) : 0));
    }
  };

  form.addEventListener("change", update);
  update();

  form.addEventListener("submit", (event) => {
    const answered = cards.filter((card) => card.querySelector("input[type=radio]:checked")).length;
    if (answered < total) {
      const message = t("Has respondido {answered} de {total} preguntas. ¿Enviar de todos modos?", { answered, total });
      if (!window.confirm(message)) event.preventDefault();
    }
  });
}

/* --------------------------------------------------------------------------
   Ejemplos de Python ejecutables
   -------------------------------------------------------------------------- */
function initPythonRunners() {
  const runners = $$("[data-python-runner]");
  if (!runners.length) return;
  const csrf = $('meta[name="csrf-token"]')?.content || "";

  runners.forEach((runner) => {
    const source = $(".py-source", runner);
    const gutter = $("[data-py-gutter]", runner);
    const runButton = $("[data-py-run]", runner);
    const resetButton = $("[data-py-reset]", runner);
    const clearButton = $("[data-py-clear]", runner);
    const output = $("[data-py-output]", runner);
    const status = $("[data-py-status]", runner);
    const duration = $("[data-py-duration]", runner);
    const stdout = $("[data-py-stdout]", runner);
    const errorBox = $("[data-py-error]", runner);
    const results = $("[data-py-results]", runner);
    if (!source || !output || !runButton) return;

    const original = source.value;
    let running = false;

    const updateGutter = () => {
      if (!gutter) return;
      const lines = source.value.split("\n").length;
      gutter.textContent = Array.from({ length: lines }, (_, i) => i + 1).join("\n");
      source.style.height = "auto";
      source.style.height = `${Math.max(180, source.scrollHeight)}px`;
      gutter.style.height = `${source.scrollHeight}px`;
    };

    const resetOutput = () => {
      output.hidden = true;
      stdout.textContent = "";
      results.replaceChildren();
      errorBox.hidden = true;
      errorBox.textContent = "";
      if (duration) duration.textContent = "";
      if (status) status.textContent = t("Salida");
    };

    const appendText = (text) => {
      if (text) stdout.textContent += text;
    };

    const showResults = (items) => {
      (items || []).forEach((item) => {
        if (item.type === "image" && item.data) {
          const image = document.createElement("img");
          image.className = "py-plot";
          image.loading = "lazy";
          image.alt = t("Gráfico generado por el ejemplo");
          image.src = `data:${item.mime || "image/png"};base64,${item.data}`;
          results.append(image);
        } else if (item.type === "table" && item.html) {
          const wrapper = document.createElement("div");
          wrapper.className = "py-table-wrap";
          wrapper.innerHTML = item.html;
          results.append(wrapper);
        } else if (item.type === "text" && item.text) {
          const pre = document.createElement("pre");
          pre.className = "py-result-text";
          pre.textContent = item.text;
          results.append(pre);
        }
      });
    };

    const run = async () => {
      if (running) return;
      running = true;
      runButton.disabled = true;
      output.hidden = false;
      status.textContent = t("Ejecutando…");
      duration.textContent = "";
      stdout.textContent = "";
      results.replaceChildren();
      errorBox.hidden = true;
      errorBox.textContent = "";
      const started = performance.now();
      try {
        const response = await fetch("/api/ejecutar", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrf,
          },
          body: JSON.stringify({
            code: source.value,
            lesson: runner.dataset.lesson || null,
          }),
        });
        let data = null;
        try { data = await response.json(); } catch (error) { data = null; }
        const elapsed = Math.max(1, Math.round(performance.now() - started));
        if (!response.ok) {
          const detail =
            (typeof data?.error === "string" && data.error) ||
            (typeof data?.detail === "string" && data.detail) ||
            t("No se pudo ejecutar el código.");
          throw new Error(detail);
        }
        appendText(data.stdout || "");
        showResults(data.outputs || []);
        if (data.error) {
          errorBox.hidden = false;
          errorBox.textContent = data.error;
          status.textContent = t("El código devolvió un error.");
        } else {
          status.textContent = t("El código se ejecutó correctamente.");
        }
        if (!stdout.textContent && !(data.outputs || []).length && !data.error) {
          appendText(t("Sin salida."));
        }
        duration.textContent = `${elapsed} ms`;
      } catch (error) {
        errorBox.hidden = false;
        errorBox.textContent = error.message || t("El servidor no respondió. Inténtalo de nuevo.");
        status.textContent = t("El código devolvió un error.");
      } finally {
        running = false;
        runButton.disabled = false;
      }
    };

    runButton.addEventListener("click", run);
    resetButton?.addEventListener("click", () => {
      source.value = original;
      updateGutter();
      resetOutput();
    });
    clearButton?.addEventListener("click", resetOutput);
    source.addEventListener("input", updateGutter);
    source.addEventListener("keydown", (event) => {
      if (event.key === "Tab") {
        event.preventDefault();
        const start = source.selectionStart;
        const end = source.selectionEnd;
        source.setRangeText("    ", start, end, "end");
        updateGutter();
      }
      if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        run();
      }
    });
    updateGutter();
  });
}

/* --------------------------------------------------------------------------
   Arranque
   -------------------------------------------------------------------------- */
function boot() {
  initTheme();
  initSidebar();
  initFlash();
  initCopyButtons();
  initLightbox();
  initReadingProgress();
  initSearchShortcut();
  initNotes();
  initConfirmations();
  initGlossary();
  initLabs();
  initPythonRunners();
  initQuiz();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
