"""Contenido de SLAnything, organizado por idioma y por curso.

La biblioteca la forman los cursos publicados desde el Estudio y, de forma
opcional, los cursos de ejemplo del repositorio (``AULA_SAMPLE_COURSES=1``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace

from webapp import config
from webapp.content.catalog import Book, Course, validate_catalog
from webapp.content.chapters import MODULES
from webapp.content.course import (
    CATALOG,
    CATALOG_EN,
    CATALOGS,
    CHAPTERS,
    CHAPTERS_EN,
    COURSE,
    COURSE_EN,
    COURSE_LLM,
    COURSE_LLM_EN,
    COURSES,
    PROGRAM,
    PROGRAM_EN,
)
from webapp.content.glossary import GLOSSARY as _GLOSSARY_1
from webapp.content.glossary_en import GLOSSARY as _GLOSSARY_1_EN
from webapp.content.program import Program, validate_program
from webapp.content.quizzes import QUIZZES as _QUIZZES_1
from webapp.content.quizzes_en import QUIZZES as _QUIZZES_1_EN
from webapp.content.schema import (
    Chapter,
    GlossaryTerm,
    Lesson,
    Question,
    Quiz,
    validate_content,
)
from webapp.i18n import DEFAULT_LANG

logger = logging.getLogger("aula.content")


def _merge_glossaries(
    base: tuple[GlossaryTerm, ...],
    attr: str,
) -> tuple[GlossaryTerm, ...]:
    merged = list(base)
    seen = {term.term.casefold() for term in merged}
    for module in MODULES:
        for term in getattr(module, attr):
            key = term.term.casefold()
            if key in seen:
                raise ValueError(
                    f"Término de glosario duplicado en {module.__name__}: {term.term!r}."
                )
            seen.add(key)
            merged.append(term)
    return tuple(merged)


def _merge_quizzes(base: dict[str, Quiz], attr: str) -> dict[str, Quiz]:
    merged = dict(base)
    for module in MODULES:
        for quiz_id, quiz in getattr(module, attr).items():
            if quiz_id in merged:
                raise ValueError(
                    f"Quiz duplicado en {module.__name__}: {quiz_id!r}."
                )
            merged[quiz_id] = quiz
    return merged


GLOSSARY = _merge_glossaries(_GLOSSARY_1, "GLOSSARY_ES")
GLOSSARY_EN = _merge_glossaries(_GLOSSARY_1_EN, "GLOSSARY_EN")
QUIZZES = _merge_quizzes(_QUIZZES_1, "QUIZZES_ES")
QUIZZES_EN = _merge_quizzes(_QUIZZES_1_EN, "QUIZZES_EN")

GLOSSARIES: dict[str, tuple[GlossaryTerm, ...]] = {"es": GLOSSARY, "en": GLOSSARY_EN}
QUIZZES_BY_LANG: dict[str, dict[str, Quiz]] = {"es": QUIZZES, "en": QUIZZES_EN}


@dataclass(frozen=True)
class ContentBundle:
    """Contenido visible para una petición: catálogo, curso activo y anexos.

    ``course`` es ``None`` cuando la biblioteca está vacía (lo normal en una
    instalación nueva sin cursos de ejemplo): la plataforma no exige ningún
    curso para funcionar (ADR-020).
    """

    lang: str
    course: Course | None
    catalog: tuple[Course, ...]
    glossaries: dict[str, tuple[GlossaryTerm, ...]]
    quizzes: dict[str, Quiz]

    @property
    def chapters(self) -> tuple[Chapter, ...]:
        return self.course.chapters if self.course else ()

    @property
    def glossary(self) -> tuple[GlossaryTerm, ...]:
        """Glosario del curso activo (vacío sin curso)."""
        return self.glossary_for(self.course.slug) if self.course else ()

    def glossary_for(self, slug: str) -> tuple[GlossaryTerm, ...]:
        return self.glossaries.get(slug, ())

    @property
    def published_catalog(self) -> tuple[Course, ...]:
        return tuple(course for course in self.catalog if course.is_published)

    @property
    def default_course(self) -> Course | None:
        """Primer curso publicado: los del espacio antes que los ejemplos."""
        published = self.published_catalog
        return published[0] if published else None

    def course_for(self, slug: str | None) -> Course | None:
        if not slug:
            return None
        return next((course for course in self.catalog if course.slug == slug), None)

    def course_for_lesson(self, lesson_slug: str) -> Course | None:
        return next(
            (course for course in self.catalog if course.lesson(lesson_slug) is not None),
            None,
        )

    def course_for_quiz(self, quiz_id: str) -> Course | None:
        return next(
            (
                course
                for course in self.catalog
                if course.chapter_for_quiz(quiz_id) is not None
            ),
            None,
        )

    def select(self, slug: str | None) -> ContentBundle:
        """Devuelve el mismo bundle con otro curso activo."""
        selected = self.course_for(slug) or self.default_course
        if selected is self.course:
            return self
        return replace(self, course=selected)


def _dynamic_content(code: str, workspace_ids: frozenset[int] | None = None):
    """Cursos publicados desde el Estudio, sin romper el catálogo estático.

    Se importa aquí para evitar un ciclo: el paquete de autoría usa los modelos
    de contenido, y este módulo solo necesita consultarlos en tiempo de petición.
    """
    if not config.AUTHORING_ENABLED:
        return [], {}, {}
    try:
        from webapp.authoring.store import dynamic_content

        return dynamic_content(code, workspace_ids)
    except Exception:  # noqa: BLE001 - el sitio debe seguir vivo sin el Estudio
        logger.exception("No se pudo cargar el contenido generado para %s", code)
        return [], {}, {}


def sample_catalog(lang: str) -> tuple[Course, ...]:
    """Cursos de ejemplo del repositorio, o ``()`` si están desactivados."""
    if not config.SAMPLE_COURSES:
        return ()
    return CATALOGS.get(lang, CATALOGS[DEFAULT_LANG])


def content_for(
    lang: str | None,
    course_slug: str | None = None,
    workspace_ids: frozenset[int] | None = frozenset(),
) -> ContentBundle:
    """Bundle de contenido para un idioma.

    ``workspace_ids`` limita los cursos generados a esos espacios (más los
    públicos); la API pasa solo el espacio **activo**. ``None`` desactiva el
    filtro (scripts y tareas internas). Los cursos de ejemplo van al final y
    solo existen con ``config.SAMPLE_COURSES``.
    """
    code = lang if lang in CATALOGS else DEFAULT_LANG
    samples = sample_catalog(code)
    dynamic_courses, dynamic_quizzes, dynamic_glossaries = _dynamic_content(
        code, workspace_ids
    )
    sample_slugs = {item.slug for item in samples}
    catalog = tuple(
        course for course in dynamic_courses if course.slug not in sample_slugs
    ) + samples

    quizzes: dict[str, Quiz] = dict(QUIZZES_BY_LANG[code]) if samples else {}
    for quiz_id, quiz in dynamic_quizzes.items():
        if quiz_id in quizzes:
            logger.warning("Se ignora el quiz generado duplicado: %s", quiz_id)
            continue
        quizzes[quiz_id] = quiz

    glossaries: dict[str, tuple[GlossaryTerm, ...]] = {}
    for course in samples:
        glossaries[course.slug] = GLOSSARIES[code]
    for slug, terms in dynamic_glossaries.items():
        if slug not in glossaries:
            glossaries[slug] = tuple(terms)

    course = next((item for item in catalog if item.slug == course_slug), None)
    if course is None:
        course = next((item for item in catalog if item.is_published), None)
    return ContentBundle(
        lang=code,
        course=course,
        catalog=catalog,
        glossaries=glossaries,
        quizzes=quizzes,
    )


__all__ = [
    "CATALOG",
    "CATALOG_EN",
    "CATALOGS",
    "CHAPTERS",
    "CHAPTERS_EN",
    "COURSE",
    "COURSE_EN",
    "COURSE_LLM",
    "COURSE_LLM_EN",
    "COURSES",
    "PROGRAM",
    "PROGRAM_EN",
    "GLOSSARY",
    "GLOSSARY_EN",
    "GLOSSARIES",
    "QUIZZES",
    "QUIZZES_EN",
    "QUIZZES_BY_LANG",
    "Book",
    "ContentBundle",
    "Course",
    "Chapter",
    "GlossaryTerm",
    "Lesson",
    "Program",
    "Question",
    "Quiz",
    "content_for",
    "sample_catalog",
    "validate_catalog",
    "validate_program",
    "validate_content",
]
