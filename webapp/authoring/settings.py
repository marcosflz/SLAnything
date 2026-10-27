"""Ajustes del Estudio: proveedor, modelo y API key.

La credencial se guarda en ``AUTHORING_DIR/settings.json`` con permisos 0600, no
en SQLite ni en el repositorio. La API pública solo devuelve si hay clave y sus
cuatro últimos caracteres; la clave completa se inyecta al subproceso de
OpenCode como variable de entorno.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from webapp import config
from webapp.authoring import providers

DEFAULT_PROVIDER = "opencode-go"
DEFAULT_MODEL = "deepseek-v4.1-flash"
MAX_KEY_LENGTH = 600
MAX_BASE_URL_LENGTH = 500
_ENGINE_TTL = 60.0
_engine_lock = threading.Lock()
_engine_cached: tuple[float, dict[str, Any]] | None = None


def _path() -> Path:
    return config.AUTHORING_DIR / "settings.json"


def _defaults() -> dict[str, Any]:
    return {
        "provider": DEFAULT_PROVIDER,
        "model": DEFAULT_MODEL,
        "base_url": "",
        "api_key": "",
        "updated_at": None,
    }


def _read() -> dict[str, Any]:
    path = _path()
    data = _defaults()
    if not path.is_file():
        return data
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return data
    if isinstance(stored, dict):
        for key in ("provider", "model", "base_url", "api_key", "updated_at"):
            if key in stored:
                data[key] = stored[key]
    if data["provider"] not in providers.PROVIDER_MAP:
        data["provider"] = DEFAULT_PROVIDER
    if not isinstance(data["api_key"], str):
        data["api_key"] = ""
    return data


def _write(data: dict[str, Any]) -> None:
    base = config.AUTHORING_DIR
    base.mkdir(parents=True, exist_ok=True)
    try:
        base.chmod(0o700)
    except OSError:
        pass
    target = _path()
    temporary = target.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    os.replace(temporary, target)


def _validate_base_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if not value:
        return ""
    if len(value) > MAX_BASE_URL_LENGTH:
        raise ValueError("La base URL es demasiado larga.")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("La base URL debe empezar por http:// o https://.")
    return value


def load_settings() -> dict[str, Any]:
    """Ajustes completos, incluida la clave. Solo para el backend."""
    return _read()


def public_settings() -> dict[str, Any]:
    data = _read()
    key = data.get("api_key") or ""
    info = providers.provider(data["provider"])
    return {
        "provider": data["provider"],
        "model": data["model"],
        "base_url": data.get("base_url") or "",
        "key_configured": bool(key),
        "key_hint": f"••••{key[-4:]}" if len(key) >= 4 else "",
        "requires_key": info.requires_key,
        "updated_at": data.get("updated_at"),
        "providers": providers.providers_payload(),
        "engine": engine_status(),
    }


def save_settings(
    *,
    provider: str,
    model: str,
    base_url: str = "",
    api_key: str | None = None,
    clear_key: bool = False,
) -> dict[str, Any]:
    provider = (provider or DEFAULT_PROVIDER).strip()
    info = providers.provider(provider)
    model = (model or "").strip()
    if not model:
        raise ValueError("Indica el modelo que usará OpenCode.")
    if len(model) > 160 or any(char.isspace() for char in model):
        raise ValueError("El identificador del modelo no es válido.")
    if info.custom and not base_url.strip():
        raise ValueError("Este proveedor necesita una base URL.")
    if provider in {"ollama", "lmstudio"} and not base_url.strip():
        base_url = info.default_base_url or ""
    cleaned_base = _validate_base_url(base_url or "")

    current = _read()
    key = "" if clear_key else (current.get("api_key") or "")
    if api_key is not None and api_key.strip():
        key = api_key.strip()
        if len(key) > MAX_KEY_LENGTH:
            raise ValueError("La API key es demasiado larga.")

    data = {
        "provider": provider,
        "model": model,
        "base_url": cleaned_base,
        "api_key": key,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _write(data)
    return public_settings()


def engine_status() -> dict[str, Any]:
    global _engine_cached
    now = time.monotonic()
    with _engine_lock:
        if _engine_cached and now - _engine_cached[0] < _ENGINE_TTL:
            return dict(_engine_cached[1])
    result = _engine_status_uncached()
    with _engine_lock:
        _engine_cached = (now, result)
    return dict(result)


def _engine_status_uncached() -> dict[str, Any]:
    if not config.AUTHORING_ENABLED:
        return {
            "enabled": False,
            "available": False,
            "version": None,
            "binary": config.AUTHORING_OPENCODE_BIN,
            "message": "El Estudio está desactivado (AULA_AUTHORING_ENABLED=0).",
        }
    binary = config.AUTHORING_OPENCODE_BIN
    resolved = shutil.which(binary)
    if not resolved and Path(binary).is_file():
        resolved = str(Path(binary))
    if not resolved:
        return {
            "enabled": True,
            "available": False,
            "version": None,
            "binary": binary,
            "message": (
                "No se encontró OpenCode. En Docker viene incluido; en local "
                "instálalo con `npm install -g @opencode/cli`."
            ),
        }
    version_env = dict(os.environ)
    version_env.update(
        {
            "HOME": str(config.AUTHORING_HOME),
            "OPENCODE_DISABLE_AUTOUPDATE": "1",
            "NO_COLOR": "1",
        }
    )
    try:
        completed = subprocess.run(
            [resolved, "--version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
            env=version_env,
        )
        version = (completed.stdout or completed.stderr or "").strip().splitlines()
        version_text = version[0] if version else "desconocida"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "enabled": True,
            "available": False,
            "version": None,
            "binary": resolved,
            "message": f"OpenCode no respondió: {exc}",
        }
    return {
        "enabled": True,
        "available": True,
        "version": version_text,
        "binary": resolved,
        "message": "OpenCode listo para generar unidades.",
    }
