"""Chapter 5 quiz (EN)."""

from webapp.content.schema import Question, Quiz

QUIZZES_EN: dict[str, Quiz] = {
    "quiz-capitulo-5": Quiz(
        id="quiz-capitulo-5",
        title="Self-assessment · Chapter 5",
        description=(
            "Ten questions on loss, training, data, evaluation, and cost. You need 80 % "
            "to pass the self-assessment; you can retake it as often as you like."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="What does a GPT's training loss measure?",
                options=(
                    "The percentage of words generated without spelling mistakes.",
                    "The probability assigned to the correct token, transformed with −log and averaged.",
                    "The number of parameters that change at each step.",
                    "The time an epoch takes to complete.",
                ),
                correct=1,
                explanation=(
                    "The loss compares the model's distribution with the token that actually "
                    "comes next in the text. It takes the probability of the correct token, "
                    "applies −log, and averages over the batch. The higher that probability, "
                    "the lower the loss."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "If the model assigns probability 0.25 to the correct token, what is "
                    "that token's loss?"
                ),
                options=("0.25", "0.75", "1.386", "4.000"),
                correct=2,
                explanation=(
                    "The loss is −ln(0.25). Since ln(0.25) ≈ −1.386, the result is ≈ 1.386. "
                    "A probability of 1 gives 0; a probability of 0.5 gives ≈ 0.693."
                ),
            ),
            Question(
                id="q3",
                prompt=(
                    "A batch has two tokens with losses 0.5 and 1.5. What is the batch "
                    "perplexity?"
                ),
                options=("1.00", "1.65", "2.72", "4.48"),
                correct=2,
                explanation=(
                    "The mean loss is (0.5 + 1.5) / 2 = 1.0. Perplexity is exp(1.0) ≈ 2.72. "
                    "It can be read as the effective number of candidates among which the "
                    "model is uncertain."
                ),
            ),
            Question(
                id="q4",
                prompt="What is the correct order of a PyTorch training step?",
                options=(
                    "backward → zero_grad → forward → step.",
                    "zero_grad → forward and loss → backward → step.",
                    "step → forward → backward → zero_grad.",
                    "forward → step → zero_grad → backward.",
                ),
                correct=1,
                explanation=(
                    "First clear the gradients from the previous step, then compute the "
                    "output and loss, backpropagate to obtain gradients, and finally let the "
                    "optimizer update the weights."
                ),
            ),
            Question(
                id="q5",
                prompt="What distinguishes AdamW from classic Adam?",
                options=(
                    "AdamW does not use first- and second-order moments.",
                    "AdamW applies weight decay decoupled from the gradient.",
                    "AdamW only works with models under 1 billion parameters.",
                    "AdamW removes the need for a learning rate.",
                ),
                correct=1,
                explanation=(
                    "AdamW separates weight decay from the adaptive update. This keeps "
                    "regularisation out of the moment estimates and often generalises better. "
                    "It still uses a learning rate."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "The book's training data loader uses drop_last=True. What is it for?"
                ),
                options=(
                    "To shuffle examples in every epoch.",
                    "To discard an incomplete final batch and keep shapes stable.",
                    "To use the validation set as training data.",
                    "To duplicate the last batch and balance the classes.",
                ),
                correct=1,
                explanation=(
                    "With drop_last=True, the loader skips the final batch when it is not "
                    "full. Every training batch then has the same shape and updates do not "
                    "run on very few examples. Validation uses False so no data is lost."
                ),
            ),
            Question(
                id="q7",
                prompt=(
                    "Training loss keeps falling, but validation loss stalls or rises. "
                    "What does that indicate?"
                ),
                options=(
                    "That the model has completely stopped learning the language.",
                    "That the optimizer's learning rate is too low.",
                    "That the model is overfitting the training set.",
                    "That the tokenizer's vocabulary is too large.",
                ),
                correct=2,
                explanation=(
                    "This is the classic overfitting pattern: the model improves on the data "
                    "it sees but does not generalise to unseen text. In the book it happens "
                    "because the corpus is tiny and training runs for several epochs; with "
                    "more data, a single pass is often enough."
                ),
            ),
            Question(
                id="q8",
                prompt=(
                    "Which configuration produces the most deterministic generation, close "
                    "to always picking the most likely token?"
                ),
                options=(
                    "High temperature and a large top-k.",
                    "Temperature 0 or argmax selection.",
                    "Temperature 1.5 and top-k 50.",
                    "More epochs at inference time.",
                ),
                correct=1,
                explanation=(
                    "At temperature 0 sampling is disabled and argmax is used; argmax can "
                    "also be applied directly. High temperature flattens the distribution "
                    "and increases variety, not determinism."
                ),
            ),
            Question(
                id="q9",
                prompt=(
                    "Using FLOPs ≈ 6 · N · D, how many FLOPs does training a 124 M parameter "
                    "model on 1,000 M tokens require?"
                ),
                options=("7.44 × 10¹⁵", "7.44 × 10¹⁷", "7.44 × 10²⁰", "1.24 × 10¹⁷"),
                correct=1,
                explanation=(
                    "6 × 124 × 10⁶ × 1 × 10⁹ = 7.44 × 10¹⁷ FLOPs. This is an order-of-"
                    "magnitude estimate: it ignores hardware inefficiency, inter-GPU "
                    "communication, and inference cost."
                ),
            ),
            Question(
                id="q10",
                prompt="Which sequence best summarises chapter 5?",
                options=(
                    "Load GPT-2 → finetune → measure loss → classify.",
                    "Tokenize → build attention → train → delete the weights.",
                    "Measure loss → train → evaluate and sample → save or load weights.",
                    "Quantize → distill → align with RLHF → deploy.",
                ),
                correct=2,
                explanation=(
                    "The chapter covers numerical evaluation, the training loop, decoding "
                    "strategies, and saving or loading weights. Loading GPT-2 lets you start "
                    "from an already trained model. RLHF alignment and quantisation belong "
                    "to other stages."
                ),
            ),
        ),
    )
}
