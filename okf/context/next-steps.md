---
type: Backlog
title: Siguientes pasos
description: Backlog priorizado de SLAnything tras convertirla en plataforma genérica con perfiles individual, academia y superadmin.
tags: [backlog, roadmap, calidad, accesibilidad, producto]
status: stable
stale_after: 2026-12-31T00:00:00Z
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
sources:
  - id: roadmap
    resource: /project/roadmap.md
    title: Roadmap del proyecto
  - id: status
    resource: /project/status.md
    title: Estado actual
---

# Prioridad 0 · Tras la plataforma genérica (2026-11-14)

- Generar unidades reales con un proveedor y documentos de materias no técnicas
  (historia, derecho, idiomas) y revisar que lecciones, quiz y glosario no
  arrastren supuestos de programación.
- E2E de Playwright del asistente del Estudio (subida → temario → revisión →
  publicar) por perfil: cuenta individual y profesorado.
- Decidir si el alumnado debe ver solo los cursos asignados (hoy ve todos los
  publicados de su academia, con los asignados primero).
- Revisar en navegador `/plataforma` a 768 px y en tema oscuro.
- Rehacer las capturas de `docs/capturas/` con la portada y los perfiles nuevos.

# Prioridad 0 (anterior) · Consolidar SLAnything 2.0 (2026-11-13)

- ~~Probar en navegador el Estudio por etapas, la analítica y la administración
  y actualizar los E2E de Playwright.~~ Hecho en parte el 2026-11-14 (E2E por
  perfiles; falta el asistente del Estudio).
- Generar una unidad real con un proveedor (PDF de ~40 páginas) midiendo
  tiempo, coste y % de bloques con cita.
- Recuperación de contraseña y verificación de correo (servicio SMTP/Resend),
  invitaciones por correo y OAuth Google/Microsoft.
- ~~Aplicar las matrículas: «Mis cursos» con fechas límite.~~ Hecho
  (2026-11-14); falta el catálogo restringido por grupo si se decide.
- Migrar lección, quiz, progreso, glosario y catálogo a los componentes nuevos;
  reproductor a tres columnas con panel de fuentes y tutor.
- Repaso espaciado y flashcards; preguntas de respuesta corta corregidas por IA.
- SQLAlchemy/Alembic y PostgreSQL; claves de proveedor por espacio cifradas.
- ~~Superadministración de plataforma (`/plataforma`).~~ Hecho (2026-11-14);
  quedan planes de pago y medidores de uso por proveedor.

# Prioridad 0 (anterior) · Cerrar la entrega

- Probar el Estudio con el proveedor real del centro y una unidad completa
  (PDF de un capítulo, ES/EN) midiendo tiempo, coste y calidad.
- Decidir si los cursos generados necesitan revisión editorial obligatoria antes
  de publicarse o si el borrador + validación es suficiente.
- ~~Publicar el segundo curso o explicar `coming_soon`.~~ Resuelto por
  [ADR-020](/decisions/adr-020-generic-platform.md): no hay placeholder.
- Revisar la interacción profunda de los 15 labs en Chrome/Edge; el montaje ya
  está automatizado con `npm run e2e:labs`.
- Validar el responsive de las páginas nuevas (360, 768 y 1440 px) y la vista
  inglesa de los capítulos 2-7.
- ~~Retirar Jinja.~~ Hecho en 2.0 (ADR-013).
- Reconstruir las imágenes Docker (ahora `slanything-*`) y repetir el smoke
  contra Compose con `AULA_SAMPLE_COURSES=0` y `=1`.

# Prioridad 1 · Calidad

- Suite Playwright del Estudio: subida, polling, log, reparación, publicación y
  borrado.
- Editor de revisión del paquete generado antes de publicar (hoy se revisa
  abriendo el curso y el log).
- Suite Playwright completa: interacción de cada lab, runner Python, quiz,
  revisión y cambio ES/EN.
- Auditoría de accesibilidad con axe y lector de pantalla.
- Pruebas de carga ligeras del quiz, del corpus y del sandbox.
- Capturas automáticas de regresión visual, incluida la vista inglesa.
- Revisar que los 15 labs mantienen el idioma y el foco de teclado.

# Prioridad 2 · Producto

- Exportar apuntes y progreso a Markdown/PDF.
- Certificado de finalización del curso.
- Repaso espaciado y recomendaciones de repaso entre capítulos.
- Modo offline de las lecciones ya visitadas.
- Más idiomas sobre el mismo modelo de bundles (francés, portugués…).

# Prioridad 3 · Plataforma

- Separar las dependencias de cuaderno (`jupyterlab`, `ipykernel`…) para reducir
  el tamaño de la imagen backend.
- Añadir un perfil de Compose con Caddy/TLS y `AULA_SECURE_COOKIES=1`.
- PostgreSQL y migraciones para despliegues mayores.
- Pool de runners o contenedores efímeros para ejecución Python a escala.
- OAuth y recuperación de contraseña.
- Matrículas y permisos por curso cuando exista más de un curso publicado.
- Cola de generación separada del backend y cuotas por profesor/proveedor.
- OCR opcional para PDFs escaneados.
- Wrapper Tauri 2 si se necesita escritorio offline; ver `docs/DESKTOP.md`.
- Exportar/importar paquetes `course.json` para edición externa y control de
  versiones.

# Criterio de “entrega cerrada”

1. Catálogo y 7 capítulos navegables en Next y Jinja.
2. 15 labs con interacción real y al menos un smoke automatizado por capítulo.
3. 7 quizzes con revisión.
4. Glosario global sin términos repetidos.
5. Progreso aislado por curso y migración v1→v2 verificada.
6. Tests de contenido y flujo en verde.
7. Capturas y README actualizados.
8. OKF actualizado y validador en verde.
