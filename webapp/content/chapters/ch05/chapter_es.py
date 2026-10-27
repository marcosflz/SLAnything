"""Capítulo 5 · Pretraining (ES)."""

from __future__ import annotations

from webapp.content.schema import Chapter

from .lessons_es import LESSONS

CHAPTER_ES = Chapter(
    number=5,
    slug="capitulo-5",
    title="Pretraining",
    subtitle="Enseñar a un GPT a predecir el siguiente token",
    description=(
        "Ocho lecciones para convertir un GPT recién inicializado en un modelo base: "
        "medir la pérdida, ejecutar el bucle de entrenamiento, preparar lotes, evaluar "
        "sin engañarse, muestrear texto y estimar el coste antes de gastar una GPU."
    ),
    level="Intermedio · sin GPU",
    lessons=LESSONS,
)
