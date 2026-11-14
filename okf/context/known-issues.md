---
type: Known Issues
title: Problemas conocidos y limitaciones
description: Bugs, deudas técnicas y limitaciones conscientes de SLAnything, con impacto y workaround.
tags: [bugs, deuda-tecnica, limitaciones, operaciones]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T18:00:00Z }
sources:
  - id: qa
    resource: ../../docs/QA.md
    title: Informe de QA
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Bloqueantes

No hay ningún bug bloqueante conocido a 14 de noviembre de 2026. La suite de 181
tests pasa, el build de Next compila, el smoke y el E2E por perfiles pasan con y
sin cursos de ejemplo (biblioteca vacía, alumno, autodidacta, academia y
superadmin), y los 15 labs del ejemplo montan sin errores.

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
- **Curso de ejemplo opcional.** El único curso estático es `llm-desde-cero` y
  solo aparece con `AULA_SAMPLE_COURSES=1`. Sin él la biblioteca empieza vacía
  y el contenido llega del Estudio ([ADR-020](/decisions/adr-020-generic-platform.md)).
  Los 15 laboratorios JS solo los usa ese ejemplo.
- **Sin recuperación de contraseña ni OAuth.** Las cuentas se crean con correo y
  contraseña; no hay verificación de correo.
- **SQLite y un solo proceso.** No está pensado para escritura concurrente intensa;
  el rate limit de login vive en memoria y no se comparte entre workers.
- **Migración v2 manual en código.** `init_db()` renombra las tablas v1 sin
  `course_slug`, copia sus datos al curso de ejemplo y las elimina. Desde v4 los
  cambios van en `webapp/migrations.py`.
- **Sin suite E2E completa de interacciones.** `npm run e2e` recorre la portada,
  el alta individual, los cuatro perfiles, el menú activo, el tema, el idioma y
  el móvil a 360 px (y, con ejemplos, lección, lab, runner y quiz);
  `npm run e2e:labs` comprueba que los 15 labs montan sin errores de consola.
  El flujo del Estudio en navegador (subida, temario, revisión) sigue sin E2E. La interacción profunda de cada control
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

1. Probar el Estudio con un proveedor real y documentos de materias no técnicas.
2. Tests E2E de interacción profunda de los 15 laboratorios y del flujo completo.
3. Revisión visual y responsive de los capítulos 2-7 en ES/EN.
4. PostgreSQL y SQLAlchemy/Alembic si crece la concurrencia.
5. Rate limit persistente si se despliega con más de un worker.
6. Revisión con lector de pantalla (axe o VoiceOver/NVDA).

# Tras la evolución 2026-11-13

- **Estudio en navegador sin E2E.** El flujo completo se probó por API contra
  los servidores reales (LLM falso): generar, publicar, asignar a un grupo y
  verlo como alumno. Falta automatizar el asistente en Playwright.
- **Motor direct sin probar con un proveedor real.** Los tests usan
  `FakeLLM`. Las URLs base de OpenCode Zen/Go en `generation/llm.py` son una
  suposición; se pueden fijar con `base_url`.
- **Respaldo de citas léxico**: solo compara vocabulario en el idioma principal.
- **Sin correo**: las invitaciones son enlaces que la administración copia.
- **Sin recuperación de contraseña, verificación de correo, OAuth ni 2FA.**
- **SQLite y un proceso**; PostgreSQL pendiente ([ADR-015](/decisions/adr-015-versioned-migrations.md)).
- **Matrículas**: el catálogo marca los cursos asignados y su fecha límite y los
  pone primero, pero no restringe el resto de cursos publicados de la academia.
- **Páginas heredadas** (lección, quiz, progreso, glosario, catálogo, landing,
  `/profesor`) siguen con estilos de `app.css` dentro del shell nuevo.
- Los ajustes del proveedor siguen siendo globales de plataforma (no por
  espacio) y la API key sigue en `settings.json`. La cuota mensual sí se puede
  fijar por espacio desde `/plataforma/espacios`.

# Registro por invitación (2026-11-14)

- **Sin correo saliente.** Las invitaciones son enlaces que se copian y se
  envían a mano; no hay aviso por correo ni reenvío.
- **Cambio de rol fuera de invitaciones.** Un owner puede ascender a un alumno a
  profesorado desde `/admin/usuarios`; el registro cerrado solo limita las altas.
- **Código de clase.** Sigue funcionando para usuarios ya registrados (los
  administra la academia); no crea cuentas nuevas.

# Tras la plataforma genérica (2026-11-14)

- **`users.role` heredado.** Ya no se lee ni se envía al frontend; la columna se
  conserva en el esquema.
- **Biblioteca por espacio activo.** Un curso de la academia no aparece en la
  cuenta individual del mismo usuario (y viceversa); para verlo hay que cambiar
  de espacio.
- **El superadmin no hereda la gestión de academias ajenas.** Desde
  `/plataforma` ajusta plan, plazas, cuotas y visibilidad, pero no entra en los
  grupos ni la analítica de una academia de la que no es miembro.
- **Cuentas demo antiguas.** La migración v6 renombra `demo@`/`profe@aulallm.local`
  y les pone las contraseñas nuevas; cualquier otra cuenta `@aulallm.local` se
  conserva tal cual.
