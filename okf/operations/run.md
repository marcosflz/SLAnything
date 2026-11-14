---
type: Runbook
title: Arranque local de SLAnything
description: Comandos para instalar, arrancar, comprobar y reiniciar la plataforma en local.
tags: [runbook, arranque, uv, fastapi, local]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
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

Con `AULA_SEED_DEMO=1` (una por perfil, [ADR-021](/decisions/adr-021-account-profiles.md)):

| Perfil | Correo | Contraseña |
|---|---|---|
| Alumno de la Academia Demo | `alumno@slanything.local` | `alumno1234` |
| Profesora y propietaria de la academia | `profe@slanything.local` | `profe1234` |
| Cuenta individual (autodidacta) | `autodidacta@slanything.local` | `auto1234` |
| Superadmin de la plataforma | `admin@slanything.local` | `admin1234` |

Las bases antiguas se migran solas: `demo@aulallm.local` pasa a
`alumno@slanything.local` y `profe@aulallm.local` a `profe@slanything.local`,
con las contraseñas nuevas.

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

# Variables nuevas (2026-11-13)

| Variable | Defecto | Uso |
|---|---|---|
| `AULA_SEED_DEMO` | `1` | Crea cuentas y academia demo; pon `0` en producción |
| `AULA_SAMPLE_COURSES` | `0` | Muestra el curso de ejemplo «Construye un LLM desde cero» (ADR-020) |
| `AULA_OPEN_SIGNUP` | `0` | Registro abierto; con `0` solo se entra por invitación (ADR-022) |
| `AULA_PLATFORM_ADMINS` | — | Correos con superadministración (coma) |
| `AULA_GEN_ENGINE` | `direct` | Motor por defecto del Estudio |
| `AULA_GEN_WORKERS` | `2` | Hilos del pool de generación |
| `AULA_GEN_CONCURRENCY` | `3` | Lecciones en paralelo por trabajo |
| `AULA_GEN_INPROCESS` | `1` | `0` = usar `uv run python -m webapp.generation.worker` |
| `AULA_GEN_MAX_CHARS` | `3000000` | Texto máximo procesado por trabajo |
| `AULA_GEN_MONTHLY_PERSONAL` / `_ORG` | `10` / `100` | Cuotas mensuales por espacio |
| `AULA_LLM_FAKE` | `0` | Modelo falso determinista (demos sin red) |

La interfaz Jinja ya no existe: `:8000` solo sirve la API.
