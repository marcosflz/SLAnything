"""Lesson 5 · The transformer block."""

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
)

LESSON = Lesson(
    number=5,
    slug="bloque-transformer",
    title="The transformer block",
    summary=(
        "The complete assembly: LayerNorm, multi-head attention, residual, LayerNorm, "
        "feed-forward network, and residual, with the same input and output shape."
    ),
    minutes=12,
    objectives=(
        "Order the six operations of a Pre-LN transformer block.",
        "Explain where each residual connection goes and what it requires.",
        "Verify that the [batch, tokens, 768] shape is preserved.",
        "Relate the block to the twelve stacked in GPT-2 small.",
    ),
    blocks=(
        lead(
            "You already have the loose pieces: LayerNorm, attention, GELU, the "
            "feed-forward network, and residual connections. The transformer block puts "
            "them in a repeatable order. That order is the heart of GPT: twelve copies with "
            "the same input and output tensors, but different weights, turn a sequence of "
            "vectors into a richer, more contextual sequence of vectors."
        ),
        h2("The block's sequence"),
        p(
            "The Pre-LN block used by GPT-2 follows this order. First it saves the input "
            "<code>x</code> and normalizes it with <code>norm1</code>. Then it applies "
            "multi-head attention, which mixes information across positions. It adds the "
            "result to the original input: <code>x = x + attention(norm1(x))</code>. Next it "
            "saves the new <code>x</code>, normalizes it with <code>norm2</code>, sends it "
            "through the feed-forward network, and adds again: "
            "<code>x = x + ffn(norm2(x))</code>. The book applies dropout after each "
            "sublayer during training."
        ),
        figure(
            "img/ch04/bloque-gpt.svg",
            "Transformer block diagram: LayerNorm, multi-head attention, residual sum, LayerNorm, feed-forward network, and second residual sum.",
            "The block preserves the input shape: each sublayer transforms the content, "
            "but not the number of tokens or the vector dimension.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "The key lies in the two sums. The first residual wraps attention; the second "
            "wraps the FFN. Both require the sublayer's output to have exactly the same shape "
            "as its input. That is why attention projects from 768 to 768 and the FFN returns "
            "to 768 after expanding. Without that match, the sum would not be possible and "
            "the block would need another operation to combine the paths. The shape "
            "<code>[batch, tokens, 768]</code> is preserved from start to finish."
        ),
        p(
            "That repetition is what turns a local operation into a deep model. Each block "
            "receives the residual stream from the previous one, normalizes it, enriches it "
            "with attention, and transforms it with the FFN. No block needs to know how many "
            "follow it: its contract is always the same, a sequence of 768-dimensional "
            "vectors. That uniformity lets you change the number of layers without rewriting "
            "the architecture, and it is why the same code works for GPT-2 small and for "
            "larger variants."
        ),
        h2("Pre-LN and constant shape"),
        p(
            "Order matters. In Pre-LN, normalization happens before the sublayer; the "
            "residual sum happens afterwards, over the unnormalized input. That leaves a "
            "direct path —<code>x</code> itself— that crosses the block without going through "
            "attention or the FFN. In Post-LN, normalization would be applied after the sum, "
            "inside the main path. GPT-2 chose Pre-LN because it makes deep stacks easier to "
            "train; the book notes that Post-LN often gives worse dynamics."
        ),
        p(
            "Each GPT-2 small block contains about 7.09 million parameters: 2.36 M for "
            "attention, 4.72 M for the FFN, and 3,072 for the two LayerNorms. Twelve blocks "
            "add up to about 85.03 M. The block does not change the sequence length or the "
            "embedding dimension; what changes is the content of each vector, which now "
            "incorporates context. The shape is the same, but the meaning is not: a vector "
            "for “cat” on the way in and on the way out does not encode the same thing."
        ),
        lab("gpt-block"),
        callout(
            "note",
            "A block is not a model",
            "The transformer block is the repeatable unit, not the complete GPT. The model "
            "still needs input embeddings, a final normalization, and an output head. The "
            "block only transforms the sequence it receives; the full architecture decides "
            "how to enter it and how to turn the result into logits.",
        ),
        check(
            "Why is the attention residual added to the original input rather than to the "
            "LayerNorm output?",
            "Because the residual must preserve a direct path with the starting information. "
            "LayerNorm prepares the input for attention, but the sum uses the unnormalized "
            "<code>x</code> that existed before the sublayer. That way the gradient and the "
            "original information can cross the block without depending on the learned "
            "transformation.",
        ),
        keypoints(
            [
                "The Pre-LN block orders: LayerNorm, attention, residual, LayerNorm, FFN, residual.",
                "Attention mixes tokens; the FFN transforms each token separately.",
                "Both residual connections require matching input and output shapes.",
                "The [batch, tokens, 768] shape is preserved throughout the block.",
                "Twelve blocks add about 85.03 M parameters in GPT-2 small.",
                "The block transforms contextual content, not the tensor shape.",
            ]
        ),
    ),
    key_points=(
        "A transformer block combines two sublayers with normalization and residuals.",
        "The Pre-LN order is LN → attention → residual → LN → FFN → residual.",
        "Residual sums require matching shapes.",
        "The sequence shape is preserved; the content becomes contextual.",
        "GPT-2 small stacks twelve blocks of about 7.09 M parameters each.",
        "The block is not the whole model: embeddings and an output head are still missing.",
    ),
)
