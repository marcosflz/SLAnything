---
type: Decision
title: ADR-004 · Laboratorios en JavaScript vanilla
description: Reimplementar los labs interactivos como módulos ES sin React ni bundler.
tags: [adr, javascript, labs, interactividad, frontend]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: appjs
    resource: ../../webapp/static/js/app.js
    title: Carga de labs
  - id: common
    resource: ../../webapp/static/js/labs/common.js
    title: Utilidades
---

# Contexto

Los cuadernos usan `ipywidgets`; en web hacía falta interacción real (n-gramas,
atención, prompts, memoria) sin introducir un framework ni un build.

# Decisión

Módulos ES en `static/js/labs/`, cargados bajo demanda con `IntersectionObserver`
e `import()`. Contrato `export default { id, mount(root) }`. Helpers compartidos en
`common.js`.

# Consecuencias

- Cero dependencias JS y cero bundler.
- Cada lab es un archivo aislado y fácil de revisar.
- La carga diferida mantiene rápida la lección.
- No hay estado reactivo global; cada lab gestiona su DOM.
- Duplicación moderada de utilidades de UI.

# Alternativas descartadas

- React/Vue: más estructura, pero build y peso para 7 widgets.
- Pyodide: fiel al cuaderno, pero muy pesado y complejo para el MVP.
