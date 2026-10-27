# SLAnything · frontend Next.js

Interfaz React 19 + Next.js 16 (App Router) de SLAnything. FastAPI sigue siendo el
backend: contenido, SQLite, sesiones, CSRF, ejecución de Python y API JSON.

## Desarrollo

```powershell
# Terminal 1 · backend
uv run python aula.py

# Terminal 2 · frontend
cd frontend
npm install
npm run dev
```

Abrir <http://127.0.0.1:3000>.

El frontend habla con FastAPI mediante los *rewrites* de `next.config.ts`:

- `/api/v1/*` → `http://127.0.0.1:8000/api/v1/*`
- `/api/ejecutar` → `http://127.0.0.1:8000/api/ejecutar`
- `/static/*` → `http://127.0.0.1:8000/static/*`

Así el navegador permanece en el origen de Next y la cookie de sesión
`aula_session` funciona sin CORS. El servidor de Next usa `API_INTERNAL_URL`
para renderizar en servidor.

## Scripts

| Comando | Efecto |
|---|---|
| `npm run dev` | Servidor de desarrollo en el puerto 3000 |
| `npm run build` | Build de producción |
| `npm start` | Servidor de producción en el puerto 3000 |
| `npm run typecheck` | TypeScript sin emitir |
| `npm run e2e` | Smoke E2E con Playwright (requiere ambos servidores) |
| `npm run export:messages` | Exporta las traducciones desde `webapp/i18n.py` |
| `npm run sync:assets` | Sincroniza `app.css` desde `webapp/static/css/` |

Para el smoke E2E la primera vez:

```powershell
npx playwright install chromium
npm run e2e
```

## Estructura

```text
src/app/                 rutas App Router
src/components/          shell, bloques de lección, labs, quiz y UI
src/lib/                 API, tipos, mensajes, formato y cliente HTTP
src/app/app.css          copia de webapp/static/css/app.css
src/lib/messages.json    traducciones exportadas desde FastAPI
```

## Estudio y PWA

- `/estudio` es la pantalla docente de autoría; el componente cliente está en
  `src/components/authoring/StudioPanel.tsx` y consume `/api/v1/authoring`.
- `src/app/manifest.ts`, `src/app/icon.svg`, `public/icon.svg`, `public/sw.js` y
  `PWARegister` hacen la web instalable. El service worker solo cachea estáticos.
- La guía completa está en [`../docs/AUTHORING.md`](../docs/AUTHORING.md) y la
  decisión web/escritorio en [`../docs/DESKTOP.md`](../docs/DESKTOP.md).

## Notas de migración

- Las páginas son Server Components por defecto; solo los controles
  interactivos llevan `"use client"`.
- El contenido didáctico se renderiza con `BlockRenderer`; el curso estático es
  de confianza y el generado desde `/estudio` pasa antes por
  `webapp/authoring/sanitize.py`.
- Los laboratorios se cargan desde `/static/js/labs/*.js` en tiempo de
  ejecución, sin reescribirlos en React.
- La interfaz Jinja sigue disponible en `http://127.0.0.1:8000` como red de
  seguridad durante la transición.
