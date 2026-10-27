---
type: Decision
title: ADR-001 · FastAPI + Jinja2
description: Usar FastAPI con plantillas Jinja2 en lugar de una SPA React o Next.js.
tags: [adr, arquitectura, fastapi, jinja2, spa]
status: deprecated
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Contexto

El proyecto ya era Python/uv y el contenido vivía en cuadernos. Se quería una web
tipo Moodle con autenticación, progreso y quiz, mantenible por una sola persona.

# Decisión

FastAPI + Jinja2 + HTML server-side, con CSS y JS propios. Sin SPA ni build de
frontend.

# Consecuencias

- Un solo runtime para app, contenido y tests.
- Formularios, redirects y SEO simples.
- Menos dependencias y arranque más rápido.
- Las interacciones ricas se resuelven con módulos JS aislados.
- No hay hot reload de React ni ecosistema de componentes.

# Alternativas descartadas

- Next.js/React: más potencia, pero dos runtimes, build y más superficie.
- Django: más baterías, pero pesado para este alcance.

# Superseded

Esta decisión queda **deprecada** por [ADR-008](/decisions/adr-008-nextjs-frontend.md):
la interfaz principal pasa a Next.js y FastAPI conserva el backend y una API
JSON. Las rutas Jinja se mantienen temporalmente como fallback durante la
migración.
