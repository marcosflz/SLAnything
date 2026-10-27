"""Lesson 4 · The scale of data."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=4,
    slug="escala-de-datos",
    title="The scale of data",
    summary=(
        "Which corpus trained GPT-3, how the sources are mixed, and why quality "
        "matters as much as quantity."
    ),
    minutes=8,
    objectives=(
        "Identify the five sources in GPT-3's corpus and their weight in the mix.",
        "Read a table of figures critically and spot a sum that does not add up.",
        "Explain why filtering, deduplication, and choosing the mix are part of the design.",
        "Connect corpus biases to model biases.",
    ),
    blocks=(
        lead(
            "An LLM does not learn from a book: it learns from a library. But that library "
            "is neither neutral nor sorted. Before training, you must decide what goes in, "
            "what is discarded, and how much weight each source gets."
        ),
        h2("The GPT-3 corpus"),
        p(
            "Table 1.1 of the book breaks down GPT-3's corpus. There are five sources: "
            "filtered CommonCrawl, WebText2, Books1, Books2, and Wikipedia. Together they add "
            "up to hundreds of billions of available tokens, with a very uneven mix: the web "
            "dominates and Wikipedia contributes a small but high-quality fraction. A "
            "<strong>token</strong> is a unit of text that the model reads and generates; it "
            "can be a word, a word fragment, or a punctuation mark. In English, one token is "
            "often estimated at about 0.75 words; in Spanish, somewhat less."
        ),
        table(
            ["Source", "Type", "Available tokens", "Weight in the mix"],
            [
                ["CommonCrawl (filtered)", "Web crawl", "410 billion", "60%"],
                ["WebText2", "Web crawl", "19 billion", "22%"],
                ["Books1", "Book corpus", "12 billion", "8%"],
                ["Books2", "Book corpus", "55 billion", "8%"],
                ["Wikipedia", "High-quality text", "3 billion", "3%"],
            ],
            caption=(
                "Table 1.1 · Raschka, Build a Large Language Model (From Scratch), Manning, "
                "2024. Available tokens and each source's weight in the mix."
            ),
            note=(
                "The weight is the proportion with which each source is sampled during "
                "training, not the percentage of total available tokens; the percentages "
                "are approximate."
            ),
        ),
        callout(
            "warning",
            "A sum that does not add up",
            "Add the rows: 410 + 19 + 12 + 55 + 3 = <strong>499 billion</strong>. The book's "
            "text says <strong>509 billion</strong>. That leaves a 10 billion difference. The "
            "book does not explain it at that point, and we should not invent an explanation. "
            "The methodological lesson is the important one: <strong>tables must be "
            "audited too</strong>. And do not confuse two figures: GPT-3 was trained on about "
            "300 billion tokens, not on all the available ones."
        ),
        h2("Quality, not only quantity"),
        p(
            "The quantity is impressive, but filtering decides a good part of the result. "
            "CommonCrawl is a crawl of the open web: it contains spam, automatically generated "
            "text, duplicates, templates, encoding errors, and toxic content. Training without "
            "cleaning teaches the model to reproduce that noise. That is why teams apply "
            "quality filters, remove duplicates, and adjust the mix. Deduplication matters "
            "especially: if a sentence appears a thousand times, the model memorizes it and "
            "spends capacity repeating it instead of learning general patterns."
        ),
        bullets(
            [
                "<strong>Filtering</strong>: discard empty pages, spam, broken code, or automatically generated text.",
                "<strong>Deduplication</strong>: prevent the same page or sentence from appearing many times.",
                "<strong>Mixing</strong>: decide how much weight the web, books, or the encyclopedia get.",
                "<strong>Evaluation</strong>: measure which biases and gaps remain after filtering.",
            ]
        ),
        p(
            "No corpus is neutral. The web overrepresents languages, countries, and viewpoints "
            "with a larger digital presence; books carry the biases of their authors and their "
            "time; Wikipedia, despite its encyclopedic ambition, also has gaps. A model trained "
            "on that mix inherits and amplifies those imbalances. The decision about which data "
            "goes in is therefore both a technical and an editorial decision. More data does "
            "not fix a badly chosen corpus: sometimes it only makes the bias harder to detect."
        ),
        p(
            "The weight column does not measure quality or size: it indicates the probability "
            "with which each source is sampled when building training batches. That is why "
            "WebText2, with only 19 billion tokens, weighs more than Books2, which has almost "
            "three times as many. The mix is a design decision: changing those percentages "
            "changes what the model sees and what it learns."
        ),
        py(
            """
DATA = [
    ("CommonCrawl (filtered)", 410, 60),
    ("WebText2", 19, 22),
    ("Books1", 12, 8),
    ("Books2", 55, 8),
    ("Wikipedia", 3, 3),
]

print(f"{'Source':24} {'Tokens':>8} {'Weight':>7}")
print("-" * 42)
for source, tokens, weight in DATA:
    print(f"{source:24} {tokens:>6} B {weight:>6} %")

total = sum(tokens for _, tokens, _ in DATA)
print(f"\\nSum of available tokens: {total:,} billion")
print("GPT-3 was trained on about 300 billion, not on the whole corpus.")
""",
            caption=(
                "The table as code: change a weight and check that the total available "
                "tokens does not change, but the mix does."
            ),
        ),
        check(
            "The table adds up to 499 billion tokens and the text says 509 billion. What do you conclude?",
            "That there is a 10 billion discrepancy that the book does not explain at that "
            "point. We should not invent a cause. The useful conclusion is methodological: "
            "check the figures and do not confuse the available corpus with the 300 billion "
            "tokens GPT-3 was trained on.",
        ),
        keypoints(
            [
                "GPT-3 mixed five sources: CommonCrawl, WebText2, Books1, Books2, and Wikipedia.",
                "The web dominates the mix; books and Wikipedia add diversity and quality.",
                "The table adds up to 499 billion, but the text says 509 billion: an unexplained discrepancy.",
                "GPT-3 was trained on about 300 billion tokens, not on the whole available corpus.",
                "Filtering, deduplicating, and choosing the mix matter as much as accumulating data.",
                "Every corpus has biases; the model inherits them.",
            ]
        ),
    ),
    key_points=(
        "GPT-3's corpus combines web, books, and Wikipedia in very uneven proportions.",
        "Table 1.1 adds up to 499 billion tokens, but the text says 509 billion.",
        "The available corpus is not the same as the 300 billion tokens actually seen.",
        "Quality, deduplication, and mixing are design decisions, not details.",
        "A biased corpus produces a biased model.",
    ),
)
