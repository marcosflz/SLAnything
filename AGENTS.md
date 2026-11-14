# AGENTS.md · SLAnything

> Este archivo es el punto de entrada para cualquier agente que trabaje en este
> repositorio. El contexto persistente vive en el bundle **Open Knowledge Format
> (OKF) v0.2** de `okf/`.

## Regla principal

**El agente es el responsable de mantener actualizado el OKF.** No es un extra
opcional ni una tarea que deba pedir el usuario: forma parte de la definición de
terminado de cualquier cambio. Si una sesión modifica el producto, la
arquitectura, las operaciones, el contenido o una decisión, debe actualizar los
conceptos OKF afectados y registrar el cambio en `okf/log.md`.

## Arranque obligatorio de sesión

Antes de explorar código o proponer cambios:

1. Lee [`okf/index.md`](okf/index.md). Es el catálogo del contexto.
2. Lee [`okf/context/session-playbook.md`](okf/context/session-playbook.md) y
   [`okf/project/status.md`](okf/project/status.md).
3. Lee [`okf/log.md`](okf/log.md) para conocer los últimos cambios.
4. Abre solo los conceptos relacionados con la tarea. Empieza por:
   - producto → `okf/product/`
   - arquitectura → `okf/architecture/`
   - ejecución y pruebas → `okf/operations/`
   - decisiones → `okf/decisions/`
   - problemas y siguientes pasos → `okf/context/`
5. Contrasta el OKF con el código y los tests. **Si hay conflicto, mandan el
   código, los tests y la documentación fuente**; corrige el OKF.

No empieces una tarea importante sin haber leído el índice y el estado actual.

## Cuándo actualizar el OKF

Actualiza el OKF en la misma sesión en la que ocurra el cambio. Como mínimo:

| Si cambias… | Actualiza… |
|---|---|
| Una lección, quiz, glosario o figura | `okf/product/lessons.md`, `okf/product/quiz.md` o `okf/product/course.md` |
| Un laboratorio o su contrato | `okf/product/labs.md`, `okf/architecture/frontend.md` |
| Una ruta, modelo de datos o módulo | `okf/architecture/backend.md`, `okf/architecture/data-model.md` |
| Autenticación, sesiones o CSRF | `okf/architecture/security.md` |
| Diseño, plantillas o responsive | `okf/product/ux.md`, `okf/architecture/frontend.md` |
| Frontend Next.js o API JSON | `okf/architecture/nextjs-frontend.md`, `okf/architecture/api.md` |
| Espacios, roles, administración o KPIs | `okf/architecture/tenancy-analytics.md` |
| Generación por etapas | `okf/architecture/generation.md` |
| Estudio de autoría, OpenCode o generación desde documentos | `okf/architecture/authoring.md`, `okf/decisions/adr-012-authoring-opencode.md` |
| Traducciones ES/EN o contenido inglés | `okf/architecture/i18n.md`, `okf/product/lessons.md` |
| Ejecución de Python o sandbox | `okf/architecture/execution.md`, `okf/architecture/security.md` |
| Dependencias, comandos o puertos | `okf/operations/run.md`, `okf/references/commands.md` |
| Tests o cobertura | `okf/operations/testing.md`, `okf/project/status.md` |
| Una decisión técnica relevante | Un ADR nuevo en `okf/decisions/` y su índice |
| Un bug conocido o una limitación | `okf/context/known-issues.md` |
| El siguiente paso o el roadmap | `okf/context/next-steps.md`, `okf/project/roadmap.md` |
| El estado general | `okf/project/status.md` |

Además, **siempre**:

- Añade una entrada con la fecha de hoy al principio de `okf/log.md`, con el
  formato `## YYYY-MM-DD` y viñetas `* **Update**: …`.
- Actualiza `okf/project/status.md` si cambia el estado de entrega, el número de
  tests, el capítulo activo o las limitaciones.
- Ejecuta `uv run python tools/check_okf.py` y deja el validador en verde.
- Si el cambio invalida una captura o un enlace, actualízalo.

## Reglas de formato OKF

- El bundle está en `okf/` y declara `okf_version: "0.2"` en `okf/index.md`.
- Cada concepto es un `.md` con frontmatter YAML parseable y un campo `type` no
  vacío. `title`, `description`, `tags`, `sources`, `generated` y `status` son
  recomendados.
- `generated.by` usa el convenio de actor: `opencode/<modelo>` para agentes,
  `human:<id>` para personas y `process:<id>` para procesos.
- `generated.at` es ISO 8601 con offset UTC, por ejemplo
  `2026-10-24T12:00:00Z`.
- Los enlaces internos del bundle usan rutas absolutas desde la raíz del bundle:
  `/architecture/overview.md`. Los enlaces a documentación externa al bundle
  pueden ser rutas relativas (`../README.md`) o URLs.
- `index.md` no lleva frontmatter, salvo `okf/index.md`, que solo lleva
  `okf_version`.
- `log.md` va del más reciente al más antiguo; las cabeceras de fecha son
  `## YYYY-MM-DD`.
- No guardes secretos, tokens ni datos personales en el OKF. Las credenciales de
  demostración documentadas sí pueden aparecer.
- No dupliques código ni documentación extensa: resume, enlaza a la fuente y
  mantén el concepto actualizado.
- Los conceptos no son inmutables: si una decisión cambia, actualiza el ADR
  existente o crea uno nuevo que lo superseda y enlaza ambos.

## Comandos de referencia

```powershell
uv sync
uv run python aula.py                 # backend FastAPI · http://127.0.0.1:8000
uv run python -m pytest -q           # suite del proyecto (140 tests)
uv run python tools/check_chapter.py ch02   # valida un paquete de capítulo
uv run python tools/validate_all_chapters.py
uv run python tools/check_okf.py     # conformidad y enlaces del OKF

cd frontend
npm install
npm run dev                          # Next.js · http://127.0.0.1:3000
npm run typecheck
npm run build
```

Con ambos servidores arrancados:

```powershell
uv run python tools/smoke_next.py
```

`aula.py` no recarga automáticamente. Si cambias Python o routers, reinicia el
backend antes de probar. Para probar el Estudio sin red usa `AULA_LLM_FAKE=1`.

Cuentas de demostración: `demo@aulallm.local / demo1234` y
`profe@aulallm.local / profe1234`.

## Cierre de sesión

Antes de responder que el trabajo está terminado:

1. ¿El código y los tests pasan?
2. ¿El OKF refleja lo que acabas de cambiar?
3. ¿`okf/log.md` tiene la entrada de hoy?
4. ¿`uv run python tools/check_okf.py` termina sin errores?
5. ¿Quedan limitaciones o siguientes pasos anotados en
   `okf/context/known-issues.md` o `okf/context/next-steps.md`?

Si la respuesta a 2, 3 o 4 es no, el trabajo **no** está terminado.

## Contexto de producto en una frase

SLAnything es una plataforma web **bilingüe (ES/EN)**, tipo aula virtual, con un
catálogo de cursos y un **Estudio de autoría** que convierte documentos en
unidades didácticas con OpenCode. El curso publicado convierte los 7 capítulos de
*Build a Large Language Model (From Scratch)* en 56 lecciones, 15 laboratorios
interactivos, 26 ejemplos de Python ejecutables, 7 quizzes de 10 preguntas y un
panel de progreso. Es SaaS multi-organización (espacios personales y academias
con roles, grupos e invitaciones) con paneles de KPIs. La única interfaz es
**Next.js 16 + React 19** (Tailwind v4); el backend es **FastAPI + SQLite** y
solo expone API. Los identificadores internos `aula_*` se mantienen por
compatibilidad.

## Arquitectura en una mirada

- **Next.js (`frontend/`, puerto 3000)** es la única interfaz. Primitivas en
  `src/components/ui/`, gráficos en `src/components/charts/`, shell en
  `src/components/shell/`. `app.css` es estilo heredado en la capa `legacy`.
- **API JSON (`/api/v1`)** es la frontera; FastAPI no sirve HTML.
- **Contenido** vive en `webapp/content/`, en módulos ES y EN.
- **Espacios, roles y administración**: `webapp/workspaces.py`,
  `webapp/deps.py` (`require_role`), `webapp/routers/admin.py`.
- **Analítica**: `webapp/analytics.py` y `webapp/routers/analytics.py`.
- **Generación por etapas**: `webapp/generation/` (motor `direct`); el motor
  OpenCode sigue en `webapp/authoring/` y su agente en
  `webapp/authoring/agent/AGENTS.md`.
- **Esquema**: cambios nuevos solo como migración en `webapp/migrations.py`.
- **Ejecución Python** vive en `webapp/execution.py` + `sandbox_runner.py`.

Si cambias una lección o un lab, revisa el contenido en los dos idiomas.
