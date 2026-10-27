"""Metadatos del capítulo 6 en español."""

from webapp.content.schema import Chapter

from .lessons_es import LESSONS

CHAPTER_ES = Chapter(
    number=6,
    slug="capitulo-6",
    title="Clasificación",
    subtitle="Convertir un modelo generativo en un clasificador",
    description=(
        "Convierte un GPT-2 preentrenado en un clasificador de spam: prepara datos "
        "etiquetados, sustituye la cabeza de salida, ajusta las últimas capas y elige "
        "métricas y umbrales con criterio."
    ),
    level="Intermedio · sin GPU",
    lessons=LESSONS,
)
