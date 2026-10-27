---
type: Project
title: Visión de SLAnything
description: Plataforma web bilingüe (ES/EN) con Next.js y FastAPI para aprender a construir un LLM y convertir documentos en unidades didácticas con OpenCode.
tags: [producto, vision, educacion, llm]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README del proyecto
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Misión

Convertir libros técnicos en experiencias de aprendizaje guiadas, interactivas y
medibles, bilingües, sin exigir que el estudiante instale Jupyter ni tenga GPU.
El primer curso convierte *Build a Large Language Model (From Scratch)* de
Sebastian Raschka en 7 capítulos interactivos; el catálogo está preparado para
incorporar nuevos libros y el **Estudio** permite crear unidades a partir de
documentos propios con OpenCode. La interfaz principal es Next.js; FastAPI
conserva el contenido, la autenticación, la autoría y la ejecución de Python.

# Usuarios

- **Estudiante:** quiere elegir un curso, entender un tema y practicar sin
  configurar un entorno.
- **Autodidacta:** quiere explorar el catálogo y probar antes de registrarse.
- **Profesor:** quiere ver avance, actividad y resultados del grupo, y convertir
  sus propios documentos en unidades revisables.
- **Autor de contenido:** quiere añadir capítulos o un libro completo sin tocar el
  motor, o subir un PDF y obtener una primera versión publicable.

# Principios

1. **Entender haciendo.** Cada idea va acompañada de una demo, una figura o una
   comprobación.
2. **Sin magia.** El código y las decisiones están a la vista; las estimaciones se
   presentan como estimaciones.
3. **Progreso real.** El estado del estudiante persiste y se puede consultar.
4. **Accesible y sobrio.** Español e inglés claros, diseño responsive, modo oscuro
   y navegación por teclado.
5. **Extensible.** Un capítulo o un curso nuevo debe ser contenido, no una
   reescritura del motor.
6. **Código vivo.** Los ejemplos del libro se pueden editar, ejecutar en un runner
   aislado y descargar.

# No objetivos del MVP

- LMS multi-institución, foros, vídeo o matrículas de pago.
- Ejecución de Python en el navegador (se ejecuta en servidor).
- Certificados oficiales o analítica avanzada.
- Sustituir al libro: cada curso lo acompaña y cita.

# Éxito

Un visitante puede explorar el catálogo, registrarse, recorrer el curso de
referencia (7 capítulos y 56 lecciones) en español o inglés, experimentar con los
15 laboratorios, ejecutar los 26 ejemplos de Python, aprobar los 7 quizzes y ver
su progreso sin ayuda externa. El siguiente hito es publicar el segundo curso y
consolidar calidad, accesibilidad y producto.
