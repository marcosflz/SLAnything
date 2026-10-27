---
type: Playbook
title: Playbook de sesión
description: Procedimiento para arrancar, trabajar y cerrar cualquier sesión de agente en SLAnything sin perder el contexto.
tags: [agentes, contexto, okf, sesion, handoff]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: Instrucciones para agentes
  - id: status
    resource: /project/status.md
    title: Estado actual del proyecto
---

# Arranque

1. Lee [AGENTS.md](../../AGENTS.md), este playbook, [status](/project/status.md) y
   [log](/log.md).
2. Comprueba que el entorno responde:

   ```powershell
   uv sync
   uv run python tools/check_okf.py
   uv run pytest -q
   ```

3. Si vas a usar la web, arranca backend y frontend:

   ```powershell
   # Terminal 1
   uv run python aula.py
   # Terminal 2
   cd frontend
   npm run dev
   ```

   Comprueba `http://127.0.0.1:8000/health` y `http://127.0.0.1:3000/salud`.
   Para el Estudio en local, `opencode --version` debe responder; en Docker ya
   viene incluido y `/estudio` muestra el estado del motor.

4. Abre solo los conceptos relacionados con la tarea. Para contenido, empieza por
   [lecciones](/product/lessons.md); para backend, por
   [backend](/architecture/backend.md); para Next, por
   [nextjs-frontend](/architecture/nextjs-frontend.md); para i18n, por
   [i18n](/architecture/i18n.md).

5. Si cambias Python, routers o plantillas, reinicia el backend. `aula.py` no
   recarga automáticamente; un proceso viejo puede dar errores falsos (por
   ejemplo `'t' is undefined`).

# Durante el trabajo

- El código y los tests son la fuente de verdad. Si el OKF dice algo distinto,
  investiga y corrige el OKF.
- No reescribas el OKF «de memoria»: enlaza al archivo real, a la ruta real y al
  test real.
- Si tomas una decisión nueva, crea un ADR en `/decisions/` y enlázalo desde
  `/decisions/index.md`.
- Si encuentras un bug que no vas a arreglar ahora, anótalo en
  [known-issues](/context/known-issues.md) con síntoma, impacto y workaround.
- Mantén el alcance: el curso de referencia está cerrado y la biblioteca ya es
  multi-curso; el siguiente hito es publicar el segundo libro, calidad,
  accesibilidad y producto.

# Cierre obligatorio

1. Ejecuta `uv run pytest -q`, `uv run python tools/validate_all_chapters.py` y
   `uv run python tools/check_okf.py`.
2. Si tocaste el frontend, ejecuta `npm run typecheck` (y `npm run build` si es un
   cambio de estructura). Si tocaste ambos servidores, ejecuta
   `uv run python tools/smoke_next.py`; para labs o navegación, `npm run e2e`.
3. Actualiza los conceptos afectados según la tabla de `AGENTS.md`.
4. Añade la entrada del día al principio de [log](/log.md).
5. Actualiza [status](/project/status.md) si cambió el estado de entrega, el
   número de tests o el capítulo activo.
6. Deja en [next-steps](/context/next-steps.md) el siguiente paso concreto.

# Handoff en una frase

Si otra sesión empieza mañana, debe poder responder en menos de dos minutos:
qué es SLAnything, qué está hecho, cómo se arranca, qué tests pasan, qué se está
tocando y cuál es el siguiente paso. Si el OKF no permite responder eso, está
incompleto.
