"""Lesson 4 · The feed-forward network."""

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
    number=4,
    slug="feed-forward",
    title="The feed-forward network",
    summary=(
        "The subnetwork that expands each token to 3,072 dimensions, applies GELU, and "
        "returns to 768: where its capacity lives and why it does not mix tokens."
    ),
    minutes=10,
    objectives=(
        "Describe the structure and dimensions of GPT-2 small's FFN.",
        "Calculate its parameters and compare them with the rest of the block.",
        "Explain why the FFN does not replace attention.",
        "Understand why input and output dimensions are kept equal.",
    ),
    blocks=(
        lead(
            "Attention gets much of the fame, but in GPT-2 small the feed-forward network "
            "is the largest subnetwork in the block: almost twice as many parameters as "
            "attention. Its job is not to mix tokens but to transform each one separately, "
            "give it room for non-linear combinations, and return it to the same dimension "
            "so the next block can keep stacking."
        ),
        p(
            "The book's FFN has two linear layers and a GELU in between: "
            "<code>Linear(768, 3072) → GELU → Linear(3072, 768)</code>. The first projection "
            "expands the vector fourfold; the second compresses it again. The book's figure "
            "4.9 summarizes that path. The intermediate dimension is not a whim: it gives the "
            "network a wider space in which to combine the 768 components before returning to "
            "the representation shared by every block. The factor 4 is a common convention, "
            "not a law of nature."
        ),
        table(
            ["Piece", "Shape", "Parameters"],
            [
                ["First projection", "768 → 3,072", "768 × 3,072 + 3,072 = 2,362,368"],
                ["Second projection", "3,072 → 768", "3,072 × 768 + 768 = 2,360,064"],
                ["FFN total", "768 → 3,072 → 768", "4,722,432"],
                ["Block attention", "Q, K, V, and output", "2,360,064"],
                ["LayerNorm (two)", "768", "3,072"],
                ["Complete block", "—", "7,085,568"],
            ],
            caption="FFN parameters compared with the rest of GPT-2 small's block.",
            note=(
                "Our own calculation from the book's dimensions. Linear biases are included; "
                "qkv_bias stays disabled."
            ),
        ),
        p(
            "The comparison is revealing. The FFN contributes 4,722,432 parameters per "
            "block; attention contributes 2,360,064. Multiplied by twelve, the FFN adds "
            "about 56.67 million and attention about 28.32 million. In the tied model, that "
            "means the FFN holds roughly 45.5% of the parameters, compared with 22.8% for "
            "attention. These percentages are calculated here to guide intuition: most of the "
            "block's capacity is not in deciding what to look at but in transforming what has "
            "already been looked at."
        ),
        h2("Expand, activate, project"),
        p(
            "Think of the FFN as a three-step machine applied to every position in the "
            "sequence. First, a linear projection takes the vector from 768 to 3,072 "
            "dimensions: more room to represent combinations of features. Then GELU decides "
            "which components pass and how strongly. Finally, the second projection returns "
            "to 768. The result keeps the <code>[batch, tokens, 768]</code> shape, so it can "
            "be added to the residual and enter the next block without resizing."
        ),
        p(
            "That constant shape is a design decision, not a detail. If the FFN returned a "
            "different size, an additional projection would be needed in every block and the "
            "residual connection would no longer be a direct sum. Keeping the shape lets "
            "twelve blocks share the same interface, change only their weights, and reuse the "
            "same logic. It also lets attention and the FFN alternate smoothly: one mixes "
            "information across tokens; the other processes each token with a wider network."
        ),
        h2("Capacity without mixing tokens"),
        p(
            "Attention and the FFN do complementary work. Attention computes weights across "
            "positions and builds contextual representations; the FFN does not look at other "
            "tokens and applies the same transformation to each one. That division prevents "
            "the network from having to solve two problems in the same operation. The FFN "
            "adds depth and non-linearity per token; attention adds communication between "
            "tokens. Together they form the block, and the repeated block forms the model."
        ),
        p(
            "There is a practical consequence: the FFN is computationally expensive because "
            "it works with an intermediate dimension four times larger. In GPT-2 small, 3,072 "
            "columns per token per block account for a significant share of the operations. "
            "Later models have explored variants such as SwiGLU or different expansion "
            "factors to balance capacity and cost. The principle remains the same: expand, "
            "apply a non-linearity, and project back."
        ),
        callout(
            "tip",
            "A way to remember the block",
            "Attention = communicate across tokens. FFN = transform each token. "
            "LayerNorm = keep the scale under control. Residual = preserve the direct path. "
            "If you can say these four sentences, you can rebuild the block without "
            "memorizing the diagram.",
        ),
        check(
            "Why can't the FFN replace attention?",
            "Because the FFN applies the same transformation to every position and does not "
            "compare tokens with one another. It cannot decide that “cat” should influence "
            "“tired” or move information between positions. Attention builds that contextual "
            "mixture; the FFN only transforms each vector independently.",
        ),
        keypoints(
            [
                "The FFN has two linear projections and a GELU between them.",
                "It expands from 768 to 3,072 dimensions and returns to 768.",
                "It contributes 4,722,432 parameters per block, more than attention.",
                "It does not mix tokens: it applies the same network to every position.",
                "It preserves the [batch, tokens, 768] shape for residuals and stacking.",
                "Attention communicates; the FFN transforms and adds non-linear capacity.",
            ]
        ),
    ),
    key_points=(
        "The FFN expands fourfold, applies GELU, and projects back.",
        "It is the block's largest subnetwork: 4.72 M versus 2.36 M for attention.",
        "It does not mix information across tokens; attention does that.",
        "Keeping input and output shapes enables stacking and residual sums.",
        "The expansion factor is a design convention, not an obligation.",
        "Block capacity depends on both communicating and transforming.",
    ),
)
