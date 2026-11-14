"""Herramientas Python de los agentes del Estudio (ADR-023).

Cada ``JobToolbox`` se crea para una tarea concreta de un trabajo: solo puede
leer los fragmentos de ``document.json`` de ese trabajo y entregar su resultado.
No hay shell, red ni rutas de archivo: los fragmentos se piden por id.

El agente entrega llamando a ``submit_<tarea>(data)``. La herramienta valida con
las reglas reales del producto; si algo falla, lanza ``ValueError`` y nas-adk
devuelve el error al modelo para que corrija en el mismo turno.
"""

from __future__ import annotations

import copy
import json
from typing import Any

from nas.adk import FunctionTool

from webapp.authoring.package import validate_assessment, validate_lesson
from webapp.generation import verify

MAX_SEARCH_RESULTS = 8
FRAGMENT_PREVIEW = 1800


class JobToolbox:
    """Herramientas y resultado entregado para una tarea de un trabajo."""

    def __init__(
        self,
        *,
        task: str,
        document: dict,
        languages: list[str],
        scope_chunk_ids: list[str] | None = None,
        lesson_slugs: list[str] | None = None,
        lesson_slug: str | None = None,
    ) -> None:
        self.task = task
        self.languages = list(languages) or ["es"]
        self.chunks: dict[str, dict] = {chunk["id"]: chunk for chunk in document.get("chunks", [])}
        scope = [cid for cid in (scope_chunk_ids or []) if cid in self.chunks]
        self.scope = scope or list(self.chunks)
        self.lesson_slugs = list(lesson_slugs or [])
        self.lesson_slug = lesson_slug
        self.submitted: dict | None = None
        self.reads: list[str] = []

    # ------------------------------------------------------------------ lectura

    def read_fragment(self, chunk_id: str) -> str:
        """Devuelve el texto completo de un fragmento del documento por su id (p. ej. "d1:p3:c1")."""
        chunk = self.chunks.get(chunk_id.strip())
        if chunk is None:
            raise ValueError(f"No existe el fragmento {chunk_id!r}.")
        self.reads.append(chunk_id)
        return json.dumps({"id": chunk["id"], "page": chunk.get("page"), "text": chunk["text"]}, ensure_ascii=False)

    def search_document(self, query: str, limit: int = 5) -> str:
        """Busca en los fragmentos de esta tarea los que más vocabulario comparten con la consulta."""
        wanted = verify._words(query)
        if not wanted:
            raise ValueError("La consulta necesita palabras de al menos 5 letras.")
        scored = []
        for cid in self.scope:
            words = verify._words(self.chunks[cid]["text"])
            score = len(wanted & words)
            if score:
                scored.append((score, cid))
        scored.sort(key=lambda item: (-item[0], item[1]))
        top = max(1, min(int(limit or 5), MAX_SEARCH_RESULTS))
        results = [
            {
                "id": cid,
                "page": self.chunks[cid].get("page"),
                "score": score,
                "text": self.chunks[cid]["text"][:FRAGMENT_PREVIEW],
            }
            for score, cid in scored[:top]
        ]
        return json.dumps({"results": results}, ensure_ascii=False)

    # ------------------------------------------------------------------ entregas

    def _need(self, data: Any) -> dict:
        if not isinstance(data, dict):
            raise ValueError("data debe ser un objeto JSON.")
        return data

    def _localized(self, value: Any, field: str) -> None:
        if isinstance(value, str) and value.strip() and len(self.languages) == 1:
            return
        if not isinstance(value, dict):
            raise ValueError(f"{field}: se esperaba un objeto por idioma {self.languages}.")
        missing = [lang for lang in self.languages if not str(value.get(lang) or "").strip()]
        if missing:
            raise ValueError(f"{field}: falta el texto en {missing}.")

    def submit_outline(self, data: dict) -> str:
        """Entrega el temario del capítulo (title, subtitle, description, objectives, lessons)."""
        data = self._need(data)
        self._localized(data.get("title"), "title")
        lessons = data.get("lessons")
        if not isinstance(lessons, list) or not lessons:
            raise ValueError("lessons: se esperaba una lista con al menos una lección.")
        for index, lesson in enumerate(lessons):
            if not isinstance(lesson, dict):
                raise ValueError(f"lessons[{index}]: se esperaba un objeto.")
            self._localized(lesson.get("title"), f"lessons[{index}].title")
            unknown = [c for c in lesson.get("chunk_ids") or [] if c not in self.chunks]
            if unknown:
                raise ValueError(f"lessons[{index}].chunk_ids: ids inexistentes {unknown[:5]}.")
        self.submitted = data
        return "Temario recibido. Responde solo OK."

    def submit_course(self, data: dict) -> str:
        """Entrega la ficha del curso (title, subtitle, description, level, tags, source)."""
        data = self._need(data)
        for field in ("title", "description"):
            self._localized(data.get(field), field)
        self.submitted = data
        return "Ficha recibida. Responde solo OK."

    def _lesson_errors(self, data: dict) -> list[str]:
        try:
            validate_lesson(data, self.languages)
        except (ValueError, TypeError) as exc:
            return [str(exc)]
        return []

    def check_lesson(self, data: dict) -> str:
        """Comprueba una lección sin entregarla: errores de formato y bloques con citas dudosas."""
        data = self._need(data)
        errors = self._lesson_errors(data)
        package = {"languages": self.languages, "chapters": [{"lessons": [copy.deepcopy(data)]}]}
        report = verify.verify_package(package, self.chunks)
        return json.dumps(
            {
                "ok": not errors,
                "errors": errors,
                "invalid_refs": report["invalid_refs"][:10],
                "unsupported_blocks": [item["block"] for item in report["unsupported"]][:20],
                "cited_pct": report["cited_pct"],
            },
            ensure_ascii=False,
        )

    def submit_lesson(self, data: dict) -> str:
        """Entrega la lección completa (slug, title, summary, minutes, objectives, key_points, blocks)."""
        data = self._need(data)
        errors = self._lesson_errors(data)
        if errors:
            raise ValueError("La lección no pasa la validación: " + "; ".join(errors) + ". Corrígela y vuelve a entregarla.")
        if self.lesson_slug:
            data["slug"] = self.lesson_slug
        self.submitted = data
        return "Lección guardada. Responde solo OK."

    def submit_assessment(self, data: dict) -> str:
        """Entrega la autoevaluación y el glosario del capítulo ({"quiz": {...}, "glossary": [...]})."""
        data = self._need(data)
        validate_assessment(data, self.languages, self.lesson_slugs)
        self.submitted = data
        return "Autoevaluación guardada. Responde solo OK."

    # ------------------------------------------------------------------ catálogo

    def tools(self) -> list[FunctionTool]:
        readers = [
            FunctionTool(self.read_fragment, parallel_safe=True),
            FunctionTool(self.search_document, parallel_safe=True),
        ]
        if self.task == "outline":
            return [*readers, FunctionTool(self.submit_outline)]
        if self.task == "course":
            return [FunctionTool(self.submit_course)]
        if self.task == "lesson":
            return [*readers, FunctionTool(self.check_lesson), FunctionTool(self.submit_lesson)]
        if self.task == "assessment":
            return [*readers, FunctionTool(self.submit_assessment)]
        raise ValueError(f"Tarea desconocida: {self.task}")

    @property
    def submit_name(self) -> str:
        return f"submit_{self.task}"
