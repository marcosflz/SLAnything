---
type: Decision
title: ADR-005 · OKF como memoria persistente
description: Adoptar Open Knowledge Format v0.2 como contexto duradero entre sesiones y hacer al agente responsable de mantenerlo.
tags: [adr, okf, agentes, contexto, memoria]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: agents
    resource: ../../AGENTS.md
    title: Instrucciones para agentes
  - id: spec
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: OKF v0.2 specification
---

# Contexto

Cada sesión de agente empieza sin memoria de la anterior. README, plan y QA
contienen contexto, pero están dispersos y no siempre se leen. Se necesita un
punto de entrada estable, navegable y actualizado.

# Decisión

Crear un bundle OKF v0.2 en `okf/` con conceptos de producto, arquitectura,
operaciones y decisiones. `AGENTS.md` obliga a leer el índice y el estado al
empezar y a actualizar los conceptos y `log.md` al terminar. Un validador
(`tools/check_okf.py`) comprueba frontmatter, enlaces, índices y log.

# Consecuencias

- Contexto portable, legible por humanos y agentes, y versionado en git.
- La calidad depende de que el agente lo mantenga; por eso es una regla dura.
- Hay duplicación resumida de README/plan; el OKF enlaza a las fuentes.
- Si el OKF se desactualiza, el validador no siempre lo detecta (solo estructura).

# Alternativas descartadas

- Un único `AGENTS.md` gigante: se vuelve obsoleto y difícil de navegar.
- Memoria propietaria del harness: no portable entre sesiones o herramientas.
- Solo README: sin index, log ni conceptos enlazados.
