"""Ensamblado de los programas y del catálogo de cursos.

El capítulo 1 conserva sus módulos históricos. Los capítulos 2-7 viven en
``webapp/content/chapters/`` y se integran aquí. ``PROGRAM`` representa un curso
completo y ``CATALOG`` la biblioteca de cursos publicados por la plataforma.
"""

from __future__ import annotations

from webapp import config
from webapp.content.catalog import Book, Course
from webapp.content.chapters import MODULES
from webapp.content.lessons import LESSONS
from webapp.content.lessons.en import LESSONS as LESSONS_EN
from webapp.content.program import Program
from webapp.content.schema import Chapter

CHAPTER_1 = Chapter(
    number=1,
    slug="capitulo-1",
    title="Entender los LLM",
    subtitle="Qué son, de dónde vienen y cómo se construyen",
    description=(
        "Un recorrido interactivo por las ideas que sostienen a ChatGPT: la tarea de "
        "predecir el siguiente token, el transformer, la escala de los datos y el mapa "
        "del libro que vamos a construir."
    ),
    level="Principiante · sin GPU",
    lessons=LESSONS,
)

CHAPTER_1_EN = Chapter(
    number=1,
    slug="capitulo-1",
    title="Understanding LLMs",
    subtitle="What they are, where they come from, and how they are built",
    description=(
        "An interactive tour of the ideas behind ChatGPT: next-token prediction, the "
        "transformer, the scale of data, and the map of the book we are going to build."
    ),
    level="Beginner · no GPU",
    lessons=LESSONS_EN,
)

CHAPTERS = (CHAPTER_1, *(module.CHAPTER_ES for module in MODULES))
CHAPTERS_EN = (CHAPTER_1_EN, *(module.CHAPTER_EN for module in MODULES))

PROGRAM = Program(
    title="Construye un LLM desde cero",
    subtitle="De la palabra que sigue a un GPT que sigue instrucciones",
    description=(
        "Curso interactivo de siete capítulos que recorre el libro de Sebastian Raschka: "
        "entender los LLM, preparar texto, atención, arquitectura GPT, pretraining, "
        "clasificación y ajuste por instrucciones. Sin GPU y con ejemplos que puedes "
        "ejecutar en el navegador."
    ),
    level="De principiante a avanzado · sin GPU",
    chapters=CHAPTERS,
)

PROGRAM_EN = Program(
    title="Build an LLM from Scratch",
    subtitle="From the next word to a GPT that follows instructions",
    description=(
        "A seven-chapter interactive course based on Sebastian Raschka's book: "
        "understanding LLMs, text processing, attention, GPT architecture, pretraining, "
        "classification, and instruction tuning. No GPU required, with runnable examples "
        "in the browser."
    ),
    level="Beginner to advanced · no GPU",
    chapters=CHAPTERS_EN,
)

BOOK_LLM_ES = Book(
    title="Build a Large Language Model (From Scratch)",
    author="Sebastian Raschka",
    year=2024,
)
BOOK_LLM_EN = Book(
    title="Build a Large Language Model (From Scratch)",
    author="Sebastian Raschka",
    year=2024,
)

COURSE_LLM = Course(
    slug=config.DEFAULT_COURSE_SLUG,
    title=PROGRAM.title,
    subtitle=PROGRAM.subtitle,
    description=PROGRAM.description,
    level=PROGRAM.level,
    program=PROGRAM,
    book=BOOK_LLM_ES,
    accent="blue",
    order=1,
    tags=("LLM", "transformers", "Python"),
)

COURSE_LLM_EN = Course(
    slug=config.DEFAULT_COURSE_SLUG,
    title=PROGRAM_EN.title,
    subtitle=PROGRAM_EN.subtitle,
    description=PROGRAM_EN.description,
    level=PROGRAM_EN.level,
    program=PROGRAM_EN,
    book=BOOK_LLM_EN,
    accent="blue",
    order=1,
    tags=("LLM", "transformers", "Python"),
)

CATALOG = (COURSE_LLM,)
CATALOG_EN = (COURSE_LLM_EN,)
CATALOGS = {"es": CATALOG, "en": CATALOG_EN}

# Compatibilidad con el contenido y los tests del capítulo 1.
COURSE = CHAPTER_1
COURSE_EN = CHAPTER_1_EN
COURSES = {"es": PROGRAM, "en": PROGRAM_EN}
