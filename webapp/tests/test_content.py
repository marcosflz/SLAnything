"""Contrato del contenido didáctico: lecciones, quiz, glosario y figuras."""

from __future__ import annotations

import dataclasses

import pytest

from webapp import config
from webapp.content import (
    CATALOGS,
    COURSE,
    COURSES,
    GLOSSARY,
    GLOSSARIES,
    QUIZZES,
    QUIZZES_BY_LANG,
    validate_catalog,
    validate_content,
    validate_program,
)
from webapp.content.schema import figure
from webapp.labs import LAB_META

EXPECTED_LESSONS = [
    ("que-es-un-llm", 10),
    ("pretraining-y-finetuning", 10),
    ("transformer-y-atencion", 12),
    ("escala-de-datos", 8),
    ("predecir-la-siguiente-palabra", 15),
    ("zero-shot-y-few-shot", 10),
    ("como-se-construye", 8),
    ("repaso", 10),
]


def test_course_has_eight_ordered_lessons():
    assert len(COURSE.lessons) == 8
    assert [lesson.number for lesson in COURSE.lessons] == list(range(1, 9))
    assert [(lesson.slug, lesson.minutes) for lesson in COURSE.lessons] == EXPECTED_LESSONS
    assert len({lesson.slug for lesson in COURSE.lessons}) == 8
    assert COURSE.total_minutes == 83


def test_quiz_capitulo_1_contract():
    assert "quiz-capitulo-1" in QUIZZES
    quiz = QUIZZES["quiz-capitulo-1"]

    assert quiz.total == 10
    assert quiz.pass_score == 80
    assert len({question.id for question in quiz.questions}) == 10

    for question in quiz.questions:
        assert question.prompt.strip()
        assert len(question.options) >= 2
        assert 0 <= question.correct < len(question.options)
        assert question.explanation.strip()


def test_quiz_is_linked_from_the_last_lesson():
    lessons_with_quiz = [lesson for lesson in COURSE.lessons if lesson.quiz_id]
    assert [lesson.slug for lesson in lessons_with_quiz] == ["repaso"]
    assert lessons_with_quiz[0].quiz_id in QUIZZES


def test_glossary_has_enough_terms_and_valid_lesson_links():
    assert len(GLOSSARY) >= 30
    assert len({term.term.casefold() for term in GLOSSARY}) == len(GLOSSARY)

    slugs = {lesson.slug for lesson in COURSES["es"].lessons}
    for term in GLOSSARY:
        assert term.term.strip()
        assert term.definition.strip()
        if term.lesson is not None:
            assert term.lesson in slugs, f"Término {term.term!r} apunta a {term.lesson!r}"


def test_lessons_follow_the_pedagogical_structure():
    for lesson in COURSE.lessons:
        kinds = [block["type"] for block in lesson.blocks]

        assert kinds[0] == "lead", f"{lesson.slug}: debe empezar con lead"
        assert kinds[-1] == "keypoints", f"{lesson.slug}: debe terminar con keypoints"
        assert "check" in kinds, f"{lesson.slug}: falta un bloque check"
        assert lesson.objectives, f"{lesson.slug}: sin objetivos"
        assert lesson.key_points, f"{lesson.slug}: sin ideas clave"
        assert all(lab_id in config.KNOWN_LABS for lab_id in lesson.labs)


def test_every_known_lab_has_metadata_and_a_javascript_module():
    assert set(LAB_META) == config.KNOWN_LABS

    for lab_id in config.KNOWN_LABS:
        module = config.STATIC_DIR / "js" / "labs" / f"{lab_id}.js"
        assert module.is_file(), f"Falta el módulo JS del laboratorio {lab_id}"


def test_all_chapters_follow_the_pedagogical_structure():
    for lang in ("es", "en"):
        for chapter in COURSES[lang].chapters:
            assert len(chapter.lessons) == 8
            assert [lesson.number for lesson in chapter.lessons] == list(range(1, 9))
            assert chapter.lessons[-1].quiz_id == f"quiz-capitulo-{chapter.number}"
            assert chapter.lessons[-1].quiz_id in QUIZZES_BY_LANG[lang]
            for lesson in chapter.lessons:
                kinds = [block["type"] for block in lesson.blocks]
                assert kinds[0] == "lead"
                assert kinds[-1] == "keypoints"
                assert "check" in kinds
                assert "callout" in kinds
                assert lesson.word_count >= 350
                assert all(
                    lab_id in config.KNOWN_LABS for lab_id in lesson.labs
                )


def test_program_has_all_chapters_and_global_slugs():
    program = COURSES["es"]

    assert program.chapter_count == 7
    assert program.lesson_count == 56
    assert program.total_minutes == 584
    assert [chapter.number for chapter in program.chapters] == list(range(1, 8))
    assert len({lesson.slug for lesson in program.lessons}) == 56
    assert program.chapter_for("que-es-un-llm").number == 1
    assert program.chapter_for("byte-pair-encoding").number == 2
    assert program.chapter_for_quiz("quiz-capitulo-7").number == 7
    assert program.neighbours("repaso")[1].slug == "tokens-y-vocabulario"
    assert program.chapter_neighbours(7)[1] is None


def test_program_validation_passes():
    validate_program(
        COURSES["es"],
        QUIZZES_BY_LANG["es"],
        config.KNOWN_LABS,
        config.STATIC_DIR,
        GLOSSARIES["es"],
    )


def test_catalog_has_a_published_course_with_book_metadata():
    course = CATALOGS["es"][0]

    assert course.slug == "llm-desde-cero"
    assert course.is_published
    assert course.lesson_count == 56
    assert course.chapter_count == 7
    assert course.book is not None
    assert course.book.author == "Sebastian Raschka"
    assert course.lesson("que-es-un-llm") is not None
    assert course.chapter_for("byte-pair-encoding").number == 2


def test_catalog_validation_passes():
    validate_catalog(
        CATALOGS["es"],
        QUIZZES_BY_LANG["es"],
        config.KNOWN_LABS,
        config.STATIC_DIR,
        GLOSSARIES["es"],
    )


def test_validate_content_passes_and_all_figures_exist():
    # No debe lanzar: es la misma validación que ejecuta el lifespan.
    validate_content(
        COURSE,
        QUIZZES,
        config.KNOWN_LABS,
        config.STATIC_DIR,
        GLOSSARY,
    )

    figures = [
        (lesson.slug, block["src"])
        for lesson in COURSE.lessons
        for block in lesson.blocks
        if block["type"] == "figure"
    ]
    assert figures, "El curso no referencia ninguna figura"
    for slug, src in figures:
        path = config.STATIC_DIR / src
        assert path.is_file(), f"{slug}: falta {src} en {config.STATIC_DIR}"


def test_validate_content_rejects_missing_figures(tmp_path):
    broken_lesson = dataclasses.replace(
        COURSE.lessons[0],
        blocks=(figure("img/ch01/no-existe.png", "Figura inexistente", "Prueba"),),
    )
    broken_course = dataclasses.replace(COURSE, lessons=(broken_lesson,))

    with pytest.raises(ValueError, match="falta la imagen"):
        validate_content(
            broken_course,
            QUIZZES,
            config.KNOWN_LABS,
            tmp_path,
            (),
        )
