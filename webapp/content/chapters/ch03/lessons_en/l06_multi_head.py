"""Lesson 6 · Multi-head attention."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=6,
    slug="multi-head-attention",
    title="Multi-head attention",
    summary=(
        "A single head produces one mixture of relations. Several heads look at the sequence "
        "from different subspaces and then concatenate their results."
    ),
    minutes=11,
    objectives=(
        "Explain why attention uses several heads.",
        "Describe how d_out is split across heads and concatenated.",
        "Compute the dimension per head for GPT-2 and the original transformer.",
        "Distinguish stacked-head implementations from the fused one.",
    ),
    blocks=(
        lead(
            "One attention head produces one weight matrix and therefore one way of mixing the "
            "sequence. If the model needs to link a pronoun to its antecedent, a verb to its "
            "subject, and a word to the previous one at the same time, a single mixture may not "
            "be enough. <strong>Multi-head attention</strong> runs several heads in parallel, "
            "each with its own projections."
        ),
        p(
            "The idea is not to repeat the same computation. Each head learns its own "
            "W<sub>q</sub>, W<sub>k</sub>, and W<sub>v</sub> matrices, so it can specialize in a "
            "type of relation or a subspace of the representation. The outputs of all heads are "
            "concatenated and passed through an output projection. The block remains one unit: "
            "internally, it looks at the sequence from several angles."
        ),
        h2("Several heads, one block"),
        p(
            "If the model has d<sub>model</sub> dimensions and h heads, each head works with "
            "d<sub>head</sub> = d<sub>model</sub> / h. In GPT-2 small, 768 / 12 = 64. In the "
            "original transformer, 512 / 8 = 64. Each head computes its own attention over its "
            "projection, produces a 64-dimensional context vector, and at the end the 12 vectors "
            "are concatenated back to 768. A final matrix W<sub>O</sub> mixes the information from "
            "the heads."
        ),
        figure(
            "img/ch03/multi-cabeza.svg",
            "Multi-head attention diagram: the input is projected into several heads, each computes attention, the results are concatenated and projected to the output.",
            "Each head has its own Q, K, and V projections. Their outputs are concatenated and "
            "a final projection combines them into the block's context vector.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "The arithmetic requirement is that d<sub>model</sub> be divisible by h. Otherwise the "
            "dimensions cannot be split into equal parts. The book's toy example uses d<sub>in</sub> "
            "= 3, d<sub>out</sub> = 2, and two heads: each head works with one dimension and "
            "concatenation returns two. The fused implementation projects Q, K, and V once, then "
            "reshapes the tensor to separate the heads; the stacked implementation creates several "
            "causal attention instances and runs them one after another."
        ),
        table(
            ["Model", "d_model", "heads", "d per head", "context"],
            [
                ["Original transformer", "512", "8", "64", "—"],
                ["GPT-2 small", "768", "12", "64", "1024"],
                ["GPT-2 large", "1600", "25", "64", "1024"],
            ],
            caption=(
                "The dimension per head stays at 64 as the number of heads and the total dimension "
                "grow. Concatenation reconstructs d_model."
            ),
            note="Architecture figures cited in the book; “context” is the maximum sequence length.",
        ),
        h2("What each head learns"),
        p(
            "In trained models, some heads attend to the previous position, to punctuation, to "
            "verbs, or to pronouns. It is tempting to assign each head a linguistic label, but "
            "reality is blurrier: many heads are redundant, others change function across layers "
            "and contexts, and one task may be split across several heads. Interpretability "
            "research finds recurring patterns, not a clean org chart."
        ),
        p(
            "That specialization is not programmed. It emerges from training: if several heads help "
            "reduce the loss, the model learns to use them. Early layers often show local and "
            "positional patterns; deeper layers capture more abstract relations. But a high weight "
            "is still a clue, not a complete explanation of the prediction. Multi-head attention "
            "expands representational capacity, not transparency."
        ),
        h2("Cost and efficiency"),
        p(
            "With a fixed d<sub>model</sub> budget, splitting into more heads does not simply "
            "multiply attention cost: each head is narrower and the sum of their products stays in "
            "the same order. What changes is expressiveness and optimization difficulty. If "
            "instead of fusing the heads we stack independent modules, we repeat projections and "
            "waste parallelism; that is why the usual implementation projects once, splits, and "
            "processes the heads as a batch."
        ),
        p(
            "Concatenation is not addition. Each head occupies a different slice of the final "
            "vector; the W<sub>O</sub> projection then decides how to combine them. That separation "
            "lets one head avoid erasing what another has captured. If they were simply added, the "
            "signals would compete in the same coordinates from the start."
        ),
        callout(
            "info",
            "More heads does not mean more intelligence",
            "The number of heads is a hyperparameter, not a measure of quality. With fixed "
            "d_model, adding heads reduces the dimension of each one. A model with many heads may "
            "be better for certain tasks, but it can also be harder to train and interpret. Fair "
            "comparisons use the same parameter and compute budget.",
        ),
        check(
            "A model has d_model = 768 and 12 heads. How many dimensions does each head have? What "
            "if it used 16 heads?",
            "With 12 heads, 768 / 12 = 64 dimensions per head. With 16 heads, 768 / 16 = 48. Both "
            "splits are exact because 768 is divisible by 12 and 16. If the division were not "
            "whole, the architecture would need to adjust d_model or the number of heads.",
        ),
        keypoints(
            [
                "Multi-head runs several attentions in parallel with different projections.",
                "Each head produces a context vector of dimension d_model / h.",
                "Outputs are concatenated and combined by an output projection.",
                "GPT-2 small uses 12 heads of 64 dimensions over a total of 768.",
                "Head specialization emerges from training and is not a fixed org chart.",
                "The fused implementation projects once and splits the tensor; it is more efficient than stacking modules.",
            ]
        ),
    ),
    key_points=(
        "Multi-head attention splits d_model across several heads.",
        "Each head learns its own Q, K, and V projections.",
        "Outputs are concatenated and projected with W_O.",
        "GPT-2 small: 768 dimensions, 12 heads, 64 per head.",
        "Heads can specialize, but interpreting them is not automatic.",
    ),
)
