"""Chapter 7 self-assessment (EN)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-7": Quiz(
        id="quiz-capitulo-7",
        title="Self-assessment · Chapter 7",
        description=(
            "Ten questions on instruction tuning, templates, masks, evaluation, and "
            "preferences. You need 80% to pass the chapter; you can retake it."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="What distinguishes supervised instruction tuning from pretraining?",
                options=(
                    "SFT uses unlabelled text, while pretraining uses instruction-response pairs.",
                    "SFT uses instruction-response pairs; pretraining predicts the next token on general text.",
                    "SFT changes the transformer architecture.",
                    "Pretraining only works with small models.",
                ),
                correct=1,
                explanation=(
                    "Both optimise next-token prediction. The difference is the data: SFT uses "
                    "requests with desired responses and a mask that decides which tokens "
                    "contribute to the loss."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "A record has “instruction” and “output”, but “input” is empty. What "
                    "should a well-built Alpaca template do?"
                ),
                options=(
                    "Include “### Input:” followed by a blank line.",
                    "Omit the “### Input:” section.",
                    "Copy the instruction into “### Input:”.",
                    "Discard the record as incomplete.",
                ),
                correct=1,
                explanation=(
                    "The input section is optional. Including it empty adds noise and teaches a "
                    "pattern that carries no information; the book omits it when the field has "
                    "no content."
                ),
            ),
            Question(
                id="q3",
                prompt="Why should the same chat template be used for training and inference?",
                options=(
                    "Because it reduces the model's memory use.",
                    "Because the template changes the weights automatically.",
                    "Because the model learns markers and format distributions; changing them creates a mismatch.",
                    "Because templates only work once.",
                ),
                correct=2,
                explanation=(
                    "The model does not see roles, it sees tokens. If production uses markers, "
                    "spaces, or turns different from training, the sequence changes and the "
                    "response may degrade."
                ),
            ),
            Question(
                id="q4",
                prompt="What exactly does the value -100 do in the target tensor?",
                options=(
                    "Cross-entropy ignores it by default, so it does not contribute to the loss.",
                    "It removes the token from the model's vocabulary.",
                    "It automatically turns it into an end-of-sequence token.",
                    "It doubles the loss of the previous position.",
                ),
                correct=0,
                explanation=(
                    "-100 is the default ignore_index of cross_entropy in PyTorch. Positions "
                    "marked this way are excluded from the loss average, which allows padding "
                    "to be ignored."
                ),
            ),
            Question(
                id="q5",
                prompt=(
                    "In a batch, one response ends before the longest one. After shifting the "
                    "targets, how are the padding positions handled?"
                ),
                options=(
                    "All are kept as EOS to teach the model to stop.",
                    "All are replaced with 0.",
                    "They are removed from the batch and the sequence is shortened.",
                    "The first EOS is kept and the rest are marked -100.",
                ),
                correct=3,
                explanation=(
                    "The first EOS is the end-of-response signal and is kept. Later EOS tokens "
                    "are padding and are replaced with -100 so they do not contribute to the "
                    "loss."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "Training loss falls to 0.30, validation loss stays at 0.657 and stops "
                    "improving. What is the most reasonable reading?"
                ),
                options=(
                    "The model has learned perfectly and needs five more epochs.",
                    "Validation loss is irrelevant; only training loss matters.",
                    "Overfitting is possible; stop or review the data and responses.",
                    "Double the learning rate to unlock further progress.",
                ),
                correct=2,
                explanation=(
                    "A growing gap between training and validation is a sign of overfitting. "
                    "Before training further, read responses and review whether the data are "
                    "representative."
                ),
            ),
            Question(
                id="q7",
                prompt="What does an LLM used as a judge contribute to evaluation?",
                options=(
                    "A scalable quality estimate under a rubric, which must be calibrated.",
                    "An exact measure of factual truth.",
                    "A guarantee that the evaluated model is safe.",
                    "A way to avoid any human review.",
                ),
                correct=0,
                explanation=(
                    "The judge approximates human judgement and can score many cases, but it "
                    "inherits biases, is not deterministic, and needs calibration against a "
                    "sample reviewed by people."
                ),
            ),
            Question(
                id="q8",
                prompt="A judge scores three responses 90, 60, and 30. What conclusion is correct?",
                options=(
                    "The 60 average proves the model is mediocre at every task.",
                    "It is a descriptive signal about those three responses; a larger sample and context are needed.",
                    "The 30 response is necessarily false and the 90 one necessarily true.",
                    "The judge failed because the scores are not identical.",
                ),
                correct=1,
                explanation=(
                    "Three scores describe three cases. Estimating overall quality requires a "
                    "representative set, a stable rubric, and preferably human validation."
                ),
            ),
            Question(
                id="q9",
                prompt="What does DPO use that does not require a separate reward model?",
                options=(
                    "An unlabelled text corpus.",
                    "An exhaustive search for correct answers.",
                    "A spam classifier.",
                    "Preferred and rejected response pairs to optimise the model directly.",
                ),
                correct=3,
                explanation=(
                    "DPO optimises the model on comparisons between a preferred and a rejected "
                    "response, keeping a reference. Classic RLHF trains a reward model and then "
                    "optimises the policy with reinforcement learning."
                ),
            ),
            Question(
                id="q10",
                prompt="What is the correct order of the instruction-tuning pipeline?",
                options=(
                    "Format and tokenise → build batches and mask → train → generate and evaluate.",
                    "Train → format → evaluate → tokenise.",
                    "Evaluate → train → tokenise → mask.",
                    "Tokenise → evaluate → train → format.",
                ),
                correct=0,
                explanation=(
                    "First prepare the pairs and the template, then build batches with targets "
                    "and a mask, then train, and finally generate responses on the test set for "
                    "evaluation."
                ),
            ),
        ),
    ),
}
