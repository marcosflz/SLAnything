"""Valida un paquete de capítulo antes de integrarlo en el curso.

Uso:

    uv run python tools/check_chapter.py ch02

Comprueba estructura, pedagogía, figuras, ejemplos Python, quiz, glosario y
laboratorios. Es el contrato que deben cumplir los paquetes de los capítulos
2-7 para que la integración central sea segura.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp import config  # noqa: E402
from webapp.content.glossary import GLOSSARY  # noqa: E402
from webapp.content.glossary_en import GLOSSARY as GLOSSARY_EN  # noqa: E402
from webapp.content.quizzes import QUIZZES  # noqa: E402
from webapp.content.quizzes_en import QUIZZES as QUIZZES_EN  # noqa: E402

CHAPTER_1_LABS = {
    "memory",
    "labels",
    "transformer",
    "attention",
    "ngram",
    "prompt",
    "cost",
}
from webapp.content.schema import (  # noqa: E402
    Chapter,
    GlossaryTerm,
    Lesson,
    Quiz,
    validate_content,
)


def _fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter", help="Nombre del paquete, por ejemplo ch02")
    args = parser.parse_args()

    name = args.chapter
    if not name.startswith("ch") or not name[2:].isdigit():
        print(f"Nombre de capítulo inválido: {name}")
        return 2
    number = int(name[2:])

    try:
        module = importlib.import_module(f"webapp.content.chapters.{name}")
    except Exception as exc:  # pragma: no cover - diagnóstico para agentes
        print(f"No se pudo importar webapp.content.chapters.{name}: {exc}")
        raise

    errors: list[str] = []

    def require(attr: str):
        if not hasattr(module, attr):
            _fail(errors, f"Falta el export obligatorio {attr}.")
            return None
        return getattr(module, attr)

    chapter_es = require("CHAPTER_ES")
    chapter_en = require("CHAPTER_EN")
    quizzes_es = require("QUIZZES_ES")
    quizzes_en = require("QUIZZES_EN")
    glossary_es = require("GLOSSARY_ES")
    glossary_en = require("GLOSSARY_EN")
    lab_meta_es = require("LAB_META_ES")
    lab_meta_en = require("LAB_META_EN")
    lab_ids = require("LAB_IDS")

    if not isinstance(chapter_es, Chapter):
        _fail(errors, "CHAPTER_ES no es un Chapter.")
    if not isinstance(chapter_en, Chapter):
        _fail(errors, "CHAPTER_EN no es un Chapter.")
    if not isinstance(quizzes_es, dict):
        _fail(errors, "QUIZZES_ES no es un dict.")
    if not isinstance(quizzes_en, dict):
        _fail(errors, "QUIZZES_EN no es un dict.")
    if not isinstance(glossary_es, tuple):
        _fail(errors, "GLOSSARY_ES no es una tupla.")
    if not isinstance(glossary_en, tuple):
        _fail(errors, "GLOSSARY_EN no es una tupla.")
    if not isinstance(lab_meta_es, dict):
        _fail(errors, "LAB_META_ES no es un dict.")
    if not isinstance(lab_meta_en, dict):
        _fail(errors, "LAB_META_EN no es un dict.")
    if not isinstance(lab_ids, (set, frozenset)):
        _fail(errors, "LAB_IDS no es un set/frozenset.")

    if errors:
        for error in errors:
            print(f"- {error}")
        return 1

    for chapter, lang in ((chapter_es, "ES"), (chapter_en, "EN")):
        if chapter.number != number:
            _fail(errors, f"{lang}: chapter.number={chapter.number}, se esperaba {number}.")
        if len(chapter.lessons) != 8:
            _fail(errors, f"{lang}: {len(chapter.lessons)} lecciones, se esperaban 8.")
        if [lesson.number for lesson in chapter.lessons] != list(range(1, 9)):
            _fail(errors, f"{lang}: los números de lección deben ser 1..8.")
        if not chapter.title.strip() or not chapter.description.strip():
            _fail(errors, f"{lang}: título o descripción vacíos.")
        if chapter.slug != f"capitulo-{number}":
            _fail(errors, f"{lang}: slug {chapter.slug!r}, se esperaba 'capitulo-{number}'.")

        for lesson in chapter.lessons:
            if not isinstance(lesson, Lesson):
                _fail(errors, f"{lang}: la lección {lesson!r} no es un Lesson.")
                continue
            kinds = [block["type"] for block in lesson.blocks]
            if not kinds or kinds[0] != "lead":
                _fail(errors, f"{lang}/{lesson.slug}: debe empezar con lead.")
            if kinds[-1] != "keypoints":
                _fail(errors, f"{lang}/{lesson.slug}: debe terminar con keypoints.")
            if "check" not in kinds:
                _fail(errors, f"{lang}/{lesson.slug}: falta un check.")
            if "callout" not in kinds:
                _fail(errors, f"{lang}/{lesson.slug}: falta un callout.")
            if not lesson.objectives or not lesson.key_points:
                _fail(errors, f"{lang}/{lesson.slug}: faltan objetivos o ideas clave.")
            if lesson.minutes <= 0:
                _fail(errors, f"{lang}/{lesson.slug}: duración inválida.")
            if lesson.word_count < 350:
                _fail(
                    errors,
                    f"{lang}/{lesson.slug}: solo {lesson.word_count} palabras; "
                    "se esperaban al menos 350.",
                )
            if len(lesson.python_blocks) > 4:
                _fail(errors, f"{lang}/{lesson.slug}: demasiados ejemplos Python.")

    if chapter_es.lessons and chapter_en.lessons:
        slugs_es = [lesson.slug for lesson in chapter_es.lessons]
        slugs_en = [lesson.slug for lesson in chapter_en.lessons]
        if slugs_es != slugs_en:
            _fail(errors, "ES y EN deben compartir los mismos slugs y orden.")
        minutes_es = [lesson.minutes for lesson in chapter_es.lessons]
        minutes_en = [lesson.minutes for lesson in chapter_en.lessons]
        if minutes_es != minutes_en:
            _fail(errors, "ES y EN deben compartir las mismas duraciones.")

    base_slugs = set(QUIZZES)  # noqa: F841 - documenta la intención
    existing_slugs = {lesson.slug for lesson in __import__(
        "webapp.content", fromlist=["COURSE"]
    ).COURSE.lessons}
    for lang, chapter in (("ES", chapter_es), ("EN", chapter_en)):
        for lesson in chapter.lessons:
            if lesson.slug in existing_slugs:
                _fail(errors, f"{lang}: el slug {lesson.slug!r} ya existe en el capítulo 1.")

    for lang, quizzes in (("ES", quizzes_es), ("EN", quizzes_en)):
        expected = f"quiz-capitulo-{number}"
        if expected not in quizzes:
            _fail(errors, f"{lang}: falta el quiz {expected!r}.")
        else:
            quiz = quizzes[expected]
            if not isinstance(quiz, Quiz):
                _fail(errors, f"{lang}: {expected} no es un Quiz.")
            else:
                if quiz.total != 10:
                    _fail(errors, f"{lang}/{expected}: {quiz.total} preguntas, se esperaban 10.")
                if quiz.pass_score != 80:
                    _fail(errors, f"{lang}/{expected}: pass_score debe ser 80.")
                if not quiz.title.strip() or not quiz.description.strip():
                    _fail(errors, f"{lang}/{expected}: título o descripción vacíos.")
                for question in quiz.questions:
                    if not question.prompt.strip() or not question.explanation.strip():
                        _fail(errors, f"{lang}/{question.id}: pregunta o explicación vacía.")
                    if len(question.options) < 3:
                        _fail(errors, f"{lang}/{question.id}: se esperaban al menos 3 opciones.")
        for other in quizzes:
            if other in QUIZZES or other in QUIZZES_EN:
                _fail(errors, f"{lang}: el quiz {other!r} ya existe en el capítulo 1.")

    if chapter_es.lessons:
        last = chapter_es.lessons[-1]
        if last.quiz_id != f"quiz-capitulo-{number}":
            _fail(errors, "La última lección debe enlazar el quiz del capítulo.")
    if chapter_en.lessons:
        last = chapter_en.lessons[-1]
        if last.quiz_id != f"quiz-capitulo-{number}":
            _fail(errors, "La última lección EN debe enlazar el quiz del capítulo.")

    base_terms = {term.term.casefold() for term in GLOSSARY}
    base_terms_en = {term.term.casefold() for term in GLOSSARY_EN}
    for lang, glossary, base in (
        ("ES", glossary_es, base_terms),
        ("EN", glossary_en, base_terms_en),
    ):
        if len(glossary) < 10:
            _fail(errors, f"{lang}: el glosario tiene {len(glossary)} términos; mínimo 10.")
        seen: set[str] = set()
        chapter_slugs = {lesson.slug for lesson in (chapter_es if lang == "ES" else chapter_en).lessons}
        for term in glossary:
            if not isinstance(term, GlossaryTerm):
                _fail(errors, f"{lang}: término inválido {term!r}.")
                continue
            key = term.term.casefold()
            if key in base:
                _fail(errors, f"{lang}: el término {term.term!r} ya existe en el capítulo 1.")
            if key in seen:
                _fail(errors, f"{lang}: término duplicado {term.term!r}.")
            seen.add(key)
            if not term.term.strip() or not term.definition.strip():
                _fail(errors, f"{lang}: término o definición vacíos.")
            if term.lesson is not None and term.lesson not in chapter_slugs:
                _fail(errors, f"{lang}: {term.term!r} apunta a {term.lesson!r}, fuera del capítulo.")

    if set(lab_meta_es) != set(lab_meta_en):
        _fail(errors, "LAB_META_ES y LAB_META_EN deben tener las mismas claves.")
    if set(lab_meta_es) != set(lab_ids):
        _fail(errors, "LAB_IDS debe coincidir con las claves de LAB_META_ES.")
    for lab_id in sorted(lab_ids):
        if lab_id in CHAPTER_1_LABS:
            _fail(errors, f"El laboratorio {lab_id!r} ya existe en el capítulo 1.")
        module = config.STATIC_DIR / "js" / "labs" / f"{lab_id}.js"
        if not module.is_file():
            _fail(errors, f"Falta el módulo JS del laboratorio {lab_id!r}: {module}.")
        for lang, meta in (("ES", lab_meta_es), ("EN", lab_meta_en)):
            info = meta.get(lab_id, {})
            for field in ("title", "description", "icon", "accent"):
                if not isinstance(info.get(field), str) or not info[field].strip():
                    _fail(errors, f"{lang}/{lab_id}: falta {field!r} en los metadatos.")

    known_labs = set(config.KNOWN_LABS) | set(lab_ids)
    for lang, chapter, quizzes, glossary in (
        ("ES", chapter_es, quizzes_es, glossary_es),
        ("EN", chapter_en, quizzes_en, glossary_en),
    ):
        try:
            validate_content(
                chapter,
                quizzes,
                known_labs,
                config.STATIC_DIR,
                glossary,
            )
        except ValueError as exc:
            _fail(errors, f"{lang}: validate_content falló:\n{exc}")

        for lesson in chapter.lessons:
            for block in lesson.blocks:
                if block["type"] == "figure":
                    path = config.STATIC_DIR / block["src"]
                    if path.suffix.lower() not in {".svg", ".png", ".webp", ".jpg", ".jpeg"}:
                        _fail(errors, f"{lang}/{lesson.slug}: figura con extensión no soportada {path.suffix}.")

    py_es = sum(len(lesson.python_blocks) for lesson in chapter_es.lessons)
    py_en = sum(len(lesson.python_blocks) for lesson in chapter_en.lessons)
    if py_es < 2:
        _fail(errors, f"ES: solo {py_es} bloques Python; mínimo 2.")
    if py_en < 2:
        _fail(errors, f"EN: solo {py_en} bloques Python; mínimo 2.")

    if errors:
        print(f"Capítulo {name}: {len(errors)} problema(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"OK {name}: {len(chapter_es.lessons)} lecciones, "
        f"{chapter_es.total_minutes} min, {py_es} ejemplos Python, "
        f"{len(glossary_es)} términos ES / {len(glossary_en)} EN, "
        f"labs: {', '.join(sorted(lab_ids)) or 'ninguno'}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
