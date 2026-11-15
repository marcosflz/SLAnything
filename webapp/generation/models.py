"""Construcción de modelos nas-adk a partir de los ajustes resueltos (ADR-023/024).

- ``build_model(settings)`` devuelve un ``BaseLlm`` nuevo por ejecución: el
  cliente HTTP async de nas-adk queda ligado al bucle de eventos que lo crea.
- La suscripción de Claude (``claude-code``) recibe el token de su titular con
  ``ClaudeCodeLlm(oauth_token=…)`` (nas-adk ≥ 0.4: solo llega al proceso hijo) y un
  ``CLAUDE_CONFIG_DIR``/``HOME`` propio por usuario vía ``UserEnvTransport``.
  ``os.environ`` nunca se modifica.
- El plan de ChatGPT (``chatgpt``) usa ``ChatGptPlanLlm`` con el token de acceso vigente
  de su titular (``credentials.chatgpt_access_token``).
- ``FakeAgentLlm`` (``AULA_LLM_FAKE=1`` y tests) llama a la herramienta
  ``submit_*`` de la tarea con el contenido determinista de ``fake.respond``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Callable, ClassVar
from uuid import uuid4

from nas.adk.models import BaseLlm, LlmRequest, LlmResponse, ModelCapabilities, ToolCall
from nas.adk.models.claude_code import AsyncioProcessTransport, ClaudeCodeLlm

from webapp import config
from webapp.authoring import providers


class UserEnvTransport(AsyncioProcessTransport):
    """Transporte de procesos que añade el entorno de una sola persona."""

    def __init__(self, extra_env: Mapping[str, str]) -> None:
        super().__init__()
        self._extra = dict(extra_env)

    def which(self, name: str) -> str | None:
        return super().which(name)

    async def spawn(self, argv: Sequence[str], *, env: Mapping[str, str], cwd: str):
        merged = dict(env)
        merged.update(self._extra)
        return await super().spawn(argv, env=merged, cwd=cwd)


def claude_config_dir(user_id: int | None) -> Path:
    base = config.AUTHORING_DIR / "claude" / str(int(user_id or 0))
    base.mkdir(parents=True, exist_ok=True)
    for path in (base.parent, base):
        try:
            path.chmod(0o700)
        except OSError:
            pass
    return base


def subscription_env(user_id: int | None) -> dict[str, str]:
    """Directorio de configuración propio del CLI para cada persona (sin el token)."""
    home = claude_config_dir(user_id)
    return {"CLAUDE_CONFIG_DIR": str(home), "HOME": str(home)}


def claude_code_llm(token: str, user_id: int | None, *, model: str = "", transport: Any = None) -> ClaudeCodeLlm:
    return ClaudeCodeLlm(
        model=model,
        oauth_token=token,
        executable=config.CLAUDE_CODE_BIN,
        timeout=float(max(60, config.AUTHORING_TIMEOUT)),
        env_policy="scrub",
        max_concurrency=1,
        transport=transport or UserEnvTransport(subscription_env(user_id)),
    )


def is_subscription(settings: Mapping[str, Any]) -> bool:
    try:
        return providers.provider(str(settings.get("provider") or "")).adk_provider == "claude-code"
    except ValueError:
        return False


def build_model(settings: Mapping[str, Any], *, transport: Any = None) -> BaseLlm:
    """Modelo nas-adk listo para un ``Runner``. Lanza ``ValueError`` si falta algo."""
    if config.LLM_FAKE:
        return FakeAgentLlm()
    from nas.adk.models import ModelRouter

    kwargs = providers.router_kwargs(dict(settings))
    if kwargs["provider"] == "claude-code":
        token = str(settings.get("api_key") or "").strip()
        if not token:
            raise ValueError("Falta el token de tu suscripción de Claude.")
        model = str(kwargs.get("model") or "")
        return claude_code_llm(token, settings.get("user_id"), model="" if model == "default" else model, transport=transport)
    if kwargs["provider"] == "chatgpt":
        from nas.adk.models.chatgpt import ChatGptPlanLlm

        token = str(settings.get("api_key") or "").strip()
        if not token:
            raise ValueError("Vuelve a vincular tu cuenta de ChatGPT.")
        return ChatGptPlanLlm(model=str(kwargs.get("model") or ""), access_token=token, timeout=180.0)
    return ModelRouter(timeout=180.0, max_retries=3, **kwargs)


# ---------------------------------------------------------------------------
# Modelo falso
# ---------------------------------------------------------------------------

Responder = Callable[[str, str, str], dict]


class FakeAgentLlm(BaseLlm):
    """Agente determinista: entrega con ``submit_*`` y después responde «OK»."""

    model: str = "fake"
    responder: Any = None
    calls: list[str] = []

    capabilities: ClassVar[ModelCapabilities | None] = ModelCapabilities(
        tool_calling="native", usage="reported"
    )

    async def generate_content_async(self, request: LlmRequest) -> LlmResponse:
        from webapp.generation import fake

        messages = request.messages
        if messages and messages[-1].get("role") == "tool":
            return LlmResponse(content="OK", usage={"input_tokens": 10, "output_tokens": 2})
        submit = next(
            (
                (tool.get("function") or {}).get("name", "")
                for tool in request.tools or []
                if (tool.get("function") or {}).get("name", "").startswith("submit_")
            ),
            "",
        )
        system = next((m.get("content") or "" for m in messages if m.get("role") == "system"), "")
        user = next((m.get("content") or "" for m in reversed(messages) if m.get("role") == "user"), "")
        task = submit.removeprefix("submit_")
        self.calls.append(task)
        responder = self.responder or fake.respond
        data = responder(task, system, user)
        usage = {"input_tokens": len(system + user) // 4, "output_tokens": 400}
        if not submit:
            return LlmResponse(content=json.dumps(data, ensure_ascii=False), usage=usage)
        return LlmResponse(
            content="",
            tool_calls=[
                ToolCall(
                    id=f"call_{uuid4().hex[:12]}",
                    function={"name": submit, "arguments": json.dumps({"data": data}, ensure_ascii=False)},
                )
            ],
            finish_reason="tool_calls",
            usage=usage,
        )
