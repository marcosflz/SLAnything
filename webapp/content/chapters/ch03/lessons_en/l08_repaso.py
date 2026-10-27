"""Lesson 8 · Review and self-assessment."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=8,
    slug="repaso-atencion",
    title="Review and self-assessment",
    summary=(
        "A review of the full journey —from fixed memory to multi-head— and a ten-question "
        "self-assessment to check what you have internalized."
    ),
    minutes=10,
    objectives=(
        "Reconstruct the full attention chain from Q, K, and V to the context.",
        "Relate model dimensions to the split across heads.",
        "Spot common confusions about weights, masks, and cost.",
        "Assess the chapter with a ten-question quiz.",
    ),
    blocks=(
        lead(
            "Attention is easiest to understand as a chain of small decisions: project, score, "
            "scale, mask, normalize, and mix. If you can walk through that chain and justify each "
            "step, you have the essentials of chapter 3. The final quiz will show which parts need "
            "another pass."
        ),
        h2("The mechanism in one sentence"),
        p(
            "Self-attention takes a sequence of vectors X and computes three projections: Q = "
            "XW<sub>q</sub>, K = XW<sub>k</sub>, and V = XW<sub>v</sub>. It compares each query "
            "with all keys through QK<sup>T</sup>, divides by √d<sub>k</sub>, masks future "
            "positions if the model is causal, and applies row-wise softmax. The result is a weight "
            "matrix that, multiplied by V, produces the context vectors Z. In multi-head, the "
            "process runs in several heads and their outputs are concatenated."
        ),
        p(
            "Each step has a reason. Projections allow the same token to play different roles. The "
            "dot product measures alignment. Scaling prevents softmax saturation. The mask stops "
            "future leakage. Softmax turns scores into positive proportions that sum to one. The "
            "weighted sum mixes content. Remove any of these steps and the mechanism changes "
            "behavior, not just efficiency."
        ),
        h2("From toy to model"),
        p(
            "The chapter's examples use three tokens of four dimensions so the arithmetic can be "
            "followed. The book uses six tokens and three-dimensional vectors in the simple "
            "version, and projections from 3 to 2 in the version with weights. Those numbers do "
            "not describe a real GPT: they are mock-ups. GPT-2 small works with 768 dimensions, 12 "
            "heads of 64, and a 1024-token window. GPT-2 large rises to 1600 dimensions and 25 "
            "heads, also of 64."
        ),
        table(
            ["Idea", "What to retain", "Where it appeared"],
            [
                [
                    "Fixed memory",
                    "A single hidden state compresses the input and loses long dependencies.",
                    "Lesson 1",
                ],
                [
                    "Attention weights",
                    "Computed per input and summing to one per row; not parameters.",
                    "Lesson 2",
                ],
                [
                    "Q, K, and V",
                    "Three learned projections with different roles.",
                    "Lesson 3",
                ],
                [
                    "Scaling",
                    "Dividing by √d_k controls softmax saturation.",
                    "Lesson 4",
                ],
                [
                    "Causal mask",
                    "−∞ before softmax removes the future and rows renormalize.",
                    "Lesson 5",
                ],
                [
                    "Multi-head",
                    "Several heads of d_model / h, concatenated and projected.",
                    "Lesson 6",
                ],
                [
                    "Cost",
                    "n² scores per head and layer; long context is expensive.",
                    "Lesson 7",
                ],
            ],
            caption=(
                "Review map: each row connects an idea with the lesson where it was developed. If "
                "one feels opaque, revisit that lesson before the quiz."
            ),
        ),
        h2("Common mistakes"),
        p(
            "The first is confusing attention weights with model weights. The former are dynamic "
            "and sum to one per row; the latter are parameters that persist after training. The "
            "second is believing the mask removes tokens from the tensor: it assigns them zero "
            "weight, but they still occupy positions and memory. The third is thinking a high "
            "weight explains the prediction. Attention shows where information was mixed, not why "
            "the model chose a word."
        ),
        p(
            "It is also easy to forget the scaling or apply it incorrectly. Dividing by d<sub>k</sub> "
            "instead of its square root makes scores too small and softmax nearly uniform. Another "
            "mistake is masking after softmax without renormalizing: the remaining weights no "
            "longer sum to one and the value mixture is unbalanced. Finally, do not confuse "
            "attention cost with total cost: the n² term dominates for long contexts, but it is not "
            "the only operation in the block."
        ),
        callout(
            "tip",
            "How to use the quiz",
            "Answer without looking at your notes and read the explanation for every question, "
            "whether you are right or wrong. A score of 80% means you have the basics; below that, "
            "review the lessons indicated in the table. You can retake the quiz as many times as "
            "you like: the goal is understanding, not luck.",
        ),
        check(
            "Write the scaled attention formula from memory and point out where the causal mask "
            "enters.",
            "The formula is softmax(QK<sup>T</sup> / √d<sub>k</sub>) · V. In a causal model, −∞ is "
            "added to future positions of QK<sup>T</sup> (or those positions are replaced by −∞) "
            "before softmax. Their exponential is then zero, they do not contribute to the sum, "
            "and normalization distributes weight only over past and present.",
        ),
        keypoints(
            [
                "Attention projects X into Q, K, and V, scores with QKᵀ, scales, masks, and normalizes.",
                "The context Z is the weighted sum of V with the attention weights.",
                "Attention weights are dynamic; projections are learned parameters.",
                "The causal mask runs before softmax and produces exact zeros in the future.",
                "Multi-head splits d_model across heads and concatenates their outputs.",
                "Cost is n² per head and layer; long context requires trade-offs.",
                "The chapter quiz checks these ideas with ten questions.",
            ]
        ),
    ),
    key_points=(
        "The full chain is project, score, scale, mask, normalize, and mix V.",
        "Attention weights are not model parameters.",
        "The causal mask acts before softmax and removes the future.",
        "Multi-head concatenates several heads and projects them to d_model.",
        "Attention's quadratic cost limits long context.",
    ),
    quiz_id="quiz-capitulo-3",
)
