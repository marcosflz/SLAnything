import { chromium } from "playwright";

const base = "http://127.0.0.1:3000";

// Una lección representativa por laboratorio. Cubre los 15 IDs del curso.
const checks = [
  ["que-es-un-llm", "memory"],
  ["pares-entrada-objetivo", "labels"],
  ["atencion-en-gpt", "transformer"],
  ["self-attention", "attention"],
  ["predecir-la-siguiente-palabra", "ngram"],
  ["zero-shot-y-few-shot", "prompt"],
  ["escala-y-coste", "cost"],
  ["byte-pair-encoding", "tokenizer"],
  ["ventana-deslizante", "window"],
  ["embeddings-y-significado", "embedding"],
  ["consultas-claves-valores", "qkv"],
  ["bloque-transformer", "gpt-block"],
  ["entropia-cruzada", "loss"],
  ["cabeza-clasificacion", "classifier"],
  ["plantillas-chat", "chat-template"],
];

const failures = [];
const errors = [];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
page.on("console", (message) => {
  if (message.type() === "error") errors.push(message.text());
});
page.on("pageerror", (error) => errors.push(String(error)));

await page.goto(`${base}/entrar`, { waitUntil: "networkidle" });
await page.fill("#email", "demo@aulallm.local");
await page.fill("#password", "demo1234");
await Promise.all([
  page.waitForURL(`${base}/`, { timeout: 15000 }),
  page.locator('button[type="submit"]').click(),
]);

for (const [slug, lab] of checks) {
  try {
    await page.goto(`${base}/leccion/${slug}`, { waitUntil: "networkidle" });
    await page.locator(`.lab[data-lab="${lab}"]`).scrollIntoViewIfNeeded();
    await page.waitForSelector(`.lab[data-lab="${lab}"].is-ready`, {
      timeout: 20000,
    });
    console.log(`ok · ${slug} · ${lab}`);
  } catch (error) {
    console.log(`FALLA · ${slug} · ${lab}: ${error.message}`);
    failures.push(`${slug}/${lab}`);
  }
}

console.log(`errores de consola: ${errors.length}`);
if (errors.length) console.log(errors.slice(0, 10));
await browser.close();

if (failures.length || errors.length) {
  console.error(`\nFallos: ${failures.join(", ")}`);
  process.exit(1);
}
console.log("\nLos 15 laboratorios montan correctamente.");
