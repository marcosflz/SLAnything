"""Agentes nas-adk del Estudio: herramientas, runtime y modelos (ADR-023)."""

from __future__ import annotations

import json
import os

import pytest
from nas.adk.models import BaseLlm, LlmQuotaError, LlmRequest, LlmResponse, ToolCall

from webapp import config
from webapp.generation import fake, models, prompts, runtime
from webapp.generation.tools import JobToolbox

PARAGRAPH = (
    "La fotosíntesis transforma la energía luminosa en energía química dentro de los "
    "cloroplastos. Las plantas capturan dióxido de carbono y liberan oxígeno."
)
DOCUMENT = {
    "chunks": [
        {"id": "d1:c1", "page": 1, "text": PARAGRAPH},
        {"id": "d1:c2", "page": 2, "text": "La respiración celular libera energía almacenada en la glucosa."},
    ]
}


def _lesson_data() -> dict:
    task = prompts.lesson(
        chapter={"title": {"es": "Plantas"}},
        lesson_plan={"slug": "luz", "title": {"es": "La luz"}, "summary": {"es": "Cómo usan la luz las plantas verdes."}},
        lesson_number=1,
        lesson_count=1,
        fragments=DOCUMENT["chunks"],
        options={"languages": ["es"]},
    )
    return fake.respond("lesson", "", task)


def test_toolbox_reads_only_known_fragments_and_searches():
    box = JobToolbox(task="lesson", document=DOCUMENT, languages=["es"])
    assert json.loads(box.read_fragment("d1:c1"))["text"] == PARAGRAPH
    with pytest.raises(ValueError):
        box.read_fragment("../../etc/passwd")
    results = json.loads(box.search_document("respiración glucosa"))["results"]
    assert results[0]["id"] == "d1:c2"
    with pytest.raises(ValueError):
        box.search_document("a b")


def test_submit_lesson_validates_before_accepting():
    box = JobToolbox(task="lesson", document=DOCUMENT, languages=["es"], lesson_slug="luz")
    with pytest.raises(ValueError, match="no pasa la validación"):
        box.submit_lesson({"title": {"es": "Corta"}, "blocks": {"es": []}})
    assert box.submitted is None
    report = json.loads(box.check_lesson(_lesson_data()))
    assert report["ok"] is True
    box.submit_lesson({**_lesson_data(), "slug": "otro"})
    assert box.submitted["slug"] == "luz"  # el slug lo fija el temario
    assert {tool.name for tool in box.tools()} == {"read_fragment", "search_document", "check_lesson", "submit_lesson"}


def test_submit_assessment_rejects_unknown_lessons():
    box = JobToolbox(task="assessment", document=DOCUMENT, languages=["es"], lesson_slugs=["luz"])
    data = fake.respond(
        "assessment", "", prompts.assessment(chapter={}, lessons=[{"slug": "luz"}], fragments=DOCUMENT["chunks"], options={"languages": ["es"]})
    )
    box.submit_assessment(data)
    data["glossary"][0]["lesson"] = "inventada"
    with pytest.raises(ValueError, match="no existe"):
        box.submit_assessment(data)


class ScriptedLlm(BaseLlm):
    """Devuelve las respuestas indicadas en orden y registra cada petición."""

    model: str = "scripted"
    script: list = []
    seen: list = []

    async def generate_content_async(self, request: LlmRequest) -> LlmResponse:
        self.seen.append(request)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _call(name: str, data: dict) -> LlmResponse:
    return LlmResponse(
        tool_calls=[ToolCall(id=f"c{len(json.dumps(data))}", function={"name": name, "arguments": json.dumps({"data": data})})],
        finish_reason="tool_calls",
        usage={"input_tokens": 100, "output_tokens": 50},
    )


def _ok() -> LlmResponse:
    return LlmResponse(content="OK", usage={"input_tokens": 10, "output_tokens": 1})


def test_runtime_lets_the_agent_fix_a_rejected_submission():
    llm = ScriptedLlm(script=[_call("submit_lesson", {"title": "x"}), _call("submit_lesson", _lesson_data()), _ok()])
    box = JobToolbox(task="lesson", document=DOCUMENT, languages=["es"], lesson_slug="luz")
    result = runtime.run_agent(box, {}, "Escribe la lección", model_factory=lambda _: llm)
    assert result.data["slug"] == "luz"
    assert result.model_calls == 3
    assert (result.input_tokens, result.output_tokens) == (210, 101)
    # El error de validación vuelve al modelo como resultado de la herramienta.
    tool_messages = [m for m in llm.seen[1].messages if m["role"] == "tool"]
    assert "no pasa la validación" in tool_messages[0]["content"]


def test_runtime_retries_once_when_nothing_is_submitted():
    llm = ScriptedLlm(script=[_ok(), _ok()])
    box = JobToolbox(task="course", document=DOCUMENT, languages=["es"])
    with pytest.raises(runtime.LLMError, match="sin entregar"):
        runtime.run_agent(box, {}, "Ficha", model_factory=lambda _: llm)
    assert len(llm.seen) == 2
    assert "IMPORTANTE" in llm.seen[1].messages[-1]["content"]


def test_runtime_explains_provider_errors_without_fallback():
    llm = ScriptedLlm(script=[LlmQuotaError("limit reached")])
    box = JobToolbox(task="course", document=DOCUMENT, languages=["es"])
    with pytest.raises(runtime.LLMError, match="cuota"):
        runtime.run_agent(box, {}, "Ficha", model_factory=lambda _: llm)
    assert len(llm.seen) == 1


def test_runtime_stops_when_the_job_is_cancelled():
    llm = ScriptedLlm(script=[_ok()])
    box = JobToolbox(task="course", document=DOCUMENT, languages=["es"])
    with pytest.raises(runtime.Cancelled):
        runtime.run_agent(box, {}, "Ficha", is_cancelled=lambda: True, model_factory=lambda _: llm)
    assert llm.seen == []


def test_fake_agent_runs_through_the_real_runner(monkeypatch):
    monkeypatch.setattr(config, "LLM_FAKE", True)
    box = JobToolbox(task="course", document=DOCUMENT, languages=["es", "en"])
    message = prompts.course(chapters=[], options={"languages": ["es", "en"]}, source_names=["doc.md"])
    result = runtime.run_agent(box, {}, message)
    assert result.data["title"]["en"]


def test_subscription_model_gets_the_token_only_in_the_child_env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "AUTHORING_DIR", tmp_path)
    monkeypatch.setattr(config, "LLM_FAKE", False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-server-key")
    model = models.build_model({"provider": "claude-code", "model": "sonnet", "api_key": "tok-ana", "user_id": 7})
    assert type(model).__name__ == "ClaudeCodeLlm"
    assert model.env_policy == "scrub"
    assert model.max_concurrency == 1

    captured = {}

    async def fake_spawn(self, argv, *, env, cwd):
        captured.update(env)
        return None

    from nas.adk.models.claude_code import AsyncioProcessTransport

    monkeypatch.setattr(AsyncioProcessTransport, "spawn", fake_spawn)
    import asyncio

    asyncio.run(model.transport.spawn(["claude"], env={"PATH": "/bin"}, cwd=str(tmp_path)))
    assert captured["CLAUDE_CODE_OAUTH_TOKEN"] == "tok-ana"
    assert captured["CLAUDE_CONFIG_DIR"].endswith("/claude/7")
    assert "CLAUDE_CODE_OAUTH_TOKEN" not in os.environ
    assert oct((tmp_path / "claude" / "7").stat().st_mode & 0o777) == "0o700"

    other = models.build_model({"provider": "claude-code", "model": "", "api_key": "tok-luis", "user_id": 8})
    assert other.transport is not model.transport
    with pytest.raises(ValueError):
        models.build_model({"provider": "claude-code", "model": "", "api_key": "", "user_id": 9})
