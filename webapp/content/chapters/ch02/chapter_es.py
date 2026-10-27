"""Capítulo 2 en español."""

from webapp.content.schema import Chapter

from .lessons_es import LESSONS

CHAPTER = Chapter(
    number=2,
    slug="capitulo-2",
    title="Trabajar con texto",
    subtitle="Del texto bruto a tensores que el modelo puede leer",
    description=(
        "Ocho lecciones para convertir texto en datos de entrenamiento: tokenización, "
        "vocabulario, tokens especiales, BPE, ventanas deslizantes, pares entrada-objetivo, "
        "embeddings y similitud. Sin GPU y con ejemplos que puedes ejecutar."
    ),
    level="Principiante · sin GPU",
    lessons=LESSONS,
)
