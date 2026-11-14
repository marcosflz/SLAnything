"""Respuestas deterministas que cumplen el contrato, para tests y demos sin red.

Construye el contenido a partir de los propios fragmentos del documento, así
las citas y la verificación funcionan igual que con un modelo real.
"""

from __future__ import annotations

import re

from webapp.generation.prompts import parse_task


def _loc(languages: list[str], es: str, en: str | None = None) -> dict:
    return {lang: (es if lang == "es" else (en or f"[EN] {es}")) for lang in languages}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "leccion"


def respond(task: str, system: str, user: str) -> dict:
    data = parse_task(user)
    kind = data.get("task") or task
    languages = data.get("languages") or ["es"]
    if kind == "outline":
        return _outline(data, languages)
    if kind == "course":
        return {
            "title": _loc(languages, data.get("title_hint") or "Unidad generada", "Generated unit"),
            "subtitle": _loc(languages, "Aprendizaje guiado a partir del documento", "Guided learning from the document"),
            "description": _loc(
                languages,
                "Unidad didáctica generada a partir del documento subido, con lecciones, autoevaluación y glosario.",
                "Learning unit generated from the uploaded document, with lessons, self-assessment and glossary.",
            ),
            "level": _loc(languages, "Principiante", "Beginner"),
            "tags": ["documento", "generado"],
            "source": {"title": (data.get("documents") or ["Documento"])[0], "author": "Documento de origen", "year": None},
        }
    if kind == "lesson":
        return _lesson(data, languages)
    if kind == "assessment":
        return _assessment(data, languages)
    raise ValueError(f"Tarea desconocida para el modelo falso: {kind}")


def _outline(data: dict, languages: list[str]) -> dict:
    fragments = data.get("fragments") or []
    ids = [fragment["id"] for fragment in fragments]
    wanted = data.get("lessons_per_chapter")
    count = wanted if isinstance(wanted, int) else 3
    count = max(2, min(count, max(2, len(ids))))
    groups = [ids[index::count] for index in range(count)]
    title = data.get("section_title") or f"Capítulo {data.get('chapter_number', 1)}"
    return {
        "title": _loc(languages, title, title),
        "subtitle": _loc(languages, f"Ideas clave de «{title}»", f"Key ideas of “{title}”"),
        "description": _loc(
            languages,
            f"Recorrido guiado por {title}: conceptos, ejemplos del documento y autoevaluación.",
            f"A guided tour of {title}: concepts, examples from the document and self-assessment.",
        ),
        "objectives": [
            {"id": f"o{n}", "text": _loc(languages, f"Explicar la idea {n} de {title}", f"Explain idea {n} of {title}")}
            for n in range(1, 4)
        ],
        "lessons": [
            {
                "slug": f"parte-{n}",
                "title": _loc(languages, f"{title} · parte {n}", f"{title} · part {n}"),
                "summary": _loc(
                    languages,
                    f"Segunda aproximación a {title}, centrada en la parte {n} del texto original." if n > 1 else f"Primera aproximación a {title} a partir del documento original.",
                    f"Part {n} of {title}, based on the original document.",
                ),
                "objectives": [f"o{min(n, 3)}"],
                "chunk_ids": group or ids[:1],
            }
            for n, group in enumerate(groups, start=1)
        ],
    }


def _paragraph(fragment: dict, lang: str) -> str:
    words = re.findall(r"\w+", fragment.get("text", ""))[:60]
    body = " ".join(words)
    prefix = "Según el documento, " if lang == "es" else "According to the document, "
    return f"{prefix}{body}."


def _lesson(data: dict, languages: list[str]) -> dict:
    plan = data.get("lesson") or {}
    fragments = data.get("fragments") or [{"id": "d1:c1", "text": "contenido"}]
    title = plan.get("title") or _loc(languages, "Lección", "Lesson")
    filler_es = (
        "Este apartado desarrolla la idea con calma, relaciona los conceptos entre sí "
        "y propone un ejemplo sencillo para comprobar que se ha entendido bien antes "
        "de avanzar a la siguiente parte de la unidad didáctica."
    )
    filler_en = (
        "This section develops the idea calmly, connects the concepts with each other "
        "and proposes a simple example to check understanding before moving on to the "
        "next part of the learning unit."
    )
    blocks: dict[str, list] = {}
    for lang in languages:
        filler = filler_es if lang == "es" else filler_en
        items: list[dict] = [{"type": "lead", "html": f"<strong>{title.get(lang, '')}</strong>: {filler}"}]
        for index, fragment in enumerate(fragments[:6]):
            items.append({"type": "p", "html": f"{_paragraph(fragment, lang)} {filler}", "sources": [fragment["id"]]})
            if index == 0:
                items.append({"type": "h2", "text": "Idea principal" if lang == "es" else "Main idea"})
        items.append(
            {
                "type": "callout",
                "tone": "tip",
                "title": "Para recordar" if lang == "es" else "Remember",
                "html": filler,
                "sources": [fragments[0]["id"]],
            }
        )
        while sum(len(str(block).split()) for block in items) < 330:
            items.append({"type": "p", "html": f"{_paragraph(fragments[-1], lang)} {filler}", "sources": [fragments[-1]["id"]]})
        items.append(
            {
                "type": "check",
                "question": "¿Cuál es la idea principal de esta lección?" if lang == "es" else "What is the main idea of this lesson?",
                "answer": filler,
            }
        )
        items.append(
            {
                "type": "keypoints",
                "items": [
                    "Primera idea clave de la lección." if lang == "es" else "First key idea of the lesson.",
                    "Segunda idea clave de la lección." if lang == "es" else "Second key idea of the lesson.",
                    "Tercera idea clave de la lección." if lang == "es" else "Third key idea of the lesson.",
                ],
            }
        )
        blocks[lang] = items
    return {
        "slug": plan.get("slug") or "leccion",
        "title": title,
        "summary": plan.get("summary") or _loc(languages, "Resumen de la lección generada.", "Summary of the generated lesson."),
        "minutes": data.get("minutes") or 12,
        "objectives": {lang: ["Comprender la idea principal.", "Aplicarla a un ejemplo."] if lang == "es" else ["Understand the main idea.", "Apply it to an example."] for lang in languages},
        "key_points": {lang: ["Idea uno.", "Idea dos."] if lang == "es" else ["Idea one.", "Idea two."] for lang in languages},
        "blocks": blocks,
    }


def _assessment(data: dict, languages: list[str]) -> dict:
    lessons = data.get("lessons") or []
    fragments = data.get("fragments") or [{"id": "d1:c1"}]
    count = int(data.get("question_count") or 8)
    kinds = data.get("question_kinds") or ["single", "multiple", "true_false"]
    questions = []
    for n in range(1, max(4, count) + 1):
        kind = kinds[(n - 1) % len(kinds)]
        if kind == "true_false":
            options = {lang: ["Verdadero", "Falso"] if lang == "es" else ["True", "False"] for lang in languages}
            correct: int | list[int] = n % 2
        elif kind == "multiple":
            options = {lang: [f"Opción {c}" if lang == "es" else f"Option {c}" for c in "ABCD"] for lang in languages}
            correct = [0, 2]
        else:
            options = {lang: [f"Respuesta {c}" if lang == "es" else f"Answer {c}" for c in "ABCD"] for lang in languages}
            correct = n % 4
        questions.append(
            {
                "id": f"q{n}",
                "kind": kind,
                "prompt": _loc(languages, f"Pregunta {n} sobre el capítulo", f"Question {n} about the chapter"),
                "options": options,
                "correct": correct,
                "explanation": _loc(languages, "La explicación justifica la respuesta correcta.", "The explanation justifies the correct answer."),
                "difficulty": ["easy", "medium", "hard"][n % 3],
                "objective": "o1",
                "source": fragments[(n - 1) % len(fragments)]["id"],
            }
        )
    lesson_slug = lessons[0]["slug"] if lessons else None
    return {
        "quiz": {
            "id": "autoevaluacion",
            "title": _loc(languages, "Autoevaluación del capítulo", "Chapter self-assessment"),
            "description": _loc(languages, "Comprueba lo que has aprendido en este capítulo.", "Check what you learned in this chapter."),
            "pass_score": 80,
            "questions": questions,
        },
        "glossary": [
            {
                "term": _loc(languages, f"Término {n}", f"Term {n}"),
                "definition": _loc(languages, f"Definición del término {n} según el documento.", f"Definition of term {n} according to the document."),
                "lesson": lesson_slug,
            }
            for n in range(1, 7)
        ],
    }
