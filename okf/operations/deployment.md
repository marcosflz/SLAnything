---
type: Runbook
title: Despliegue mínimo
description: Cómo desplegar SLAnything con Uvicorn, SQLite, OpenCode y un proxy TLS.
tags: [despliegue, produccion, sqlite, tls, uvicorn]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
  - id: run
    resource: /operations/run.md
    title: Arranque local
---

# Docker Compose

La vía empaquetada está en `compose.yaml` y se detalla en
[docs/DOCKER.md](../../docs/DOCKER.md):

```powershell
Copy-Item .env.example .env
# Cambia AULA_SECRET
docker compose up -d --build
docker compose ps
```

- `backend` no publica el 8000; solo es accesible en la red interna.
- `frontend` publica `${AULA_HTTP_PORT:-3000}`.
- SQLite vive en el volumen `aula-llm-data` (`/data/aula.db`).
- El Estudio vive en el mismo volumen (`/data/authoring`): subidas, logs,
  `settings.json` y el `HOME` aislado de OpenCode.
- La imagen del backend incluye OpenCode (`/usr/local/bin/opencode` v2.1.4);
  necesita salida a Internet hacia el proveedor LLM elegido.
- Healthchecks: `/health` en backend y `/salud` a través de Next.
- `docker compose down` conserva datos; `down -v` los borra.

# Comando manual

```powershell
# Backend FastAPI (solo loopback; el navegador habla con Next)
$env:AULA_ENV="production"
$env:AULA_SECURE_COOKIES="1"
$env:AULA_DB="C:\datos\aula.db"
uv run uvicorn webapp.main:app --host 127.0.0.1 --port 8000

# Frontend Next.js
cd frontend
$env:API_INTERNAL_URL="http://127.0.0.1:8000"
npm ci
npm run build
npm start
```

# Requisitos

- TLS terminado en Caddy/Nginx delante de Next (puerto 3000).
- `AULA_SECURE_COOKIES=1` solo con HTTPS.
- Un worker mientras se use SQLite.
- Copia de seguridad diaria de `aula.db`.
- `/health` en FastAPI y `/salud` a través de Next como health checks.
- Decidir si se permite ejecución Python. Para un aula pública, `AULA_EXEC_ENABLED=0`
  o ejecutar el runner en un contenedor sin red y con usuario sin privilegios.
- Decidir si se permite el Estudio. Para un aula pública, `AULA_AUTHORING_ENABLED=0`
  salvo para docentes; el Estudio gasta cuota del proveedor y escribe documentos.
- El Estudio no es multiusuario en cuota: un trabajo a la vez y 3 activos por
  profesor. Para más escala, separa el runner en un servicio propio con cola.
- La API key vive en el volumen, no en `.env`. Protege backups y permisos del
  volumen (`/data/authoring/settings.json` es 0600).

# Ejemplo Caddy

```caddyfile
aula.example.com {
    reverse_proxy 127.0.0.1:3000
}
```

FastAPI no se expone directamente: Next reescribe `/api/v1/*`,
`/api/ejecutar` y `/static/*` al loopback 8000.

# Checklist

- [ ] HTTPS y cookie `Secure`.
- [ ] `aula.db` fuera del árbol servido por el proxy.
- [ ] Copia de seguridad y restauración probadas.
- [ ] Panel `/profesor` y `/estudio` solo para docentes.
- [ ] Copia del volumen `/data/authoring` y de la API key.
- [ ] Aviso de privacidad y retención de datos, incluidos los documentos subidos.
- [ ] Límites de login y proxy delante.
- [ ] Política de ejecución Python (activada con límites o desactivada).
- [ ] Logs sin secretos.
- [ ] Créditos de las figuras visibles.

# Limitaciones

- SQLite no es ideal para muchos usuarios concurrentes.
- El rate limit en memoria no se comparte entre workers.
- No hay migraciones versionadas; un cambio de esquema requiere plan.
- No hay monitorización ni alertas incluidas.
