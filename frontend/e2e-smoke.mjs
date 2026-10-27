import { chromium } from "playwright";

const base = "http://127.0.0.1:3000";
const errors = [];
const failures = [];

function check(name, condition) {
  console.log(`${condition ? "ok" : "FALLA"} · ${name}`);
  if (!condition) failures.push(name);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
page.on("console", (message) => {
  if (message.type() === "error") errors.push(message.text());
});
page.on("pageerror", (error) => errors.push(String(error)));
page.on("dialog", (dialog) => dialog.accept());

async function switchLanguage(label, expected) {
  await page.locator(".lang-switch a", { hasText: label }).first().click();
  await page.waitForLoadState("networkidle");
  return (
    (await page.evaluate(() => document.documentElement.lang)) === expected
  );
}

// Landing pública: el selector debe funcionar en ambos sentidos.
await page.goto(base, { waitUntil: "networkidle" });
check("landing en español", (await page.evaluate(() => document.documentElement.lang)) === "es");
check("landing → EN", await switchLanguage("EN", "en"));
check("landing → ES", await switchLanguage("ES", "es"));

// Login real.
await page.goto(`${base}/entrar`, { waitUntil: "networkidle" });
await page.fill("#email", "demo@aulallm.local");
await page.fill("#password", "demo1234");
await Promise.all([
  page.waitForURL(`${base}/`, { timeout: 15000 }),
  page.locator('button[type="submit"]').click(),
]);
check("login", page.url() === `${base}/`);

// Catálogo: acceso diferenciado a cursos y curso público.
await page.goto(`${base}/cursos`, { waitUntil: "networkidle" });
check("catálogo muestra el curso", (await page.locator(".course-card").count()) >= 1);
await page.goto(`${base}/cursos/llm-desde-cero`, { waitUntil: "networkidle" });
check("detalle de curso muestra 7 capítulos", (await page.locator(".chapter-section").count()) === 7);

// Curso: cambio de idioma con navegación completa.
await page.goto(`${base}/curso`, { waitUntil: "networkidle" });
check("curso muestra 7 capítulos", (await page.locator(".chapter-section").count()) === 7);
check("sidebar agrupa 7 capítulos", (await page.locator(".side-chapter").count()) === 7);
check(
  "sidebar limpia sin curso actual duplicado",
  (await page.locator('.side-link[href="/curso"]').count()) === 0 &&
    (await page.locator(".sidebar-course-switch").count()) === 0
);
check(
  "sidebar enlaza al catálogo de cursos",
  (await page.locator('.side-link[href="/cursos"]').count()) === 1
);
const chapterTwo = page.locator(".side-chapter").nth(1);
await chapterTwo.locator("summary").click();
check(
  "sidebar abre el capítulo 2",
  await chapterTwo.evaluate((element) => element.open)
);
check(
  "el capítulo 2 enlaza sus lecciones",
  (await chapterTwo.locator(".side-lesson").count()) === 8
);
check("curso → EN", await switchLanguage("EN", "en"));
check("curso → ES", await switchLanguage("ES", "es"));

// Barra lateral colapsable y persistente.
const beforeWidth = await page
  .locator(".app-main")
  .evaluate((element) => element.getBoundingClientRect().width);
await page.locator("[data-sidebar-collapse]").click();
await page.waitForTimeout(350);
const afterWidth = await page
  .locator(".app-main")
  .evaluate((element) => element.getBoundingClientRect().width);
check(
  "sidebar colapsada",
  (await page.evaluate(() =>
    document.documentElement.classList.contains("sidebar-collapsed")
  )) && afterWidth > beforeWidth
);
await page.reload({ waitUntil: "networkidle" });
check(
  "sidebar persistida",
  await page.evaluate(() =>
    document.documentElement.classList.contains("sidebar-collapsed")
  )
);
await page.locator("[data-sidebar-collapse]").click();
await page.waitForTimeout(300);

// Lección: laboratorio y runner Python.
await page.goto(`${base}/leccion/que-es-un-llm`, { waitUntil: "networkidle" });
await page.locator('.lab[data-lab="memory"]').scrollIntoViewIfNeeded();
await page.waitForSelector('.lab[data-lab="memory"].is-ready', { timeout: 20000 });
check("lab memory montado", true);

const run = page.locator("[data-py-run]").first();
check("runner Python presente", (await run.count()) > 0);
if (await run.count()) {
  await run.click();
  await page.waitForSelector("[data-py-output]:not([hidden])", { timeout: 30000 });
  const stdout = (await page.locator("[data-py-stdout]").first().textContent()) ?? "";
  check("runner Python devuelve stdout", stdout.trim().length > 0);
}

// Capítulo 2: laboratorio nuevo y navegación entre capítulos.
await page.goto(`${base}/leccion/byte-pair-encoding`, {
  waitUntil: "networkidle",
});
await page.locator('.lab[data-lab="tokenizer"]').scrollIntoViewIfNeeded();
await page.waitForSelector('.lab[data-lab="tokenizer"].is-ready', {
  timeout: 20000,
});
check("lab tokenizer montado", true);
const tokenizerText = await page
  .locator('.lab[data-lab="tokenizer"]')
  .innerText();
check("lab tokenizer con contenido", /BPE|Tokeniz|token/i.test(tokenizerText));

// Tema: claro por defecto y alternancia manual.
const beforeTheme = await page.evaluate(
  () => document.documentElement.dataset.theme
);
check("tema claro por defecto", beforeTheme === "light");
await page.locator("[data-theme-toggle]").first().click();
const afterTheme = await page.evaluate(
  () => document.documentElement.dataset.theme
);
check("tema cambia", beforeTheme !== afterTheme);

// Quiz de un capítulo nuevo y revisión del capítulo 1.
await page.goto(`${base}/quiz/quiz-capitulo-2`, { waitUntil: "networkidle" });
check(
  "quiz capítulo 2 disponible",
  (await page.locator("h2").first().innerText()).includes("Capítulo 2")
);
await page.goto(`${base}/quiz/quiz-capitulo-1`, { waitUntil: "networkidle" });
await page.locator(".quiz-card input[type=radio]").first().check();
await page.locator('button[type="submit"]').click();
await page.waitForURL(/\/quiz\/intento\/\d+/, { timeout: 15000 });
check("quiz enviado y revisión", /\/quiz\/intento\/\d+/.test(page.url()));

// El anillo debe usar la circunferencia como dasharray, no el tamaño en px.
await page.goto(`${base}/progreso`, { waitUntil: "networkidle" });
const ring = await page.locator(".ring").first().evaluate((element) => {
  const fill = element.querySelector(".ring-fill");
  if (!fill) return null;
  const style = getComputedStyle(fill);
  return {
    dasharray: parseFloat(style.strokeDasharray),
    box: element.getBoundingClientRect().width,
  };
});
check(
  "anillo con geometría correcta",
  Boolean(ring) && Math.abs(ring.dasharray - ring.box) > 10
);

check("sin errores de consola", errors.length === 0);
if (errors.length) console.log(errors);

await browser.close();
if (failures.length) {
  console.error(`\n${failures.length} comprobaciones fallidas:`, failures);
  process.exit(1);
}
console.log("\nE2E correcto.");
