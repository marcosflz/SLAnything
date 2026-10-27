"""Chapter 1 quiz (English)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-1": Quiz(
        id="quiz-capitulo-1",
        title="Self-assessment · Chapter 1",
        description=(
            "Ten questions on the central concepts. You need 80% to consider the chapter "
            "passed; you can retake it as many times as you like."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="What two things does the “large” in large language model measure?",
                options=(
                    "Only the number of parameters.",
                    "The number of parameters and the size and diversity of the corpus.",
                    "The maximum prompt length.",
                    "The number of simultaneous users.",
                ),
                correct=1,
                explanation=(
                    "“Large” refers both to the parameters —the network's adjustable "
                    "weights— and to the amount and diversity of training data. Neither "
                    "dimension is enough on its own."
                ),
            ),
            Question(
                id="q2",
                prompt="What is the central task of GPT pretraining?",
                options=(
                    "Classifying emails as spam.",
                    "Translating without examples.",
                    "Predicting the next token.",
                    "Summarizing long documents.",
                ),
                correct=2,
                explanation=(
                    "GPT is trained to predict the next token in an enormous corpus. "
                    "Translating, summarizing, or classifying are capabilities exploited "
                    "later, not the pretraining task."
                ),
            ),
            Question(
                id="q3",
                prompt="Why is pretraining self-supervised?",
                options=(
                    "Because a human labels every sentence.",
                    "Because it uses reinforcement with rewards.",
                    "Because it does not need data.",
                    "Because the label is the text itself: the next token.",
                ),
                correct=3,
                explanation=(
                    "The text provides the input and the target at the same time. If the "
                    "sentence is “The cat sleeps on the sofa”, the input can be “The cat sleeps "
                    "on the” and the label “sofa”. No human annotation is needed."
                ),
            ),
            Question(
                id="q4",
                prompt="Which part of the original transformer does GPT use?",
                options=(
                    "The encoder.",
                    "The decoder.",
                    "Encoder and decoder.",
                    "Neither; GPT does not use a transformer.",
                ),
                correct=1,
                explanation=(
                    "GPT is a decoder-only model: it processes from left to right and "
                    "generates text autoregressively. BERT, by contrast, is based on the encoder."
                ),
            ),
            Question(
                id="q5",
                prompt="What is BERT especially designed for?",
                options=(
                    "Generating text from left to right.",
                    "Translating without data.",
                    "Predicting masked words and classifying.",
                    "Training with RLHF.",
                ),
                correct=2,
                explanation=(
                    "BERT uses the encoder and is trained by filling in hidden words while "
                    "looking at context in both directions. That is why it excels at "
                    "classification and information extraction more than open-ended generation."
                ),
            ),
            Question(
                id="q6",
                prompt="What does the self-attention mechanism allow?",
                options=(
                    "Looking only at the previous word.",
                    "Weighting the relevance of other tokens in the context.",
                    "Reducing the vocabulary.",
                    "Avoiding training.",
                ),
                correct=1,
                explanation=(
                    "Each token computes weights over the others to build a contextual "
                    "representation. That connects distant words, such as “cat” and “tired” in "
                    "a long sentence."
                ),
            ),
            Question(
                id="q7",
                prompt="What is a few-shot prompt?",
                options=(
                    "Training the model with little data.",
                    "Using a model with few parameters.",
                    "Generating very few words.",
                    "Including a few solved examples in the prompt.",
                ),
                correct=3,
                explanation=(
                    "Few-shot means giving examples inside the context, not retraining. The "
                    "weights do not change: the model learns in context and the effect lasts as "
                    "long as the conversation."
                ),
            ),
            Question(
                id="q8",
                prompt="What does finetuning change, unlike few-shot?",
                options=(
                    "The prompt.",
                    "The model's weights.",
                    "The tokenizer.",
                    "The hardware.",
                ),
                correct=1,
                explanation=(
                    "Finetuning updates the weights with labeled data and the change persists. "
                    "Few-shot only conditions generation with examples in the context."
                ),
            ),
            Question(
                id="q9",
                prompt="What does it mean that GPT is autoregressive?",
                options=(
                    "That it uses its previous output as the next step's input.",
                    "That it trains without labels.",
                    "That it generates all tokens in parallel.",
                    "That it does not need context.",
                ),
                correct=0,
                explanation=(
                    "It generates a token, appends it to the sequence, and predicts again. That "
                    "loop —predict, append, repeat— is autoregressive generation."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "Why can GPT translate even though it was not specifically trained for it?"
                ),
                options=(
                    "Because it includes a translation module.",
                    "Because the prompt changes the weights.",
                    "Because it uses BERT's encoder.",
                    "Because of emergent behaviour from scale and multilingual data.",
                ),
                correct=3,
                explanation=(
                    "Translation emerges as a capability that was not explicitly trained when "
                    "the model is large and has seen enough text in several languages. It is an "
                    "example of emergent behaviour, not magic."
                ),
            ),
        ),
    )
}
