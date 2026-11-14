---
type: Project
title: Visión de SLAnything
description: Aula virtual genérica y bilingüe (ES/EN) con Next.js y FastAPI que convierte cualquier material de aprendizaje en cursos, para cuentas individuales y academias.
tags: [producto, vision, educacion, perfiles]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README del proyecto
  - id: plan
    resource: ../../docs/PLAN_PLATAFORMA_WEB.md
    title: Plan de la plataforma
---

# Misión

Convertir **cualquier material de aprendizaje** (apuntes, libros, manuales,
artículos, de cualquier materia) en cursos guiados, autoevaluables y medibles,
bilingües, sin instalar nada. El **Estudio** genera lecciones con citas a la
fuente, cuestionarios y glosario; la persona revisa el temario y decide qué se
publica. La plataforma no depende de ningún curso concreto: el curso «Construye
un LLM desde cero» es solo un ejemplo opcional
([ADR-020](/decisions/adr-020-generic-platform.md)). La interfaz es Next.js;
FastAPI conserva el contenido, la autenticación, la autoría y la ejecución.

# Usuarios (perfiles, ADR-021)

- **Autodidacta (cuenta individual):** sube su material, genera sus unidades y
  estudia con su propio progreso. No gestiona aulas.
- **Alumno:** entra en una academia por invitación o código, estudia los cursos
  que se publican o le asignan y consulta su progreso. No crea unidades.
- **Profesorado:** crea unidades en el Estudio de su academia y sigue la
  analítica de clase, el alumnado en riesgo y la calidad de las preguntas.
- **Administración de la academia (admin/owner):** además gestiona miembros,
  grupos, matrículas, invitaciones, código de clase y auditoría.
- **Superadmin de la plataforma:** usuarios, espacios, cuotas, cursos abiertos y
  proveedor de IA de toda la plataforma.

# Principios

1. **Entender haciendo.** Cada idea va acompañada de una demo, una figura o una
   comprobación.
2. **Sin magia.** El código y las decisiones están a la vista; las estimaciones se
   presentan como estimaciones.
3. **Progreso real.** El estado del estudiante persiste y se puede consultar.
4. **Accesible y sobrio.** Español e inglés claros, diseño responsive, modo oscuro
   y navegación por teclado.
5. **Genérico.** Ningún texto fijo de la interfaz asume una materia; un curso
   nuevo es contenido (del Estudio), no una reescritura del motor.
6. **Código vivo.** Los ejemplos del libro se pueden editar, ejecutar en un runner
   aislado y descargar.

# No objetivos del MVP

- Foros, vídeo o matrículas de pago. (Desde 2026-11-13 la plataforma sí es
  multi-organización: academias y cuentas personales, ver ADR-016.)
- Ejecución de Python en el navegador (se ejecuta en servidor).
- Certificados oficiales o analítica avanzada.
- Sustituir la fuente: cada curso la acompaña y la cita.

# Éxito

Una persona se registra como cuenta individual, sube un documento de cualquier
materia, revisa el temario y estudia el curso generado en español o inglés. Una
academia invita a su profesorado y alumnado, asigna cursos por grupo con fecha
límite y sigue la analítica. La superadministración ajusta cuotas y visibilidad
sin tocar código. Todo ello con la biblioteca vacía al empezar.
