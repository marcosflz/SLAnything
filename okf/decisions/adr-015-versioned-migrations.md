---
type: ADR
title: ADR-015 · Migraciones versionadas (PostgreSQL pendiente)
description: Migraciones numeradas con PRAGMA user_version sobre SQLite; el paso a SQLAlchemy/PostgreSQL queda como siguiente fase.
tags: [adr, datos, sqlite, migraciones]
status: stable
date: 2026-11-13
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-13T12:00:00Z }
sources:
  - id: migrations
    resource: ../../webapp/migrations.py
    title: Migraciones
  - id: db
    resource: ../../webapp/db.py
    title: Esquema base
---

# Contexto

El plan proponía SQLAlchemy 2 + Alembic + PostgreSQL para el SaaS. El acceso a
datos es SQL directo en `repositories.py`, `deps.py`, `authoring/store.py` y
los módulos nuevos; portarlo todo de golpe era el cambio de mayor riesgo y no
desbloqueaba ninguna funcionalidad inmediata.

# Decisión

- `db.SCHEMA` queda como **línea base v3**. Cada cambio posterior es una
  función idempotente en `webapp/migrations.py` (`MIGRATIONS`), aplicada en
  orden según `PRAGMA user_version`. Hoy: v4 (espacios, grupos, matrículas,
  invitaciones, auditoría, eventos) y v5 (estados del motor por etapas).
- Las migraciones publicadas no se reescriben; se añade una nueva.
- El puerto a SQLAlchemy/Alembic y PostgreSQL (con `FOR UPDATE SKIP LOCKED`
  para la cola) se mantiene como objetivo, ahora acotado.

# Consecuencias

- Un solo proceso y SQLite siguen siendo el límite de escala (ver
  [known-issues](/context/known-issues.md)).
