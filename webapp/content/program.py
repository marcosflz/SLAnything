"""Modelo del programa completo: varios capítulos bajo un mismo curso.

``Chapter`` sigue siendo la unidad editorial (8 lecciones y su quiz). ``Program``
es la unidad de navegación y progreso: agrupa capítulos, aplana las lecciones y
resuelve búsquedas y vecinos entre capítulos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from webapp.content.schema import Chapter, GlossaryTerm, Lesson, Quiz, validate_content


@dataclass(frozen=True)
class Program:
    title: str
    subtitle: str
    description: str
    level: str
    chapters: tuple[Chapter, ...] = field(default_factory=tuple)

    @property
    def lessons(self) -> tuple[Lesson, ...]:
        return tuple(lesson for chapter in self.chapters for lesson in chapter.lessons)

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def total_minutes(self) -> int:
        return sum(chapter.total_minutes for chapter in self.chapters)

    def chapter(self, number: int) -> Chapter | None:
        return next((item for item in self.chapters if item.number == number), None)

    def lesson(self, slug: str) -> Lesson | None:
        return next((item for item in self.lessons if item.slug == slug), None)

    def chapter_for(self, slug: str) -> Chapter | None:
        for chapter in self.chapters:
            if chapter.lesson(slug) is not None:
                return chapter
        return None

    def chapter_for_quiz(self, quiz_id: str) -> Chapter | None:
        for chapter in self.chapters:
            if any(lesson.quiz_id == quiz_id for lesson in chapter.lessons):
                return chapter
        return None

    def neighbours(self, slug: str) -> tuple[Lesson | None, Lesson | None]:
        lessons = self.lessons
        for index, lesson in enumerate(lessons):
            if lesson.slug == slug:
                previous = lessons[index - 1] if index > 0 else None
                following = lessons[index + 1] if index + 1 < len(lessons) else None
                return previous, following
        return None, None

    def chapter_neighbours(self, number: int) -> tuple[Chapter | None, Chapter | None]:
        for index, chapter in enumerate(self.chapters):
            if chapter.number == number:
                previous = self.chapters[index - 1] if index > 0 else None
                following = (
                    self.chapters[index + 1]
                    if index + 1 < len(self.chapters)
                    else None
                )
                return previous, following
        return None, None


def validate_program(
    program: Program,
    quizzes: dict[str, Quiz],
    known_labs: set[str],
    static_root: Path,
    glossary: tuple[GlossaryTerm, ...] = (),
) -> None:
    """Valida el programa completo, no solo un capítulo.

    Además de delegar en ``validate_content`` para cada capítulo, comprueba que
    los capítulos estén numerados de forma consecutiva y que los slugs, los ids
    de quiz y los enlaces del glosario no se repitan entre capítulos.
    """
    errors: list[str] = []

    if [chapter.number for chapter in program.chapters] != list(
        range(1, len(program.chapters) + 1)
    ):
        errors.append("Los capítulos deben estar numerados de forma consecutiva desde 1.")

    slugs: set[str] = set()
    for chapter in program.chapters:
        for lesson in chapter.lessons:
            if lesson.slug in slugs:
                errors.append(f"Slug duplicado entre capítulos: {lesson.slug}.")
            slugs.add(lesson.slug)

    quiz_ids: set[str] = set()
    for chapter in program.chapters:
        for lesson in chapter.lessons:
            if lesson.quiz_id:
                if lesson.quiz_id in quiz_ids:
                    errors.append(f"Quiz repetido entre capítulos: {lesson.quiz_id}.")
                quiz_ids.add(lesson.quiz_id)

    for term in glossary:
        if term.lesson is not None and term.lesson not in slugs:
            errors.append(
                f"Glosario: el término {term.term!r} apunta a {term.lesson!r}, "
                "que no existe en el programa."
            )

    if errors:
        raise ValueError("Programa inválido:\n- " + "\n- ".join(errors))

    for chapter in program.chapters:
        validate_content(
            chapter,
            quizzes,
            known_labs,
            static_root,
            glossary,
        )
