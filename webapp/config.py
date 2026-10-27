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
TEMPLATES_DIR = WEBAPP_DIR / "templates"

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
