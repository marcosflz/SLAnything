"""Catálogo de cursos.

``Chapter`` sigue siendo la unidad editorial y ``Program`` la unidad de
navegación dentro de un curso. ``Course`` añade la capa que faltaba para que la
plataforma no gire alrededor de un único libro: metadatos editoriales, crédito
del libro, estado de publicación y un programa propio.

Los cursos son datos inmutables. Añadir un libro nuevo consiste en crear su
``Program`` (con sus capítulos) y registrarlo en ``CATALOGS``; ni los routers ni
SQLite necesitan cambios.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from webapp.content.program import Program, validate_program
from webapp.content.schema import GlossaryTerm, Quiz

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_COURSE_STATUSES = {"published", "coming_soon"}


@dataclass(frozen=True)
class Book:
    """Crédito editorial del libro en el que se basa un curso."""

    title: str
    author: str
    year: int | None = None
    url: str | None = None


@dataclass(frozen=True)
class Course:
    """Un curso publicado dentro de la biblioteca de SLAnything.

    Delega la navegación en su ``Program`` para que el resto del código pueda
    seguir tratando un curso como «el programa activo» sin conocer la diferencia.
    """

    slug: str
    title: str
    subtitle: str
    description: str
    level: str
    program: Program
    book: Book | None = None
    status: str = "published"
    accent: str = "blue"
    cover: str | None = None
    order: int = 0
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def chapters(self):
        return self.program.chapters

    @property
    def lessons(self):
        return self.program.lessons

    @property
    def lesson_count(self) -> int:
        return self.program.lesson_count

    @property
    def chapter_count(self) -> int:
        return self.program.chapter_count

    @property
    def total_minutes(self) -> int:
        return self.program.total_minutes

    @property
    def lab_count(self) -> int:
        return len(
            {
                lab_id
                for lesson in self.program.lessons
                for lab_id in lesson.labs
            }
        )

    @property
    def is_published(self) -> bool:
        return self.status == "published"

    def chapter(self, number: int):
        return self.program.chapter(number)

    def lesson(self, slug: str):
        return self.program.lesson(slug)

    def chapter_for(self, slug: str):
        return self.program.chapter_for(slug)

    def chapter_for_quiz(self, quiz_id: str):
        return self.program.chapter_for_quiz(quiz_id)

    def neighbours(self, slug: str):
        return self.program.neighbours(slug)

    def chapter_neighbours(self, number: int):
        return self.program.chapter_neighbours(number)


def validate_catalog(
    catalog: tuple[Course, ...],
    quizzes: dict[str, Quiz],
    known_labs: set[str],
    static_root,
    glossary: tuple[GlossaryTerm, ...] = (),
) -> None:
    """Valida el catálogo completo y la coherencia entre cursos.

    Los slugs de curso, lección y quiz son globales: simplifican las URLs
    históricas y permiten que el progreso y los intentos existentes sigan
    funcionando. La validación falla al arrancar si dos cursos chocan.
    """
    errors: list[str] = []
    course_slugs: set[str] = set()
    lesson_slugs: set[str] = set()
    quiz_ids: set[str] = set()

    if not catalog:
        errors.append("El catálogo no contiene cursos.")

    for course in catalog:
        if not _SLUG_RE.match(course.slug):
            errors.append(
                f"Curso {course.slug!r}: el slug debe usar minúsculas, números y guiones."
            )
        if course.slug in course_slugs:
            errors.append(f"Slug de curso duplicado: {course.slug}.")
        course_slugs.add(course.slug)

        if course.status not in _COURSE_STATUSES:
            errors.append(
                f"Curso {course.slug}: estado {course.status!r} desconocido."
            )
        if course.status == "published" and not course.lessons:
            errors.append(f"Curso {course.slug}: un curso publicado no puede estar vacío.")
        if not course.title.strip():
            errors.append(f"Curso {course.slug}: falta el título.")

        for chapter in course.chapters:
            for lesson in chapter.lessons:
                if lesson.slug in lesson_slugs:
                    errors.append(
                        f"Slug de lección duplicado entre cursos: {lesson.slug}."
                    )
                lesson_slugs.add(lesson.slug)
                if lesson.quiz_id:
                    if lesson.quiz_id in quiz_ids:
                        errors.append(
                            f"Quiz duplicado entre cursos: {lesson.quiz_id}."
                        )
                    quiz_ids.add(lesson.quiz_id)

    for term in glossary:
        if term.lesson is not None and term.lesson not in lesson_slugs:
            errors.append(
                f"Glosario: el término {term.term!r} apunta a {term.lesson!r}, "
                "que no existe en el catálogo."
            )

    if errors:
        raise ValueError("Catálogo inválido:\n- " + "\n- ".join(errors))

    # La validación de cada programa se hace sin glosario: los enlaces se
    # comprueban arriba contra la unión de todos los cursos.
    for course in catalog:
        validate_program(
            course.program,
            quizzes,
            known_labs,
            static_root,
            (),
        )
