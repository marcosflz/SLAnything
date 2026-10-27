---
type: Runbook
title: Arranque local de SLAnything
description: Comandos para instalar, arrancar, comprobar y reiniciar la plataforma en local.
tags: [runbook, arranque, uv, fastapi, local]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README
  - id: main
    resource: ../../webapp/main.py
    title: Punto de entrada
  - id: pyproject
    resource: ../../pyproject.toml
    title: Dependencias
---

# Requisitos

- [uv](https://docs.astral.sh/uv/) y Python 3.10+ (el entorno actual usa 3.14).
- Node.js 20+ y npm para el frontend Next.js (el entorno actual usa Node 24).
- **OpenCode** solo si vas a usar `/estudio` en local: `npm install -g @opencode/cli`.
  La imagen Docker ya lo incluye y no hace falta instalarlo en el host.
- No hace falta GPU.
- Un navegador moderno.

# Docker

```powershell
Copy-Item .env.example .env
# Cambia AULA_SECRET en .env
docker compose up -d --build
docker compose ps
```

Abre `http://127.0.0.1:3000`. La guía completa —volumen, backups, variables y
troubleshooting— está en [Docker](../../docs/DOCKER.md).

# Instalación y arranque manual

La interfaz principal es Next.js. Arranca los dos procesos en terminales
distintas:

```powershell
# Terminal 1 · backend FastAPI (puerto 8000)
uv sync
uv run python aula.py

# Terminal 2 · frontend Next.js (puerto 3000)
cd frontend
npm install
npm run dev
```

Abre `http://127.0.0.1:3000`. Para el Estudio en local, instala también
`npm install -g @opencode/cli` y configura el proveedor en `/estudio`.

El frontend habla con FastAPI mediante los *rewrites* de
`frontend/next.config.ts`; no hace falta configurar CORS. La URL interna se
puede cambiar con `API_INTERNAL_URL` (por defecto `http://127.0.0.1:8000`).

La interfaz Jinja sigue disponible en `http://127.0.0.1:8000` como fallback
durante la migración.

Alternativa con Uvicorn:

```powershell
uv run uvicorn webapp.main:app --host 127.0.0.1 --port 8000
```

`aula.py` llama a `webapp.main.run()`. La recarga automática está desactivada por
defecto para que SQLite no provoque reinicios; se activa con `AULA_RELOAD=1`.

# Comprobación

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/salud
uv run pytest -q
uv run python tools/check_okf.py
cd frontend; npm run typecheck; npm run build
```

# Cuentas

| Perfil | Correo | Contraseña |
|---|---|---|
| Estudiante | `demo@aulallm.local` | `demo1234` |
| Profesora | `profe@aulallm.local` | `profe1234` |

# Variables de entorno

| Variable | Efecto | Defecto |
|---|---|---|
| `AULA_DB` | Ruta de SQLite | `<repo>/aula.db` |
| `AULA_ENV` | Entorno informativo | `development` |
| `AULA_SECURE_COOKIES` | Cookie `Secure` | `0` |
| `AULA_RELOAD` | Recarga Uvicorn | `0` |
| `AULA_SECRET` | Reservado para firmas futuras | valor local |
| `AULA_EXEC_ENABLED` | Activa `POST /api/ejecutar` | `1` |
| `AULA_EXEC_TIMEOUT` | Segundos máximos por ejemplo | `10` |
| `AULA_EXEC_MEMORY_MB` | Memoria máxima best effort | `1024` |
| `AULA_EXEC_MAX_CODE` | Caracteres máximos de código | `16000` |
| `AULA_EXEC_MAX_OUTPUT` | Caracteres máximos de salida | `20000` |
| `AULA_EXEC_RUNS_PER_MINUTE` | Ejecuciones por usuario/minuto | `12` |
| `AULA_EXEC_CONCURRENT` | Ejecuciones simultáneas | `2` |
| `AULA_AUTHORING_ENABLED` | Activa el Estudio | `1` |
| `AULA_AUTHORING_DIR` | Subidas, logs y ajustes | `<repo>/authoring-data` |
| `AULA_AUTHORING_OPENCODE_BIN` | Binario de OpenCode | `opencode` |
| `AULA_AUTHORING_TIMEOUT` | Segundos por trabajo | `1800` |
| `AULA_AUTHORING_MAX_UPLOAD_MB` | MB por archivo | `25` |
| `AULA_AUTHORING_MAX_FILES` | Archivos por unidad | `5` |
| `AULA_AUTHORING_MAX_CHARS` | Texto extraído máximo | `300000` |
| `AULA_AUTHORING_MAX_JOBS` | Trabajos activos por profesor | `3` |

La API key del proveedor **no** es una variable de entorno del proceso: se guarda
desde `/estudio` en `AULA_AUTHORING_DIR/settings.json` (0600) y se inyecta solo
al subproceso de OpenCode. Los ejemplos Python necesitan `psutil`, `numpy`, `pandas` y `matplotlib`, que ya
están en `pyproject.toml`. El idioma se guarda en la cookie `aula_lang`; también
se puede forzar con `?lang=en` o `?lang=es`.

# Reiniciar / limpiar

```powershell
$c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($c) { Stop-Process -Id $c.OwningProcess -Force }
Remove-Item aula.db,aula.db-wal,aula.db-shm -Force -ErrorAction SilentlyContinue
uv run python aula.py
```

Al borrar la BD se pierden usuarios, progreso, notas, intentos y las referencias a
cursos generados. El contenido estático vive en código; los documentos y logs del
Estudio viven en `authoring-data/` (o `/data/authoring` en Docker). Para limpiar
todo el Estudio local: `Remove-Item -Recurse -Force authoring-data`.

`init_db()` migra automáticamente una base v1 (sin `course_slug`) al esquema v3:
copia el progreso, las notas, los marcadores y los intentos al curso
`llm-desde-cero`, añade `authoring_jobs` y `generated_courses` y elimina las
tablas antiguas. Haz una copia de `aula.db` antes de cambiar de versión si el
progreso es importante.

# Problemas típicos

- **Error 500 con `'t' is undefined` o rutas nuevas en 404:** el proceso Uvicorn
  es anterior a los últimos cambios. `aula.py` no recarga automáticamente; páralo
  y vuelve a arrancarlo. La causa habitual es editar `templating.py`/plantillas o
  añadir routers con el servidor en marcha.
- **Puerto ocupado:** mata el proceso de la sección anterior o usa `--port 8001`.
- **Cookie no persiste:** comprueba que no estás mezclando `127.0.0.1` y `localhost`.
- **`AULA_SECURE_COOKIES=1` en HTTP:** el login no funciona; actívalo solo con TLS.
- **Imágenes rotas:** `validate_content()` falla al arrancar; revisa
  `webapp/static/img/ch01/`.
