"""Chapter 6 metadata in English."""

from webapp.content.schema import Chapter

from .lessons_en import LESSONS

CHAPTER_EN = Chapter(
    number=6,
    slug="capitulo-6",
    title="Classification",
    subtitle="Turning a generative model into a classifier",
    description=(
        "Turn a pretrained GPT-2 into a spam classifier: prepare labelled data, replace "
        "the output head, adjust the last layers, and choose metrics and thresholds with "
        "judgement."
    ),
    level="Intermediate · no GPU",
    lessons=LESSONS,
)
