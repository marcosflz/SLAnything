"""Chapter 3 quiz (EN)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-3": Quiz(
        id="quiz-capitulo-3",
        title="Self-assessment · Chapter 3",
        description=(
            "Ten questions on attention, Q/K/V, scaling, the causal mask, multi-head, and cost. "
            "You need 80% to consider the chapter complete; you can retake it as often as you "
            "like."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt=(
                    "Which limitation of recurrent encoder-decoders motivated attention "
                    "mechanisms?"
                ),
                options=(
                    "They could only translate between two languages.",
                    "The decoder relied on a single hidden state with the whole input compressed.",
                    "They did not use vector representations.",
                    "They could not be trained with backpropagation.",
                ),
                correct=1,
                explanation=(
                    "The encoder compressed the whole sentence into a fixed-size hidden state, and "
                    "the decoder saw only that summary. Attention let the decoder consult input "
                    "positions directly and distribute weight across them."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "In simplified self-attention, what is the correct order of operations?"
                ),
                options=(
                    "Softmax, dot product, and weighted sum.",
                    "Dot product, softmax, and weighted sum of the input vectors.",
                    "Weighted sum, dot product, and softmax.",
                    "Dot product, weighted sum, and softmax.",
                ),
                correct=1,
                explanation=(
                    "Scores are computed first with dot products, then normalized row-wise with "
                    "softmax, and finally the input vectors are mixed with those weights."
                ),
            ),
            Question(
                id="q3",
                prompt="What does a token's key represent in attention?",
                options=(
                    "What that token seeks in the others.",
                    "The content it contributes when attended to.",
                    "What that token offers so other queries can compare against it.",
                    "Its absolute position in the sequence.",
                ),
                correct=2,
                explanation=(
                    "The query expresses what the current token seeks; the key, what each "
                    "candidate offers; the value, what content is mixed. All three come from "
                    "different projections of the same embedding."
                ),
            ),
            Question(
                id="q4",
                prompt=(
                    "An unscaled attention score is 16 and the key dimension is d_k = 64. What is "
                    "the scaled score?"
                ),
                options=("0.25", "2", "4", "8"),
                correct=1,
                explanation=(
                    "Divide by √d_k = √64 = 8. Therefore, 16 / 8 = 2. Dividing by d_k would give "
                    "0.25, which is too aggressive a scale."
                ),
            ),
            Question(
                id="q5",
                prompt=(
                    "In causal attention, why replace future positions with −∞ before softmax "
                    "instead of using zero?"
                ),
                options=(
                    "Because exp(−∞) is zero, while exp(0) = 1 would still contribute.",
                    "Because zero would make the matrix non-triangular.",
                    "Because −∞ removes the token from the tensor and saves memory.",
                    "Because softmax does not accept positive values.",
                ),
                correct=0,
                explanation=(
                    "Softmax exponentiates every score. Zero would become 1 and give weight to the "
                    "future position; −∞ becomes 0 and removes it completely. The row is then "
                    "normalized only over allowed positions."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "In a causal attention matrix for 4 tokens, how many non-zero weights are "
                    "there in total?"
                ),
                options=("4", "6", "10", "16"),
                correct=2,
                explanation=(
                    "The mask keeps the diagonal and the lower part. Row 1 has 1 weight, row 2 has "
                    "2, row 3 has 3, and row 4 has 4: 1 + 2 + 3 + 4 = 10. The other 6 weights are "
                    "zero."
                ),
            ),
            Question(
                id="q7",
                prompt=(
                    "A model has d_model = 768 and 12 attention heads. How many dimensions does "
                    "each head have?"
                ),
                options=("32", "48", "64", "96"),
                correct=2,
                explanation=(
                    "The dimension per head is d_model / h = 768 / 12 = 64. GPT-2 small uses "
                    "exactly that split: 12 heads of 64 dimensions."
                ),
            ),
            Question(
                id="q8",
                prompt=(
                    "What role does the output projection W_O play after concatenating the heads "
                    "in multi-head attention?"
                ),
                options=(
                    "It applies the causal mask to each head.",
                    "It combines information from the heads into a d_model vector.",
                    "It normalizes the weights so they sum to one.",
                    "It reduces the vocabulary to the number of tokens.",
                ),
                correct=1,
                explanation=(
                    "The heads produce distinct slices that are concatenated. W_O mixes those "
                    "slices and returns a representation of the model's size. The mask and softmax "
                    "were already applied inside each head."
                ),
            ),
            Question(
                id="q9",
                prompt=(
                    "A layer with 12 heads processes 1024 tokens. How many attention scores does "
                    "it generate, approximately?"
                ),
                options=("12,288", "1.05 million", "12.6 million", "150 million"),
                correct=2,
                explanation=(
                    "Each head builds a 1024 × 1024 = 1,048,576 score matrix. Multiplying by 12 "
                    "heads gives 12,582,912, about 12.6 million per layer."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "What is the correct order of steps in causal attention with trainable "
                    "weights?"
                ),
                options=(
                    "Project Q, K, and V; compute QKᵀ; scale; mask; softmax; multiply by V.",
                    "Project Q, K, and V; softmax; compute QKᵀ; mask; multiply by V.",
                    "Compute QKᵀ; project Q, K, and V; mask; softmax; multiply by V.",
                    "Mask; project Q, K, and V; softmax; compute QKᵀ; multiply by V.",
                ),
                correct=0,
                explanation=(
                    "First project queries, keys, and values. Then score with QKᵀ, scale by √d_k, "
                    "mask the future with −∞, apply softmax, and mix the values. Changing that "
                    "order changes the result."
                ),
            ),
        ),
    )
}
