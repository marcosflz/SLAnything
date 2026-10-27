---
type: Architecture
title: Ejecución de Python en servidor
description: Runner aislado para los ejemplos del libro, con límites de tiempo, memoria, salida y concurrencia.
tags: [python, ejecucion, sandbox, seguridad, runner]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T13:30:00Z }
sources:
  - id: execution
    resource: ../../webapp/execution.py
    title: Límites y subprocess
  - id: runner
    resource: ../../webapp/sandbox_runner.py
    title: Runner aislado
  - id: route
    resource: ../../webapp/routers/execution.py
    title: Endpoint /api/ejecutar
---

# Qué hace

Permite editar y ejecutar los **26 ejemplos de Python** de las lecciones desde la
web. El resultado incluye `stdout`, errores, figuras/tablas y duración. El código
también se puede descargar como `.py`.

# Arquitectura

1. `POST /api/ejecutar` (requiere sesión y CSRF) recibe `code` y `lesson`.
2. `webapp/execution.py` valida tamaño, rate limit por usuario y concurrencia.
3. Lanza `python -I webapp/sandbox_runner.py` en un subproceso con cwd temporal.
4. El runner aplica:
   - AST con imports permitidos (`math`, `numpy`, `pandas`, `matplotlib`…);
   - nombres y atributos peligrosos bloqueados (`eval`, `exec`, `open`, `__class__`…);
   - hook de auditoría que bloquea archivos, red, procesos y `ctypes`;
   - límites de memoria, tiempo, salida y sin persistencia entre ejecuciones.
5. El resultado se escribe en `result.json` y se devuelve como JSON.

# Límites por defecto

| Límite | Valor | Variable |
|---|---|---|
| Tiempo | 10 s | `AULA_EXEC_TIMEOUT` |
| Memoria | 1024 MB | `AULA_EXEC_MEMORY_MB` |
| Código | 16 000 chars | `AULA_EXEC_MAX_CODE` |
| Salida | 20 000 chars | `AULA_EXEC_MAX_OUTPUT` |
| Ejecuciones/minuto | 12 | `AULA_EXEC_RUNS_PER_MINUTE` |
| Concurrencia | 2 | `AULA_EXEC_CONCURRENT` |
| Activado | sí | `AULA_EXEC_ENABLED` |

# Seguridad

**No es un sandbox de nivel producción.** Es defensa en profundidad para un aula
local. Para exponer a Internet:

- ejecuta el runner en un contenedor sin red, sin privilegios y con usuario no root;
- o desactiva la ejecución con `AULA_EXEC_ENABLED=0`.

Nunca se usa `exec()` en el proceso FastAPI. El runner es un archivo independiente
que no importa `webapp`.

# UI

- Jinja: bloque `python` con botón Ejecutar, salida y descarga.
- Next.js: `frontend/src/components/PythonRunner.tsx`.
- Descargas: `/api/v1/downloads/lessons/{slug}/code` y `.../code/{index}`.

# Pruebas

`webapp/tests/test_execution.py` (9 tests) cubre stdout, tablas, gráficos, imports
bloqueados, CSRF, timeout, descargas y ejemplos en inglés.
