"""Chapter 4 · GPT Architecture (English)."""

from webapp.content.chapters.ch04.lessons_en import LESSONS
from webapp.content.schema import Chapter

CHAPTER_EN = Chapter(
    number=4,
    slug="capitulo-4",
    title="GPT Architecture",
    subtitle="From individual blocks to a model that generates",
    description=(
        "Configure a small GPT-2, understand LayerNorm, GELU, and the feed-forward "
        "network, assemble the transformer block with residual connections, and follow "
        "a vector all the way to the logits. At the end you will see why the architecture "
        "alone still does not produce coherent text."
    ),
    level="Intermediate · no GPU",
    lessons=LESSONS,
)
