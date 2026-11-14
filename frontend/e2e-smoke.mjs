// E2E de navegador por perfiles (ADR-020/021).
//
//   npm run e2e                                  # contra http://127.0.0.1:3000
//   E2E_BASE=http://127.0.0.1:3200 npm run e2e   # otra URL
//
// Requiere la siembra demo (AULA_SEED_DEMO=1). Si los cursos de ejemplo están
// activos (AULA_SAMPLE_COURSES=1) también recorre una lección, un laboratorio,
// el runner de Python y un quiz.
import { chromium } from "playwright";

const base = process.env.E2E_BASE ?? "http://127.0.0.1:3000";
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined;
const errors = [];
const failures = [];

function check(name, condition) {
  console.log(`${condition ? "ok" : "FALLA"} · ${name}`);
  if (!condition) failures.push(name);
}

const health = await fetch(`${base}/salud`).then((response) => response.json());
const samples = Boolean(health.ejemplos);
console.log(`cursos de ejemplo: ${samples ? "activos" : "desactivados"}`);

const browser = await chromium.launch({ executablePath });

async function newPage(viewport = { width: 1280, height: 900 }) {
  const page = await browser.newPage({ viewport });
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`${page.url()} ${message.text()}`);
  });
  page.on("pageerror", (error) => errors.push(`${page.url()} ${error}`));
  page.on("dialog", (dialog) => dialog.accept());
  return page;
}

async function login(page, email, password) {
  await page.goto(`${base}/entrar`, { waitUntil: "networkidle" });
  await page.fill("#email", email);
  await page.fill("#password", password);
  await Promise.all([
    page.waitForURL(`${base}/`, { timeout: 15000 }),
    page.locator('button[type="submit"]').click(),
  ]);
  await page.waitForLoadState("networkidle");
}

const navLinks = (page) =>
  page.locator('nav[aria-label="Navegación principal"] a').evaluateAll((links) => links.map((link) => link.getAttribute("href")));
const noOverflow = (page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);

// Portada pública genérica e idioma.
let page = await newPage();
await page.goto(base, { waitUntil: "networkidle" });
// La cabecera y las secciones fijas no mencionan ninguna materia concreta. Con
// AULA_SAMPLE_COURSES=1 el curso de ejemplo puede aparecer en «Biblioteca abierta».
const hero = await page.locator(".hero").innerText();
const howTo = await page.locator("#como-funciona").innerText();
check("portada genérica", hero.includes("Convierte cualquier material") && !/LLM|ChatGPT|GPT/.test(hero + howTo));
await page.locator(".lang-switch a", { hasText: "EN" }).first().click();
await page.waitForLoadState("networkidle");
check("portada → EN", (await page.evaluate(() => document.documentElement.lang)) === "en");
await page.locator(".lang-switch a", { hasText: "ES" }).first().click();
await page.waitForLoadState("networkidle");
check("portada → ES", (await page.evaluate(() => document.documentElement.lang)) === "es");

// Alta de cuenta individual por la interfaz.
await page.goto(`${base}/registro`, { waitUntil: "networkidle" });
await page.fill("#name", "Prueba E2E");
await page.fill("#email", `e2e-${Date.now()}@example.com`);
await page.fill("#password", "clave-segura-123");
await page.fill("#password2", "clave-segura-123");
await Promise.all([
  page.waitForURL(`${base}/`, { timeout: 15000 }),
  page.locator('button[type="submit"]').click(),
]);
await page.waitForLoadState("networkidle");
let links = await navLinks(page);
check("cuenta individual ve el Estudio", links.includes("/estudio"));
check("cuenta individual sin gestión de aula", !links.includes("/admin") && !links.includes("/analitica"));

// Tema claro por defecto y alternancia.
const beforeTheme = await page.evaluate(() => document.documentElement.dataset.theme);
check("tema claro por defecto", beforeTheme === "light");
await page.locator("[data-theme-toggle]").first().click();
check("tema cambia", (await page.evaluate(() => document.documentElement.dataset.theme)) !== beforeTheme);
await page.close();

// Alumno: solo consume.
page = await newPage();
await login(page, "alumno@slanything.local", "alumno1234");
links = await navLinks(page);
check("alumno sin Estudio en el menú", !links.includes("/estudio"));
await page.goto(`${base}/estudio`, { waitUntil: "networkidle" });
check("alumno: Estudio restringido", (await page.locator("main").innerText()).includes("Acceso restringido"));

if (samples) {
  await page.goto(`${base}/cursos/llm-desde-cero`, { waitUntil: "networkidle" });
  check("curso de ejemplo: 7 capítulos", (await page.locator(".chapter-section").count()) === 7);
  await page.goto(`${base}/leccion/que-es-un-llm`, { waitUntil: "networkidle" });
  await page.locator('.lab[data-lab="memory"]').scrollIntoViewIfNeeded();
  await page.waitForSelector('.lab[data-lab="memory"].is-ready', { timeout: 20000 });
  check("lab memory montado", true);
  const run = page.locator("[data-py-run]").first();
  if (await run.count()) {
    await run.click();
    await page.waitForSelector("[data-py-output]:not([hidden])", { timeout: 30000 });
    const stdout = (await page.locator("[data-py-stdout]").first().textContent()) ?? "";
    check("runner Python devuelve stdout", stdout.trim().length > 0);
  }
  await page.goto(`${base}/quiz/quiz-capitulo-1`, { waitUntil: "networkidle" });
  await page.locator(".quiz-card input[type=radio]").first().check();
  await page.locator('button[type="submit"]').click();
  await page.waitForURL(/\/quiz\/intento\/\d+/, { timeout: 15000 });
  check("quiz enviado y revisión", /\/quiz\/intento\/\d+/.test(page.url()));
}
await page.close();

// Profesora y propietaria de la academia.
page = await newPage();
await login(page, "profe@slanything.local", "profe1234");
links = await navLinks(page);
check("academia: Estudio, analítica y administración", ["/estudio", "/analitica", "/profesor", "/admin"].every((href) => links.includes(href)));
check("academia: sin plataforma", !links.includes("/plataforma"));
await page.goto(`${base}/admin/grupos`, { waitUntil: "networkidle" });
const active = await page.locator('nav[aria-label="Navegación principal"] a[aria-current="page"]').evaluateAll((items) => items.map((item) => item.getAttribute("href")));
check("menú marca solo la sección activa", active.length === 1 && active[0] === "/admin/grupos");
await page.close();

// Superadministración.
page = await newPage();
await login(page, "admin@slanything.local", "admin1234");
await page.goto(`${base}/plataforma/usuarios`, { waitUntil: "networkidle" });
check("plataforma: lista de usuarios", (await page.locator("table tbody tr").count()) >= 4);
await page.close();

// Móvil: sin desbordamiento horizontal.
page = await newPage({ width: 360, height: 780 });
for (const path of ["/", "/registro", "/entrar", "/cursos"]) {
  await page.goto(`${base}${path}`, { waitUntil: "networkidle" });
  check(`360 px sin desbordar ${path}`, await noOverflow(page));
}
await login(page, "alumno@slanything.local", "alumno1234");
check("360 px sin desbordar inicio del alumno", await noOverflow(page));
await page.close();

check("sin errores de consola", errors.length === 0);
if (errors.length) console.log(errors);

await browser.close();
if (failures.length) {
  console.error(`\n${failures.length} comprobaciones fallidas:`, failures);
  process.exit(1);
}
console.log("\nE2E correcto.");
