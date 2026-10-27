---
type: Runbook
title: Frontend Next.js en local
description: Arranque, verificación y soluciones a problemas del frontend Next.js.
tags: [frontend, nextjs, npm, desarrollo, smoke]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T13:30:00Z }
sources:
  - id: readme
    resource: ../../frontend/README.md
    title: README del frontend
  - id: package
    resource: ../../frontend/package.json
    title: Scripts
---

# Arranque

```powershell
# Terminal 1 · backend
uv run python aula.py

# Terminal 2 · frontend
cd frontend
npm install
npm run dev
```

Abrir `http://127.0.0.1:3000`.

Los scripts `dev` y `start` escuchan en `127.0.0.1` para que la URL documentada
funcione también en Windows. Si necesitas exponerlo en red, usa
`npx next dev -H 0.0.0.0 -p 3000` y un proxy.

# Docker

```powershell
docker compose build frontend
docker compose up -d frontend
```

La imagen usa `output: "standalone"` y `API_INTERNAL_URL=http://backend:8000`
como build arg. El runtime no incluye `node_modules`.

# Verificación

```powershell
cd frontend
npm run typecheck
npm run build
# Rutas nuevas: /estudio (docente), /manifest.webmanifest y /sw.js (PWA)
```

Con ambos servidores:

```powershell
uv run python tools/smoke_next.py
```

# Sincronización

```powershell
cd frontend
npm run sync:assets      # copia webapp/static/css/app.css
npm run export:messages  # exporta webapp/i18n.py a messages.json
```

# Problemas típicos

- **Connection refused en 3000:** el frontend no está arrancado o escucha solo en
  IPv6. Comprueba `Get-NetTCPConnection -LocalPort 3000` y usa la URL `localhost`
  o reinicia con los scripts actuales.
- **`/salud` falla:** el backend no está en `API_INTERNAL_URL` (por defecto
  `http://127.0.0.1:8000`).
- **Sin sesión:** las cookies son del origen Next; no mezcles `localhost` y
  `127.0.0.1` en el navegador.
- **Diseño desincronizado:** ejecuta `npm run sync:assets`.
- **Textos sin traducir:** ejecuta `npm run export:messages` tras editar
  `webapp/i18n.py`.
