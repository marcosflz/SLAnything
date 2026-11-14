---
type: Design System
title: Diseño y experiencia de SLAnything
description: Identidad, sistema visual, pantallas, responsive, modo oscuro y accesibilidad.
tags: [ux, diseno, css, accesibilidad, responsive]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
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
- Lema: «Convierte cualquier material en un curso». Marca «S» y subtítulo
  «Aula virtual»; ningún texto fijo de la interfaz menciona una materia concreta
  ([ADR-020](/decisions/adr-020-generic-platform.md)).
- Tono: cercano, riguroso, sin hype; español de España.
- Paleta: azul tinta, azul académico, ámbar, verde, rojo y neutros cálidos.
- Tipografía: pila del sistema (Inter/Segoe UI/system-ui) + monoespaciada para código.

# Estructura visual

- **Interfaz principal:** Next.js (`frontend/`) reproduce el shell, las páginas y
  los componentes; Jinja (`webapp/templates/`) es el fallback de diseño.
- **Público:** nav (Cómo funciona · Para quién · Biblioteca), hero con el flujo
  documento → temario → curso, «Cómo funciona» en tres pasos, «Para quién»
  (cuenta individual, academia, alumno con código → `/registro?tipo=…`),
  funciones, biblioteca abierta (solo si hay cursos públicos), CTA y footer.
- **Registro:** elección de cuenta individual, academia (pide el nombre) o
  código de clase; con `?invite=` muestra la academia y el rol de la invitación.
  Login con las cuatro cuentas demo si la siembra está activa.
- **Catálogo:** `/cursos` agrupa «Asignados por tu academia», el resto y «Cursos
  de ejemplo»; las tarjetas muestran fuente, nivel, labs (solo si hay) y la
  insignia «Asignado · fecha» o «Curso de ejemplo». Estado vacío por perfil.
- **Inicio por perfil:** sin curso, saludo y CTA (Estudio para quien crea,
  biblioteca para el alumnado); con curso, KPIs y «Tus cursos». Cuentas con
  Estudio ven «Tus unidades» (trabajos, borradores y cuota); profesorado y
  administración, accesos a analítica, estudiantes e invitaciones.
- **Bienvenida:** `/bienvenida` para usuarios sin espacio (código, cuenta
  individual o academia).
- **Plataforma:** `/plataforma/*` con pestañas, KPIs globales y tablas de
  usuarios, espacios (cuota y plazas editables) y cursos.
- **App:** navegación por permisos (Aprender · Crear/Enseñar · Administrar
  academia · Plataforma; solo se marca la entrada más específica). Sidebar de
  286 px con una tarjeta de contexto del curso activo (o un estado vacío) y las
  lecciones agrupadas por capítulo (`<details>`; el capítulo activo se abre
  solo), colapsable en escritorio (estado persistido y aplicado antes de pintar),
  topbar con búsqueda global, selector ES/EN, tema y usuario, contenido máximo
  1180 px y footer. El cambio de curso se hace desde «Cursos», no desde enlaces
  duplicados en la sidebar.
- **Curso:** `/cursos/{slug}` con hero, crédito del libro, progreso y secciones
  `#capitulo-N`, cada una con sus lecciones y progreso parcial. `/curso` abre el
  curso activo y redirige a `/cursos` si no hay ninguno.
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

# Rediseño 2026-11-13 · «Moodle moderno»

- Sistema de diseño en [ADR-014](/decisions/adr-014-design-system.md):
  Tailwind v4, componentes propios (Radix), gráficos Recharts con tabla
  alternativa, iconos lucide.
- **Shell**: sidebar clara con selector de espacio (personal/academias, crear
  academia, unirse con código), navegación por rol (Aprender · Crear y enseñar ·
  Administrar), temario del curso actual con estado por lección; topbar con
  búsqueda/comandos ⌘K o «/», idioma, tema y menú de usuario.
- **Inicio**: saludo con «Continuar», KPIs (estudio semanal, progreso, nota
  media, racha), tiempo de estudio 28 días, preguntas a repasar, dominio por
  capítulo, evolución de notas y cursos del espacio.
- **Analítica**, **Estudio** (asistente por pasos y revisión) y
  **Administración** descritos en [generation](/architecture/generation.md) y
  [tenancy-analytics](/architecture/tenancy-analytics.md).
- `loading.tsx` con esqueletos en las rutas principales.
- Las lecciones generadas muestran «Fuente: p. N» bajo cada bloque citado; el
  quiz admite respuesta múltiple.
- Pendiente: migrar lección, quiz, progreso, glosario y catálogo a componentes
  nuevos; revisión visual a 360/768/1440 px y con lector de pantalla.
