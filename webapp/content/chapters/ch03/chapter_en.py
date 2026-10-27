"""Chapter 3 · Attention (EN)."""

from webapp.content.chapters.ch03.lessons_en import LESSONS
from webapp.content.schema import Chapter

CHAPTER = Chapter(
    number=3,
    slug="capitulo-3",
    title="Attention",
    subtitle="How the model decides what to look at",
    description=(
        "From the bottleneck of fixed memory to multi-head attention: build, step by step, the "
        "mechanism that lets GPT decide which tokens to look at, with numerical examples, "
        "runnable code, and interactive labs."
    ),
    level="Intermediate · no GPU",
    lessons=LESSONS,
)
