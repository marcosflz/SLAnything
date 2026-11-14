"""Los cuatro agentes del Estudio: instrucciones y límites (ADR-023)."""

from __future__ import annotations

from dataclasses import dataclass

from webapp.generation import prompts


@dataclass(frozen=True)
class AgentSpec:
    name: str
    instruction: str
    max_model_calls: int
    max_turns: int


_TOOLS_NOTE = {
    "outline": (
        "Herramientas: read_fragment(chunk_id) para leer un fragmento completo, "
        "search_document(query) para buscar en la sección y submit_outline(data) para entregar."
    ),
    "course": "Herramienta: submit_course(data) para entregar la ficha.",
    "lesson": (
        "Herramientas: read_fragment(chunk_id), search_document(query), "
        "check_lesson(data) para comprobar un borrador sin entregarlo y "
        "submit_lesson(data) para entregar la lección definitiva."
    ),
    "assessment": (
        "Herramientas: read_fragment(chunk_id), search_document(query) y "
        "submit_assessment(data) para entregar quiz y glosario."
    ),
}

_LIMITS = {
    "outline": (8, 8),
    "course": (4, 4),
    "lesson": (12, 12),
    "assessment": (8, 8),
}


def spec(task: str) -> AgentSpec:
    calls, turns = _LIMITS[task]
    instruction = (
        f"{prompts.SYSTEM}\n\n{_TOOLS_NOTE[task]}\n\n"
        f"Entrega SIEMPRE el resultado llamando a submit_{task} con el argumento "
        "\"data\" (el objeto completo). Si la herramienta devuelve un error, corrige "
        "exactamente lo que indica y vuelve a llamarla. Después de una entrega "
        "aceptada, responde solo «OK». No escribas el resultado como texto."
    )
    return AgentSpec(name=f"slanything-{task}", instruction=instruction, max_model_calls=calls, max_turns=turns)
