---
type: Design System
title: Diseño y experiencia de SLAnything
description: Identidad, sistema visual, pantallas, responsive, modo oscuro y accesibilidad.
tags: [ux, diseno, css, accesibilidad, responsive]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-27T10:30:00Z }
sources:
  - id: css
    resource: ../../webapp/static/css/app.css
    title: Sistema de diseño
  - id: base
    resource: ../../webapp/templates/base.html
    title: Shell y navegación
  - id: next-shell
    resource: ../../frontend/src/components/AppShell.tsx
    title: Shell Next.js
  - id: next-public
    resource: ../../frontend/src/components/PublicShell.tsx
    title: Shell público Next.js
---

# Identidad

- Nombre: **SLAnything**.
- Lema: «Aprende IA desde los libros que la explican».
- Tono: cercano, riguroso, sin hype; español de España.
- Paleta: azul tinta, azul académico, ámbar, verde, rojo y neutros cálidos.
- Tipografía: pila del sistema (Inter/Segoe UI/system-ui) + monoespaciada para código.

# Estructura visual

- **Interfaz principal:** Next.js (`frontend/`) reproduce el shell, las páginas y
  los componentes; Jinja (`webapp/templates/`) es el fallback de diseño.
- **Público:** nav superior, hero de biblioteca a dos columnas, catálogo de
  cursos, features, detalle del curso de referencia, pasos, CTA y footer.
- **Catálogo:** `/cursos` con tarjetas de curso, libro, metadatos y progreso;
  incluye una tarjeta «En preparación» para los próximos libros.
- **App:** sidebar de 286 px con una tarjeta de contexto del curso activo y las
  lecciones agrupadas por capítulo (`<details>`; el capítulo activo se abre
  solo), colapsable en escritorio (estado persistido y aplicado antes de pintar),
  topbar con búsqueda global, selector ES/EN, tema y usuario, contenido máximo
  1180 px y footer. El cambio de curso se hace desde «Cursos», no desde enlaces
  duplicados en la sidebar.
- **Curso:** `/cursos/{slug}` con hero, crédito del libro, progreso y secciones
  `#capitulo-N`, cada una con sus 8 lecciones y progreso parcial. `/curso` se
  mantiene como alias del curso por defecto.
- **Lección y quiz:** muestran el capítulo activo; la navegación anterior/siguiente
  cruza capítulos y el final del curso vuelve al programa.
- **Lección:** contenido + aside sticky con progreso, apuntes, marcador y quiz.
- **Quiz:** tarjetas de pregunta, barra de progreso y revisión.
- **Profesor:** tarjetas de métricas y tabla de estudiantes.

# Componentes

Botones, badges, cards, stat cards, progress bars, ring SVG con circunferencia
real, lesson rows, callouts,
figures con lightbox, code blocks, editores Python con salida, labs, token chips,
heatmap, pipeline, quiz cards, tablas, glosario, auth y empty states.

# Idioma

El selector ES/EN vive en la topbar de la app y en la nav pública. Cambia la cookie
`aula_lang` y recarga la misma ruta; el contenido, las etiquetas, el quiz, el
glosario y los meses de las fechas cambian de idioma. Los slugs no cambian.

# Responsive

- 1180 px: hero y dashboard a una columna.
- 1024 px: sidebar fija con backdrop; menú móvil.
- 820 px: grids a una columna; búsqueda oculta en topbar.
- 600 px: tipografía y paddings reducidos; quiz y stats a una columna.
- Verificado sin overflow a 360, 768 y 1440 px.

# Tema claro y oscuro

El **tema claro es el predeterminado**. Variables CSS con
`html[data-theme="dark"]`; la elección del usuario se guarda en
`localStorage("aula-theme")` y se aplica antes de pintar para evitar flash. Si no
hay preferencia guardada, se usa el tema claro aunque el sistema prefiera oscuro;
el botón de la topbar permite cambiarlo.

# Accesibilidad

- Skip link, landmarks, foco visible, `prefers-reduced-motion`.
- Contraste AA en ambos temas.
- Formularios etiquetados; radios dentro de `label`.
- Lightbox con `dialog`; figuras con `alt` y botón de ampliación.
- Navegación por teclado en login, lecciones, quiz y menú.

# Capturas

En `docs/capturas/` hay 21 imágenes de referencia (landing, dashboard, curso,
lección, labs, quiz, glosario, recursos, progreso, login, registro, móvil y modo
oscuro). El README usa `00b_landing_programa.png` como portada y muestra el
resto agrupado por área; `docs/capturas/README.md` describe cada archivo.
