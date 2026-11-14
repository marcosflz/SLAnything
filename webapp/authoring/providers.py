"""Proveedores de IA del Estudio y su traducción a ``nas-adk`` (ADR-023).

Cada proveedor de SLAnything se ejecuta con un ``ModelRouter`` de nas-adk. Los
proveedores con ``scope`` ``platform`` solo los configura la superadministración
(los que aceptan base URL, para no abrir SSRF desde cuentas de usuario); los de
``user`` solo una persona para sí misma (la suscripción de Claude, ADR-024).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Scope = Literal["platform", "user", "both"]


@dataclass(frozen=True)
class Provider:
    id: str
    label: str
    adk_provider: str
    requires_key: bool
    default_base_url: str | None
    models: tuple[str, ...]
    notes: str
    scope: Scope = "both"
    custom: bool = False
    personal: bool = False
    # Si la base URL la elige quien configura (custom/ollama/lmstudio).
    base_url_editable: bool = False

    def allowed_for(self, level: str) -> bool:
        return self.scope == "both" or self.scope == level


PROVIDERS: tuple[Provider, ...] = (
    Provider(
        id="opencode-go",
        label="OpenCode Go",
        adk_provider="opencode",
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
        ),
        notes="Suscripción de OpenCode Go. Pega la API key del Console de OpenCode.",
    ),
    Provider(
        id="opencode",
        label="OpenCode Zen · modelos gratuitos",
        adk_provider="openai-compatible",
        requires_key=False,
        default_base_url="https://opencode.ai/zen/v1",
        models=(
            "deepseek-v4.1-flash-free",
            "glm-5.3-flash-free",
            "mimo-v2.6-flash-free",
            "nemotron-3-ultra-free",
        ),
        notes=(
            "Modelos gratuitos de OpenCode Zen para probar el Estudio. Tienen límites "
            "y pueden cambiar; para uso real, usa Go u otro proveedor."
        ),
    ),
    Provider(
        id="anthropic",
        label="Anthropic (API)",
        adk_provider="anthropic",
        requires_key=True,
        default_base_url=None,
        models=("claude-sonnet-5-5", "claude-haiku-5-5", "claude-opus-5-5"),
        notes="API key de console.anthropic.com (facturación por uso).",
    ),
    Provider(
        id="claude-code",
        label="Claude · mi suscripción personal",
        adk_provider="claude-code",
        requires_key=True,
        default_base_url=None,
        models=("", "sonnet", "opus", "haiku"),
        notes=(
            "Tu suscripción de Claude (Pro/Max) a través del CLI oficial de Claude Code. "
            "Ejecuta `claude setup-token` en tu equipo y pega aquí el token. Solo se usa "
            "en las unidades que generas tú; nadie más puede usarla."
        ),
        scope="user",
        personal=True,
    ),
    Provider(
        id="openrouter",
        label="OpenRouter",
        adk_provider="openrouter",
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
        id="openai",
        label="OpenAI",
        adk_provider="openai-compatible",
        requires_key=True,
        default_base_url="https://api.openai.com/v1",
        models=("gpt-6.1-sol", "gpt-6-luna", "gpt-5.6-luna"),
        notes="API key de platform.openai.com.",
    ),
    Provider(
        id="google",
        label="Google Gemini",
        adk_provider="openai-compatible",
        requires_key=True,
        default_base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        models=("gemini-4-argon", "gemini-3-pro"),
        notes="API key de Google AI Studio (endpoint compatible con OpenAI).",
    ),
    Provider(
        id="deepseek",
        label="DeepSeek",
        adk_provider="openai-compatible",
        requires_key=True,
        default_base_url="https://api.deepseek.com/v1",
        models=("deepseek-chat", "deepseek-reasoner"),
        notes="API directa de DeepSeek.",
    ),
    Provider(
        id="custom",
        label="OpenAI-compatible (vLLM, LM Studio, gateway)",
        adk_provider="openai-compatible",
        requires_key=False,
        default_base_url="http://host.docker.internal:11434/v1",
        models=(),
        notes=(
            "Cualquier endpoint /v1 compatible con OpenAI. La API key es opcional. "
            "En Docker, host.docker.internal apunta al equipo anfitrión."
        ),
        scope="platform",
        custom=True,
        base_url_editable=True,
    ),
    Provider(
        id="ollama",
        label="Ollama",
        adk_provider="openai-compatible",
        requires_key=False,
        default_base_url="http://host.docker.internal:11434/v1",
        models=("qwen3:8b", "llama3.2"),
        notes="Ollama local; en Docker, host.docker.internal apunta al equipo anfitrión.",
        scope="platform",
        base_url_editable=True,
    ),
    Provider(
        id="lmstudio",
        label="LM Studio",
        adk_provider="openai-compatible",
        requires_key=False,
        default_base_url="http://host.docker.internal:1234/v1",
        models=("local-model",),
        notes="LM Studio con el servidor local compatible con OpenAI activado.",
        scope="platform",
        base_url_editable=True,
    ),
)

PROVIDER_MAP = {provider.id: provider for provider in PROVIDERS}


def provider(provider_id: str) -> Provider:
    try:
        return PROVIDER_MAP[provider_id]
    except KeyError as exc:
        raise ValueError(f"Proveedor desconocido: {provider_id!r}.") from exc


def providers_payload(level: str = "platform") -> list[dict[str, Any]]:
    """Catálogo para la UI. ``level`` es ``platform`` o ``user``."""
    return [
        {
            "id": item.id,
            "label": item.label,
            "requires_key": item.requires_key,
            "default_base_url": item.default_base_url if item.base_url_editable else None,
            "base_url_editable": item.base_url_editable,
            "models": [model for model in item.models if model],
            "model_optional": item.adk_provider == "claude-code",
            "notes": item.notes,
            "personal": item.personal,
        }
        for item in PROVIDERS
        if item.allowed_for(level)
    ]


def router_kwargs(settings: dict[str, Any]) -> dict[str, Any]:
    """Argumentos de ``ModelRouter`` para unos ajustes (sin la suscripción)."""
    info = provider(str(settings.get("provider") or ""))
    model = str(settings.get("model") or "").strip()
    key = str(settings.get("api_key") or "").strip()
    if info.adk_provider != "claude-code" and not model:
        raise ValueError("Falta el modelo del proveedor.")
    if info.requires_key and not key:
        raise ValueError(f"Falta la credencial de {info.label}.")
    kwargs: dict[str, Any] = {"provider": info.adk_provider, "model": model}
    if info.adk_provider == "claude-code":
        return kwargs
    kwargs["api_key"] = key
    base_url = str(settings.get("base_url") or "").strip() if info.base_url_editable else ""
    base_url = base_url or info.default_base_url or ""
    if base_url:
        kwargs["base_url"] = base_url
    elif info.adk_provider == "openai-compatible":
        raise ValueError("El proveedor necesita una base URL.")
    return kwargs
