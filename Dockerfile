# syntax=docker/dockerfile:1
# SLAnything · backend FastAPI + OpenCode
#
# Imagen de runtime con el contenido del curso, Jinja de fallback, API JSON,
# estáticos y el runner de Python. SQLite vive en el volumen /data.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime

# OpenCode se instala como binario portable dentro de la imagen. El Estudio lo
# ejecuta con permisos restringidos (sin shell ni red desde el agente).
ARG OPENCODE_VERSION=2.1.4
ARG TARGETARCH=amd64

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:/home/aula/.local/bin:$PATH" \
    AULA_ENV=production \
    AULA_DB=/data/aula.db \
    AULA_AUTHORING_DIR=/data/authoring \
    AULA_AUTHORING_ENABLED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        libgomp1 \
        ripgrep \
        tar \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system aula \
    && useradd --system --gid aula --create-home --home-dir /home/aula aula \
    && arch=$([ "$TARGETARCH" = "arm64" ] && echo arm64 || echo x64) \
    && curl -fsSL "https://registry.npmjs.org/@opencode/cli-linux-${arch}/-/cli-linux-${arch}-${OPENCODE_VERSION}.tgz" -o /tmp/opencode.tgz \
    && tar -xzf /tmp/opencode.tgz -C /tmp \
    && install -m 0755 /tmp/package/bin/opencode /usr/local/bin/opencode \
    && rm -rf /tmp/package /tmp/opencode.tgz \
    && opencode --version

WORKDIR /app

# Capa de dependencias: se invalida solo cuando cambian pyproject/uv.lock.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Código y datos que la app sirve o descarga.
COPY aula.py ./
COPY webapp ./webapp
COPY docs/PLAN_PLATAFORMA_WEB.md ./docs/PLAN_PLATAFORMA_WEB.md
COPY notebooks/capitulo_01_entender_los_llms.ipynb ./notebooks/

RUN mkdir -p /data \
    && chown aula:aula /data

USER aula

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
