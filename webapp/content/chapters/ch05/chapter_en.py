"""Chapter 5 · Pretraining (EN)."""

from __future__ import annotations

from webapp.content.schema import Chapter

from .lessons_en import LESSONS

CHAPTER_EN = Chapter(
    number=5,
    slug="capitulo-5",
    title="Pretraining",
    subtitle="Teaching a GPT to predict the next token",
    description=(
        "Eight lessons that turn a freshly initialised GPT into a base model: measure "
        "the loss, run the training loop, prepare batches, evaluate without fooling "
        "yourself, sample text, and estimate the cost before spending a GPU."
    ),
    level="Intermediate · no GPU",
    lessons=LESSONS,
)
