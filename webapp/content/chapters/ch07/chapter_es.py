"""Capítulo 7 en español · Instrucciones."""

from webapp.content.schema import Chapter

from .lessons_es import LESSONS

CHAPTER_ES = Chapter(
    number=7,
    slug="capitulo-7",
    title="Instrucciones",
    subtitle="Enseñar al modelo a seguir órdenes con seguridad",
    description=(
        "Del ajuste supervisado de instrucciones a la evaluación con un juez LLM: datos, "
        "plantillas de chat, máscara de pérdida, entrenamiento, preferencias y seguridad."
    ),
    level="Avanzado · sin GPU",
    lessons=LESSONS,
)
