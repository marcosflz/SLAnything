"""Lesson 2 · Layer normalization."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=2,
    slug="layer-normalization",
    title="Layer normalization",
    summary=(
        "How LayerNorm centers and scales each token's activations, why it stabilizes "
        "training, and what changes when it is placed before each sublayer."
    ),
    minutes=10,
    objectives=(
        "Explain what LayerNorm computes and along which dimension it does so.",
        "Interpret the role of epsilon, scale, and shift.",
        "Compare LayerNorm with BatchNorm in the context of an LLM.",
        "Place Pre-LN normalization inside the transformer block.",
    ),
    blocks=(
        lead(
            "LayerNorm does not change what information a vector contains: it changes its "
            "scale. It is a small operation —a mean, a variance, and two parameters per "
            "dimension— but without it, stacking twelve blocks becomes fragile. "
            "Understanding it means understanding why a deep transformer can train without "
            "its activations exploding or fading away."
        ),
        h2("Mean, variance, and two parameters"),
        p(
            "For each token, LayerNorm walks through its 768 components, computes the mean "
            "and the variance, subtracts the mean, and divides by the standard deviation. "
            "The result has mean zero and variance one. Then it applies a learnable scale and "
            "shift, one per component, so the network can recover a different scale if that "
            "helps. The formula is "
            "<code>(x − μ) / sqrt(σ² + ε) · γ + β</code>, where <code>ε</code> prevents "
            "division by zero when the variance is tiny."
        ),
        p(
            "The book uses <code>eps = 1e-5</code> and computes variance by dividing by "
            "<em>n</em>, not <em>n − 1</em>. This is the so-called biased variance, the same "
            "convention as TensorFlow and the original GPT-2 weights. With 768 components, "
            "the difference between the two denominators is negligible; what matters is that "
            "the result is reproducible and compatible with the weights loaded later. The "
            "<code>scale</code> and <code>shift</code> parameters start at ones and zeros, "
            "and training adjusts them if doing so improves the loss."
        ),
        h2("Why it stabilizes training, and why Pre-LN"),
        p(
            "In a deep network, gradients are multiplied layer after layer. If the factors "
            "are slightly below one, the gradient vanishes; if they are slightly above one, "
            "it explodes. Normalizing activations keeps their scale under control and makes "
            "the loss behave more predictably. In a transformer, LayerNorm is applied before "
            "attention and before the feed-forward network; after each sublayer, the residual "
            "connection is added. That arrangement is called <strong>Pre-LN</strong> and it is "
            "what GPT-2 uses. The original transformer applied Post-LN, with normalization "
            "after the sublayer, and usually required more care to train."
        ),
        p(
            "The difference from BatchNorm matters. BatchNorm computes statistics across the "
            "batch for each feature; its result depends on which examples happen to be "
            "grouped together and on the batch size. LayerNorm computes statistics inside each "
            "token, independently of the rest of the batch. That fits LLMs, which are often "
            "trained with variable batch sizes or deployed in resource-constrained "
            "environments. It also fits the <code>[batch, tokens, 768]</code> shape: "
            "normalization runs over the last dimension, and each position is handled "
            "separately."
        ),
        py(
            """
import math

def layer_norm(row, eps=1e-5):
    mean = sum(row) / len(row)
    var = sum((x - mean) ** 2 for x in row) / len(row)
    norm = [(x - mean) / math.sqrt(var + eps) for x in row]
    return mean, var, norm

rows = [
    [0.9, -0.4, 0.2, 1.1, -0.8],
    [2.0, 2.1, 1.9, 2.2, 1.8],
]

for i, row in enumerate(rows, start=1):
    mean, var, output = layer_norm(row)
    out_mean = sum(output) / len(output)
    out_var = sum((x - out_mean) ** 2 for x in output) / len(output)
    print(f"Row {i}: mean={mean:.3f}, variance={var:.3f}")
    print("  normalized:", [round(x, 3) for x in output])
    print(f"  output mean={out_mean:.6f}, output variance={out_var:.6f}")
""",
            caption=(
                "LayerNorm computed by hand on two vectors. The example is our own; it "
                "checks that the output has mean 0 and variance 1."
            ),
        ),
        callout(
            "info",
            "Normalizing is not losing information",
            "LayerNorm does not erase the direction of the vector: it preserves it and "
            "rescales its components. The learnable scale and shift let the network recover "
            "useful amplitudes. What is removed is the global drift in magnitude, not the "
            "relative content of each dimension.",
        ),
        check(
            "Why does LayerNorm work even when the batch has a different size at every step?",
            "Because it computes the mean and variance inside each token, not across the "
            "batch. Each vector is normalized with its own statistics, so it does not depend "
            "on which other examples accompany it. BatchNorm, by contrast, mixes information "
            "from the batch and needs more stable sizes and distributions.",
        ),
        keypoints(
            [
                "LayerNorm normalizes each token along the embedding dimension.",
                "Mean and variance are computed per vector, not per batch.",
                "Epsilon prevents division by zero; scale and shift are learnable parameters.",
                "GPT-2 uses Pre-LN: normalization before attention and before the FFN.",
                "BatchNorm depends on the batch; LayerNorm is more flexible for LLMs.",
                "Normalization stabilizes activations and gradients in deep stacks.",
            ]
        ),
    ),
    key_points=(
        "LayerNorm centers and scales each token across its 768 components.",
        "It uses a per-vector mean and variance, with epsilon for numerical stability.",
        "Scale and shift recover a useful scale during training.",
        "Pre-LN normalizes before each sublayer; that is GPT-2's choice.",
        "Unlike BatchNorm, it does not depend on batch size or composition.",
        "Its job is to keep activations and gradients stable.",
    ),
)
