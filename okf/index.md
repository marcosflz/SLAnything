---
okf_version: "0.2"
---

# SLAnything · contexto persistente

Este bundle OKF es la **memoria de trabajo** del proyecto. Cualquier agente debe
leerlo al empezar una sesión y actualizarlo al terminarla. El código, los tests y
la documentación fuente mandan si hay contradicciones.

## Empieza aquí

* [Playbook de sesión](/context/session-playbook.md) - Cómo arrancar, trabajar y cerrar una sesión sin perder contexto.
* [Estado actual](/project/status.md) - Qué está entregado, qué se está tocando y qué falta.
* [Problemas conocidos](/context/known-issues.md) - Limitaciones y deudas que no deben redescubrirse.
* [Siguientes pasos](/context/next-steps.md) - Backlog priorizado tras abrir la biblioteca multi-curso.
* [Glosario del proyecto](/context/glossary.md) - Vocabulario interno para leer el resto del bundle.

## Proyecto

* [Visión](/project/vision.md) - Misión, usuarios, principios y no objetivos.
* [Estado](/project/status.md) - Entrega, cifras, servidor, tests y handoff.
* [Roadmap](/project/roadmap.md) - Capítulos, fases y evolución prevista.

## Producto

* [Cursos](/product/course.md) - Catálogo modular, curso de referencia y experiencia de aprendizaje.
* [Lecciones](/product/lessons.md) - Las 56 lecciones del curso de referencia, con slugs, labs y figuras.
* [Laboratorios](/product/labs.md) - Los 15 labs interactivos y su contrato.
* [Ejemplos Python](/product/python-examples.md) - Los 26 ejemplos ejecutables y descargables.
* [Quizzes](/product/quiz.md) - Siete evaluaciones, corrección y revisión.
* [Diseño y UX](/product/ux.md) - Sistema visual, páginas, responsive y tema claro/oscuro.

## Arquitectura

* [Visión general](/architecture/overview.md) - Stack, flujo de una petición y mapa de carpetas.
* [Backend](/architecture/backend.md) - FastAPI, routers, dependencias y repositorios.
* [Frontend](/architecture/frontend.md) - UI Next.js, shell, CSS, JS y carga de laboratorios.
* [Frontend Next.js](/architecture/nextjs-frontend.md) - App Router, componentes, rutas y build.
* [API JSON](/architecture/api.md) - Contrato `/api/v1`, rewrites, CSRF y descargas.
* [Internacionalización](/architecture/i18n.md) - Fuentes ES/EN, export y selección de idioma.
* [Ejecución Python](/architecture/execution.md) - Runner aislado, límites y editor.
* [Modelo de datos](/architecture/data-model.md) - Tablas SQLite y relaciones.
* [Seguridad](/architecture/security.md) - scrypt, sesiones, CSRF, rate limit y cabeceras.
* [Modelo de contenido](/architecture/content-model.md) - Cómo se escribe y valida una lección.
* [Estudio de autoría](/architecture/authoring.md) - Documentos, OpenCode, contrato JSON y catálogo dinámico.

## Operaciones

* [Arranque](/operations/run.md) - Comandos, cuentas, variables y problemas típicos.
* [Frontend Next.js](/operations/frontend.md) - Arranque, build, smoke y troubleshooting.
* [Pruebas](/operations/testing.md) - Suite de 95 tests, validadores de capítulo y E2E.
* [Despliegue](/operations/deployment.md) - Producción mínima con SQLite y TLS.
* [Mapa del repositorio](/operations/repository-map.md) - Qué vive en cada carpeta.

## Decisiones

* [ADRs](/decisions/index.md) - Registro de decisiones de arquitectura.
* [ADR-001 · FastAPI + Jinja](/decisions/adr-001-fastapi-jinja.md)
* [ADR-002 · SQLite](/decisions/adr-002-sqlite.md)
* [ADR-003 · Contenido en Python](/decisions/adr-003-content-python.md)
* [ADR-004 · Labs en JS vanilla](/decisions/adr-004-vanilla-js-labs.md)
* [ADR-005 · OKF como memoria](/decisions/adr-005-okf-memory.md)
* [ADR-006 · Ejecución Python](/decisions/adr-006-server-python.md)
* [ADR-007 · Contenido bilingüe](/decisions/adr-007-bilingual-content.md)
* [ADR-008 · Frontend Next.js](/decisions/adr-008-nextjs-frontend.md)
* [ADR-009 · Docker](/decisions/adr-009-docker.md)
* [ADR-010 · Programa multi-capítulo](/decisions/adr-010-multi-chapter.md)
* [ADR-011 · Catálogo multi-curso](/decisions/adr-011-multi-course.md)
* [ADR-012 · Estudio de autoría con OpenCode](/decisions/adr-012-authoring-opencode.md)

## Referencias e historial

* [Fuentes](/references/sources.md) - Documentación, libro, especificación OKF y enlaces.
* [Comandos](/references/commands.md) - Chuleta de comandos del proyecto.
* [Historial de cambios](/log.md) - Entradas newest-first con las modificaciones del OKF.
