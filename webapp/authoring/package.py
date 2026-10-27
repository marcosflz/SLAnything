"""Contrato JSON de una unidad didáctica generada.

El agente de OpenCode nunca escribe módulos Python. Produce un único
``course.json`` con datos bilingües; este módulo lo valida, sanea el HTML y lo
convierte en los objetos inmutables que ya consume el catálogo. Así el contenido
generado no se ejecuta y un paquete roto se rechaza antes de publicarse.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from webapp.authoring.sanitize import sanitize_html
from webapp.content.catalog import Book, Course
from webapp.content.program import Program
from webapp.content.schema import (
    Chapter,
    GlossaryTerm,
    Lesson,
    Question,
    Quiz,
)

LANGS = ("es", "en")
ALLOWED_ACCENTS = {"blue", "violet", "green", "amber"}
ALLOWED_TONES = {"info", "tip", "warning", "danger", "success", "note"}
TONE_ALIASES = {
    "warn": "warning",
    "caution": "warning",
    "error": "danger",
    "important": "warning",
    "hint": "tip",
    "neutral": "info",
}
ALLOWED_CODE_LANGS = {"python", "bash", "text", "json", "sql", "html", "css", "javascript"}
ALLOWED_BLOCKS = {
    "lead",
    "p",
    "h2",
    "h3",
    "callout",
    "table",
    "quote",
    "list",
    "keypoints",
    "check",
    "divider",
    "code",
    "python",
}

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str, fallback: str = "unidad", max_length: int = 72) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = _SLUG_RE.sub("-", value.lower()).strip("-")
    value = re.sub(r"-{2,}", "-", value)
    return (value[:max_length].strip("-") or fallback)


def _text(value: Any, where: str, minimum: int = 1, maximum: int = 8000) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{where}: se esperaba texto.")
    value = value.strip()
    if len(value) < minimum:
        raise ValueError(f"{where}: texto demasiado corto.")
    if len(value) > maximum:
        raise ValueError(f"{where}: texto demasiado largo (máximo {maximum}).")
    return value


def _html(value: Any, where: str, minimum: int = 20, maximum: int = 12_000) -> str:
    cleaned = sanitize_html(_text(value, where, minimum=1, maximum=maximum), maximum)
    if len(cleaned) < minimum:
        raise ValueError(f"{where}: HTML demasiado corto.")
    return cleaned


def _localized(value: Any, lang: str, where: str) -> Any:
    """Lee un campo localizado; acepta una cadena si hay un solo idioma."""
    if isinstance(value, dict):
        if lang not in value:
            raise ValueError(f"{where}: falta la versión «{lang}».")
        return value[lang]
    if isinstance(value, str):
        return value
    raise ValueError(f"{where}: se esperaba texto o un objeto por idioma.")


def _localized_text(
    value: Any,
    lang: str,
    where: str,
    minimum: int = 1,
    maximum: int = 8000,
) -> str:
    return _text(_localized(value, lang, where), f"{where}.{lang}", minimum, maximum)


def _localized_list(
    value: Any,
    lang: str,
    where: str,
    minimum: int,
    maximum: int,
    item_max: int = 500,
) -> tuple[str, ...]:
    data = _localized(value, lang, where)
    if not isinstance(data, list):
        raise ValueError(f"{where}.{lang}: se esperaba una lista.")
    if not minimum <= len(data) <= maximum:
        raise ValueError(
            f"{where}.{lang}: se esperaban entre {minimum} y {maximum} elementos."
        )
    return tuple(
        _text(item, f"{where}.{lang}[{index}]", 2, item_max)
        for index, item in enumerate(data)
    )


def _languages(package: dict[str, Any]) -> tuple[str, ...]:
    declared = package.get("languages")
    if declared is None:
        title = package.get("course", {}).get("title")
        declared = [lang for lang in LANGS if isinstance(title, dict) and lang in title]
        if not declared:
            declared = ["es"]
    if not isinstance(declared, list) or not declared:
        raise ValueError("languages: se esperaba una lista no vacía.")
    result: list[str] = []
    for lang in declared:
        if lang not in LANGS:
            raise ValueError(f"languages: idioma desconocido {lang!r}.")
        if lang not in result:
            result.append(lang)
    return tuple(result)


def _block(raw: Any, lang: str, where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}: cada bloque debe ser un objeto.")
    kind = raw.get("type")
    if kind not in ALLOWED_BLOCKS:
        raise ValueError(
            f"{where}: tipo de bloque no permitido {kind!r}. "
            f"Permitidos: {', '.join(sorted(ALLOWED_BLOCKS))}."
        )

    if kind in {"p", "lead"}:
        return {"type": kind, "html": _html(raw.get("html"), f"{where}.html")}
    if kind in {"h2", "h3"}:
        text = _text(raw.get("text"), f"{where}.text", 3, 180)
        return {"type": kind, "text": text, "anchor": slugify(text, "seccion")}
    if kind == "callout":
        tone = str(raw.get("tone", "info")).lower()
        tone = TONE_ALIASES.get(tone, tone)
        if tone not in ALLOWED_TONES:
            raise ValueError(f"{where}.tone: tono desconocido {tone!r}.")
        return {
            "type": "callout",
            "tone": tone,
            "title": _text(raw.get("title"), f"{where}.title", 2, 160),
            "html": _html(raw.get("html"), f"{where}.html"),
        }
    if kind == "table":
        headers = raw.get("headers")
        rows = raw.get("rows")
        if not isinstance(headers, list) or not 2 <= len(headers) <= 6:
            raise ValueError(f"{where}.headers: se esperaban entre 2 y 6 columnas.")
        if not isinstance(rows, list) or not 1 <= len(rows) <= 20:
            raise ValueError(f"{where}.rows: se esperaban entre 1 y 20 filas.")
        clean_headers = tuple(
            _html(header, f"{where}.headers[{index}]", 1, 500)
            for index, header in enumerate(headers)
        )
        clean_rows: list[list[str]] = []
        for row_index, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != len(headers):
                raise ValueError(f"{where}.rows[{row_index}]: columnas desiguales.")
            clean_rows.append(
                [
                    _html(cell, f"{where}.rows[{row_index}][{column_index}]", 1, 1000)
                    for column_index, cell in enumerate(row)
                ]
            )
        caption = raw.get("caption")
        note = raw.get("note")
        return {
            "type": "table",
            "headers": list(clean_headers),
            "rows": clean_rows,
            "caption": _text(caption, f"{where}.caption", 1, 300) if caption else None,
            "note": _html(note, f"{where}.note", 1, 1000) if note else None,
        }
    if kind == "quote":
        source = raw.get("source")
        return {
            "type": "quote",
            "text": _html(raw.get("text"), f"{where}.text", 10, 2000),
            "source": _text(source, f"{where}.source", 1, 200) if source else None,
        }
    if kind == "list":
        items = raw.get("items")
        if not isinstance(items, list) or not 2 <= len(items) <= 15:
            raise ValueError(f"{where}.items: se esperaban entre 2 y 15 elementos.")
        return {
            "type": "list",
            "items": [
                _html(item, f"{where}.items[{index}]", 2, 800)
                for index, item in enumerate(items)
            ],
            "ordered": bool(raw.get("ordered", False)),
        }
    if kind == "keypoints":
        items = raw.get("items")
        if not isinstance(items, list) or not 3 <= len(items) <= 10:
            raise ValueError(f"{where}.items: se esperaban entre 3 y 10 ideas clave.")
        return {
            "type": "keypoints",
            "items": [
                _html(item, f"{where}.items[{index}]", 4, 600)
                for index, item in enumerate(items)
            ],
        }
    if kind == "check":
        return {
            "type": "check",
            "question": _text(raw.get("question"), f"{where}.question", 8, 300),
            "answer": _html(raw.get("answer"), f"{where}.answer", 10, 3000),
        }
    if kind == "divider":
        return {"type": "divider"}
    if kind == "code":
        language = str(raw.get("language", "text")).lower()
        if language not in ALLOWED_CODE_LANGS:
            raise ValueError(f"{where}.language: lenguaje no permitido {language!r}.")
        caption = raw.get("caption")
        return {
            "type": "code",
            "language": language,
            "code": _text(raw.get("code"), f"{where}.code", 3, 12_000),
            "caption": _text(caption, f"{where}.caption", 1, 200) if caption else None,
        }
    # kind == "python": se valida sintaxis antes de guardar.
    source = _text(raw.get("code"), f"{where}.code", 3, 16_000)
    try:
        compile(source, f"<{where}>", "exec")
    except SyntaxError as exc:
        raise ValueError(
            f"{where}.code: Python inválido (línea {exc.lineno}): {exc.msg}."
        ) from exc
    caption = raw.get("caption")
    return {
        "type": "python",
        "language": "python",
        "code": source,
        "caption": _text(caption, f"{where}.caption", 1, 200) if caption else None,
    }


def _blocks(value: Any, lang: str, where: str) -> tuple[dict[str, Any], ...]:
    if isinstance(value, dict):
        data = value.get(lang)
    else:
        data = value
    if not isinstance(data, list):
        raise ValueError(f"{where}.{lang}: falta la lista de bloques.")
    if not 5 <= len(data) <= 40:
        raise ValueError(f"{where}.{lang}: se esperaban entre 5 y 40 bloques.")
    blocks = tuple(
        _block(block, lang, f"{where}.{lang}[{index}]")
        for index, block in enumerate(data)
    )
    kinds = [block["type"] for block in blocks]
    if kinds[0] != "lead":
        raise ValueError(f"{where}.{lang}: debe empezar con un bloque «lead».")
    if kinds[-1] != "keypoints":
        raise ValueError(f"{where}.{lang}: debe terminar con «keypoints».")
    if "check" not in kinds:
        raise ValueError(f"{where}.{lang}: falta al menos un bloque «check».")
    if "callout" not in kinds:
        raise ValueError(f"{where}.{lang}: falta al menos un bloque «callout».")
    return blocks


def _quiz(raw: Any, lang: str, where: str) -> Quiz:
    if not isinstance(raw, dict):
        raise ValueError(f"{where}.{lang}: falta el quiz del capítulo.")
    questions_raw = raw.get("questions")
    if not isinstance(questions_raw, list) or not 4 <= len(questions_raw) <= 10:
        raise ValueError(f"{where}.questions: se esperaban entre 4 y 10 preguntas.")
    questions: list[Question] = []
    seen: set[str] = set()
    for index, item in enumerate(questions_raw):
        if not isinstance(item, dict):
            raise ValueError(f"{where}.questions[{index}]: se esperaba un objeto.")
        question_id = slugify(item.get("id", f"q{index + 1}"), f"q{index + 1}", 24)
        if question_id in seen:
            raise ValueError(f"{where}.questions: id duplicado {question_id!r}.")
        seen.add(question_id)
        options = _localized_list(
            item.get("options"), lang, f"{where}.questions[{index}].options", 2, 5, 400
        )
        correct = item.get("correct")
        if not isinstance(correct, int) or not 0 <= correct < len(options):
            raise ValueError(f"{where}.questions[{index}].correct: índice fuera de rango.")
        questions.append(
            Question(
                id=question_id,
                prompt=_localized_text(
                    item.get("prompt"), lang, f"{where}.questions[{index}].prompt", 8, 500
                ),
                options=options,
                correct=correct,
                explanation=_localized_text(
                    item.get("explanation"),
                    lang,
                    f"{where}.questions[{index}].explanation",
                    15,
                    1200,
                ),
            )
        )
    quiz_id = slugify(raw.get("id", f"{where}-quiz"), f"{where}-quiz", 90)
    return Quiz(
        id=quiz_id,
        title=_localized_text(raw.get("title"), lang, f"{where}.title", 3, 200),
        description=_localized_text(
            raw.get("description"), lang, f"{where}.description", 10, 1200
        ),
        pass_score=int(raw.get("pass_score", 80)),
        questions=tuple(questions),
    )


@dataclass(frozen=True)
class ParsedPackage:
    slug: str
    languages: tuple[str, ...]
    courses: dict[str, Course]
    quizzes: dict[str, dict[str, Quiz]]
    glossaries: dict[str, tuple[GlossaryTerm, ...]]
    summary: dict[str, Any]

    def course_for(self, lang: str) -> Course | None:
        return self.courses.get(lang)


def parse_package(
    package: dict[str, Any],
    *,
    slug_override: str | None = None,
) -> ParsedPackage:
    """Valida y convierte un paquete JSON en cursos, quizzes y glosario."""
    if not isinstance(package, dict):
        raise ValueError("El paquete debe ser un objeto JSON.")
    if int(package.get("schema_version", 0)) != 1:
        raise ValueError("schema_version: se esperaba 1.")

    languages = _languages(package)
    raw_course = package.get("course")
    if not isinstance(raw_course, dict):
        raise ValueError("course: falta el objeto del curso.")
    base_slug = slug_override or package.get("slug") or raw_course.get("slug") or "unidad"
    base_slug = slugify(base_slug)
    course_slug = base_slug if base_slug.startswith("gen-") else f"gen-{base_slug}"

    raw_chapters = package.get("chapters")
    if not isinstance(raw_chapters, list) or not 1 <= len(raw_chapters) <= 4:
        raise ValueError("chapters: se esperaban entre 1 y 4 capítulos.")

    source = raw_course.get("source") if isinstance(raw_course.get("source"), dict) else {}
    book = None
    source_title = str(source.get("title") or "").strip()
    if source_title:
        year = source.get("year")
        book = Book(
            title=source_title[:300],
            author=str(source.get("author") or "Documento de origen")[:200],
            year=int(year) if isinstance(year, int) and 1000 <= year <= 2200 else None,
            url=(
                str(source.get("url"))[:500]
                if str(source.get("url") or "").startswith(("http://", "https://"))
                else None
            ),
        )

    tags_raw = raw_course.get("tags")
    tags = tuple(
        _text(tag, "course.tags", 2, 40)
        for tag in (tags_raw if isinstance(tags_raw, list) else [])
    )[:6] or ("documento", "generado")
    accent = str(raw_course.get("accent") or "violet")
    if accent not in ALLOWED_ACCENTS:
        accent = "violet"

    courses: dict[str, Course] = {}
    all_quizzes: dict[str, dict[str, Quiz]] = {lang: {} for lang in languages}
    all_glossaries: dict[str, tuple[GlossaryTerm, ...]] = {lang: () for lang in languages}

    for lang in languages:
        title = _localized_text(raw_course.get("title"), lang, "course.title", 3, 200)
        subtitle = _localized_text(
            raw_course.get("subtitle"), lang, "course.subtitle", 3, 300
        )
        description = _localized_text(
            raw_course.get("description"), lang, "course.description", 20, 1500
        )
        level = _localized_text(raw_course.get("level"), lang, "course.level", 3, 120)
        chapters: list[Chapter] = []
        quiz_map: dict[str, Quiz] = {}
        glossary: list[GlossaryTerm] = []
        chapter_slugs: set[str] = set()
        lesson_slugs_seen: set[str] = set()
        total_lessons = 0

        for chapter_index, raw_chapter in enumerate(raw_chapters, start=1):
            if not isinstance(raw_chapter, dict):
                raise ValueError(f"chapters[{chapter_index - 1}]: se esperaba un objeto.")
            number = raw_chapter.get("number", chapter_index)
            if number != chapter_index:
                raise ValueError(
                    f"chapters[{chapter_index - 1}].number: se esperaba {chapter_index}."
                )
            chapter_base = slugify(
                raw_chapter.get("slug", f"capitulo-{chapter_index}"),
                f"capitulo-{chapter_index}",
                50,
            )
            chapter_slug = slugify(f"{course_slug}-{chapter_base}", chapter_base, 100)
            if chapter_slug in chapter_slugs:
                raise ValueError(f"Capítulo duplicado: {chapter_slug}.")
            chapter_slugs.add(chapter_slug)
            chapter_title = _localized_text(
                raw_chapter.get("title"), lang, f"chapter[{chapter_index}].title", 3, 200
            )
            chapter_subtitle = _localized_text(
                raw_chapter.get("subtitle"),
                lang,
                f"chapter[{chapter_index}].subtitle",
                3,
                300,
            )
            chapter_description = _localized_text(
                raw_chapter.get("description"),
                lang,
                f"chapter[{chapter_index}].description",
                20,
                1500,
            )
            chapter_level = _localized_text(
                raw_chapter.get("level", raw_course.get("level")),
                lang,
                f"chapter[{chapter_index}].level",
                3,
                120,
            )

            lessons_raw = raw_chapter.get("lessons")
            if not isinstance(lessons_raw, list) or not 3 <= len(lessons_raw) <= 8:
                raise ValueError(
                    f"chapter[{chapter_index}].lessons: se esperaban entre 3 y 8 lecciones."
                )
            quiz = _quiz(raw_chapter.get("quiz"), lang, f"chapter[{chapter_index}].quiz")
            final_quiz_id = slugify(f"{course_slug}-{quiz.id}", quiz.id, 110)
            quiz = Quiz(
                id=final_quiz_id,
                title=quiz.title,
                description=quiz.description,
                pass_score=max(0, min(100, quiz.pass_score)),
                questions=quiz.questions,
            )
            if final_quiz_id in quiz_map:
                raise ValueError(f"chapter[{chapter_index}]: quiz duplicado.")
            quiz_map[final_quiz_id] = quiz

            lesson_slugs: dict[str, str] = {}
            lessons: list[Lesson] = []
            for lesson_index, raw_lesson in enumerate(lessons_raw, start=1):
                if not isinstance(raw_lesson, dict):
                    raise ValueError(
                        f"chapter[{chapter_index}].lessons[{lesson_index - 1}]: "
                        "se esperaba un objeto."
                    )
                number = raw_lesson.get("number", lesson_index)
                if number != lesson_index:
                    raise ValueError(
                        f"chapter[{chapter_index}].lessons[{lesson_index - 1}].number: "
                        f"se esperaba {lesson_index}."
                    )
                lesson_base = slugify(
                    raw_lesson.get("slug", f"leccion-{lesson_index}"),
                    f"leccion-{lesson_index}",
                    55,
                )
                lesson_slug = slugify(f"{course_slug}-{lesson_base}", lesson_base, 115)
                if lesson_slug in lesson_slugs_seen:
                    raise ValueError(f"Lección duplicada: {lesson_slug}.")
                lesson_slugs_seen.add(lesson_slug)
                total_lessons += 1
                if total_lessons > 30:
                    raise ValueError("El paquete no puede superar 30 lecciones.")
                lesson_slugs[lesson_base] = lesson_slug
                blocks = _blocks(
                    raw_lesson.get("blocks"),
                    lang,
                    f"chapter[{chapter_index}].lesson[{lesson_index}]",
                )
                lesson = Lesson(
                    number=lesson_index,
                    slug=lesson_slug,
                    title=_localized_text(
                        raw_lesson.get("title"),
                        lang,
                        f"chapter[{chapter_index}].lesson[{lesson_index}].title",
                        3,
                        200,
                    ),
                    summary=_localized_text(
                        raw_lesson.get("summary"),
                        lang,
                        f"chapter[{chapter_index}].lesson[{lesson_index}].summary",
                        20,
                        800,
                    ),
                    minutes=int(raw_lesson.get("minutes", 10)),
                    objectives=_localized_list(
                        raw_lesson.get("objectives"),
                        lang,
                        f"chapter[{chapter_index}].lesson[{lesson_index}].objectives",
                        2,
                        6,
                        300,
                    ),
                    blocks=blocks,
                    key_points=_localized_list(
                        raw_lesson.get("key_points"),
                        lang,
                        f"chapter[{chapter_index}].lesson[{lesson_index}].key_points",
                        2,
                        8,
                        300,
                    ),
                    quiz_id=final_quiz_id if lesson_index == len(lessons_raw) else None,
                )
                if not 3 <= lesson.minutes <= 60:
                    raise ValueError(
                        f"{lesson_slug}: minutes debe estar entre 3 y 60."
                    )
                if lesson.word_count < 220:
                    raise ValueError(
                        f"{lesson_slug}: la lección es demasiado corta "
                        f"({lesson.word_count} palabras)."
                    )
                lessons.append(lesson)

            glossary_raw = raw_chapter.get("glossary")
            if not isinstance(glossary_raw, list) or not 6 <= len(glossary_raw) <= 24:
                raise ValueError(
                    f"chapter[{chapter_index}].glossary: se esperaban entre 6 y 24 términos."
                )
            for term_index, item in enumerate(glossary_raw):
                if not isinstance(item, dict):
                    raise ValueError(
                        f"chapter[{chapter_index}].glossary[{term_index}]: objeto esperado."
                    )
                target = item.get("lesson")
                target_slug = (
                    lesson_slugs.get(slugify(target)) if isinstance(target, str) and target else None
                )
                if target and target_slug is None:
                    raise ValueError(
                        f"chapter[{chapter_index}].glossary[{term_index}].lesson: "
                        f"la lección {target!r} no existe en el capítulo."
                    )
                glossary.append(
                    GlossaryTerm(
                        term=_localized_text(
                            item.get("term"),
                            lang,
                            f"chapter[{chapter_index}].glossary[{term_index}].term",
                            2,
                            120,
                        ),
                        definition=_localized_text(
                            item.get("definition"),
                            lang,
                            f"chapter[{chapter_index}].glossary[{term_index}].definition",
                            10,
                            600,
                        ),
                        lesson=target_slug,
                    )
                )

            chapters.append(
                Chapter(
                    number=chapter_index,
                    slug=chapter_slug,
                    title=chapter_title,
                    subtitle=chapter_subtitle,
                    description=chapter_description,
                    level=chapter_level,
                    lessons=tuple(lessons),
                )
            )

        program = Program(
            title=title,
            subtitle=subtitle,
            description=description,
            level=level,
            chapters=tuple(chapters),
        )
        courses[lang] = Course(
            slug=course_slug,
            title=title,
            subtitle=subtitle,
            description=description,
            level=level,
            program=program,
            book=book,
            accent=accent,
            order=100,
            tags=tags,
        )
        all_quizzes[lang] = quiz_map
        all_glossaries[lang] = tuple(glossary)

    # Paridad estructural entre idiomas: mismos slugs, números y respuestas.
    if len(languages) > 1:
        reference = courses[languages[0]]
        for lang in languages[1:]:
            other = courses[lang]
            if [c.slug for c in other.chapters] != [c.slug for c in reference.chapters]:
                raise ValueError("Los capítulos deben tener los mismos slugs en ES y EN.")
            for ref_chapter, other_chapter in zip(reference.chapters, other.chapters):
                if [l.slug for l in other_chapter.lessons] != [
                    l.slug for l in ref_chapter.lessons
                ]:
                    raise ValueError(
                        f"Capítulo {ref_chapter.slug}: las lecciones deben tener "
                        "los mismos slugs en ES y EN."
                    )
            ref_quizzes = all_quizzes[languages[0]]
            for quiz_id, quiz in all_quizzes[lang].items():
                if quiz_id not in ref_quizzes:
                    raise ValueError(f"Quiz {quiz_id}: falta en el otro idioma.")
                if [q.correct for q in quiz.questions] != [
                    q.correct for q in ref_quizzes[quiz_id].questions
                ]:
                    raise ValueError(
                        f"Quiz {quiz_id}: las respuestas correctas deben coincidir "
                        "en ES y EN."
                    )

    titles = {
        lang: course.title for lang, course in courses.items()
    }
    summary = {
        "slug": course_slug,
        "languages": list(languages),
        "titles": titles,
        "chapter_count": courses[languages[0]].chapter_count,
        "lesson_count": courses[languages[0]].lesson_count,
        "quiz_count": len(all_quizzes[languages[0]]),
        "glossary_count": len(all_glossaries[languages[0]]),
        "tags": list(tags),
        "book": (
            {
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "url": book.url,
            }
            if book
            else None
        ),
    }
    return ParsedPackage(
        slug=course_slug,
        languages=languages,
        courses=courses,
        quizzes=all_quizzes,
        glossaries=all_glossaries,
        summary=summary,
    )
