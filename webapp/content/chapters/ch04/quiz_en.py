"""Chapter 4 self-assessment (English)."""

from webapp.content.schema import Question, Quiz

QUIZZES_EN: dict[str, Quiz] = {
    "quiz-capitulo-4": Quiz(
        id="quiz-capitulo-4",
        title="Self-assessment · Chapter 4",
        description=(
            "Ten questions on the GPT-2 small configuration, LayerNorm, GELU, the "
            "feed-forward network, the transformer block, residual connections, and "
            "the output head. You need 80% to pass the chapter."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="In GPT_CONFIG_124M, what does context_length = 1024 control?",
                options=(
                    "The number of transformer layers.",
                    "The maximum number of tokens the model can process at once.",
                    "The vocabulary size.",
                    "The dimension of each attention head.",
                ),
                correct=1,
                explanation=(
                    "context_length sets the context window: 1,024 positions. n_layers "
                    "controls the layers, vocab_size the vocabulary, and emb_dim the "
                    "vector dimension. The per-head dimension is emb_dim divided by n_heads."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "How many parameters does the token embedding table of GPT-2 small "
                    "have (50,257 × 768)?"
                ),
                options=(
                    "786,432",
                    "4,722,432",
                    "38,597,376",
                    "124,412,160",
                ),
                correct=2,
                explanation=(
                    "50,257 × 768 = 38,597,376. It is the largest table in the model if we "
                    "exclude the output head, which has exactly the same shape. 786,432 "
                    "corresponds to the positional embeddings (1,024 × 768)."
                ),
            ),
            Question(
                id="q3",
                prompt="Along which dimension does LayerNorm normalize each token?",
                options=(
                    "The embedding dimension, with mean 0 and variance 1.",
                    "The batch dimension.",
                    "The time dimension across tokens.",
                    "The entire vocabulary.",
                ),
                correct=0,
                explanation=(
                    "LayerNorm computes the mean and variance over the 768 components of "
                    "each token and normalizes inside that vector. BatchNorm, by contrast, "
                    "normalizes across the batch for each feature."
                ),
            ),
            Question(
                id="q4",
                prompt="Where does a Pre-LN transformer block place LayerNorm?",
                options=(
                    "Only after the output head.",
                    "After attention and after the FFN.",
                    "Only in the positional embedding.",
                    "Before attention and before the FFN.",
                ),
                correct=3,
                explanation=(
                    "In Pre-LN, normalization comes before each sublayer, and the residual "
                    "sum is applied afterwards. The original transformer used Post-LN, with "
                    "normalization after the sublayers."
                ),
            ),
            Question(
                id="q5",
                prompt="What distinguishes GELU from ReLU?",
                options=(
                    "It removes every negative value.",
                    "It is smooth and keeps a small output for negative inputs.",
                    "It needs no parameters and no computation.",
                    "It only works with batch size 1.",
                ),
                correct=1,
                explanation=(
                    "ReLU has a corner at zero and zeroes every negative input. GELU is a "
                    "smooth curve that approximates ReLU but leaves a small non-zero value "
                    "—and a gradient— in the negative region."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "The GPT-2 small FFN expands 768 → 3,072 → 768. How many parameters "
                    "does it have, approximately, including weights and biases?"
                ),
                options=(
                    "2.36 M",
                    "38.6 M",
                    "4.72 M",
                    "7.09 M",
                ),
                correct=2,
                explanation=(
                    "The first projection has 768 × 3,072 weights and 3,072 biases; the "
                    "second has 3,072 × 768 weights and 768 biases. The total is 4,722,432, "
                    "about 4.72 M. The 7.09 M figure also includes attention and the two "
                    "LayerNorms in the block."
                ),
            ),
            Question(
                id="q7",
                prompt="What is the correct order inside a Pre-LN transformer block?",
                options=(
                    "LN → attention → residual → LN → FFN → residual",
                    "attention → LN → FFN → residual → LN",
                    "LN → FFN → attention → residual",
                    "residual → LN → attention → FFN",
                ),
                correct=0,
                explanation=(
                    "The input is normalized first, then multi-head attention is applied and "
                    "the residual is added. After that the result is normalized again, the "
                    "feed-forward network is applied, and a second residual is added. The "
                    "shape is preserved."
                ),
            ),
            Question(
                id="q8",
                prompt="What problem does a residual connection help mitigate?",
                options=(
                    "An excessively large vocabulary.",
                    "The lack of a tokenizer.",
                    "Too much softmax.",
                    "Vanishing gradients in deep networks.",
                ),
                correct=3,
                explanation=(
                    "The sum x + f(x) creates an identity path through which the gradient can "
                    "travel back without being multiplied by every intermediate derivative. "
                    "That makes it feasible to stack many blocks."
                ),
            ),
            Question(
                id="q9",
                prompt="What does the output head produce for each sequence position?",
                options=(
                    "The chosen token directly.",
                    "A vector of 50,257 logits, before softmax.",
                    "A probability that already sums to 1 without softmax.",
                    "A 768-dimensional embedding.",
                ),
                correct=1,
                explanation=(
                    "The final linear layer projects each 768-dimensional vector into the "
                    "vocabulary and returns 50,257 unnormalized logits. Softmax then turns "
                    "them into a probability distribution."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "You have defined GPTModel and initialized its weights randomly. What is "
                    "still missing before it can generate coherent text?"
                ),
                options=(
                    "Add more layers without training.",
                    "Remove the output head.",
                    "Train it on data; the architecture alone does not learn.",
                    "Replace the tokenizer with another one.",
                ),
                correct=2,
                explanation=(
                    "The architecture defines the computation, but random weights contain no "
                    "knowledge of language. The book shows that an untrained model produces "
                    "incoherent text; pretraining is the next chapter."
                ),
            ),
        ),
    )
}
