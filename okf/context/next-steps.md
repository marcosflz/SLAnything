---
type: Backlog
title: Siguientes pasos
description: Backlog priorizado de SLAnything tras abrir el catálogo multi-curso y completar el curso de referencia.
tags: [backlog, roadmap, calidad, accesibilidad, producto]
status: stable
stale_after: 2026-12-31T00:00:00Z
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: roadmap
    resource: /project/roadmap.md
    title: Roadmap del proyecto
  - id: status
    resource: /project/status.md
    title: Estado actual
---

# Prioridad 0 · Cerrar la entrega

- Probar el Estudio con el proveedor real del centro y una unidad completa
  (PDF de un capítulo, ES/EN) midiendo tiempo, coste y calidad.
- Decidir si los cursos generados necesitan revisión editorial obligatoria antes
  de publicarse o si el borrador + validación es suficiente.
- Publicar el segundo curso del catálogo o dejar explícito que `coming_soon` es
  solo una vista de producto.
- Revisar la interacción profunda de los 15 labs en Chrome/Edge; el montaje ya
  está automatizado con `npm run e2e:labs`.
- Validar el responsive de las páginas nuevas (360, 768 y 1440 px) y la vista
  inglesa de los capítulos 2-7.
- Decidir cuándo retirar `webapp/templates/`, `webapp/templating.py` y las rutas
  HTML; hasta entonces son el fallback del puerto 8000.
- Reconstruir las imágenes Docker y repetir el smoke contra Compose.

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
