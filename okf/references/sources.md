---
type: Reference
title: Fuentes y documentación
description: Documentos internos y enlaces externos que sostienen el contenido y la arquitectura de SLAnything.
tags: [referencias, fuentes, libro, okf, documentacion]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T12:00:00Z }
sources:
  - id: readme
    resource: ../../README.md
    title: README del proyecto
---

# Documentación interna

| Documento | Ruta | Papel |
|---|---|---|
| README | `../../README.md` | Arranque, alcance, estructura y créditos |
| Plan | `../../docs/PLAN_PLATAFORMA_WEB.md` | Plan de acción, fases, criterios y decisiones |
| Contrato de agentes | `../../docs/CONTRATO_AGENTES.md` | Interfaces y propiedad de archivos del swarm |
| QA | `../../docs/QA.md` | Suite, cobertura y comprobaciones manuales |
| Autoría | `../../docs/AUTHORING.md` | Estudio, proveedores, contrato y seguridad |
| Escritorio | `../../docs/DESKTOP.md` | Web + PWA y ruta a Tauri |
| AGENTS.md | `../../AGENTS.md` | Arranque y obligaciones de mantenimiento del OKF |
| Frontend | `../../frontend/README.md` | Next.js, rewrites, scripts y estructura |
| Migración Next | `../../docs/MIGRATION_NEXTJS.md` | Plan de migración de Jinja a Next |
| Cuaderno | `../../notebooks/capitulo_01_entender_los_llms.ipynb` | Capítulo 1 interactivo en Jupyter |
| Capturas | `../../docs/capturas/` | 21 imágenes de referencia |
| Runner | `../../webapp/sandbox_runner.py` | Ejecución aislada de Python |
| API | `../../webapp/routers/api.py` | Contrato JSON `/api/v1` |

# Libro

- Sebastian Raschka, *Build a Large Language Model (From Scratch)*, Manning, 2024.
- El PDF no se versiona. Las figuras 1.1–1.9 se usan con atribución y solo con
  fines educativos; los derechos son de Manning y del autor.

# Especificación OKF

- [OKF v0.2 · SPEC.md](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
- [Google Cloud Blog · Introducing OKF](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- [Open Knowledge Format Academy](https://openknowledgeformat.academy/)

# Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [SQLite](https://www.sqlite.org/docs.html)
- [Next.js](https://nextjs.org/docs)
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/docs/)
- [uv](https://docs.astral.sh/uv/)
- [Node.js](https://nodejs.org/docs/latest-v24.x/api/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [OpenCode V2 · docs](https://opencode.ai/v2/docs/)
- [OpenCode V2 · proveedores](https://opencode.ai/v2/docs/providers)
- [OpenCode Go](https://opencode.ai/v2/docs/console/go)

# Corpus

- *Don Quijote de la Mancha*, Project Gutenberg #2000, dominio público.
- Fragmento usado en el lab de n-gramas: `webapp/static/data/quijote_fragmento.txt`.
