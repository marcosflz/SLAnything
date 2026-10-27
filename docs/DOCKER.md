# Docker · SLAnything

SLAnything se empaqueta en dos imágenes:

| Imagen | Contenido | Puerto |
|---|---|---|
| `aula-llm-backend:local` | FastAPI, contenido, SQLite, API JSON, runner Python y OpenCode portable | 8000 interno |
| `aula-llm-frontend:local` | Next.js 16 en modo `standalone` + PWA | 3000 público |

`compose.yaml` las conecta en una red privada. El navegador solo habla con el
frontend; Next reescribe `/api/v1/*`, `/api/ejecutar` y `/static/*` al servicio
`backend`. La cookie `aula_session` y el CSRF siguen funcionando sin CORS.

## Arranque rápido

```powershell
Copy-Item .env.example .env
# Edita .env: como mínimo cambia AULA_SECRET.
docker compose up -d --build
docker compose ps
```

Abrir <http://127.0.0.1:3000>.

Cuentas de demostración:

| Perfil | Correo | Contraseña |
|---|---|---|
| Estudiante | `demo@aulallm.local` | `demo1234` |
| Profesora | `profe@aulallm.local` | `profe1234` |

El frontend espera a que el backend esté `healthy`. El primer arranque crea
`/data/aula.db` y `/data/authoring/` en el volumen `aula-llm-data` y siembra las
cuentas demo. La imagen del backend incluye OpenCode (`/usr/local/bin/opencode`)
para el Estudio; configura el proveedor en `/estudio`.

## Comandos habituales

```powershell
docker compose up -d --build       # construir y arrancar
docker compose ps                  # estado y healthchecks
docker compose logs -f frontend    # logs de Next
docker compose logs -f backend     # logs de FastAPI
docker compose restart backend     # reiniciar solo el backend
docker compose down                # parar; conserva el volumen
docker compose down -v             # parar y borrar la base de datos
```

Si el puerto 3000 está ocupado:

```powershell
$env:AULA_HTTP_PORT="8080"
docker compose up -d
# http://127.0.0.1:8080
```

## Variables de entorno

Se leen de `.env` en la raíz. Las principales:

| Variable | Defecto | Uso |
|---|---|---|
| `AULA_HTTP_PORT` | `3000` | Puerto público del frontend |
| `AULA_SECRET` | valor local | Secreto de aplicación; cámbialo |
| `AULA_SECURE_COOKIES` | `0` | `1` solo con HTTPS/TLS |
| `AULA_EXEC_ENABLED` | `1` | Ejecución Python en servidor |
| `AULA_EXEC_TIMEOUT` | `10` | Segundos máximos por ejecución |
| `AULA_EXEC_MEMORY_MB` | `1024` | Límite de memoria best effort |
| `AULA_EXEC_CONCURRENT` | `2` | Ejecuciones simultáneas |
| `AULA_EXEC_RUNS_PER_MINUTE` | `12` | Rate limit por usuario |
| `AULA_AUTHORING_ENABLED` | `1` | Activa el Estudio |
| `AULA_AUTHORING_TIMEOUT` | `1800` | Segundos por generación |
| `AULA_AUTHORING_MAX_UPLOAD_MB` | `25` | Tamaño por documento |
| `AULA_AUTHORING_MAX_FILES` | `5` | Documentos por unidad |
| `AULA_AUTHORING_MAX_CHARS` | `300000` | Texto extraído máximo |
| `AULA_AUTHORING_MAX_JOBS` | `3` | Trabajos activos por profesor |
| `TZ` | `Europe/Madrid` | Zona horaria de actividad/rachas |

La API key del proveedor **no** va en `.env`: se guarda desde `/estudio` en
`/data/authoring/settings.json` (0600) y viaja al subproceso de OpenCode como
variable de entorno.

`API_INTERNAL_URL` está fijada a `http://backend:8000` dentro de Compose. Si
cambias el nombre del servicio, actualiza también el `build.args` del frontend.

## Datos y copias de seguridad

SQLite y el Estudio viven en el volumen `aula-llm-data`:

```powershell
# Copia en caliente
docker compose cp backend:/data/aula.db ./aula-backup.db
docker compose cp backend:/data/authoring ./authoring-backup

# Restaurar
docker compose stop frontend backend
docker compose cp ./aula-backup.db backend:/data/aula.db
docker compose start backend
docker compose start frontend
```

También puedes inspeccionar la BD sin salir de Docker:

```powershell
docker compose exec backend python -c "import sqlite3; c=sqlite3.connect('/data/aula.db'); print(c.execute('select count(*) from users').fetchone())"
```

No uses `docker compose down -v` si quieres conservar progreso, notas e intentos.

## Ejecución de Python

El runner sigue siendo el mismo: subproceso `python -I`, AST, lista blanca de
imports, hook de auditoría y límites. En Docker funciona sin configuración extra
porque `numpy`, `pandas`, `matplotlib` y `psutil` están en la imagen.

Para un aula pública:

- deja `AULA_EXEC_ENABLED=0`, o
- ejecuta el backend con un aislamiento adicional (contenedor sin red, usuario
  sin privilegios, límites de CPU/memoria) y mantén el rate limit.

## Producción mínima

1. Copia `.env.example` a `.env` y cambia `AULA_SECRET`.
2. Sirve la app detrás de Caddy/Nginx con TLS apuntando a `127.0.0.1:3000`.
3. Pon `AULA_SECURE_COOKIES=1` **solo** cuando el navegador use HTTPS.
4. Haz copias de `aula.db` y prueba la restauración.
5. Limita el acceso al panel `/profesor`, revisa privacidad y retención.
6. Revisa los logs y la política de ejecución Python.

Caddy mínimo:

```caddyfile
aula.example.com {
    reverse_proxy 127.0.0.1:3000
}
```

## Construir imágenes sueltas

```powershell
# Backend (contexto raíz)
docker build -t aula-llm-backend:local .

# Frontend (contexto frontend)
docker build `
  -t aula-llm-frontend:local `
  --build-arg API_INTERNAL_URL=http://backend:8000 `
  .\frontend
```

El frontend usa `output: "standalone"`; el runtime solo necesita
`.next/standalone` y `.next/static`, no `node_modules`.

## Troubleshooting

- **El frontend está unhealthy:** comprueba `docker compose logs backend` y que
  `/salud` responda. Next lo reescribe a `/health` del backend.
- **Login no persiste:** no mezcles `localhost` y `127.0.0.1`; la cookie es del
  origen. Si `AULA_SECURE_COOKIES=1` sin HTTPS, el navegador no la guarda.
- **Permiso denegado en `/data`:** el volumen debe ser propiedad del usuario
  `aula`. Si usas un bind mount propio, ajusta permisos.
- **Cambios de contenido no aparecen:** reconstruye la imagen del backend:
  `docker compose build backend && docker compose up -d backend`.
- **Cambios de frontend no aparecen:** reconstruye
  `docker compose build frontend && docker compose up -d frontend`.
- **El Estudio dice que OpenCode no está:** comprueba
  `docker compose exec backend opencode --version`. Si falta, reconstruye el
  backend; el binario se instala en la imagen.
- **El Estudio no puede hablar con el proveedor:** el contenedor necesita salida
  a Internet. Para Ollama/LM Studio local, usa `host.docker.internal`; en Linux
  ya está el `extra_hosts` de Compose.
- **Un trabajo queda interrumpido:** al reiniciar, los trabajos activos se marcan
  como fallidos. Revisa `/estudio` y vuelve a subir el documento.
- **Backup del Estudio:** copia también `/data/authoring` (documentos, logs y la
  API key) además de `/data/aula.db`.
- **La app Jinja de `:8000` no está publicada:** es intencional. Compose solo
  publica el 3000. Usa `docker compose exec backend ...` para depurar dentro.
