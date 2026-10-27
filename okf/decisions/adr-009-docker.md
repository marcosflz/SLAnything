---
type: ADR
title: "ADR-009 · Empaquetado Docker con dos imágenes"
description: Backend FastAPI y frontend Next.js en imágenes separadas, orquestadas con Compose y SQLite en volumen.
tags: [adr, docker, compose, despliegue, nextjs, fastapi]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T14:30:00Z }
sources:
  - id: compose
    resource: ../../compose.yaml
    title: Docker Compose
  - id: backend
    resource: ../../Dockerfile
    title: Imagen del backend
  - id: frontend
    resource: ../../frontend/Dockerfile
    title: Imagen del frontend
  - id: docs
    resource: ../../docs/DOCKER.md
    title: Guía de Docker
---

# Contexto

La app tiene dos runtimes (FastAPI y Next.js) y una base SQLite local. Se quería
poder empaquetarla como imagen y arrancarla con Compose sin depender de `uv`,
Node ni una instalación manual en la máquina anfitriona.

# Decisión

- **Dos imágenes**:
  - `aula-llm-backend`: Python 3.12 + `uv sync --frozen --no-dev`, contenido,
    API, Jinja de fallback y runner Python. Usuario no root `aula`.
  - `aula-llm-frontend`: build multi-stage de Next.js con `output: "standalone"`
    y runtime Node 22 sin `node_modules`.
- **Compose** conecta ambos servicios en una red privada. Solo se publica el
  3000; el 8000 queda interno.
- Next conserva los rewrites a `http://backend:8000`, por lo que la cookie
  HttpOnly y el CSRF no necesitan CORS.
- SQLite vive en el volumen nombrado `aula-llm-data` montado en `/data`.
- `API_INTERNAL_URL` se pasa como build arg al frontend y como variable de
  runtime.

# Consecuencias

- Arranque reproducible con `docker compose up -d --build`.
- La base de datos sobrevive a `down` y a recrear contenedores; `down -v` la
  borra.
- Cambiar contenido o código requiere reconstruir la imagen correspondiente.
- La imagen del backend incluye dependencias de cuaderno (`jupyterlab`,
  `ipykernel`…) porque `uv sync` instala el grupo principal; se puede optimizar
  en el futuro separando un grupo `notebooks`.
- El backend no se publica directamente: para depurar la API o Jinja hay que
  usar `docker compose exec` o un override local.
- En producción sigue haciendo falta TLS y `AULA_SECURE_COOKIES=1`; Compose no
  incluye proxy inverso.

# Alternativas descartadas

- **Una sola imagen con supervisord**: mezcla runtimes, complica actualizaciones
  y obliga a reiniciar todo para cambiar una capa.
- **Solo backend en Docker**: no resuelve el empaquetado del frontend, que es la
  interfaz principal.
- **SQLite en bind mount obligatorio**: funciona en Linux, pero da problemas de
  permisos en Windows/macOS; el volumen nombrado es más portable.
