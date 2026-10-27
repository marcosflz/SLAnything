"""Lesson 8 · Review and self-assessment."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
)

LESSON = Lesson(
    number=8,
    slug="repaso-gpt",
    title="Review and self-assessment",
    summary=(
        "Eight ideas to consolidate the GPT architecture and a ten-question quiz to "
        "check that you can explain every piece and its calculations."
    ),
    minutes=10,
    objectives=(
        "Connect configuration, normalization, activation, FFN, block, and output.",
        "Rebuild the full flow of a small GPT without looking at your notes.",
        "Check your learning with the chapter self-assessment.",
    ),
    blocks=(
        lead(
            "You have traveled through the architecture from the bottom up: first the "
            "configuration numbers, then the pieces of the block, and finally the output "
            "path into the vocabulary. Now it is time to consolidate. This review adds no "
            "new concepts; it orders the ones you already have and helps you spot which "
            "piece needs another visit before training."
        ),
        p(
            "The question that organizes the chapter is simple: how do you get from a "
            "sequence of token IDs to a distribution over the next token? The answer is a "
            "chain of transformations with very specific shapes. If you can rebuild that "
            "chain and justify each step, you understand the architecture. If a link breaks, "
            "the quiz will tell you where to go back."
        ),
        h2("The complete map"),
        bullets(
            [
                "<strong>Configuration.</strong> 50,257 vocabulary tokens, 1,024 positions, 768 dimensions, 12 heads, and 12 layers. The tied model has 124,412,160 parameters.",
                "<strong>LayerNorm.</strong> Normalizes each token over its 768 components, with mean 0 and variance 1, and lets scale and shift adjust the scale.",
                "<strong>GELU.</strong> A smooth activation that replaces ReLU's corner and keeps a small signal for negative inputs.",
                "<strong>FFN.</strong> Expands from 768 to 3,072, applies GELU, and returns to 768. It contributes 4.72 M parameters per block and does not mix tokens.",
                "<strong>Transformer block.</strong> LN → attention → residual → LN → FFN → residual. The [batch, tokens, 768] shape is preserved.",
                "<strong>Residuals.</strong> The x + f(x) sum opens a direct path for the gradient and makes deep stacks trainable.",
                "<strong>Output head.</strong> Projects 768 → 50,257, produces logits, and softmax turns them into probabilities.",
                "<strong>No training, no language.</strong> The architecture defines the computation; pretrained weights provide the knowledge.",
            ],
            ordered=True,
        ),
        p(
            "There are three calculations worth repeating without a calculator. First, token "
            "embeddings: 50,257 × 768 = 38,597,376. Second, the FFN of one block: "
            "2 × 768 × 3,072 + 3,072 + 768 = 4,722,432. Third, the tied total: add the "
            "embeddings, twelve blocks, and the final normalization, and nothing else, "
            "because the head reuses the embedding matrix. Add a separate head and you get "
            "163,009,536. These numbers are not decoration: they explain why the model takes "
            "the memory it does and why weight tying matters."
        ),
        h2("Check what you know"),
        p(
            "The chapter self-assessment has <strong>ten questions</strong> with four options "
            "and an explanation for every answer. It covers all eight lessons and includes "
            "two calculation questions. You need <strong>80%</strong> —eight correct— to pass "
            "the chapter. There is no time limit and no penalty for retrying: the goal is to "
            "find gaps, not to pass by luck. If you miss one, return to the relevant lesson "
            "and rebuild the reasoning before trying again."
        ),
        p(
            "Before opening the quiz, try to explain the model in one sentence: “A GPT turns "
            "tokens into vectors, passes them through blocks that mix context and transform "
            "each position, normalizes the result, and projects it into the vocabulary to "
            "choose the next token.” If you can add what each block does, which shape it "
            "preserves, and how many parameters it contributes, you have the complete mental "
            "map. The next chapter puts that map to work."
        ),
        callout(
            "success",
            "Now it is your turn",
            "Open the <strong>chapter 4 self-assessment</strong>: ten questions and one "
            "explanation per answer. You need 80% to pass. You can retake it as many times as "
            "you want; if you miss one, the explanation tells you which lesson to review. The "
            "quiz does not replace practice, but it does tell you whether the architecture is "
            "clear.",
        ),
        check(
            "Explain in two sentences why the transformer block preserves the input shape "
            "and yet changes its content.",
            "Because every sublayer —attention and FFN— projects back to 768 dimensions, so "
            "the residual sum and stacking remain possible. What changes is not the number of "
            "tokens or the dimension but the representation: each vector incorporates context "
            "and the learned transformations.",
        ),
        keypoints(
            [
                "GPT-2 small's configuration fixes vocabulary, context, dimension, heads, and layers.",
                "LayerNorm stabilizes each token; GELU provides a smooth non-linearity.",
                "The FFN expands, activates, and projects without mixing positions.",
                "The block combines two sublayers, two LayerNorms, and two residuals.",
                "The [batch, tokens, 768] shape is preserved; the content becomes contextual.",
                "The output head produces logits and softmax turns them into probabilities.",
                "The chapter quiz requires 80% and can be retaken without penalty.",
            ]
        ),
    ),
    key_points=(
        "A small GPT is the same architecture as a large one, with manageable dimensions.",
        "LayerNorm, GELU, the FFN, residuals, and the block form a repeatable sequence.",
        "The sequence shape is preserved; the representation is enriched.",
        "Parameter calculations explain the model's size and the role of weight tying.",
        "The self-assessment covers all eight lessons and requires 80%.",
    ),
    quiz_id="quiz-capitulo-4",
)
