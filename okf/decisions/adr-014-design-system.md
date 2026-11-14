---
type: ADR
title: ADR-014 · Sistema de diseño Tailwind + componentes estilo shadcn
description: Tailwind v4 con componentes propios sobre Radix, Recharts, cmdk y lucide; el CSS heredado vive en una capa legacy.
tags: [adr, ux, tailwind, radix, recharts]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: globals
    resource: ../../frontend/src/app/globals.css
    title: Tokens y capas
  - id: ui
    resource: ../../frontend/src/components/ui
    title: Primitivas
---

# Contexto

El objetivo de producto es un «Moodle moderno» minimalista con paneles de KPIs.
El frontend solo tenía un `app.css` global de 1 471 líneas y seis primitivas, sin
gráficos ni estados de carga.

# Decisión

- **Tailwind CSS v4** (`@tailwindcss/postcss`) con tokens expuestos mediante
  `@theme inline` a partir de las variables de `app.css`: un único origen de
  color para lo nuevo y lo heredado, claro/oscuro con `data-theme`.
- Capas: `@layer theme, base, legacy, components, utilities`. `app.css` se
  importa en `legacy`, así gana a la base de Tailwind pero las utilidades
  siempre le ganan. La migración es por pantallas.
- Componentes propios al estilo shadcn/ui en `src/components/ui/` (Button,
  Card, Pill, Field/Input/Select, Table, Progress/Skeleton, Dialog, Menu, Tabs,
  Tooltip) sobre `radix-ui`; gráficos en `src/components/charts/` con
  **Recharts** y alternativa textual (tabla `sr-only`); iconos **lucide-react**;
  barra de comandos **cmdk**.
- El tema respeta `prefers-color-scheme` si no hay elección guardada.

# Consecuencias

- Las páginas antiguas (lección, quiz, glosario…) siguen con clases de
  `app.css` dentro del shell nuevo; conviene migrarlas progresivamente.
- `ui/legacy.tsx` conserva `Icon`, `Ring`, `Stat`… re-exportados desde
  `@/components/ui`.
