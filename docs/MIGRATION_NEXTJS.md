# Migración de SLAnything a Next.js

Fecha: 2026-10-24
Estado: paridad funcional completada; Jinja se mantiene como fallback

## Objetivo

Migrar toda la interfaz de SLAnything a **Next.js (App Router, React 19,
TypeScript)** manteniendo **FastAPI** como backend, base de datos y motor de
contenido. La migración es incremental y reversible: las rutas HTML de Jinja
siguen disponibles durante la transición, pero la interfaz principal pasa a ser
`frontend/`.

## Decisiones

1. **Strangler Fig**: no se reescribe el backend. FastAPI gana una API JSON
   versionada en `/api/v1` y conserva las rutas HTML actuales como fallback.
2. **Mismo origen**: Next.js hace *rewrites* de `/api/v1/*`, `/api/ejecutar` y
   `/static/*` hacia FastAPI. El navegador solo habla con el origen de Next, así
   que la cookie de sesión y el CSRF siguen funcionando sin CORS.
3. **Sesión y CSRF**: FastAPI sigue emitiendo `aula_session` (HttpOnly) y el
   token CSRF. Next lo reenvía en las peticiones de servidor y el cliente manda
   `X-CSRF-Token` en las mutaciones.
4. **Diseño**: se reutiliza `app.css` como sistema visual para no introducir una
   regresión estética. Los componentes React reproducen las clases existentes.
5. **Laboratorios**: se reutilizan los 7 módulos JS actuales servidos por
   FastAPI bajo `/static/js/labs/*`; Next los monta en un componente cliente con
   `import()` en tiempo de ejecución. No se reescriben en React en esta fase.
6. **Contenido**: las lecciones siguen en Python. FastAPI serializa los bloques
   a JSON y React los renderiza con un `BlockRenderer`.
7. **i18n**: FastAPI sigue siendo la fuente de las traducciones de la interfaz;
   `tools/export_messages.py` las exporta a `frontend/src/lib/messages.json`.
   La selección de idioma se guarda en la cookie `aula_lang`.

## Fases

| Fase | Trabajo | Estado |
|---|---|---|
| 0 | Línea base (77 tests) | ✅ |
| 1 | API JSON `/api/v1` + serializadores + 8 tests | ✅ 85 tests verdes |
| 2 | Scaffold Next, shell, tema, i18n, rewrites | ✅ build correcto |
| 3 | Páginas públicas y autenticación | ✅ |
| 4 | Curso, lección, bloques, Python y labs | ✅ |
| 5 | Quiz, resultado y progreso | ✅ |
| 6 | Glosario, recursos, búsqueda y profesor | ✅ |
| 7 | Verificación, documentación y OKF | ✅ smoke HTTP, smoke E2E Playwright y ADR-008 |

## Contrato de la API

- `GET /api/v1/session` → usuario y CSRF.
- `GET /api/v1/public` → curso y datos públicos.
- `GET /api/v1/shell` → shell autenticado (usuario, curso, progreso, stats).
- `GET /api/v1/dashboard`, `/course`, `/lessons/{slug}`, `/progress`,
  `/glossary`, `/resources`, `/search?q=`, `/teacher`.
- `POST /api/v1/auth/login`, `/auth/register`, `/auth/logout`.
- `POST /api/v1/lessons/{slug}/complete|note|bookmark`.
- `GET /api/v1/quiz/{id}`, `POST /api/v1/quiz/{id}`,
  `GET /api/v1/quiz/attempts/{id}`.
- `GET /api/v1/downloads/...` para código, cuaderno y plan.

## Riesgos y mitigaciones

- **Doble fuente de CSS**: `frontend/src/app/app.css` se copia desde
  `webapp/static/css/app.css`. Se documenta y se sincroniza con
  `tools/sync_frontend_assets.py`.
- **Cookies entre puertos**: en desarrollo el navegador usa `localhost:3000`;
  los rewrites hacen que la cookie se guarde en ese origen. FastAPI se consume
  por `API_INTERNAL_URL=http://127.0.0.1:8000`.
- **Labs y `import()`**: se cargan desde `/static/js/labs/` con
  `webpackIgnore` para no bundlear módulos que dependen del DOM.
- **Contenido HTML de confianza**: los bloques usan `dangerouslySetInnerHTML`
  solo con contenido estático del repositorio, nunca con entrada de usuario.

## Cómo ejecutar

```powershell
# Terminal 1
uv run python aula.py

# Terminal 2
cd frontend
npm install
npm run dev
```

Abrir `http://127.0.0.1:3000`.

Verificación de navegador:

```powershell
cd frontend
npx playwright install chromium
npm run e2e
```

## Ajustes posteriores a la primera paridad

- Selector ES/EN con navegación completa: la caché de RSC de Next podía reutilizar
  la página en el idioma anterior.
- Barra lateral colapsable en escritorio, con preferencia persistida.
- Anillo de progreso corregido: `stroke-dasharray` usa la circunferencia real.
- Smoke E2E Playwright ampliado para cubrir los tres puntos anteriores.

## Retirada de Jinja

Cuando la paridad esté verificada y el OKF lo registre, se podrán retirar
`webapp/templates/`, `webapp/templating.py` y las rutas HTML. Hasta entonces se
mantienen como red de seguridad y para los tests existentes.
