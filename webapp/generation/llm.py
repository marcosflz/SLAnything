"""Cliente LLM mínimo para las etapas JSON de la generación (ADR-017).

Cada etapa pide un objeto JSON concreto (temario, lección, banco de preguntas),
así que no hace falta un agente con herramientas: basta una llamada de chat con
salida JSON. Se habla directamente con dos dialectos usando ``httpx``:

- **OpenAI-compatible** (``/chat/completions``): OpenAI, OpenRouter, DeepSeek,
  Gemini (endpoint compatible), OpenCode Zen/Go, Ollama, LM Studio y cualquier
  gateway ``/v1``.
- **Anthropic** (``/v1/messages``).

Reintenta con *backoff* exponencial ante 429/5xx/timeouts y cuenta tokens para
el coste. ``FakeLLM`` responde de forma determinista en los tests.
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

import httpx

from webapp.authoring import providers

logger = logging.getLogger("aula.generation.llm")

# Base URL por defecto de cada proveedor en modo directo (sin OpenCode).
DIRECT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai",
    "opencode": "https://opencode.ai/zen/v1",
    "opencode-go": "https://opencode.ai/zen/go/v1",
    "anthropic": "https://api.anthropic.com/v1",
}

RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}


class LLMError(RuntimeError):
    pass


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, input_tokens: int, output_tokens: int) -> None:
        with self._lock:
            self.input_tokens += int(input_tokens or 0)
            self.output_tokens += int(output_tokens or 0)
            self.calls += 1


class JSONModel(Protocol):
    usage: Usage

    def complete_json(self, system: str, user: str, *, max_tokens: int = 8000, task: str = "") -> dict: ...


def extract_json(text: str) -> dict:
    """Extrae el primer objeto JSON de una respuesta (tolera ```json …```)."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.S)
    if fence:
        cleaned = fence.group(1)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("La respuesta del modelo no contiene un objeto JSON.")
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"JSON inválido en la respuesta del modelo: {exc}") from exc
    if not isinstance(data, dict):
        raise LLMError("Se esperaba un objeto JSON.")
    return data


class HttpLLM:
    """Cliente real. ``settings`` es el mismo dict que guarda el Estudio."""

    def __init__(
        self,
        settings: dict[str, Any],
        *,
        timeout: float = 180.0,
        retries: int = 4,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.provider_id = str(settings.get("provider") or "openai")
        info = providers.provider(self.provider_id)
        self.model = str(settings.get("model") or "").strip()
        if not self.model:
            raise LLMError("Falta el modelo del proveedor.")
        self.key = str(settings.get("api_key") or "").strip()
        if info.requires_key and not self.key:
            raise LLMError(f"Falta la API key de {info.label}.")
        self.base_url = (
            str(settings.get("base_url") or "").strip()
            or DIRECT_BASE_URLS.get(self.provider_id)
            or info.default_base_url
            or ""
        ).rstrip("/")
        if not self.base_url:
            raise LLMError("El proveedor necesita una base URL.")
        self.dialect = "anthropic" if self.provider_id == "anthropic" else "openai"
        self.timeout = timeout
        self.retries = retries
        self.sleep = sleep
        self.usage = Usage()

    def _request(self, system: str, user: str, max_tokens: int) -> tuple[str, int, int]:
        if self.dialect == "anthropic":
            response = httpx.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            body = response.json()
            text = "".join(part.get("text", "") for part in body.get("content", []) if part.get("type") == "text")
            usage = body.get("usage", {})
            return text, usage.get("input_tokens", 0), usage.get("output_tokens", 0)

        headers = {"content-type": "application/json"}
        if self.key:
            headers["authorization"] = f"Bearer {self.key}"
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=self.timeout
        )
        if response.status_code == 400 and "response_format" in response.text:
            payload.pop("response_format")
            response = httpx.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=self.timeout
            )
        response.raise_for_status()
        body = response.json()
        text = body["choices"][0]["message"].get("content") or ""
        usage = body.get("usage") or {}
        return text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

    def complete_json(self, system: str, user: str, *, max_tokens: int = 8000, task: str = "") -> dict:
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                text, tokens_in, tokens_out = self._request(system, user, max_tokens)
                self.usage.add(tokens_in, tokens_out)
                return extract_json(text)
            except httpx.HTTPStatusError as exc:
                last = exc
                if exc.response.status_code not in RETRY_STATUS:
                    detail = exc.response.text[:300]
                    raise LLMError(f"El proveedor respondió {exc.response.status_code}: {detail}") from exc
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last = exc
            except LLMError as exc:
                # JSON roto: se reintenta una vez pidiendo solo JSON.
                last = exc
                user = user + "\n\nIMPORTANTE: responde únicamente con un objeto JSON válido."
            if attempt < self.retries:
                delay = min(60.0, 2.0 * (2**attempt))
                logger.warning("LLM %s: reintento %s en %.0fs (%s)", task, attempt + 1, delay, last)
                self.sleep(delay)
        raise LLMError(f"El proveedor no respondió tras {self.retries + 1} intentos: {last}")


class FakeLLM:
    """Modelo determinista para tests y demos sin red.

    ``responder(task, system, user) -> dict`` decide la respuesta. Por defecto
    usa ``webapp.generation.fake.respond``.
    """

    def __init__(self, responder: Callable[[str, str, str], dict] | None = None) -> None:
        from webapp.generation import fake

        self.responder = responder or fake.respond
        self.usage = Usage()
        self.calls: list[str] = []

    def complete_json(self, system: str, user: str, *, max_tokens: int = 8000, task: str = "") -> dict:
        self.calls.append(task)
        self.usage.add(len(system + user) // 4, 400)
        return self.responder(task, system, user)


# Fábrica sustituible en los tests (monkeypatch) o con AULA_LLM_FAKE=1.
def make_model(settings: dict[str, Any]) -> JSONModel:
    from webapp import config

    if config.LLM_FAKE:
        return FakeLLM()
    return HttpLLM(settings)
