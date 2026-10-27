# Contrato de implementación · agent swarm

> Antes de trabajar, lee [`AGENTS.md`](../AGENTS.md) y el bundle
> [`okf/index.md`](../okf/index.md). El OKF es la memoria persistente y debe
> actualizarse al terminar cualquier cambio.

Este documento congela las interfaces que comparten los agentes. **No cambiar los
nombres de archivos, rutas, helpers ni claves de contexto sin avisar al lead.**

## 1. Propiedad de archivos

| Agente | Puede escribir en |
|---|---|
| Lead | `webapp/config.py`, `db.py`, `security.py`, `deps.py`, `repositories.py`, `main.py`, `templating.py`, `labs.py`, `content/schema.py`, `content/course.py`, `content/__init__.py`, `templates/base.html`, `templates/components/*`, `static/css/*`, `static/js/app.js`, `docs/*`, `README.md` |
| Backend | `webapp/routers/*.py` |
| Contenido A | `webapp/content/lessons/l02_pretraining.py`, `l03_transformer.py`, `l04_escala.py` |
| Contenido B | `webapp/content/lessons/l05_siguiente_palabra.py`, `l06_prompting.py`, `l07_construccion.py`, `l08_repaso.py`, `webapp/content/quizzes.py`, `webapp/content/glossary.py` |
| Labs A | `webapp/static/js/labs/ngram.js`, `memory.js`, `cost.js` |
| Labs B | `webapp/static/js/labs/labels.js`, `transformer.js`, `attention.js`, `prompt.js` |
| QA | `webapp/tests/*`, `docs/QA.md` |

Nadie toca archivos de otro agente. Si falta una interfaz, se pide al lead.

## 2. Contenido

Cada lección exporta `LESSON` usando `webapp.content.schema`:

```python
from webapp.content.schema import (
    Lesson, bullets, callout, check, code, figure, h2, h3, keypoints,
    lab, lead, p, quote, table,
)

LESSON = Lesson(
    number=2,
    slug="pretraining-y-finetuning",
    title="Las dos etapas",
    summary="Una frase de 15-30 palabras.",
    minutes=10,
    objectives=("...", "...", "..."),
    blocks=(lead("..."), h2("..."), p("..."), ...),
    key_points=("...", "...", "..."),
    quiz_id=None,
)
```

Reglas:

- Español de España, tono cercano y riguroso.
- 700-1200 palabras de contenido por lección, 6-25 bloques.
- Empezar con `lead(...)`, incluir al menos un `callout(...)`, un `check(...)` y
  terminar con `keypoints([...])`.
- Las figuras usan rutas relativas a `webapp/static/`:
  `img/ch01/fig_1_3_pretraining_finetuning.png`.
- Los laboratorios solo pueden ser: `memory`, `labels`, `transformer`, `attention`,
  `ngram`, `prompt`, `cost`.
- No usar HTML con `<script>`, `<style>` ni clases inventadas.
- No inventar cifras: las del libro y las del cuaderno son la fuente.
- `code(...)` recibe código Python real y ejecutable en el contexto del libro.

## 3. Rutas y contextos

Todas las plantillas reciben automáticamente: `request`, `user`, `course`,
`current_path`, `query`, `ok_message`, `error_message`, `site_name`, `lab_meta`.

| Ruta | Plantilla | Contexto adicional |
|---|---|---|
| `GET /` (sin sesión) | `pages/landing.html` | `total_minutes` |
| `GET /` (con sesión) | `pages/dashboard.html` | `stats`, `next_lesson`, `next_progress`, `avg_score`, `streak`, `activity`, `attempts`, `sidebar_progress` |
| `GET /curso` | `pages/course.html` | `stats`, `progress`, `next_lesson`, `sidebar_progress` |
| `GET /leccion/{slug}` | `pages/lesson.html` | `lesson`, `progress`, `note`, `bookmarked`, `prev_lesson`, `next_lesson`, `quiz`, `best_attempt`, `sidebar_progress` |
| `GET /quiz/{quiz_id}` | `pages/quiz.html` | `quiz`, `attempts`, `best_attempt`, `sidebar_progress` |
| `GET /quiz/intento/{id}` | `pages/quiz_result.html` | `quiz`, `attempt`, `review`, `sidebar_progress` |
| `GET /progreso` | `pages/progress.html` | `stats`, `progress_rows`, `attempts`, `activity`, `avg_score`, `streak`, `sidebar_progress` |
| `GET /glosario` | `pages/glossary.html` | `groups` (lista de `(letra, [terms])`), `sidebar_progress` |
| `GET /recursos` | `pages/resources.html` | `resources`, `sidebar_progress` |
| `GET /buscar` | `pages/search.html` | `results`, `sidebar_progress` |
| `GET /profesor` | `pages/teacher.html` | `students`, `stats`, `sidebar_progress` |
| `GET /entrar` | `pages/auth_login.html` | `next`, `error` |
| `GET /registro` | `pages/auth_register.html` | `next`, `error`, `values` |
| errores | `pages/error.html` | `code`, `title`, `message` |

Formularios y CSRF:

- Todos los POST llevan `csrf_token` oculto, salvo login/registro (no hay sesión).
- `ensure_csrf(request, user, form_token)` valida.
- Los formularios de completar, nota, marcador y quiz redirigen con
  `?ok=Mensaje` o `?error=Mensaje`.
- El quiz usa nombres `q_<question.id>` con el índice de la opción elegida.

## 4. Contrato de laboratorios

Cada módulo en `static/js/labs/` exporta:

```js
export default {
  id: "memory",
  mount(root) {
    const body = root.querySelector("[data-lab-body]");
    // construir UI y cablear eventos
    return () => { /* limpieza opcional */ };
  }
};
```

- `root` es `<section class="lab" data-lab="...">`.
- `body` existe y está vacío.
- Sin librerías externas ni `innerHTML` con datos de usuario sin escapar.
- Usar clases CSS existentes. Para helpers: `import { h, fmt, pct, clamp, tokenize } from "./common.js";`
- No cargar recursos de red salvo `/static/data/quijote_fragmento.txt`.
- Cada control debe producir un cambio visible inmediato.

## 5. Clases CSS disponibles

Layout: `lab`, `lab-head`, `lab-body`, `lab-grid`, `lab-controls`, `lab-output`,
`lab-stat-row`, `lab-stat`, `field`, `segmented`, `bar-list`, `bar-row`, `bar-track`,
`token-row`, `token-chip`, `output-text`, `prompt-box`, `heatmap-wrap`, `heatmap`,
`heatmap-cell`, `heatmap-label`, `pipeline`, `pipeline-step`, `step-detail`.

Estados: `is-active`, `is-done`, `is-selected`, `is-correct`, `is-wrong`, `is-masked`,
`is-target`, `is-next`, `has-activity`.

Utilidades: `btn btn-primary btn-secondary btn-ghost btn-sm`, `badge`, `card`,
`card-pad`, `muted`, `small`, `row`, `stack`, `mt-2`, `mt-3`, `mt-4`, `sr-only`.

## 6. Verificación mínima por agente

```powershell
# Contenido
uv run python -c "from webapp.content.lessons import l02_pretraining; print(l02_pretraining.LESSON.title)"

# Backend
uv run python -c "import webapp.main; print('ok')"

# Labs (sintaxis)
node --check webapp/static/js/labs/memory.js
```

El lead ejecutará además `uv run pytest` y la revisión visual.
