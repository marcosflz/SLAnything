"""Capítulo 4 · Arquitectura GPT (español)."""

from webapp.content.chapters.ch04.lessons_es import LESSONS
from webapp.content.schema import Chapter

CHAPTER_ES = Chapter(
    number=4,
    slug="capitulo-4",
    title="Arquitectura GPT",
    subtitle="De bloques sueltos a un modelo que genera",
    description=(
        "Configura un GPT-2 pequeño, entiende LayerNorm, GELU y la red feed-forward, "
        "ensambla el bloque transformer con conexiones residuales y sigue el camino "
        "de un vector hasta los logits. Al final comprobarás por qué la arquitectura, "
        "por sí sola, todavía no produce texto coherente."
    ),
    level="Intermedio · sin GPU",
    lessons=LESSONS,
)
