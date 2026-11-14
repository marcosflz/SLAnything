"""Puente entre las etapas (hilos síncronos) y el ``Runner`` async de nas-adk.

``run_agent`` crea un modelo nuevo, ejecuta un agente con su ``JobToolbox`` y
devuelve lo que el agente entregó con ``submit_*``. Traduce los errores de
nas-adk a mensajes legibles, suma el uso de tokens y respeta la cancelación del
trabajo antes de cada llamada al modelo o a una herramienta.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
from uuid import uuid4

from nas.adk import Agent, Runner
from nas.adk.core.callbacks import BaseCallback
from nas.adk.core.interrupts import ToolDecision
from nas.adk.models import (
    LlmAuthError,
    LlmBillingModeError,
    LlmError,
    LlmProcessError,
    LlmQuotaError,
    LlmRateLimitError,
    LlmTimeoutError,
)

from webapp import config
from webapp.generation import agents, models
from webapp.generation.tools import JobToolbox

logger = logging.getLogger("aula.generation.runtime")

READ_TOOLS = {"read_fragment": "Consultando un fragmento", "search_document": "Buscando en el documento", "check_lesson": "Comprobando el borrador"}


class LLMError(RuntimeError):
    """Fallo del proveedor o del agente, con un mensaje apto para la interfaz."""


class Cancelled(RuntimeError):
    pass


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, input_tokens: int, output_tokens: int, calls: int = 1) -> None:
        with self._lock:
            self.input_tokens += int(input_tokens or 0)
            self.output_tokens += int(output_tokens or 0)
            self.calls += int(calls or 0)

    def take(self) -> tuple[int, int]:
        with self._lock:
            values = (self.input_tokens, self.output_tokens)
            self.input_tokens = self.output_tokens = 0
            return values


def _tokens(usage: Mapping[str, Any]) -> tuple[int, int]:
    # Unos proveedores informan input/output_tokens, otros prompt/completion_tokens y
    # Claude Code ambos con el mismo valor: se toma el mayor para no contar doble.
    def pick(*keys: str) -> int:
        values = [usage.get(key) for key in keys]
        return max([v for v in values if isinstance(v, int) and not isinstance(v, bool)] or [0])

    return pick("input_tokens", "prompt_tokens"), pick("output_tokens", "completion_tokens")


class _JobCallback(BaseCallback):
    def __init__(self, is_cancelled: Callable[[], bool], on_tool: Callable[[str], None] | None) -> None:
        self.is_cancelled = is_cancelled
        self.on_tool = on_tool
        self.cancelled = False
        self.errors: list[BaseException] = []

    async def before_model_call(self, agent_name: str = "", messages=None, tools=None) -> None:
        if self.is_cancelled():
            self.cancelled = True
            raise Cancelled()

    async def before_tool_call(self, tool_name: str, args: dict, tool_call_id: str = "", ctx=None, agent_name: str = ""):
        if self.is_cancelled():
            self.cancelled = True
            return ToolDecision.deny("El trabajo se ha cancelado.")
        if self.on_tool and tool_name in READ_TOOLS:
            detail = str(args.get("chunk_id") or args.get("query") or "")[:80]
            self.on_tool(f"{READ_TOOLS[tool_name]}{': ' + detail if detail else ''}")
        return None

    async def on_error(self, error: Exception) -> None:
        self.errors.append(error)


def explain(error: BaseException | None, fallback: str = "") -> str:
    """Mensaje en español para un error de nas-adk."""
    if isinstance(error, LlmBillingModeError):
        return f"La suscripción no se puede usar en modo seguro: {error}"
    if isinstance(error, LlmAuthError):
        return f"El proveedor rechazó la credencial. Revisa la API key o el token. ({error})"
    if isinstance(error, LlmQuotaError):
        return f"Se agotó la cuota del proveedor; no se cambia automáticamente a otro. ({error})"
    if isinstance(error, LlmRateLimitError):
        return f"El proveedor ha limitado las peticiones; vuelve a intentarlo en unos minutos. ({error})"
    if isinstance(error, LlmTimeoutError):
        return f"El proveedor tardó demasiado en responder. ({error})"
    if isinstance(error, LlmProcessError):
        return f"No se pudo ejecutar Claude Code en el servidor. ({error})"
    if isinstance(error, LlmError):
        return f"Error del proveedor de IA: {error}"
    return fallback or (str(error) if error else "El agente no terminó la tarea.")


@dataclass
class AgentResult:
    data: dict
    input_tokens: int
    output_tokens: int
    model_calls: int


def _run_coroutine(factory: Callable[[], Any]) -> Any:
    """``asyncio.run`` en este hilo, o en uno nuevo si ya hay un bucle activo."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(factory())
    box: dict[str, Any] = {}

    def target() -> None:
        try:
            box["value"] = asyncio.run(factory())
        except BaseException as exc:  # noqa: BLE001
            box["error"] = exc

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box.get("value")


async def _execute(
    toolbox: JobToolbox,
    settings: Mapping[str, Any],
    message: str,
    callback: _JobCallback,
    timeout: float,
    model_factory: Callable[[Mapping[str, Any]], Any],
):
    spec = agents.spec(toolbox.task)
    model = model_factory(settings)
    try:
        agent = Agent(name=spec.name, model=model, instruction=spec.instruction, tools=toolbox.tools())
        runner = Runner(
            app_name="slanything",
            agent=agent,
            callbacks=[callback],
            max_model_calls=spec.max_model_calls,
            max_turns=spec.max_turns,
            timeout=timeout,
            max_context_tokens=config.GEN_CONTEXT_TOKENS,
            max_tool_result_chars=20_000,
        )
        final = None
        async for event in runner.run_async("studio", f"{spec.name}-{uuid4().hex}", message):
            if event.final:
                final = event
        return final
    finally:
        try:
            await model.aclose()
        except Exception:  # noqa: BLE001
            logger.debug("No se pudo cerrar el modelo", exc_info=True)


def run_agent(
    toolbox: JobToolbox,
    settings: Mapping[str, Any],
    message: str,
    *,
    is_cancelled: Callable[[], bool] = lambda: False,
    on_tool: Callable[[str], None] | None = None,
    timeout: float | None = None,
    model_factory: Callable[[Mapping[str, Any]], Any] | None = None,
) -> AgentResult:
    """Ejecuta un agente hasta que entrega. Un reintento si termina sin entregar."""
    factory = model_factory or (lambda current: models.build_model(current))
    limit = float(timeout or max(60, config.AUTHORING_TIMEOUT))
    tokens_in = tokens_out = calls = 0
    prompt = message
    last_error = ""
    for attempt in range(2):
        callback = _JobCallback(is_cancelled, on_tool)
        try:
            final = _run_coroutine(lambda: _execute(toolbox, settings, prompt, callback, limit, factory))
        except ValueError as exc:  # ajustes incompletos al construir el modelo
            raise LLMError(str(exc)) from exc
        if callback.cancelled:
            raise Cancelled()
        metrics = (final.metrics if final is not None else {}) or {}
        used_in, used_out = _tokens(metrics.get("total_usage") or {})
        tokens_in, tokens_out = tokens_in + used_in, tokens_out + used_out
        calls += int(metrics.get("model_calls") or 0)
        if toolbox.submitted is not None:
            return AgentResult(toolbox.submitted, tokens_in, tokens_out, calls)
        status = getattr(final, "status", None)
        if status == "error":
            provider_error = next((e for e in reversed(callback.errors) if isinstance(e, LlmError)), None)
            if provider_error is not None or attempt == 1:
                raise LLMError(explain(provider_error, getattr(final, "content", "") or ""))
            last_error = getattr(final, "content", "") or ""
        elif status == "budget_exhausted":
            last_error = "El agente agotó su presupuesto de llamadas o de tiempo sin entregar."
        else:
            last_error = "El agente terminó sin entregar el resultado."
        logger.warning("Agente %s sin entrega (intento %s): %s", toolbox.task, attempt + 1, last_error)
        prompt = (
            message
            + f"\n\nIMPORTANTE: en el intento anterior no entregaste el resultado ({last_error}). "
            f"Llama a {toolbox.submit_name} con el objeto completo en \"data\"."
        )
    raise LLMError(last_error)
