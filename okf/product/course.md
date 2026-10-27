---
type: Course
title: Catálogo de cursos de SLAnything
description: Estructura modular de la biblioteca, curso de referencia basado en Build a Large Language Model (From Scratch), progreso y experiencia de aprendizaje.
tags: [curso, producto, aprendizaje, catalogo, cursos, capitulos]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T22:00:00Z }
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

SLAnything es una **biblioteca de cursos interactivos** bilingüe (español e
inglés), sin instalación y sin GPU. Cada curso parte de un libro y lo convierte
en un recorrido guiado con lecciones, figuras, laboratorios, ejemplos de Python
ejecutables, quizzes y progreso propio.

El primer curso, **Construye un LLM desde cero**, recorre *Build a Large Language
Model (From Scratch)* de Sebastian Raschka: desde entender qué es un LLM hasta
tokenizar texto, implementar atención, montar un GPT, preentrenarlo, clasificar y
ajustarlo para seguir instrucciones.

# Estructura de la plataforma

- **Catálogo (`/cursos`):** tarjetas de cursos con libro, nivel, duración,
  laboratorios y progreso del estudiante.
- **Detalle (`/cursos/{slug}`):** portada del curso, crédito del libro, temario
  por capítulos, progreso y acceso a las lecciones.
- **Curso activo:** la sidebar muestra el curso de la lección abierta y permite
  volver al catálogo.
- **Progreso independiente:** lecciones, apuntes, marcadores e intentos se
  guardan por curso.
- **Cursos generados:** el Estudio publica unidades con prefijo `gen-` que
  aparecen en el mismo catálogo, detalle, lección, quiz y progreso. Se pueden
  despublicar sin borrar el paquete.
- **Curso por defecto:** `llm-desde-cero`; `/curso` sigue funcionando como alias
  autenticado para enlaces históricos.
- **Nuevos libros:** se incorporan como un `Program` con capítulos y una entrada
  en `CATALOGS`; la interfaz y la API no cambian.

# Curso de referencia

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

1. Landing pública → catálogo de cursos.
2. Detalle público del curso → registro o cuenta demo.
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

- Estudiante demo: `demo@aulallm.local / demo1234`.
- Profesora: `profe@aulallm.local / profe1234`.
- Registro abierto en `/registro`.

# Fuera del curso

No hay foros, vídeo ni certificados oficiales. La ejecución de Python ocurre en
el servidor, no en el navegador; el aislamiento tiene límites y se documenta en
[seguridad](/architecture/security.md). La matrícula explícita y los cursos
cerrados quedan como siguiente paso. El alcance está en
[visión](/project/vision.md) y [problemas conocidos](/context/known-issues.md).
