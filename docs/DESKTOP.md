# Web, PWA y escritorio

La decisión para esta etapa es **web primero**. La misma interfaz Next.js se
sirve desde Docker y se puede instalar como PWA en Windows, macOS, Linux,
Android o iPad. No hay dos productos que mantener.

## Por qué web primero

El Estudio necesita tres cosas que ya viven en el servidor:

1. FastAPI y SQLite con sesiones, catálogo y progreso.
2. El binario de OpenCode y el sistema de ficheros para los documentos.
3. El sandbox de Python que ejecuta los ejemplos de las lecciones.

Una app de escritorio que solo cargue la web no aporta nada nuevo. Una app que
quiera funcionar sin servidor tendría que empaquetar Python, SQLite, OpenCode y
un binario por plataforma, además de resolver actualizaciones y firma de código.
Es un producto distinto, no una versión de la web.

## Instalar como aplicación

Con `docker compose up -d --build` y la web en `http://127.0.0.1:3000` o detrás
de HTTPS:

- **Chrome/Edge**: menú ▸ *Instalar SLAnything* (icono de instalación en la
  barra de direcciones).
- **Safari/iPad**: Compartir ▸ *Añadir a pantalla de inicio*.
- **Android**: menú ▸ *Instalar aplicación*.

La PWA tiene manifiesto (`/manifest.webmanifest`), icono, `display: standalone`
y un service worker que cachea solo estáticos. Las páginas y `/api/` siempre van
a la red para no servir progreso, sesiones o resultados obsoletos.

## Cuándo tendría sentido un wrapper nativo

Si más adelante hace falta una app de escritorio “de verdad”, la ruta recomendada
es **Tauri 2** con la web existente y dos sidecars:

```text
SLAnything.app
  ├─ Tauri shell (WebView) → http://127.0.0.1:3000
  ├─ sidecar backend FastAPI + SQLite
  └─ sidecar opencode (binario por plataforma)
```

Ventajas: ventana nativa, menú, actualizaciones y acceso local sin Docker.
Costes: compilar y firmar para tres sistemas, versionar el binario de OpenCode,
gestionar el puerto local, migraciones de SQLite y el sandbox de Python.

Mientras eso no sea un requisito, Docker + PWA cubre escritorio y móvil con el
mismo código. La app de escritorio oficial de OpenCode no sustituye a SLAnything:
no tiene el catálogo, el progreso, los quizzes ni el contrato de unidades.

## Alternativas descartadas por ahora

- **Electron**: funciona, pero añade ~150 MB y un runtime propio para cargar la
  misma web.
- **Solo frontend estático**: no puede ejecutar OpenCode ni Python de forma
  segura.
- **Dos interfaces separadas**: ya existen Next y Jinja como fallback; añadir una
  tercera multiplicaría la deuda sin mejorar el producto.

## Criterio para revisar la decisión

Se creará un ADR nuevo y un wrapper Tauri cuando se cumpla alguna de estas
condiciones:

- Más del 30 % del uso sea offline o en equipos sin Docker.
- Se necesite integración con el sistema de archivos local (arrastrar carpetas,
  importar bibliotecas, exportar a PDF).
- Se publique una edición de pago que requiera firma, actualizaciones y soporte
  de escritorio.
