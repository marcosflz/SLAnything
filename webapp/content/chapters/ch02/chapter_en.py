"""Chapter 2 in English."""

from webapp.content.schema import Chapter

from .lessons_en import LESSONS

CHAPTER = Chapter(
    number=2,
    slug="capitulo-2",
    title="Working with Text Data",
    subtitle="From raw text to tensors the model can read",
    description=(
        "Eight lessons on turning text into training data: tokenization, vocabulary, special "
        "tokens, BPE, sliding windows, input-target pairs, embeddings, and similarity. No GPU "
        "required, with runnable examples."
    ),
    level="Beginner · no GPU",
    lessons=LESSONS,
)
