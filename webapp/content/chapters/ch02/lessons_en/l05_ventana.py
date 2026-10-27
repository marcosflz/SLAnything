"""Lesson 5 · The sliding window."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=5,
    slug="ventana-deslizante",
    title="The sliding window",
    summary=(
        "A tokenized corpus is a long sequence; the model trains on fixed-length fragments. "
        "The sliding window decides how much context each example sees and how much examples "
        "overlap."
    ),
    minutes=10,
    objectives=(
        "Explain why training uses fixed-length windows.",
        "Calculate how many windows a sequence yields for a given context and stride.",
        "Relate overlap, coverage, and computational cost.",
        "Choose a reasonable stride for a concrete corpus.",
    ),
    blocks=(
        lead(
            "A tokenized novel can contain millions of IDs. The network cannot receive them all "
            "at once: it needs examples of manageable size. The solution is to cut the sequence "
            "into windows and slide a fixed-length window along the text. The "
            "<strong>stride</strong> determines how far it advances between windows."
        ),
        p(
            "If the window is 256 tokens and the stride is 1, each example shares 255 tokens with "
            "the previous one. If the stride is also 256, the windows do not overlap. Between "
            "both extremes lies a continuum. The book uses <code>max_length=256</code> and "
            "<code>stride=128</code> by default: half the context repeats, so each token appears "
            "in two examples on average. That overlap helps the model see every transition from "
            "more than one viewpoint, at the cost of more compute."
        ),
        figure(
            "img/ch02/ventana-deslizante.svg",
            "A strip of tokens with several windows of length five and stride two, showing the overlap.",
            "With context 5 and stride 2, each window shares three tokens with the next one. "
            "The overlap is not a mistake: it is a decision about how much information is reused.",
            credit="Original diagram by Aula LLM.",
            wide=True,
        ),
        p(
            "The arithmetic is simple. If the sequence has <code>N</code> tokens, the window is "
            "<code>L</code>, and the stride is <code>S</code>, the number of windows with a "
            "complete target is <code>floor((N − L − 1) / S) + 1</code>. With the 5,145 BPE "
            "tokens of <em>The Verdict</em> reported in the book, <code>L = 256</code> and "
            "<code>S = 128</code> produce <strong>39 windows</strong>. With "
            "<code>S = 256</code>, they produce <strong>20</strong>. These are our calculations "
            "on the book's figure, not numbers the book enumerates."
        ),
        table(
            ["Context", "Stride", "Overlap", "Windows with 5,145 tokens", "Use"],
            [
                ["256", "128", "50 %", "39", "More variety, more compute"],
                ["256", "256", "0 %", "20", "Coverage without repetition"],
                ["128", "64", "50 %", "79", "Short context, more examples"],
                ["128", "128", "0 %", "40", "A lighter alternative"],
            ],
            caption="Number of windows with a complete target: floor((N − L − 1) / S) + 1.",
            note=(
                "These are calculated examples. It is the same count the book's implementation "
                "performs with range(0, len(token_ids) - max_length, stride)."
            ),
        ),
        h2("What the stride changes"),
        p(
            "A small stride increases the number of examples and the overlap. That can help learn "
            "local transitions, but it multiplies effective epochs over the same text and the "
            "training cost. A large stride reduces the number of examples and removes repetition; "
            "in exchange, some transitions are seen only once and the model may fit with less "
            "diversity. The book notes that too much overlap can favour overfitting because the "
            "model sees the same passages repeatedly."
        ),
        p(
            "The choice depends on the corpus and the budget. For a small corpus, a smaller "
            "stride generates enough examples. For a huge one, a stride equal to the context "
            "reduces cost without losing coverage: every token appears at least once. In any "
            "case, the last window may be incomplete; many implementations discard it to keep "
            "rectangular shapes in the batch."
        ),
        lab("window"),
        callout(
            "tip",
            "Think in film frames",
            "A window is a frame from a movie of text. The stride is how far the camera moves "
            "between frames. If it moves a little, you see continuous motion and spend more "
            "frames; if it moves a lot, you cover ground faster but lose continuity.",
        ),
        check(
            "A sequence has 1,000 tokens, the context is 100, and the stride is 50. How many windows with a complete target are there and how much do they overlap?",
            "There are floor((1000 − 100 − 1) / 50) + 1 = 18 windows. Each shares 50 tokens with "
            "the next one, half the context. The first token of window k also appears in window "
            "k−1, but not in k−2.",
        ),
        h2("The window is not the model's context"),
        p(
            "Two concepts that are easily confused should be kept apart. The "
            "<strong>training window</strong> is the fragment used in one optimisation step. The "
            "model's <strong>context window</strong> is the maximum number of tokens it can "
            "process at inference. They may coincide, but they do not have to: a model can train "
            "on 256-token windows and accept 1,024 positions if its architecture and positional "
            "embeddings allow it."
        ),
        p(
            "The window is also not used alone: input-target pairs are built inside it. A "
            "four-token window does not produce a single example but four predictions, one per "
            "position. That shift is the subject of the next lesson and the piece that connects "
            "data preparation with the loss function."
        ),
        keypoints(
            [
                "The corpus is split into fixed-length windows so training can use batches.",
                "The stride is the number of tokens the window advances between examples.",
                "A smaller stride means more overlap, more examples, and more cost.",
                "The number of windows with a complete target is floor((N − L − 1) / S) + 1.",
                "Training window and context window are different concepts.",
                "A window contains several predictions, not one.",
            ]
        ),
    ),
    key_points=(
        "The sliding window cuts the corpus into fixed-length fragments.",
        "The stride controls overlap and the number of examples.",
        "More overlap costs more compute and may favour overfitting.",
        "The training window is not necessarily the model's maximum context.",
    ),
    quiz_id=None,
)
