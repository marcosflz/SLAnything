---
type: ADR
title: ADR-018 · Eventos de aprendizaje como fuente de los KPIs
description: Tabla learning_events al estilo xAPI; los KPIs de alumno, profesor y admin se calculan a partir de ella.
tags: [adr, analítica, kpis, eventos]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: analytics
    resource: ../../webapp/analytics.py
    title: Captura y KPIs
  - id: tracker
    resource: ../../frontend/src/components/lesson/LearningTracker.tsx
    title: Tracker
---

# Contexto

Los indicadores salían de contadores diarios (`activity`) que mezclaban la hora
local con UTC, contaban el inicio de sesión como actividad y no medían tiempo de
estudio, ejecuciones de código ni respuestas por pregunta.

# Decisión

- `learning_events(ts, day, user_id, course_slug, lesson_slug, verb,
  object_id, score, success, duration_ms, meta_json)`, días en UTC.
- Verbos de servidor (no falsificables): `lesson.viewed`,
  `lesson.completed`, `quiz.submitted`, `question.answered`, `code.run`,
  `note.saved`. Verbos de cliente (`POST /api/v1/events`, CSRF en cabecera o
  cuerpo para `sendBeacon`): `lesson.heartbeat` (máx. 60 s por latido, solo
  con pestaña visible y actividad reciente), `lab.interacted`,
  `check.answered`, `search.performed`, `flashcard.reviewed`.
- KPIs bajo demanda en `analytics.py`: alumno (`/analytics/me`), curso
  (`/analytics/course`, embudo, mapa de calor, análisis de ítems, riesgo, CSV)
  y espacio (`/admin/metrics`). La racha solo cuenta aprendizaje.

# Consecuencias

- Si el volumen crece, materializar agregados diarios.
- Retención y exportación de eventos (RGPD) siguen pendientes.
