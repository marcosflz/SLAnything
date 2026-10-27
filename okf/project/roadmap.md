---
type: Roadmap
title: Roadmap de SLAnything
description: Plan de evolución desde el curso de siete capítulos entregado hasta una plataforma multi-curso con autoría asistida.
tags: [roadmap, capitulos, planificacion]
status: stable
stale_after: 2026-12-31T00:00:00Z
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Capítulos

| # | Tema | Cuaderno | Aula web |
|---|---|---|---|
| 1 | Entender los LLM | listo | **listo** |
| 2 | Trabajar con texto | — | **listo** |
| 3 | Atención | — | **listo** |
| 4 | Arquitectura GPT | — | **listo** |
| 5 | Pretraining | — | **listo** |
| 6 | Clasificación | — | **listo** |
| 7 | Instrucciones | — | **listo** |

# v1.1 · curso completo

Entregado el 24 de octubre de 2026:

- 7 capítulos, 56 lecciones y 584 minutos.
- Navegación multi-capítulo y progreso global por slug.
- 15 laboratorios y 26 ejemplos Python ejecutables.
- 7 quizzes de 10 preguntas y glosario de 113 términos.
- Contenido ES/EN completo.
- Catálogo multi-curso (`/cursos`) y progreso aislado por `course_slug`.
- 111 tests, build de Next, smoke y E2E con Playwright.

# v1.2 · Estudio y calidad

Entregado el 24 de octubre de 2026:

- Estudio `/estudio` con documentos → unidades, OpenCode en Docker, proveedor
  configurable, borrador/publicación y catálogo dinámico.
- PWA instalable y decisión web + PWA documentada.

Pendiente:

1. Publicar el segundo curso y retirar el placeholder `coming_soon`.
2. Automatizar la interacción visual de los 15 labs con Playwright.
3. Revisión de accesibilidad con axe y lector de pantalla.
4. Exportación de apuntes y progreso a Markdown/PDF.
5. Repaso espaciado y recomendaciones de repaso.
6. Capturas de regresión visual ES/EN.
7. Endurecer el sandbox para despliegues públicos.

# v1.3 · certificación y escala

- Certificado de finalización del curso.
- Modo offline de las lecciones visitadas.
- Analítica básica y paneles de clase.
- Pool de runners o contenedores efímeros para ejecución Python.

# v2 · plataforma

- PostgreSQL y un sistema general de migraciones.
- OAuth, recuperación de contraseña y verificación de correo.
- Matrículas, foros y varios cursos publicados.
- Más idiomas sobre el mismo modelo de bundles.

# Regla de crecimiento

Añadir un capítulo no debe requerir cambios en los routers ni en el esquema. Se
resuelve con un paquete autocontenido en `webapp/content/chapters/chNN/`, sus
exports (`CHAPTER_ES/EN`, quizzes, glosario y labs) y, si hace falta, nuevos labs,
ejemplos Python y estilos.

Añadir un curso tampoco debe requerir cambios en el motor: se crea un `Program`,
se envuelve en un `Course` con su `Book` y se registra en `CATALOGS`. El catálogo,
la sidebar, la API y el progreso por `course_slug` ya están preparados. El
contenido nuevo debe funcionar en Next y en Jinja.
