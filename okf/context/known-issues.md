---
type: Known Issues
title: Problemas conocidos y limitaciones
description: Bugs, deudas técnicas y limitaciones conscientes de SLAnything, con impacto y workaround.
tags: [bugs, deuda-tecnica, limitaciones, operaciones]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: qa
    resource: ../../docs/QA.md
    title: Informe de QA
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Bloqueantes

No hay ningún bug bloqueante conocido a 24 de octubre de 2026. La suite de 111
tests pasa, el build de Next compila y los flujos de estudiante, profesor y
Estudio funcionan a través de los rewrites con el catálogo y los 7 capítulos. La
generación real se validó en Docker con el modelo gratuito de OpenCode.

# Limitaciones del MVP

- **Sin foros, mensajería ni notificaciones.** El alcance Moodle es deliberadamente
  reducido a curso, progreso, quiz, notas y profesor.
- **Python en servidor, no en el navegador.** Los ejemplos se ejecutan en un
  subproceso aislado del servidor; no hay Pyodide/JupyterLite ni kernel
  persistente. El sandbox es defensa en profundidad, no aislamiento de nivel
  producción: para Internet, contenedor sin red o `AULA_EXEC_ENABLED=0`.
- **Laboratorios del capítulo 1 parcialmente traducidos.** Memoria y etiquetas
  están completos en inglés; los párrafos explicativos largos de transformer,
  atención, n-gramas, prompt y coste pueden seguir en español. Los controles
  principales sí se traducen. Los labs nuevos usan diccionario local bilingüe.
- **Un solo curso estático publicado.** El catálogo soporta varios libros y
  cursos generados, pero el contenido curado sigue siendo solo
  `llm-desde-cero`; el Estudio puede publicar unidades nuevas. No hay matrículas
  ni organizaciones.
- **Sin recuperación de contraseña ni OAuth.** Las cuentas se crean con correo y
  contraseña; no hay verificación de correo.
- **SQLite y un solo proceso.** No está pensado para escritura concurrente intensa;
  el rate limit de login vive en memoria y no se comparte entre workers.
- **Migración v2 manual en código.** `init_db()` renombra las tablas v1 sin
  `course_slug`, copia sus datos al curso por defecto y las elimina. No hay un
  sistema general de migraciones versionadas: un cambio de columna futuro requiere
  otro paso idempotente.
- **Sin suite E2E completa de interacciones.** `npm run e2e` cubre login, 7
  capítulos, tema, idioma, quiz y revisión; `npm run e2e:labs` comprueba que los
  15 labs montan sin errores de consola. La interacción profunda de cada control
  sigue validándose con tests de DOM de los módulos, no con Playwright.
- **Jinja sigue presente como fallback.** `webapp/templates/` y las rutas HTML
  del puerto 8000 se mantienen hasta cerrar la paridad. Hay dos interfaces y dos
  copias del CSS (`webapp/static/css/app.css` y `frontend/src/app/app.css`) que
  se sincronizan con `tools/sync_frontend_assets.py`.
- **Labs y runner en el navegador.** Los 15 módulos JS montan en Chrome headless
  y `/api/ejecutar` funciona a través de Next; falta automatizar cada control de
  cada laboratorio, no solo el montaje.
- **Prefetch de lecciones desactivado.** Los enlaces a lecciones usan
  `prefetch={false}` para no inflar `lesson_progress.views` y `activity` con
  visitas anticipadas de Next.
- **IP del rate limit detrás de Next.** FastAPI ve `127.0.0.1` en las peticiones
  proxeadas, así que el límite de login por email+IP no distingue clientes; el
  límite por email sigue activo. Si se necesita granularidad por IP, hay que
  confiar en un proxy propio y leer una cabecera controlada por él.

# Limitaciones del Estudio de autoría

- **Un trabajo a la vez.** El executor tiene un worker; varios profesores pueden
  encolar hasta 3 cada uno, pero se procesan en serie.
- **Sin OCR.** Un PDF escaneado no produce texto; hay que aplicar OCR antes.
- **Contexto acotado.** Se extraen como máximo ~300 000 caracteres; un libro
  completo se recorta. Para más detalle, sube un capítulo o un extracto.
- **El agente puede fallar.** El proveedor puede cortar un stream; el paquete se
  valida y hay una reparación automática, pero un modelo con poco contexto o
  cuota puede no terminar. Revisa el log y reintenta.
- **Sin imágenes ni labs generados.** El contrato permite código, tablas y
  callouts, pero no figuras ni laboratorios. Los cursos generados no tienen
  portada propia.
- **Sin vista previa navegable del borrador.** Para revisar la unidad completa
  hay que publicarla y abrirla; se puede despublicar después. El editor de
  revisión previo está en [next-steps](/context/next-steps.md).
- **La API key vive en el volumen.** `settings.json` tiene permisos 0600, pero
  los backups del volumen incluyen la clave. Rótala si compartes el backup.
- **El Estudio no es un sandbox de nivel producción.** OpenCode corre sin shell,
  web ni directorios externos, pero es un proceso con escritura en su trabajo.
  Para Internet, añade cuotas, TLS y aislamiento adicional.
- **La PWA no es offline completa.** Solo cachea estáticos; las páginas y la API
  requieren red. Una app Tauri offline queda como siguiente paso.
- **Los cursos generados se guardan como JSON.** No se convierten en módulos
  Python versionados; si se borra `aula.db`, se pierden las referencias y hay que
  volver a generarlos (los documentos siguen en `authoring-data/`).

# Avisos de Docker

- Las dos imágenes se construyen y los healthchecks pasan; el flujo E2E también
  se validó contra Compose.
- Solo se publica el frontend (`:3000`). La API y la interfaz Jinja del backend
  quedan en la red interna; para depurar usa `docker compose exec backend`.
- El frontend compila `API_INTERNAL_URL` como build arg. Si cambias el nombre del
  servicio `backend`, hay que reconstruir la imagen.
- La imagen del backend instala el grupo principal completo, incluidas las
  dependencias de cuaderno (`jupyterlab`, `ipykernel`…). Es funcional pero pesada;
  separar un grupo `notebooks` es una optimización pendiente.
- La imagen incluye OpenCode v2.1.4 (`/usr/local/bin/opencode`). El Estudio
  necesita salida a Internet hacia el proveedor; si el contenedor no tiene red,
  la generación falla aunque el resto de la app funcione.
- `/data/authoring` comparte el volumen `aula-llm-data` con SQLite. Un
  `docker compose down -v` borra base de datos, documentos, logs y la API key.
- Compose no incluye TLS. En producción, proxy inverso delante de `:3000`,
  `AULA_SECURE_COOKIES=1` y backups del volumen `aula-llm-data`.
- `docker compose down -v` borra la base de datos. No lo uses sin backup.

# Avisos operativos

- **Servidor Uvicorn obsoleto.** `aula.py` no usa recarga automática. Si cambias
  Python o plantillas y siguen apareciendo errores de nombres (`'t' is undefined`)
  o rutas nuevas en 404, el proceso en marcha es viejo: páralo y vuelve a arrancarlo.
  Esto ocurrió tras la migración de i18n; el código era correcto, pero el proceso
  anterior no tenía `t()` en el contexto.
- El servidor de desarrollo puede estar ocupando el puerto 8000. Para reiniciarlo:

  ```powershell
  $c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
  if ($c) { Stop-Process -Id $c.OwningProcess -Force }
  uv run python aula.py
  ```

- `aula.db` es local y está en `.gitignore`. Si se borra, `init_db()` vuelve a
  sembrar demo y profesor.
- Algunos comprobadores externos llaman a `/v1/models`; no es una ruta de la app y
  devuelve 404. `/health` y `/salud` sí existen.
- Las figuras 1.1–1.9 son de Manning/Raschka y están limitadas a uso educativo.
  No redistribuir fuera del contexto del curso. Los diagramas SVG de los
  capítulos 2-7 son propios y se marcan como tales en la lección.
- La ejecución remota arranca un intérprete por petición: pandas/matplotlib
  tardan más y consumen memoria. Si el servidor no da abasto, baja
  `AULA_EXEC_CONCURRENT` o reparte la ejecución en otro host.
- En instalaciones sin `psutil` o con una política de procesos restrictiva, el
  límite de memoria puede no aplicarse; el de tiempo y salida sí.

# Deuda priorizada

1. Publicar el segundo curso con contenido real y retirar el placeholder.
2. Tests E2E de interacción profunda de los 15 laboratorios y del flujo completo.
3. Revisión visual y responsive de los capítulos 2-7 en ES/EN.
4. Un sistema general de migraciones si se añaden campos nuevos.
5. Rate limit persistente si se despliega con más de un worker.
6. Revisión con lector de pantalla (axe o VoiceOver/NVDA).
