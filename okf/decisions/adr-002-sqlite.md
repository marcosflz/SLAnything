---
type: Decision
title: ADR-002 · SQLite
description: Usar SQLite con sqlite3 de la stdlib en lugar de PostgreSQL para el MVP.
tags: [adr, sqlite, datos, persistencia]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: db
    resource: ../../webapp/db.py
    title: Esquema SQLite
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan
---

# Contexto

El MVP es de un solo curso y un solo proceso. Se necesita persistir usuarios,
progreso, notas e intentos sin montar infraestructura.

# Decisión

SQLite en un archivo `aula.db`, con `sqlite3` de la biblioteca estándar, WAL,
`foreign_keys=ON` y una conexión por petición.

# Consecuencias

- Cero servicios y backups triviales (copiar el archivo).
- Tests rápidos con bases temporales.
- Un solo escritor; no apto para alta concurrencia.
- Sin migraciones versionadas todavía.
- Migrar a PostgreSQL requeriría adaptar consultas y despliegue.

# Alternativas descartadas

- PostgreSQL: mejor concurrencia, pero infraestructura innecesaria para el MVP.
- JSON en disco: sin transacciones ni consultas.
