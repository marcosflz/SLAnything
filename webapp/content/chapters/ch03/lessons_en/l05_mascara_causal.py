"""Lesson 5 · The causal mask."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=5,
    slug="mascara-causal",
    title="The causal mask",
    summary=(
        "In a generative model, each position may only look at its past. The causal mask turns "
        "that restriction into exact zeros before softmax."
    ),
    minutes=10,
    objectives=(
        "Explain why autoregressive generation needs a mask.",
        "Build a lower-triangular mask.",
        "Apply −∞ before softmax and check that rows sum to one.",
        "Distinguish causal masking from dropout.",
    ),
    blocks=(
        lead(
            "GPT is trained to predict the next token. If, when computing the representation of "
            "position 3, the model could read position 4, the task would be cheating: the answer "
            "would be in the input. The <strong>causal mask</strong> prevents that leak and forces "
            "each position to build itself only from what it has already seen."
        ),
        p(
            "Without a mask, self-attention is bidirectional: each token can consult tokens to its "
            "left and right. That is useful for understanding tasks, such as classifying a full "
            "sentence, but incompatible with left-to-right generation. During training we process "
            "all positions at once to use the GPU; the mask makes that possible without future "
            "positions leaking into past representations."
        ),
        h2("A lower-triangular matrix"),
        p(
            "For a three-token sequence, the mask lets position 1 look at 1; position 2 at 1 and "
            "2; position 3 at all three. The permission matrix is lower triangular: ones on the "
            "diagonal and below, zeros above. If the scores are S = [[2.0, 1.0, 0.5], [1.5, 2.5, "
            "0.8], [0.7, 1.2, 3.0]], the mask leaves allowed entries untouched and replaces future "
            "ones with −∞."
        ),
        table(
            ["From ↓ / To →", "t1", "t2", "t3"],
            [
                ["t1", "2.0", "−∞", "−∞"],
                ["t2", "1.5", "2.5", "−∞"],
                ["t3", "0.7", "1.2", "3.0"],
            ],
            caption=(
                "Scores after applying the causal mask. Future positions are marked with −∞ "
                "before softmax; past and current positions are kept."
            ),
            note="Toy example with three tokens; the values do not come from a trained model.",
        ),
        p(
            "When softmax is applied, exp(−∞) tends to zero, so masked positions receive exactly "
            "zero weight. Normalization is recomputed over the remaining positions and each row "
            "sums to one again. With the example scores, the first row becomes [1.000, 0, 0]; the "
            "second, [0.269, 0.731, 0]; the third, [0.079, 0.131, 0.790]. Token 1 only looks at "
            "itself; token 2 splits between 1 and 2; token 3 can use all three."
        ),
        figure(
            "img/ch03/mascara-causal.svg",
            "Score matrix with the upper right replaced by minus infinity and, on the right, the normalized weight matrix with zeros in future positions.",
            "The mask is applied before softmax: future positions become −∞ and their "
            "contribution disappears. Each resulting row sums to one.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("What is filtered and what is not"),
        p(
            "The mask hides neither the current token nor the past: the diagonal and the lower "
            "part remain visible. It does not change the values V either; it only decides which "
            "values are mixed. If it is applied after softmax instead of before, the row must be "
            "renormalized, because the remaining weights no longer sum to one. Doing that "
            "incorrectly is a classic source of information leaks: through normalization, the "
            "model may end up using something it thought it had masked."
        ),
        p(
            "Causal masking is often combined with <strong>dropout</strong>, which randomly turns "
            "off part of the weights during training to reduce overfitting. They are different "
            "mechanisms: the mask is structural and deterministic; dropout is random and only "
            "active during training. The book uses a 50% dropout rate to illustrate the effect, "
            "although GPT training uses lower rates such as 0.1 or 0.2."
        ),
        h2("Generation and context"),
        p(
            "At inference time, a decoder-only model usually generates one token at a time. The "
            "mask is still present when the full prompt is processed, because the model computes "
            "representations for all positions in parallel. After that, each new token is appended "
            "to the sequence and passes through the block again. The mask guarantees that a "
            "position's representation never depends on tokens that did not exist when it was "
            "computed."
        ),
        p(
            "Nor does the mask turn the model into a perfect search engine for the past. It only "
            "restricts access; the quality of what is retrieved depends on the projections and on "
            "training. A token can look at a position and extract nothing useful from it. Causal "
            "attention is a necessary condition for generation, not a guarantee of coherence."
        ),
        callout(
            "warning",
            "Masking is not explaining",
            "The fact that a position cannot look at the future does not mean the model has "
            "learned a human notion of causality. The mask is a computational restriction. The "
            "relations it learns within the past may still be superficial correlations or corpus "
            "shortcuts.",
        ),
        check(
            "Why use −∞ before softmax instead of setting future scores to zero?",
            "Because exp(0) = 1: a zero score would still contribute to the softmax sum and give "
            "the future position a non-zero weight. With −∞, the exponential is exactly zero, so "
            "the masked position does not participate and the row is renormalized only over the "
            "allowed positions.",
        ),
        py(
            """
import math

TOKENS = ["t1", "t2", "t3"]
SCORES = [
    [2.0, 1.0, 0.5],
    [1.5, 2.5, 0.8],
    [0.7, 1.2, 3.0],
]

def softmax(row):
    maximum = max(row)
    exp = [math.exp(value - maximum) if value != float("-inf") else 0.0 for value in row]
    total = sum(exp)
    return [value / total for value in exp]

print("Causal mask: -inf in the future")
masked = []
for i, row in enumerate(SCORES):
    new_row = [value if j <= i else float("-inf") for j, value in enumerate(row)]
    masked.append(new_row)
    print(TOKENS[i], new_row)

print("\\nWeights after softmax:")
for token, row in zip(TOKENS, masked):
    weights = softmax(row)
    print(token, [round(value, 4) for value in weights], "sum:", round(sum(weights), 6))
""",
            caption=(
                "Causal mask over a 3 × 3 matrix. The upper part is marked with −∞ and softmax "
                "turns it into exact zeros."
            ),
        ),
        keypoints(
            [
                "The causal mask prevents a position from seeing future tokens.",
                "It is implemented as a lower-triangular permission matrix.",
                "Future positions are replaced by −∞ before softmax.",
                "Exp(−∞) is zero, so the row is normalized only over past and present.",
                "The mask is structural; dropout is random and only active during training.",
                "Autoregressive generation needs this restriction to avoid cheating.",
            ]
        ),
    ),
    key_points=(
        "The causal mask restricts each position to its past and itself.",
        "It is applied before softmax with −∞ in future positions.",
        "Masked weights become exactly zero and rows sum to one.",
        "Masking after softmax requires renormalization and is error-prone.",
        "The mask is a computational restriction, not an explanation of causality.",
    ),
)
