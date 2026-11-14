"""Configuración central de SLAnything.

Todas las rutas se resuelven a partir de la raíz del repositorio para que la app
funcione igual desde `uv run aula`, desde `webapp/` o desde un test.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WEBAPP_DIR = BASE_DIR / "webapp"
STATIC_DIR = WEBAPP_DIR / "static"

NOTEBOOKS_DIR = BASE_DIR / "notebooks"
ASSETS_DIR = NOTEBOOKS_DIR / "assets"
DATA_DIR = NOTEBOOKS_DIR / "data"

# La base de datos vive fuera del paquete para no ensuciar el código.
DB_PATH = Path(os.environ.get("AULA_DB", BASE_DIR / "aula.db")).resolve()

# Secreto de aplicación (reservado para firmas futuras y mensajes flash).
SECRET_KEY = os.environ.get("AULA_SECRET", "aula-llm-desarrollo-local")

ENV = os.environ.get("AULA_ENV", "development")
SECURE_COOKIES = os.environ.get("AULA_SECURE_COOKIES", "0") == "1"
COOKIE_NAME = "aula_session"
SESSION_DAYS = 14

SITE_NAME = "SLAnything"
SITE_TAGLINE = "Aprende IA desde los libros que la explican."
COURSE_TITLE = "Construye un LLM desde cero"
COURSE_CHAPTER = "Curso completo"

# ---------------------------------------------------------------------------
# Estudio de autoría · OpenCode + documentos
# ---------------------------------------------------------------------------
# Los datos de autoría (subidas, logs y la API key) viven fuera de la base de
# datos, en un directorio privado. En Docker se monta dentro del volumen /data.
AUTHORING_DIR = Path(
    os.environ.get("AULA_AUTHORING_DIR", BASE_DIR / "authoring-data")
).resolve()
AUTHORING_ENABLED = os.environ.get("AULA_AUTHORING_ENABLED", "1") == "1"
AUTHORING_OPENCODE_BIN = os.environ.get("AULA_AUTHORING_OPENCODE_BIN", "opencode")
AUTHORING_TIMEOUT = int(os.environ.get("AULA_AUTHORING_TIMEOUT", "1800"))
AUTHORING_MAX_UPLOAD_MB = int(os.environ.get("AULA_AUTHORING_MAX_UPLOAD_MB", "25"))
AUTHORING_MAX_FILES = int(os.environ.get("AULA_AUTHORING_MAX_FILES", "5"))
# ~75k tokens de texto extraído. Un libro completo se trocea por partes; si se
# supera este límite se recorta y se avisa al agente en meta.json.
AUTHORING_MAX_CHARS = int(os.environ.get("AULA_AUTHORING_MAX_CHARS", "300000"))
AUTHORING_MAX_JOBS = int(os.environ.get("AULA_AUTHORING_MAX_JOBS", "3"))
AUTHORING_HOME = AUTHORING_DIR / "opencode-home"

# Curso que se abre por defecto en /curso y en el panel del estudiante.
DEFAULT_COURSE_SLUG = "llm-desde-cero"

# Labs que el frontend sabe montar. El contenido solo puede referenciar estos.
KNOWN_LABS = {
    "memory",
    "labels",
    "transformer",
    "attention",
    "ngram",
    "prompt",
    "cost",
    "tokenizer",
    "window",
    "embedding",
    "qkv",
    "gpt-block",
    "loss",
    "classifier",
    "chat-template",
}

DEMO_EMAIL = "demo@aulallm.local"
DEMO_PASSWORD = "demo1234"
TEACHER_EMAIL = "profe@aulallm.local"
TEACHER_PASSWORD = "profe1234"

# Siembra de cuentas y academia de demostración. Desactívala en producción.
SEED_DEMO = os.environ.get("AULA_SEED_DEMO", "1") == "1"

# Correos con rol de superadministración de la plataforma (separados por comas).
PLATFORM_ADMINS = tuple(
    email.strip().lower()
    for email in os.environ.get("AULA_PLATFORM_ADMINS", "").split(",")
    if email.strip()
)

# Cookie con el espacio de trabajo activo.
WORKSPACE_COOKIE = "aula_ws"

# ---------------------------------------------------------------------------
# Generación por etapas (webapp/generation, ADR-017/019)
# ---------------------------------------------------------------------------
# Motor por defecto del Estudio: "direct" (etapas JSON) u "opencode" (agente).
GEN_DEFAULT_ENGINE = os.environ.get("AULA_GEN_ENGINE", "direct")
# Hilos del pool de generación dentro del proceso web.
GEN_WORKERS = int(os.environ.get("AULA_GEN_WORKERS", "2"))
# Lecciones en paralelo por trabajo (limita la concurrencia contra el proveedor).
GEN_CONCURRENCY = int(os.environ.get("AULA_GEN_CONCURRENCY", "3"))
# 0 = la web solo encola; un proceso `python -m webapp.generation.worker` ejecuta.
GEN_INPROCESS = os.environ.get("AULA_GEN_INPROCESS", "1") == "1"
# Tope de texto procesado por trabajo (un libro completo cabe de sobra).
GEN_MAX_CHARS = int(os.environ.get("AULA_GEN_MAX_CHARS", "3000000"))
# Cuotas mensuales de generación por espacio de trabajo.
GEN_MONTHLY_PERSONAL = int(os.environ.get("AULA_GEN_MONTHLY_PERSONAL", "10"))
GEN_MONTHLY_ORGANIZATION = int(os.environ.get("AULA_GEN_MONTHLY_ORG", "100"))
# Modelo falso determinista (tests y demos sin red).
LLM_FAKE = os.environ.get("AULA_LLM_FAKE", "0") == "1"
