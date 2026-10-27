"""Lesson 2 · Self-attention step by step."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=2,
    slug="self-attention",
    title="Self-attention step by step",
    summary=(
        "Score, normalize, and mix: the three operations with which every token builds a "
        "contextual representation of the whole sequence."
    ),
    minutes=12,
    objectives=(
        "Describe self-attention as a weighted sum of representations.",
        "Compute attention scores with dot products.",
        "Normalize scores with softmax and interpret the weights.",
        "Build a context vector from a 3 × 3 attention matrix.",
    ),
    blocks=(
        lead(
            "The core idea of self-attention fits in one sentence: each token looks at the "
            "others, decides which ones deserve more attention, and builds a new representation "
            "of itself from them. That representation is called a <strong>context vector</strong> "
            "and replaces the isolated embedding in later layers."
        ),
        p(
            "The <em>self</em> prefix means the sequence is compared with itself: there is no "
            "separate input and output sentence. In “The cat did not cross the street because it "
            "was tired,” the word “tired” needs to find “cat” to be resolved; distance and "
            "surface order should not prevent it. Attention learns to establish that kind of "
            "connection from data."
        ),
        h2("Three steps: score, normalize, and mix"),
        p(
            "The simplest form of self-attention has no trainable weights. First, an "
            "<strong>attention score</strong> is computed for every pair of tokens with a dot "
            "product. The dot product measures how much two vectors align: similar directions "
            "give a high score, orthogonal vectors give roughly zero, and opposite directions "
            "can give a negative score. Second, the scores in each row are turned into "
            "<strong>attention weights</strong> with softmax, so they become positive and sum to "
            "one. Third, each token's context vector is the weighted sum of all input vectors."
        ),
        p(
            "The weight matrix is not a fixed parameter: it is computed for each input. Two "
            "different sentences produce different matrices, and the same word can receive "
            "different weights. That is what makes the representation contextual rather than a "
            "simple dictionary of words."
        ),
        h2("A 3 × 3 numerical example"),
        p(
            "Take three tokens —“The,” “cat,” and “sleeps”— represented by four-dimensional "
            "vectors. The values are invented so the arithmetic can be followed by hand; in a real "
            "model, embeddings are learned. With these vectors, the score matrix is symmetric "
            "because we compare each vector with itself and with the others:"
        ),
        table(
            ["From ↓ / To →", "The", "cat", "sleeps"],
            [
                ["The", "1.014", "0.992", "0.568"],
                ["cat", "0.992", "1.591", "1.082"],
                ["sleeps", "0.568", "1.082", "1.087"],
            ],
            caption=(
                "Attention scores from a toy example with four-dimensional vectors. Each row is "
                "the token that queries; each column is the token being queried."
            ),
            note="Our own calculation with the example vectors; not weights from a trained model.",
        ),
        p(
            "After softmax, the first row is approximately 0.382 / 0.374 / 0.244: “The” spreads "
            "almost evenly because its vector does not clearly resemble either of the others. "
            "“Cat” gives itself more weight (0.465) but keeps part of “The” (0.255) and “sleeps” "
            "(0.280). “Sleeps” ends at 0.230 / 0.384 / 0.386."
        ),
        p(
            "The context vector of “cat” is obtained by multiplying each input vector by its "
            "weight and adding: 0.255 · The + 0.465 · cat + 0.280 · sleeps. The result is "
            "approximately [0.427, 0.605, 0.626, 0.390]. It is no longer the original embedding: "
            "it is a mixture where “cat” dominates but “The” and “sleeps” also contribute. In a "
            "real layer, projections are learned so that the mixture becomes useful (lesson 3)."
        ),
        lab("attention"),
        h2("What context adds"),
        p(
            "Attention does not encode order by itself. Embeddings say which word it is; position "
            "says where it is. Without that signal, the weighted sum would be almost invariant to "
            "order: “the dog bites the cat” and “the cat bites the dog” could end up with similar "
            "representations. The transformer adds positional information to the inputs, and "
            "attention learns to combine it with content."
        ),
        p(
            "Nor is it a bag of words. A bag counts occurrences and loses order; attention "
            "computes weights that depend on the query and on the content of each position. The "
            "same token can look at different places depending on the sentence, which helps "
            "resolve ambiguity without hand-written rules."
        ),
        callout(
            "info",
            "Attention weights are not model weights",
            "In a neural network, “weight” usually means a trainable parameter. In attention, "
            "“attention weight” means a value computed for a specific input. Parameters are "
            "learned and persist; attention weights change with every sentence and every layer. "
            "Confusing them leads to misreading what the model has learned.",
        ),
        check(
            "In the example, the “cat” row has weights 0.255 / 0.465 / 0.280. What do those three "
            "numbers mean?",
            "They mean that the context vector of “cat” is formed from 25.5% “The,” 46.5% “cat,” "
            "and 28.0% “sleeps.” They are relative weights that sum to one, not probabilities that "
            "a word will appear. The resulting context mixes the three vectors in those "
            "proportions.",
        ),
        py(
            """
import math

TOKENS = ["The", "cat", "sleeps"]
X = [
    [0.43, 0.15, 0.89, 0.12],
    [0.55, 0.87, 0.66, 0.31],
    [0.22, 0.58, 0.33, 0.77],
]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def softmax(row):
    maximum = max(row)
    exp = [math.exp(value - maximum) for value in row]
    total = sum(exp)
    return [value / total for value in exp]

scores = [[dot(a, b) for b in X] for a in X]
weights = [softmax(row) for row in scores]
contexts = [
    [sum(weights[i][j] * X[j][d] for j in range(len(X))) for d in range(len(X[0]))]
    for i in range(len(X))
]

print("Attention scores:")
for row in scores:
    print([round(value, 3) for value in row])

print("\\nAttention weights (each row sums to 1):")
for token, row in zip(TOKENS, weights):
    print(token, [round(value, 3) for value in row], "sum:", round(sum(row), 6))

print("\\nContext vector for 'cat':")
print([round(value, 3) for value in contexts[1]])
""",
            caption=(
                "Simplified self-attention without trainable weights over three four-dimensional "
                "tokens. Change the vectors and watch the weights move."
            ),
        ),
        keypoints(
            [
                "Self-attention compares a sequence with itself.",
                "Scores come from dot products between representations.",
                "Softmax turns each row of scores into positive weights that sum to one.",
                "The context vector is a weighted sum of the input vectors.",
                "Attention weights are dynamic; model weights are learned parameters.",
                "Position must be added separately: attention alone does not encode order.",
            ]
        ),
    ),
    key_points=(
        "Self-attention builds a context vector for each token.",
        "The dot product measures alignment between representations.",
        "Softmax normalizes scores into weights that sum to one.",
        "Context is a weighted sum of the whole sequence.",
        "Attention weights change with the input; parameters do not.",
    ),
)
