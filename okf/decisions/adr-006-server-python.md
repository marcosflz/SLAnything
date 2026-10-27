---
type: Decision
title: ADR-006 · Ejecución de Python en servidor con subproceso aislado
description: Ejecutar los ejemplos de las lecciones en un runner aislado, no dentro del proceso web ni en el navegador.
tags: [adr, python, ejecucion, seguridad, sandbox]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T17:00:00Z }
sources:
  - id: runner
    resource: ../../webapp/sandbox_runner.py
    title: Runner aislado
  - id: execution
    resource: ../../webapp/execution.py
    title: Límites y subproceso
  - id: api
    resource: ../../webapp/routers/execution.py
    title: Endpoint de ejecución
---

# Contexto

Las lecciones del capítulo 1 incluyen ejemplos de Python que en el cuaderno se
ejecutan con Jupyter. El alumnado debe poder editarlos y ejecutarlos desde la web,
pero el servidor no puede ejecutar código arbitrario dentro del proceso de FastAPI.
Tampoco se eligió Pyodide porque el objetivo es usar el entorno real del proyecto
(numpy, pandas, matplotlib) y mantener el cuaderno como descarga local.

# Decisión

Cada ejecución lanza `webapp/sandbox_runner.py` en un subproceso con `python -I`.
El runner:

- valida el AST antes de ejecutar (imports permitidos, sin clases, sin atributos
  peligrosos, sin `eval`/`exec`/`open`);
- precarga los módulos permitidos y después instala un `sys.addaudithook` que
  bloquea archivos, red, procesos y `ctypes`;
- captura stdout, tablas de pandas y figuras de matplotlib;
- aplica límites de tiempo, memoria, salida y concurrencia desde el proceso padre;
- no conserva estado entre ejecuciones.

La API `POST /api/ejecutar` exige sesión, CSRF y rate limit por usuario. El código
también se puede descargar como `.py` por bloque o por lección.

# Consecuencias

- El alumnado usa el mismo código que el cuaderno sin instalar nada.
- El aislamiento es defensa en profundidad, no un sandbox de nivel producción:
  para un despliegue público hay que añadir contenedor sin red y usuario sin
  privilegios, o poner `AULA_EXEC_ENABLED=0`.
- El coste por ejecución incluye el arranque del intérprete y, si se usan, pandas
  o matplotlib.
- No hay kernel persistente: cada ejemplo es autocontenido y no comparte variables
  con el siguiente.

# Alternativas descartadas

- **Pyodide/WASM:** no cubre pandas/matplotlib completos y complica el soporte.
- **Jupyter Kernel Gateway:** potente, pero añade un servicio con estado y más
  superficie de ataque para ejemplos pequeños.
- **`exec()` en el proceso web:** inaceptable por seguridad y por bloqueo del
  event loop.
