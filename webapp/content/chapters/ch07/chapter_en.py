"""Chapter 7 in English · Instructions."""

from webapp.content.schema import Chapter

from .lessons_en import LESSONS

CHAPTER_EN = Chapter(
    number=7,
    slug="capitulo-7",
    title="Instructions",
    subtitle="Teaching the model to follow requests safely",
    description=(
        "From supervised instruction tuning to evaluation with an LLM judge: data, chat "
        "templates, loss masking, training, preferences, and safety."
    ),
    level="Advanced · no GPU",
    lessons=LESSONS,
)
