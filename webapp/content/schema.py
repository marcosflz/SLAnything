"""Contrato del contenido didáctico.

Las lecciones son datos inmutables que las plantillas renderizan. Añadir un
capítulo consiste en crear módulos de lección y registrarlos en `course.py`.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Block = dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers para construir bloques
# ---------------------------------------------------------------------------

def p(html_text: str) -> Block:
    return {"type": "p", "html": html_text}


def lead(html_text: str) -> Block:
    return {"type": "lead", "html": html_text}


def h2(text: str, anchor: str | None = None) -> Block:
    return {"type": "h2", "text": text, "anchor": anchor or _slugify(text)}


def h3(text: str, anchor: str | None = None) -> Block:
    return {"type": "h3", "text": text, "anchor": anchor or _slugify(text)}


def callout(tone: str, title: str, html_text: str) -> Block:
    tones = {"info", "tip", "warning", "danger", "success", "note"}
    if tone not in tones:
        raise ValueError(f"Tono de callout desconocido: {tone}")
    return {"type": "callout", "tone": tone, "title": title, "html": html_text}


def figure(
    src: str,
    alt: str,
    caption: str,
    credit: str | None = None,
    wide: bool = False,
) -> Block:
    return {
        "type": "figure",
        "src": src,
        "alt": alt,
        "caption": caption,
        "credit": credit,
        "wide": wide,
    }


def code(language: str, source: str, caption: str | None = None) -> Block:
    return {
        "type": "code",
        "language": language,
        "code": source.strip("\n"),
        "caption": caption,
    }


def py(source: str, caption: str | None = None) -> Block:
    """Bloque Python ejecutable en el servidor y descargable.

    El código debe ser autocontenido y usar solo los módulos permitidos por
    `webapp/sandbox_runner.py`.
    """
    return {
        "type": "python",
        "language": "python",
        "code": source.strip("\n"),
        "caption": caption,
    }


def table(
    headers: list[str],
    rows: list[list[str]],
    caption: str | None = None,
    note: str | None = None,
) -> Block:
    return {
        "type": "table",
        "headers": headers,
        "rows": rows,
        "caption": caption,
        "note": note,
    }


def quote(text: str, source: str | None = None) -> Block:
    return {"type": "quote", "text": text, "source": source}


def lab(lab_id: str) -> Block:
    return {"type": "lab", "lab": lab_id}


def keypoints(items: list[str]) -> Block:
    return {"type": "keypoints", "items": items}


def check(question: str, answer: str) -> Block:
    return {"type": "check", "question": question, "answer": answer}


def bullets(items: list[str], ordered: bool = False) -> Block:
    return {"type": "list", "items": items, "ordered": ordered}


def divider() -> Block:
    return {"type": "divider"}


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Lesson:
    number: int
    slug: str
    title: str
    summary: str
    minutes: int
    objectives: tuple[str, ...]
    blocks: tuple[Block, ...]
    key_points: tuple[str, ...] = ()
    quiz_id: str | None = None

    @property
    def labs(self) -> tuple[str, ...]:
        return tuple(
            block["lab"] for block in self.blocks if block["type"] == "lab"
        )

    @property
    def python_blocks(self) -> tuple[tuple[int, Block], ...]:
        """Pares (índice 1-based, bloque) de los ejemplos ejecutables."""
        return tuple(
            (index, block)
            for index, block in enumerate(self.blocks, start=1)
            if block["type"] == "python"
        )

    @property
    def plain_text(self) -> str:
        parts: list[str] = [self.title, self.summary, *self.objectives, *self.key_points]
        for block in self.blocks:
            for key in ("html", "text", "caption", "note", "source", "code"):
                value = block.get(key)
                if isinstance(value, str):
                    parts.append(value)
            for key in ("items", "headers"):
                value = block.get(key)
                if isinstance(value, list):
                    parts.extend(str(item) for item in value)
            for row in block.get("rows", []):
                parts.extend(str(cell) for cell in row)
        return _strip_tags(" ".join(parts))

    @property
    def word_count(self) -> int:
        return len(self.plain_text.split())


@dataclass(frozen=True)
class Chapter:
    number: int
    slug: str
    title: str
    subtitle: str
    description: str
    level: str
    lessons: tuple[Lesson, ...] = field(default_factory=tuple)

    @property
    def total_minutes(self) -> int:
        return sum(lesson.minutes for lesson in self.lessons)

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)

    def lesson(self, slug: str) -> Lesson | None:
        return next((item for item in self.lessons if item.slug == slug), None)

    def neighbours(self, slug: str) -> tuple[Lesson | None, Lesson | None]:
        for index, lesson in enumerate(self.lessons):
            if lesson.slug == slug:
                previous = self.lessons[index - 1] if index > 0 else None
                following = (
                    self.lessons[index + 1]
                    if index + 1 < len(self.lessons)
                    else None
                )
                return previous, following
        return None, None


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str
    options: tuple[str, ...]
    correct: int
    explanation: str

    @property
    def correct_option(self) -> str:
        return self.options[self.correct]


@dataclass(frozen=True)
class Quiz:
    id: str
    title: str
    description: str
    pass_score: int
    questions: tuple[Question, ...]

    @property
    def total(self) -> int:
        return len(self.questions)


@dataclass(frozen=True)
class GlossaryTerm:
    term: str
    definition: str
    lesson: str | None = None


# ---------------------------------------------------------------------------
# Utilidades y validación
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _strip_tags(value: str) -> str:
    return _SPACE_RE.sub(" ", html.unescape(_TAG_RE.sub(" ", value))).strip()


def _slugify(value: str) -> str:
    value = value.lower()
    for source, target in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        value = value.replace(source, target)
    return _SLUG_RE.sub("-", value).strip("-")


def validate_content(
    course: Chapter,
    quizzes: dict[str, Quiz],
    known_labs: set[str],
    static_root: Path,
    glossary: tuple[GlossaryTerm, ...] = (),
) -> None:
    """Falla al arrancar si el contenido está mal enlazado.

    Es mejor un error claro en desarrollo que una imagen rota o un quiz
    inexistente descubierto por el estudiante.
    """
    errors: list[str] = []
    slugs: set[str] = set()

    if not course.lessons:
        errors.append("El curso no tiene lecciones.")

    for expected, lesson in enumerate(course.lessons, start=1):
        if lesson.number != expected:
            errors.append(
                f"Lección {lesson.slug}: número {lesson.number}, se esperaba {expected}."
            )
        if lesson.slug in slugs:
            errors.append(f"Slug duplicado: {lesson.slug}.")
        slugs.add(lesson.slug)
        if lesson.minutes <= 0:
            errors.append(f"Lección {lesson.slug}: duración inválida.")
        if not lesson.objectives:
            errors.append(f"Lección {lesson.slug}: sin objetivos.")
        if not lesson.key_points:
            errors.append(f"Lección {lesson.slug}: sin ideas clave.")
        for lab_id in lesson.labs:
            if lab_id not in known_labs:
                errors.append(f"Lección {lesson.slug}: lab desconocido '{lab_id}'.")
        if lesson.quiz_id and lesson.quiz_id not in quizzes:
            errors.append(f"Lección {lesson.slug}: quiz '{lesson.quiz_id}' inexistente.")
        for block in lesson.blocks:
            if block["type"] == "figure":
                image = static_root / block["src"]
                if not image.is_file():
                    errors.append(f"Lección {lesson.slug}: falta la imagen {block['src']}.")
            if block["type"] == "lab" and block["lab"] not in known_labs:
                errors.append(f"Lección {lesson.slug}: lab desconocido '{block['lab']}'.")
            if block["type"] == "python":
                if len(block["code"]) > 16_000:
                    errors.append(f"Lección {lesson.slug}: ejemplo Python demasiado largo.")
                try:
                    compile(block["code"], f"<{lesson.slug}>", "exec")
                except SyntaxError as exc:
                    errors.append(
                        f"Lección {lesson.slug}: ejemplo Python inválido "
                        f"(línea {exc.lineno}): {exc.msg}."
                    )

    for quiz in quizzes.values():
        if not quiz.questions:
            errors.append(f"Quiz {quiz.id}: sin preguntas.")
        if not 0 <= quiz.pass_score <= 100:
            errors.append(f"Quiz {quiz.id}: pass_score fuera de rango.")
        seen: set[str] = set()
        for question in quiz.questions:
            if question.id in seen:
                errors.append(f"Quiz {quiz.id}: id de pregunta duplicado '{question.id}'.")
            seen.add(question.id)
            if not 0 <= question.correct < len(question.options):
                errors.append(
                    f"Quiz {quiz.id}/{question.id}: índice correcto fuera de rango."
                )
            if len(question.options) < 2:
                errors.append(f"Quiz {quiz.id}/{question.id}: menos de dos opciones.")

    for term in glossary:
        if not term.term.strip() or not term.definition.strip():
            errors.append("Glosario: término o definición vacíos.")

    if errors:
        raise ValueError("Contenido inválido:\n- " + "\n- ".join(errors))
