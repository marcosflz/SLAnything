"""Proveedores LLM que OpenCode puede usar desde el Estudio.

OpenCode ya conoce los proveedores de models.dev. Para los integrados basta con
pasar la variable de entorno de la credencial y elegir ``provider/modelo``. Para
un endpoint propio se declara un proveedor compatible con OpenAI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

AUTHORING_AGENT = "slanything-author"
CUSTOM_PROVIDER_ID = "slanything"
CUSTOM_ENV = "SLANYTHING_LLM_KEY"


@dataclass(frozen=True)
class Provider:
    id: str
    label: str
    env: str | None
    requires_key: bool
    default_base_url: str | None
    models: tuple[str, ...]
    notes: str
    custom: bool = False


PROVIDERS: tuple[Provider, ...] = (
    Provider(
        id="opencode-go",
        label="OpenCode Go",
        env="OPENCODE_API_KEY",
        requires_key=True,
        default_base_url=None,
        models=(
            "deepseek-v4.1-flash",
            "glm-5.3",
            "glm-5.3-flash",
            "kimi-k3",
            "kimi-k2.7-code",
            "mimo-v2.6-flash",
            "minimax-m3.1-flash",
            "longcat-2.0",
            "step-5-preview",
            "beam-free",
        ),
        notes=(
            "Suscripción de OpenCode. Pega la API key del Console; se pasa como "
            "OPENCODE_API_KEY y no se guarda en opencode.json."
        ),
    ),
    Provider(
        id="opencode",
        label="OpenCode · modelos gratuitos",
        env="OPENCODE_API_KEY",
        requires_key=False,
        default_base_url=None,
        models=(
            "deepseek-v4.1-flash-free",
            "glm-5.3-flash-free",
            "mimo-v2.6-flash-free",
            "nemotron-3-ultra-free",
        ),
        notes=(
            "Modelos gratuitos de OpenCode para probar el Estudio sin configurar "
            "facturación. Tienen límites y pueden cambiar; para uso real, usa Go."
        ),
    ),
    Provider(
        id="openai",
        label="OpenAI",
        env="OPENAI_API_KEY",
        requires_key=True,
        default_base_url=None,
        models=("gpt-6.1-sol", "gpt-6-luna", "gpt-5.6-luna"),
        notes="API key de platform.openai.com. También admite un gateway con base URL.",
    ),
    Provider(
        id="anthropic",
        label="Anthropic",
        env="ANTHROPIC_API_KEY",
        requires_key=True,
        default_base_url=None,
        models=("claude-sonnet-5-5", "claude-haiku-5-5"),
        notes="API key de console.anthropic.com.",
    ),
    Provider(
        id="openrouter",
        label="OpenRouter",
        env="OPENROUTER_API_KEY",
        requires_key=True,
        default_base_url=None,
        models=(
            "anthropic/claude-sonnet-5.5",
            "openai/gpt-6.1-sol",
            "google/gemini-4-argon",
        ),
        notes="Un solo proveedor para cientos de modelos; usa el ID completo del modelo.",
    ),
    Provider(
        id="google",
        label="Google Gemini",
        env="GOOGLE_GENERATIVE_AI_API_KEY",
        requires_key=True,
        default_base_url=None,
        models=("gemini-4-argon", "gemini-3-pro"),
        notes="API key de Google AI Studio.",
    ),
    Provider(
        id="deepseek",
        label="DeepSeek",
        env="DEEPSEEK_API_KEY",
        requires_key=True,
        default_base_url=None,
        models=("deepseek-chat", "deepseek-reasoner"),
        notes="API directa de DeepSeek.",
    ),
    Provider(
        id="custom",
        label="OpenAI-compatible (vLLM, LM Studio, gateway)",
        env=CUSTOM_ENV,
        requires_key=False,
        default_base_url="http://host.docker.internal:11434/v1",
        models=(),
        notes=(
            "Cualquier endpoint /v1 compatible con OpenAI. La API key es opcional. "
            "En Docker, host.docker.internal apunta al equipo anfitrión."
        ),
        custom=True,
    ),
    Provider(
        id="ollama",
        label="Ollama",
        env=None,
        requires_key=False,
        default_base_url="http://host.docker.internal:11434/v1",
        models=("qwen3:8b", "llama3.2"),
        notes=(
            "Ollama local. Arranca el servidor y descarga el modelo; en Docker, "
            "host.docker.internal apunta al equipo anfitrión."
        ),
    ),
    Provider(
        id="lmstudio",
        label="LM Studio",
        env=None,
        requires_key=False,
        default_base_url="http://host.docker.internal:1234/v1",
        models=("local-model",),
        notes="LM Studio con el servidor local de OpenAI-compatible activado.",
    ),
)

PROVIDER_MAP = {provider.id: provider for provider in PROVIDERS}


def provider(provider_id: str) -> Provider:
    try:
        return PROVIDER_MAP[provider_id]
    except KeyError as exc:
        raise ValueError(f"Proveedor desconocido: {provider_id!r}.") from exc


def providers_payload() -> list[dict[str, Any]]:
    return [
        {
            "id": item.id,
            "label": item.label,
            "requires_key": item.requires_key,
            "default_base_url": item.default_base_url,
            "models": list(item.models),
            "notes": item.notes,
        }
        for item in PROVIDERS
    ]


def _agent_config(model_ref: str, provider_id: str) -> dict[str, Any]:
    return {
        "$schema": "https://opencode.ai/config.json",
        "model": model_ref,
        "default_agent": AUTHORING_AGENT,
        "update": "disable",
        "share": "disabled",
        "snapshot": False,
        "formatter": False,
        "lsp": False,
        "permissions": [
            {"action": "shell", "resource": "*", "effect": "deny"},
            {"action": "webfetch", "resource": "*", "effect": "deny"},
            {"action": "websearch", "resource": "*", "effect": "deny"},
            {"action": "task", "resource": "*", "effect": "deny"},
            {"action": "external_directory", "resource": "*", "effect": "deny"},
            {"action": "question", "resource": "*", "effect": "deny"},
        ],
        "agents": {
            AUTHORING_AGENT: {
                "description": (
                    "Convierte documentos en unidades didácticas validadas para "
                    "SLAnything. No ejecuta comandos ni navega."
                ),
                "mode": "primary",
                "steps": 90,
                "system": (
                    "Eres el autor didáctico de SLAnything. Sigues AGENTS.md y "
                    "produces un único course.json válido. No pides confirmación, "
                    "no ejecutas comandos y no usas la web."
                ),
                "permissions": [
                    {"action": "read", "resource": "*", "effect": "allow"},
                    {"action": "edit", "resource": "*", "effect": "allow"},
                    {"action": "glob", "resource": "*", "effect": "allow"},
                    {"action": "grep", "resource": "*", "effect": "allow"},
                    {"action": "list", "resource": "*", "effect": "allow"},
                    {"action": "shell", "resource": "*", "effect": "deny"},
                    {"action": "webfetch", "resource": "*", "effect": "deny"},
                    {"action": "websearch", "resource": "*", "effect": "deny"},
                    {"action": "task", "resource": "*", "effect": "deny"},
                    {"action": "external_directory", "resource": "*", "effect": "deny"},
                    {"action": "question", "resource": "*", "effect": "deny"},
                ],
            }
        },
    }


def build_config(settings: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str], str]:
    """Devuelve ``(opencode.json, env, model_ref)`` sin escribir la key en disco."""
    provider_id = str(settings.get("provider") or "opencode-go")
    info = provider(provider_id)
    model = str(settings.get("model") or "").strip()
    if not model:
        raise ValueError("Falta el modelo del proveedor.")
    key = str(settings.get("api_key") or "").strip()
    base_url = str(settings.get("base_url") or "").strip() or info.default_base_url
    env: dict[str, str] = {}
    config = _agent_config("", provider_id)

    if info.custom:
        if not base_url:
            raise ValueError("El proveedor compatible necesita una base URL.")
        custom: dict[str, Any] = {
            "name": "SLAnything · endpoint compatible",
            "package": "@opencode/ai/providers/openai-compatible",
            "settings": {"baseURL": base_url},
            "models": {model: {"name": model}},
        }
        if key:
            custom["env"] = [CUSTOM_ENV]
            env[CUSTOM_ENV] = key
        config["providers"] = {CUSTOM_PROVIDER_ID: custom}
        model_ref = f"{CUSTOM_PROVIDER_ID}/{model}"
    elif provider_id in {"ollama", "lmstudio"}:
        providers = config.setdefault("providers", {})
        providers[provider_id] = {
            "settings": {"baseURL": base_url},
            "models": {model: {"name": model}},
        }
        model_ref = f"{provider_id}/{model}"
    else:
        if info.requires_key and not key:
            raise ValueError(f"Falta la API key de {info.label}.")
        if info.env and key:
            env[info.env] = key
        if base_url:
            providers = config.setdefault("providers", {})
            providers[provider_id] = {
                "settings": {"baseURL": base_url},
            }
        model_ref = f"{provider_id}/{model}"

    config["model"] = model_ref
    return config, env, model_ref
