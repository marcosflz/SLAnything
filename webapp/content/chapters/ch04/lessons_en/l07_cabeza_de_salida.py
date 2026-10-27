"""Lesson 7 · From vectors to tokens."""

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
    number=7,
    slug="cabeza-de-salida",
    title="From vectors to tokens",
    summary=(
        "How the output head turns 768 dimensions into 50,257 logits, how softmax "
        "turns them into probabilities, and how much memory weight tying saves."
    ),
    minutes=10,
    objectives=(
        "Follow a context vector through to the logits.",
        "Explain what softmax does and why argmax can be applied to logits.",
        "Calculate the output head's cost and the effect of weight tying.",
        "Relate the architecture to inference and training memory.",
    ),
    blocks=(
        lead(
            "The last block returns one context vector per position, but the model has not "
            "yet said which token comes next. For that it needs an output head: a linear "
            "layer that projects 768 dimensions into the vocabulary size and produces a "
            "score for every possible token. It is the step that turns geometry into "
            "language."
        ),
        h2("Logits and softmax"),
        p(
            "The output head is a 768 × 50,257 matrix, with no bias in GPT-2. If the input is "
            "a batch of two four-token sequences, the output has shape "
            "<code>[2, 4, 50,257]</code>: one score per position and per vocabulary token. "
            "Those scores are called <strong>logits</strong> and are not probabilities; they "
            "can be negative or positive and do not sum to anything. To generate the next "
            "token, only the last position of the sequence is used."
        ),
        figure(
            "img/ch04/cabeza-de-salida.svg",
            "Path from a 768-dimensional context vector to 50,257 logits, softmax, and the chosen token.",
            "The final projection shares its matrix with the token embeddings when weights "
            "are tied; softmax turns the logits into a distribution.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "Softmax turns the logit vector into a positive probability distribution that "
            "sums to 1. It exponentiates each logit and divides by the sum of all of them. It "
            "is a monotonic function: it preserves order, so the token with the highest logit "
            "is still the most probable after softmax. That is why greedy generation —always "
            "choosing the maximum— can apply <code>argmax</code> directly to the logits and "
            "get the same result. Softmax is still useful for seeing confidence and for "
            "sampling techniques such as temperature or top-k."
        ),
        h2("Weight tying and memory"),
        p(
            "The output head has 50,257 × 768 = 38,597,376 parameters, exactly the same shape "
            "as the token embedding table. Tying the weights means using a single matrix for "
            "both functions. The model goes from 163,009,536 parameters to 124,412,160 and "
            "saves 38.6 M weights. The idea makes sense: each row of the matrix represents a "
            "token, and that representation can serve both to read it and to score it. The "
            "book implements the separate head first and leaves sharing for chapter 6, when "
            "it loads GPT-2's weights."
        ),
        p(
            "Memory does not end with the weights. Inference must add the key-value cache, "
            "which grows with context length and the number of layers. Training must add "
            "gradients and optimizer states; with Adam in fp32, a common rule is to reserve "
            "about 16 bytes per parameter, plus activations. The memory lab lets you change "
            "model, precision, and context window to see how the figures move. These are "
            "order-of-magnitude estimates, not a hardware budget."
        ),
        lab("memory"),
        p(
            "The book calculates that the 163,009,536 parameters of the untied model occupy "
            "621.83 MB in 32-bit floating point. That is manageable for a modern laptop, but "
            "it already shows that even a small GPT is a large object. The architecture is "
            "compact; the size comes from repeating blocks and multiplying by a 50,257-token "
            "vocabulary. That relationship between shape, parameters, and memory is what lets "
            "you compare models of 124 M, 345 M, 762 M, or 1,542 M without changing the code "
            "structure."
        ),
        callout(
            "warning",
            "Architecture is not training",
            "A GPT with random weights produces logits, probabilities, and tokens, but not "
            "coherent text. The book shows it with “Hello, I am”: the output is a meaningless "
            "sequence because the model has not learned anything yet. The output head closes "
            "the circuit; pretraining is what fills the weights with useful information.",
        ),
        check(
            "Why can argmax be applied to the logits without computing softmax first?",
            "Because softmax is monotonic: if one logit is larger than another, its "
            "exponential is also larger, and normalization divides everything by the same "
            "sum. The order does not change. To choose the most probable token, argmax over "
            "the logits returns the same index; softmax is used when a distribution is "
            "needed, not just the winner.",
        ),
        keypoints(
            [
                "The output head projects each 768-dimensional vector into the vocabulary.",
                "Its output has shape [batch, tokens, 50,257] and contains unnormalized logits.",
                "Softmax turns logits into probabilities that sum to 1.",
                "Greedy generation picks the maximum logit; order is preserved.",
                "Weight tying reuses the embedding matrix and saves 38.6 M parameters.",
                "Real memory includes weights, the KV cache, and, during training, gradients and optimizer states.",
            ]
        ),
    ),
    key_points=(
        "The output head is a linear projection from 768 to 50,257.",
        "Logits are unnormalized scores, one per vocabulary token.",
        "Softmax turns them into a probability distribution.",
        "The most probable token can be chosen with argmax over logits.",
        "Weight tying reduces the model from 163 M to 124 M parameters.",
        "Inference and training add memory beyond the weights.",
    ),
)
