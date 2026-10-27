"""Capítulo 3 · Atención (ES)."""

from webapp.content.chapters.ch03.lessons_es import LESSONS
from webapp.content.schema import Chapter

CHAPTER = Chapter(
    number=3,
    slug="capitulo-3",
    title="Atención",
    subtitle="Cómo el modelo decide a qué mirar",
    description=(
        "Del cuello de botella de la memoria fija a la multi-head attention: construye paso a "
        "paso el mecanismo que permite a GPT decidir qué tokens mirar, con ejemplos numéricos, "
        "código ejecutable y laboratorios interactivos."
    ),
    level="Intermedio · sin GPU",
    lessons=LESSONS,
)
