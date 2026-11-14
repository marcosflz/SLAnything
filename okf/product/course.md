---
type: Course
title: Catálogo de cursos de SLAnything
description: Biblioteca genérica por espacio, cursos generados desde el Estudio, curso de ejemplo opcional (Build a Large Language Model) y experiencia de aprendizaje.
tags: [curso, producto, aprendizaje, catalogo, cursos, capitulos]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-11-14T12:00:00Z }
sources:
  - id: catalog
    resource: ../../webapp/content/catalog.py
    title: Modelo Course y validación del catálogo
  - id: course
    resource: ../../webapp/content/course.py
    title: Programas y catálogo ensamblado
  - id: readme
    resource: ../../README.md
    title: README del proyecto
---

# Propuesta

SLAnything es un **aula virtual genérica** y bilingüe (español e inglés): convierte
cualquier material de aprendizaje (apuntes, libros, manuales, artículos) en
cursos con lecciones guiadas, citas a la fuente, cuestionarios, glosario y
progreso propio. El contenido llega del **Estudio**; la plataforma no depende de
ningún curso concreto ([ADR-020](/decisions/adr-020-generic-platform.md)).

El repositorio incluye un **curso de ejemplo** opcional, **Construye un LLM desde
cero** (*Build a Large Language Model (From Scratch)*, Sebastian Raschka), que
solo aparece con `AULA_SAMPLE_COURSES=1`. Es el escaparate de lo que admite el
modelo de contenido estático: figuras, 15 laboratorios y Python ejecutable.

# Estructura de la plataforma

- **Biblioteca (`/cursos`):** cursos del espacio activo, cursos abiertos de la
  plataforma y, si están activos, de ejemplo; los asignados por la academia van
  primero con su fecha límite.
- **Detalle (`/cursos/{slug}`):** portada del curso, fuente, temario por
  capítulos, progreso y acceso a las lecciones.
- **Curso activo:** la sidebar muestra el curso de la lección abierta y permite
  volver al catálogo.
- **Progreso independiente:** lecciones, apuntes, marcadores e intentos se
  guardan por curso.
- **Cursos generados:** el Estudio publica unidades con prefijo `gen-` que
  aparecen en el mismo catálogo, detalle, lección, quiz y progreso. Se pueden
  despublicar sin borrar el paquete.
- **Curso activo:** el pedido, el último abierto o el primero publicado; puede
  no haber ninguno (estado vacío). `/curso` abre el curso activo.
- **Glosario y recursos por curso:** cada curso tiene su glosario y sus recursos
  (documentos fuente y descargas de código en los generados).
- **Cursos estáticos:** se pueden añadir más ejemplos como un `Program` con
  capítulos y una entrada en `CATALOGS`; no es el camino habitual.

# Curso de ejemplo (`llm-desde-cero`)

- **Capítulos:** 7 (entender los LLM, trabajar con texto, atención, arquitectura
  GPT, pretraining, clasificación e instrucciones).
- **Lecciones:** 56 (8 por capítulo).
- **Duración estimada:** 584 minutos.
- **Laboratorios:** 15.
- **Evaluación:** 7 quizzes de 10 preguntas, 80 % para aprobar.
- **Glosario:** 113 términos.
- **Idiomas:** español e inglés, con el mismo slug y progreso compartido.
- **Ejemplos ejecutables:** 26 bloques Python, ejecución aislada en servidor y
  descarga `.py` por bloque o por lección.
- **Libro:** *Build a Large Language Model (From Scratch)*, Sebastian Raschka,
  Manning, 2024.
- **Requisitos:** navegador; el servidor corre con Python/uv.

# Recorrido del estudiante

1. Landing pública → «Para quién» → registro como cuenta individual, academia o
   alumno con código (o invitación).
2. Cuenta individual o profesorado: Estudio → subir documento → temario →
   generar → revisar → publicar. Alumno: cursos que publica o asigna su academia.
3. Dashboard con siguiente lección, progreso del curso y acceso a «Tus cursos».
4. Catálogo para cambiar de curso sin perder el avance.
5. Curso con los capítulos agrupados y sus lecciones.
6. Lección con objetivos, contenido, figuras, código y labs.
7. Editar y ejecutar los ejemplos Python; descargarlos si se prefiere local.
8. Marcar completada, guardar apuntes y marcador.
9. Repaso y quiz del capítulo.
10. Revisión del intento y panel de progreso global.

# Diseño de aprendizaje

- Una idea → una imagen o demo → una comprobación.
- Preguntas antes de revelar la respuesta.
- Laboratorios con controles que cambian el resultado.
- El quiz no penaliza repetir; busca detectar huecos.
- Las explicaciones conectan cada fallo con la lección correspondiente.
- Cada capítulo cierra con un repaso y una autoevaluación.

# Cuentas

- Alumno: `alumno@slanything.local / alumno1234` (Academia Demo).
- Profesora y propietaria de la academia: `profe@slanything.local / profe1234`.
- Cuenta individual: `autodidacta@slanything.local / auto1234`.
- Superadmin: `admin@slanything.local / admin1234`.
- Registro abierto en `/registro` (individual, academia o código de clase).

# Fuera del curso

No hay foros, vídeo ni certificados oficiales. La ejecución de Python ocurre en
el servidor, no en el navegador; el aislamiento tiene límites y se documenta en
[seguridad](/architecture/security.md). La matrícula explícita y los cursos
cerrados quedan como siguiente paso. El alcance está en
[visión](/project/vision.md) y [problemas conocidos](/context/known-issues.md).
