---
type: Cheatsheet
title: Comandos del proyecto
description: Chuleta de comandos para instalar, arrancar, probar y mantener SLAnything.
tags: [comandos, cheatsheet, uv, pytest, okf]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README
  - id: agents
    resource: ../../AGENTS.md
    title: AGENTS.md
---

# Entorno

```powershell
uv sync
uv run python --version
```

# Aplicación

```powershell
# Backend FastAPI · puerto 8000
uv run python aula.py

# Frontend Next.js · puerto 3000 (otra terminal)
cd frontend
npm install
npm run dev
# http://127.0.0.1:3000

# Build de producción del frontend
npm run build
npm start
```

# Datos compartidos

```powershell
# Exportar las traducciones de FastAPI a Next
uv run python tools/export_messages.py

# Sincronizar app.css con el frontend
uv run python tools/sync_frontend_assets.py

# Smoke test con ambos servidores arrancados
uv run python tools/smoke_next.py
```

# Salud

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/salud
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/salud
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/api/v1/public
```

# Estudio de autoría

```powershell
# Agentes nas-adk (vienen con uv sync); comprobar la versión
uv run python -c "import nas.adk; print(nas.adk.__version__)"
# Suscripción de Claude: el CLI debe existir en el servidor (Docker ya lo incluye)
claude --version

# Abrir el Estudio con una cuenta individual o con la profesora
# http://127.0.0.1:3000/estudio
# autodidacta@slanything.local / auto1234 · profe@slanything.local / profe1234
# Sin red ni proveedor: arranca el backend con AULA_LLM_FAKE=1

# Proveedor propio (con sesión de autoría): GET/PUT/DELETE /api/v1/account/ai
# Cada usuario obtiene el token de su suscripción en su equipo con: claude setup-token

# Limpiar documentos, logs y API key locales del Estudio
Remove-Item -Recurse -Force authoring-data
```

# Docker

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
docker compose down -v          # borra el volumen SQLite
docker compose cp backend:/data/aula.db ./aula-backup.db
```

# Tests y contenido

```powershell
uv run pytest -q                          # 111 tests
uv run python tools/check_chapter.py ch02  # y ch03…ch07
uv run python tools/validate_all_chapters.py
cd frontend; npm run typecheck; npm run build
cd frontend; npm run e2e                   # requiere ambos servidores; E2E_BASE para otra URL
cd frontend; npm run e2e:labs              # 15 labs; requiere AULA_SAMPLE_COURSES=1
```

# OKF

```powershell
uv run python tools/check_okf.py
```

# Reiniciar / limpiar

```powershell
$c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($c) { Stop-Process -Id $c.OwningProcess -Force }
Remove-Item aula.db,aula.db-wal,aula.db-shm -Force -ErrorAction SilentlyContinue
uv run python aula.py
```

# JavaScript

```powershell
node --check webapp/static/js/app.js
node --check webapp/static/js/i18n.js
Get-ChildItem webapp/static/js/labs/*.js | ForEach-Object { node --check $_.FullName }
```

# Cuaderno

```powershell
uv run jupyter lab notebooks/capitulo_01_entender_los_llms.ipynb
```

# Git

```powershell
git status --short
git diff --stat
```
