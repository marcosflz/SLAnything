---
type: Test Plan
title: Pruebas de SLAnything
description: Suite pytest de 111 tests, cobertura por área y comprobaciones manuales.
tags: [testing, pytest, qa, cobertura]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: qa
    resource: ../../docs/QA.md
    title: Informe de QA
  - id: tests
    resource: ../../webapp/tests/
    title: Suite de tests
---

# Comando

```powershell
uv run pytest -q
```

Resultado verificado: **111 passed**. El único warning es la deprecación de
`starlette.testclient` con `httpx`.

Validación específica de contenido multi-capítulo:

```powershell
uv run python tools/check_chapter.py ch02   # y ch03…ch07
uv run python tools/validate_all_chapters.py
```

# Aislamiento

- `db_path` monkeypatchea `webapp.config.DB_PATH` a una SQLite temporal.
- `TestClient` se usa como context manager para ejecutar el lifespan.
- `login_limiter` y el rate limit de ejecución se limpian antes/después de cada test.
- Sin red ni servicios externos. Los tests de ejecución usan el runner real, pero
  sin llamadas de red; el de timeout reduce `execution.settings` a 1 s.
- Los tests del Estudio usan una SQLite y un `AUTHORING_DIR` temporales. El
  runner real se prueba con `_run_opencode` simulado; además se hizo una prueba
  manual en Docker con el modelo gratuito de OpenCode que generó, validó y
  publicó una unidad de 4 lecciones.

# Cobertura

| Área | Tests |
|---|---|
| Contenido, figuras, quiz, glosario, programa y catálogo | 13 |
| Público, estáticos y cabeceras | 7 |
| Auth, registro, logout, rate limit, next | 16 |
| Lecciones, progreso, notas, CSRF | 12 |
| Quiz, privacidad y revisión | 5 |
| Flujo completo | 1 |
| Profesor | 3 |
| Buscador, glosario, recursos | 4 |
| Errores 404 | 4 |
| Seguridad (scrypt, tokens, CSRF, limiter) | 4 |
| Ejecución Python, descargas y sandbox | 9 |
| Idiomas y contenido inglés | 6 |
| API JSON para Next.js | 11 |
| Estudio de autoría, contrato, saneado, reparación y publicación | 16 |

# Frontend

```powershell
cd frontend
npm run typecheck
npm run build
```

Con los dos servidores arrancados, `uv run python tools/smoke_next.py` comprueba
las rutas principales, el login a través del rewrite, el cambio de idioma y el
panel del profesor.

Smoke E2E de navegador (Chromium):

```powershell
cd frontend
npx playwright install chromium
npm run e2e
npm run e2e:labs
```

`e2e:labs` recorre una lección representativa de cada uno de los 15
laboratorios, espera a que el módulo monte y falla si hay errores de consola.

Cubre login, catálogo y detalle de curso, 7 capítulos en el programa y la sidebar,
apertura del capítulo 2 y sus lecciones, montaje de `memory` y `tokenizer`,
ejecución de un ejemplo Python, tema claro por defecto y alternancia, selector
ES/EN en ambos sentidos, colapso y persistencia de la sidebar, geometría del anillo
de progreso, quiz del capítulo 2, envío/revisión del quiz del capítulo 1 y errores
de consola. Son 27 comprobaciones; sigue siendo un smoke, no una suite E2E
completa.

# Manual

- Los 15 labs montan sin errores de consola en Chrome headless
  (`npm run e2e:labs`).
- `tokenizer` se comprueba además en Jinja con Playwright.
- La interacción profunda de cada lab se validó con `node --check`, DOM simulado
  y pruebas de sus agentes; el E2E cubre montaje, no cada control.
- Responsive a 360, 768 y 1440 px; sin overflow horizontal.
- Tema claro por defecto, oscuro opcional y persistencia.
- Lightbox de figuras.
- Capturas en `docs/capturas/`.

# Añadir tests

- Usa las fixtures de `webapp/tests/conftest.py`.
- No toques la BD real.
- Para CSRF, extrae el token del HTML con el helper `csrf_from`.
- Si añades una ruta o contenido, amplía la suite y actualiza
  [testing](/operations/testing.md) y [status](/project/status.md).
