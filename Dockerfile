# syntax=docker/dockerfile:1
# SLAnything · backend FastAPI + agentes nas-adk (+ CLI de Claude Code opcional)
#
# Imagen de runtime con el contenido del curso, Jinja de fallback, API JSON,
# estáticos y el runner de Python. SQLite vive en el volumen /data.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

# Los agentes del Estudio son Python (nas-adk, en uv.lock). El CLI de Claude Code
# solo hace falta para que cada usuario use su suscripción personal (ADR-024);
# INSTALL_CLAUDE_CODE=0 lo omite. Se instala con versión fija y sin autoactualizar.
ARG INSTALL_CLAUDE_CODE=1
ARG CLAUDE_CODE_VERSION=2.1.319

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:/home/aula/.local/bin:$PATH" \
    AULA_ENV=production \
    AULA_DB=/data/aula.db \
    AULA_AUTHORING_DIR=/data/authoring \
    AULA_AUTHORING_ENABLED=1 \
    DISABLE_AUTOUPDATER=1 \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system aula \
    && useradd --system --gid aula --create-home --home-dir /home/aula aula

WORKDIR /app

# Capa de dependencias: se invalida solo cuando cambian pyproject/uv.lock.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Código y datos que la app sirve o descarga.
COPY aula.py ./
COPY webapp ./webapp
# Cuaderno del curso de ejemplo (solo se sirve con AULA_SAMPLE_COURSES=1).
COPY notebooks/capitulo_01_entender_los_llms.ipynb ./notebooks/

RUN mkdir -p /data \
    && chown aula:aula /data

USER aula

# CLI de Claude Code para la suscripción personal de cada usuario. Cada ejecución
# recibe el token de su titular y un CLAUDE_CONFIG_DIR propio (ADR-024).
RUN if [ "$INSTALL_CLAUDE_CODE" = "1" ]; then \
        curl -fsSL https://claude.ai/install.sh | bash -s "$CLAUDE_CODE_VERSION" \
        && /home/aula/.local/bin/claude --version; \
    fi

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
