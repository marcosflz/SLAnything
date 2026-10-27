# Historial de cambios del OKF

## 2026-10-27

* **Update**: Primera publicación del repositorio en `origin`: 494 archivos versionados en un commit inicial sobre `main`, que queda configurada como rama de seguimiento. Antes de publicar se auditó el árbol en busca de credenciales y de artefactos locales (claves `sk-*`, tokens de GitHub/AWS/Google, bloques de clave privada, `.env`, `aula.db`, `.venv/`, `frontend/node_modules/` y `frontend/.next/`): sin hallazgos, solo placeholders en `.env.example` y en el secreto de desarrollo de `compose.yaml`.
* **Update**: La suite se ejecutó antes del commit con `uv run python -m pytest -q`: 111 tests en verde.
* **Update**: El README estrena portada (`docs/capturas/00b_landing_programa.png`) y una galería agrupada por área con las 21 capturas de `docs/capturas/`: portada, catálogo, dashboard, lección, progreso, profesorado, quiz, glosario, recursos, acceso, seis laboratorios, móvil y tema oscuro. `docs/capturas/README.md` pasa a titularse «Capturas de SLAnything» y `okf/product/ux.md` documenta qué imagen hace de portada.

## 2026-10-24

* **Update**: Se añadió el **Estudio de autoría** (`/estudio`, solo profesorado): subida de PDF, DOCX, EPUB, ODT, Markdown, HTML o TXT; extracción y troceado; generación con OpenCode; paquete JSON bilingüe validado y saneado; borrador, publicación, despublicación y borrado. Una reparación automática corrige el primer paquete rechazado.
* **Update**: OpenCode portable (`v2.1.4`) se instala en la imagen Docker del backend y se configura por trabajo con `--standalone`, `HOME` aislado y permisos que deniegan shell, web, subagentes y directorios externos. La API key vive en `authoring/settings.json` (0600) y nunca se devuelve al navegador.
* **Update**: Se añadieron proveedores configurables desde la web: OpenCode Go, modelos gratuitos de OpenCode, OpenAI, Anthropic, OpenRouter, Gemini, DeepSeek, Ollama, LM Studio y endpoints OpenAI-compatible.
* **Update**: El catálogo dinámico integra `generated_courses` en `content_for`, con slugs `gen-*`, caché invalidada al publicar y soporte en catálogo, curso, lección, quiz, glosario, búsqueda y profesor. SQLite pasa al esquema v3 con `authoring_jobs` y `generated_courses`.
* **Update**: Se añadió el contrato `course.json`, el saneado HTML con lista blanca, la validación de slugs/quiz/glosario y la compilación de bloques Python antes de guardar.
* **Update**: Se añadió `/estudio` en Next y Jinja, panel de trabajos con log y polling, formulario de subida y publicación, estilos compartidos y traducciones ES/EN.
* **Update**: La web es instalable como PWA con manifiesto, icono y service worker de estáticos; se documentó la decisión web + PWA y la ruta a Tauri en `docs/DESKTOP.md` y ADR-012.
* **Update**: Se añadieron 16 tests del Estudio (contrato, saneado, tonos, extracción, ajustes, API, permisos, publicación, reparación y runner simulado), hasta 111 tests. Se validó manualmente en Docker con el modelo gratuito de OpenCode: 4 lecciones generadas, validadas y publicadas.
* **Update**: El producto visible pasa a llamarse **SLAnything** en configuración, metadatos, cabeceras y documentación; los identificadores internos `aula_*`, `aula.db` y el volumen `aula-llm-data` se mantienen por compatibilidad.
* **Update**: Se actualizó el remoto `origin` de `LLMScratch` a `SLAnything` (`https://github.com/marcosflz/SLAnything.git`) y se documentó el repositorio canónico en el mapa y el estado. El remoto de GitHub es privado y todavía está vacío; la copia local no tiene commits.
* **Update**: Se simplificó la sidebar: se retiraron «Cambiar de curso» y «Curso actual» para evitar duplicidades. El cambio de curso se hace desde el enlace genérico «Cursos»; la tarjeta superior solo muestra el contexto del curso activo y las lecciones quedan debajo.
* **Update**: Se rediseñó la portada como biblioteca de cursos: landing de plataforma, catálogo `/cursos`, detalle `/cursos/{slug}`, sidebar con curso activo y dashboard «Tus cursos». Se actualizaron Next, Jinja, README y estilos compartidos.
* **Update**: Se completaron los capítulos 2-7 con 48 lecciones nuevas (8 por capítulo), en español e inglés, hasta un total de 7 capítulos, 56 lecciones y 584 minutos.
* **Update**: Se introdujo `Program` y el modelo multi-capítulo: paquetes autocontenidos en `webapp/content/chapters/chNN/`, slugs globales, `COURSES` como programa completo y `validate_program()`.
* **Update**: La API `/api/v1` devuelve el programa con `chapters`, `chapter_count`, `lab_count` y lecciones aplanadas; lección y quiz incluyen su capítulo y la navegación cruza capítulos.
* **Update**: Next y Jinja muestran el programa agrupado por capítulos, sidebar con capítulos colapsables y progreso global de 56 lecciones.
* **Update**: Se añadieron 8 laboratorios (`tokenizer`, `window`, `embedding`, `qkv`, `gpt-block`, `loss`, `classifier`, `chat-template`) hasta un total de 15, con metadatos por capítulo y diccionario bilingüe local.
* **Update**: Se añadieron 7 quizzes de 10 preguntas, un glosario global de 113 términos y 26 ejemplos Python ejecutables.
* **Update**: El tema claro pasa a ser el predeterminado; el oscuro solo se aplica si el usuario lo guarda en `localStorage`.
* **Update**: Se añadió el catálogo multi-curso: `Course`/`Book`/`CATALOGS`, `/cursos`, `/cursos/{slug}`, curso activo en la sidebar, API `/api/v1/catalog` y `/api/v1/courses/{slug}`, y progreso aislado por `course_slug`.
* **Update**: Se migró SQLite al esquema v2 (`course_slug` en progreso, notas, marcadores e intentos) conservando los datos v1 en el curso `llm-desde-cero`.
* **Update**: Se añadieron 7 tests de catálogo y progreso por curso; la suite pasa a 95 tests y el E2E cubre catálogo, detalle de curso, sidebar limpia y apertura de capítulos.
* **Update**: Se añadieron `tools/check_chapter.py` y `tools/validate_all_chapters.py`; el E2E de Playwright cubre 7 capítulos, `tokenizer`, tema claro, quiz del capítulo 2 y revisión.
* **Update**: Se añadió `frontend/e2e-labs.mjs` (`npm run e2e:labs`), que comprueba el montaje de los 15 laboratorios sin errores de consola; también pasó la pasada equivalente en Jinja.
* **Update**: Se actualizaron README, OKF, ADR-010, roadmap, backlog, problemas conocidos y comandos para reflejar el curso completo.
* **Update**: Se migró la interfaz a Next.js 16 + React 19 + TypeScript en `frontend/`, con App Router, Server Components y controles cliente.
* **Update**: Se añadió la API JSON `/api/v1` (`webapp/routers/api.py`) para sesión, curso, lecciones, quiz, progreso, glosario, recursos, búsqueda, profesorado y descargas; 8 tests nuevos (85 en total).
* **Update**: Se configuraron rewrites de Next a FastAPI para `/api/v1/*`, `/api/ejecutar` y `/static/*`, manteniendo cookie HttpOnly y CSRF sin CORS.
* **Update**: Se portaron las 14 páginas, el shell, los bloques de lección, el runner Python, los 7 laboratorios, el quiz y el/i18n; `app.css` se sincroniza desde el diseño existente.
* **Update**: Se añadieron `tools/export_messages.py`, `tools/sync_frontend_assets.py`, `tools/smoke_next.py`, ADR-008 y el plan `docs/MIGRATION_NEXTJS.md`.
* **Update**: Se crearon los conceptos `architecture/nextjs-frontend.md`, `architecture/api.md`, `architecture/i18n.md`, `architecture/execution.md` y `operations/frontend.md`, y se enlazaron desde los índices.
* **Update**: Se verificaron `npm run build`, `npm run typecheck`, el smoke test con ambos servidores y el flujo completo de registro, lección, nota, marcador, quiz y revisión a través de Next.
* **Update**: Se añadió `frontend/src/proxy.ts` para mantener `?lang=es|en` compatible con la etapa Jinja y se corrigió el cambio de idioma para conservar el origen y la cookie `aula_lang`.
* **Update**: Se añadió un smoke E2E con Playwright (`frontend/e2e-smoke.mjs`, `npm run e2e`) que verifica login, lab, ejecución Python, tema, cambio ES/EN, sidebar colapsable, anillo y quiz sin errores de consola.
* **Fix**: El selector ES/EN usa navegación completa (`<a>`) para invalidar la caché de RSC de Next; antes el botón podía dejar la página en el idioma anterior.
* **Fix**: La barra lateral de escritorio ahora se puede colapsar, con estado persistido en `localStorage` y sin afectar al drawer móvil.
* **Fix**: El anillo de progreso usaba el tamaño en píxeles como `stroke-dasharray`; ahora usa la circunferencia real, por lo que a 0 % no dibuja arcos sueltos.
* **Update**: Se dockerizó el proyecto con `Dockerfile` para FastAPI, `frontend/Dockerfile` para Next.js standalone, `compose.yaml` y `.env.example`.
* **Update**: Se añadieron healthchecks, usuario no root, rewrites a `http://backend:8000`, volumen `aula-llm-data` para SQLite y la guía `docs/DOCKER.md`.
* **Update**: Se validó Compose (Linux containers): build de ambas imágenes, `/salud`, login, quiz, runner Python, descargas, E2E Playwright y persistencia de `aula.db` al recrear el backend.
* **Update**: Las rutas Jinja quedan como fallback en el puerto 8000 hasta cerrar la paridad; ADR-001 queda deprecado por ADR-008.
* **Update**: Se añadieron 7 ejemplos de Python ejecutables en las lecciones, con editor, salida de stdout, tablas e imágenes, y descarga `.py` por bloque y por lección.
* **Update**: Se implementó `webapp/sandbox_runner.py` y `webapp/execution.py`: subproceso `python -I`, validación AST, hook de auditoría, límites de tiempo/memoria/salida, rate limit y concurrencia acotada.
* **Update**: Se añadió el endpoint `POST /api/ejecutar` con sesión, CSRF y errores JSON.
* **Update**: Se tradujo el curso completo al inglés: 8 lecciones, 39 términos de glosario, quiz de 10 preguntas e interfaz.
* **Update**: Se añadió el selector ES/EN con cookie `aula_lang`, `?lang=` y la ruta `/idioma/{lang}`.
* **Update**: Se añadieron ADR-006 (ejecución en servidor) y ADR-007 (contenido bilingüe), y se actualizaron estado, seguridad, frontend, backend, pruebas y runbooks.
* **Creation**: Se creó el bundle OKF v0.2 en `okf/` como memoria persistente del proyecto.
* **Creation**: Se añadieron los conceptos de contexto, proyecto, producto, arquitectura, operaciones, decisiones y referencias.
* **Creation**: Se añadió `AGENTS.md` con el arranque obligatorio de sesión y la obligación de mantener el OKF actualizado.
* **Creation**: Se añadió `tools/check_okf.py` para validar frontmatter, enlaces, índices y `log.md`.
* **Update**: Se documentó el estado entregado del capítulo 1: 8 lecciones, 7 laboratorios, quiz de 10 preguntas, 85 tests y dos servidores locales (Next 3000 y FastAPI 8000).
* **Fix**: Se reinició el backend tras la migración de i18n; el error 500 `'t' is undefined` de `/api/v1/shell`, `/api/v1/session` y `/api/v1/public` era un proceso Uvicorn obsoleto, no un fallo de código. Las rutas responden 200/401 correctamente tras el reinicio.
* **Update**: Se fijó el frontend Next.js en `127.0.0.1` para que la URL documentada y `tools/smoke_next.py` funcionen igual en Windows.
