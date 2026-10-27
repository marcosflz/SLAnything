"""Lesson 4 · Scaled dot product and softmax."""

from webapp.content.schema import (
    Lesson,
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
    slug="producto-escalado",
    title="Scaled dot product and softmax",
    summary=(
        "Dividing scores by the square root of d_k keeps softmax from saturating. Scaling is "
        "the difference between a useful distribution and an almost binary decision."
    ),
    minutes=10,
    objectives=(
        "Explain why the dot product grows with dimension.",
        "Justify the 1/√d_k scale in attention.",
        "Implement a numerically stable softmax.",
        "Interpret the effect of scaling on weights and gradients.",
    ),
    blocks=(
        lead(
            "The formula that summarizes attention is <strong>softmax(QK<sup>T</sup> / "
            "√d<sub>k</sub>) · V</strong>. Dividing by the square root of the key dimension looks "
            "like a minor detail, but it keeps softmax in a useful range: without it, scores grow "
            "with dimension and weights become almost binary."
        ),
        p(
            "The dot product of two vectors sums d<sub>k</sub> products. If the components are "
            "independent, with zero mean and unit variance, each product contributes one unit of "
            "variance and the sum accumulates d<sub>k</sub>. Its standard deviation therefore "
            "grows like √d<sub>k</sub>. In a model with 64 dimensions per head, a typical score "
            "can have a magnitude of 8; with 256, it can reach 16. That scale does not reflect "
            "greater similarity: it is an arithmetic consequence of adding more terms."
        ),
        h2("Why divide by the square root of d_k"),
        p(
            "Softmax is sensitive to scale. With small scores, the resulting distribution is "
            "smooth and spreads weight across several options. With large scores, the gap between "
            "the maximum and the rest is amplified and the distribution behaves like a switch: "
            "almost all weight falls on one position. When that happens, gradients at the other "
            "positions become tiny and learning slows down. The transformer paper describes this "
            "as a problem of vanishing gradients: as the dot product grows, softmax approaches a "
            "step function."
        ),
        p(
            "Dividing by √d<sub>k</sub> brings the score back to a comparable scale regardless of "
            "the number of dimensions. The order of the scores does not change —dividing by a "
            "positive constant is monotonic— but the shape of the distribution does. Attention "
            "still prefers the closest match, yet it stops ignoring the alternatives completely. "
            "That is why the mechanism is called <strong>scaled dot-product attention</strong>."
        ),
        p(
            "An example with one dominant score: if the unscaled score is d<sub>k</sub> and the "
            "other three are zero, the maximum softmax weight depends on the dimension. With "
            "d<sub>k</sub> = 4, the scaled score is 2 and the maximum weight is about 0.711. With "
            "d<sub>k</sub> = 16, it is 4 and rises to 0.948. With d<sub>k</sub> = 64, it is 8 and "
            "reaches 0.999. The same relative advantage becomes a dictatorship as dimension grows "
            "if we do not scale."
        ),
        table(
            ["d_k", "unscaled score", "√d_k", "scaled score", "max weight"],
            [
                ["4", "4", "2", "2", "0.711"],
                ["16", "16", "4", "4", "0.948"],
                ["64", "64", "8", "8", "0.999"],
                ["256", "256", "16", "16", "≈1.000"],
            ],
            caption=(
                "Effect of scaling on a row with one dominant score and three alternatives at "
                "zero. Without division, the distribution saturates as d_k grows."
            ),
            note="Our own calculation with four candidates; it illustrates the effect, not a trained model.",
        ),
        h2("Stable softmax"),
        p(
            "There is a second numerical detail. Computing exp(x) directly can overflow if x is "
            "large: the result exceeds the largest representable value and becomes infinity. The "
            "standard fix subtracts the row maximum before exponentiating. The operation is "
            "mathematically equivalent, because the ratio of exponentials does not change if we "
            "multiply numerator and denominator by the same factor, but it avoids the extremes. "
            "Libraries implement this stable version in practice."
        ),
        p(
            "Softmax also guarantees that weights are positive and sum to one. That property lets "
            "us read them as a distribution of relative importance. They are not probabilities "
            "that a token will occur, but proportions of a mixture over values. Confusing the two "
            "is a common mistake when reading an attention matrix."
        ),
        py(
            """
import math

def stable_softmax(row):
    maximum = max(row)
    exp = [math.exp(value - maximum) for value in row]
    total = sum(exp)
    return [value / total for value in exp]

print("d_k | score | scaled | max weight")
for d_k in (4, 16, 64, 256):
    scores = [float(d_k), 0.0, 0.0, 0.0]
    scaled = [value / math.sqrt(d_k) for value in scores]
    weights = stable_softmax(scaled)
    print(f"{d_k:>3} | {scores[0]:>5.1f} | {scaled[0]:>6.2f} | {max(weights):.4f}")

print("\\nWithout scaling, the maximum weight would be:")
for d_k in (4, 16, 64, 256):
    weights = stable_softmax([float(d_k), 0.0, 0.0, 0.0])
    print(f"d_k={d_k:>3}: {max(weights):.6f}")
""",
            caption=(
                "The same score pattern across four dimensions. Softmax subtracts the maximum "
                "before exponentiating to avoid overflow."
            ),
        ),
        callout(
            "tip",
            "Scaling does not change who wins",
            "Dividing by √d<sub>k</sub> preserves the order of scores: if a key was the closest "
            "match, it still is. What changes is how the weight is distributed. A saturated "
            "softmax learns poorly because alternatives receive almost zero gradient; a smooth "
            "one keeps signal for correction.",
        ),
        check(
            "An unscaled score is 16 and d_k = 64. What is the scaled score, and why use that "
            "divisor?",
            "The scaled score is 16 / √64 = 16 / 8 = 2. We use √d_k because the variance of a dot "
            "product of d_k independent terms grows with d_k; dividing by its square root brings "
            "the standard deviation back to a stable scale and prevents softmax from saturating.",
        ),
        keypoints(
            [
                "The dot product accumulates d_k terms and grows with dimension.",
                "The 1/√d_k scale normalizes that magnitude without changing score order.",
                "Without scaling, softmax saturates and gradients shrink.",
                "Softmax turns scores into positive weights that sum to one.",
                "Subtracting the maximum before exponentiating avoids numerical overflow.",
                "Attention weights are mixture proportions, not token probabilities.",
            ]
        ),
    ),
    key_points=(
        "Attention scales scores by 1/√d_k.",
        "Scaling compensates for variance growth with dimension.",
        "A saturated softmax produces tiny gradients and slow learning.",
        "A stable softmax subtracts the maximum before exponentiating.",
        "Weights sum to one and express relative importance.",
    ),
)
