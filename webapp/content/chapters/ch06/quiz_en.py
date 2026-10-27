"""Chapter 6 self-assessment in English."""

from webapp.content.schema import Question, Quiz

QUIZZES_EN: dict[str, Quiz] = {
    "quiz-capitulo-6": Quiz(
        id="quiz-capitulo-6",
        title="Self-assessment · Chapter 6",
        description=(
            "Ten questions on classification finetuning: data, heads, loss, training, "
            "metrics, and thresholds. You need 80% to pass the chapter."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt=(
                    "What distinguishes classification finetuning from instruction "
                    "finetuning?"
                ),
                options=(
                    "Classification can only predict the classes it saw and usually needs "
                    "less data.",
                    "Classification does not modify the model's weights.",
                    "Instruction finetuning requires changing the tokenizer.",
                    "Instruction finetuning only works for binary tasks.",
                ),
                correct=0,
                explanation=(
                    "The classifier replaces the output with a layer containing the problem's "
                    "labels and is limited to those classes. Instruction finetuning is more "
                    "flexible but needs more data and compute. Both modify weights."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "You duplicate messages and split them randomly between training and "
                    "test. What problem do you introduce?"
                ),
                options=(
                    "The test set becomes too small.",
                    "Data leakage: test contains examples seen during training.",
                    "The tokenizer changes size.",
                    "The model loses its classification head.",
                ),
                correct=1,
                explanation=(
                    "If a message or a near-identical variant appears in both splits, the "
                    "model may memorise it and evaluation stops measuring generalisation. "
                    "Remove duplicates before splitting."
                ),
            ),
            Question(
                id="q3",
                prompt=(
                    "Why is the last token used to classify a sequence with GPT?"
                ),
                options=(
                    "Because it is the shortest token in the sequence.",
                    "Because it receives a larger learning rate.",
                    "Because causal attention lets it see every previous token.",
                    "Because it avoids applying softmax.",
                ),
                correct=2,
                explanation=(
                    "With a causal mask, each token only attends to previous ones. The last "
                    "token is the only one that has been able to accumulate information from "
                    "the whole sequence, so its representation summarises the message best."
                ),
            ),
            Question(
                id="q4",
                prompt=(
                    "The model assigns probability 0.1 to the correct class. What is the "
                    "cross-entropy approximately?"
                ),
                options=("0.105", "0.693", "2.303", "10.0"),
                correct=2,
                explanation=(
                    "Binary cross-entropy is -ln(p). For p = 0.1, -ln(0.1) ≈ 2.303. The value "
                    "0.105 corresponds to p = 0.9 and 0.693 to p = 0.5."
                ),
            ),
            Question(
                id="q5",
                prompt=(
                    "A dataset has 95 ham messages and 5 spam messages. A model that always "
                    "predicts ham gets 95% accuracy. Which conclusion is correct?"
                ),
                options=(
                    "The model has learned to detect spam.",
                    "Accuracy hides that spam recall is zero.",
                    "The threshold is too low.",
                    "Cross-entropy will be negative.",
                ),
                correct=1,
                explanation=(
                    "The model gets the majority class right and misses every positive. "
                    "Global accuracy does not reveal that failure; inspect the confusion "
                    "matrix and spam recall."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "Why does finetuning use a low learning rate and freeze most of the "
                    "model?"
                ),
                options=(
                    "To increase the vocabulary during training.",
                    "To preserve prior knowledge and reduce the risk of forgetting.",
                    "To avoid having to compute the loss.",
                    "To make the test set larger than the training set.",
                ),
                correct=1,
                explanation=(
                    "Pretrained weights already contain useful language knowledge. Moving "
                    "them little and adjusting only the last layers reduces cost and limits "
                    "catastrophic forgetting, without preventing the head from learning."
                ),
            ),
            Question(
                id="q7",
                prompt=(
                    "With TP=40, FP=10, FN=20, and TN=130, what is spam recall?"
                ),
                options=("0.80", "0.667", "0.85", "0.727"),
                correct=1,
                explanation=(
                    "Recall = TP / (TP + FN) = 40 / (40 + 20) = 0.667. The 0.80 is precision, "
                    "0.85 is accuracy, and 0.727 is F1."
                ),
            ),
            Question(
                id="q8",
                prompt="What does precision measure in a binary classifier?",
                options=(
                    "Of all real positives, how many were detected.",
                    "Of all positive predictions, how many were truly positive.",
                    "The overall percentage of correct predictions.",
                    "The harmonic mean of accuracy and recall.",
                ),
                correct=1,
                explanation=(
                    "Precision = TP / (TP + FP). It answers how much of what the model marked "
                    "as spam really was spam. Recall looks at real positives, and accuracy "
                    "mixes all cells."
                ),
            ),
            Question(
                id="q9",
                prompt=(
                    "If you lower the decision threshold from 0.5 to 0.3, what is the most "
                    "likely effect?"
                ),
                options=(
                    "Recall rises and precision usually falls.",
                    "Recall and precision both rise.",
                    "Recall and precision both fall.",
                    "No metric changes because the model is the same.",
                ),
                correct=0,
                explanation=(
                    "A lower threshold marks more messages as spam: more real positives are "
                    "detected (recall rises), but more false positives also enter (precision "
                    "usually falls). It is a trade-off, not a free improvement."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "What is the correct order of the chapter's classification workflow?"
                ),
                options=(
                    "Replace the head → prepare data → choose threshold → load weights.",
                    "Prepare and split data → load the pretrained model → replace the head → "
                    "train → evaluate and choose the threshold on validation.",
                    "Train from scratch → tokenize → split → apply softmax.",
                    "Choose the threshold on test → train → split the data → save.",
                ),
                correct=1,
                explanation=(
                    "First prepare and separate the data; then reuse the pretrained model, "
                    "replace its output with the class head, and adjust the chosen layers. "
                    "Evaluation and threshold are decided on validation, and test is reserved "
                    "for the end."
                ),
            ),
        ),
    )
}

# Alias compatible con el registro global del curso.
QUIZZES = QUIZZES_EN
