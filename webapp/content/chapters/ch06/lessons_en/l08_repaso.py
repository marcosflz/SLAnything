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
    slug="repaso-clasificacion",
    title="Review and self-assessment",
    summary=(
        "Eight ideas to consolidate the chapter and a ten-question self-assessment on "
        "data, heads, training, metrics, and thresholds."
    ),
    minutes=10,
    objectives=(
        "Review the key ideas of classification finetuning.",
        "Connect data, model, loss, metrics, and the final decision.",
        "Spot common mistakes before moving to the next chapter.",
        "Check learning with the chapter self-assessment.",
    ),
    blocks=(
        lead(
            "You have completed chapter 6. The goal was not to memorise a list of formulas, "
            "but to understand a chain: data defines the problem, the head turns "
            "representations into classes, the loss guides adjustment, metrics reveal which "
            "kind of error the model makes, and the threshold decides what to do with that "
            "information. This review orders the chain."
        ),
        p(
            "If you had to explain the chapter in one sentence, it could be this: a generative "
            "model becomes a classifier when its output is replaced by a class layer and it is "
            "trained on labelled examples, but its real value depends on how errors are "
            "measured and turned into decisions. The previous lessons develop each link."
        ),
        h2("The eight ideas you take away"),
        bullets(
            [
                "<strong>Classifying means choosing among known labels.</strong> The model "
                "does not generate an open answer: it returns one score per class.",
                "<strong>The head replaces the vocabulary.</strong> A linear layer from 768 "
                "to 2 classes replaces the projection to 50,257 tokens.",
                "<strong>The last token summarises the sequence.</strong> Causal attention "
                "lets it see every previous token.",
                "<strong>Cross-entropy is the objective.</strong> It penalises low probability "
                "on the correct class and is differentiable.",
                "<strong>Imbalance is deceptive.</strong> High accuracy can coexist with zero "
                "recall; undersampling or class weights correct the bias.",
                "<strong>Finetuning is done carefully.</strong> Low rate, frozen layers, few "
                "epochs, and early stopping on validation.",
                "<strong>The confusion matrix rules.</strong> Precision, recall, and F1 "
                "describe different aspects of the same count.",
                "<strong>The threshold is a product decision.</strong> Moving it changes the "
                "balance between false positives and false negatives.",
            ],
            ordered=True,
        ),
        h2("Mistakes worth avoiding"),
        p(
            "The first is confusing prompting with finetuning. Adding examples to the context "
            "may improve a response, but it does not change weights or create a classification "
            "head. The second is celebrating high accuracy without looking at classes: on a "
            "dataset with few positives, always predicting the negative produces a misleading "
            "number. The third is contaminating test with duplicates or with decisions taken "
            "over the whole corpus. The fourth is choosing the threshold on test: that turns "
            "the final evaluation into another validation run and overestimates performance."
        ),
        p(
            "It is also worth remembering that the book's model is small: GPT-2 with 124 "
            "million parameters, a maximum length of 120 tokens, and 1,494 balanced messages. "
            "The results —97.21% on training, 97.32% on validation, and 95.67% on test— are "
            "excellent for that setup, but they do not transfer automatically to any domain. "
            "A medical, legal, or financial classifier needs its own data, validation, and "
            "error analysis. Treat every published result as a starting point, not as proof "
            "that the same recipe will work unchanged in your setting."
        ),
        p(
            "<strong>Before considering the chapter complete</strong>, check that you can "
            "answer these questions without looking at your notes:"
        ),
        bullets(
            [
                "Which layer is replaced, and how many outputs does it have in a binary problem?",
                "Why is the last token used rather than the first?",
                "What is the difference between validation and test?",
                "How would you detect data leakage in a split?",
                "When would you prefer high recall even if precision falls?",
                "Why can 95% accuracy be worse than 80% accuracy?",
            ]
        ),
        callout(
            "success",
            "Now it is your turn",
            "Open the <strong>chapter self-assessment</strong>: ten questions with an "
            "explanation for each answer. You need <strong>80%</strong> —eight out of ten— to "
            "consider the chapter complete. You can retake it as often as you like. If you "
            "miss a question, return to the corresponding lesson and rebuild the reasoning "
            "before trying again."
        ),
        check(
            "Explain in two sentences the full path from a new message to a spam decision.",
            "The message is tokenised and padded to the maximum length; the model produces "
            "logits for the last token and softmax turns them into probabilities. Then the "
            "spam probability is compared with a threshold chosen on validation, and the "
            "system decides whether to flag it, knowing the cost of each kind of error.",
        ),
        keypoints(
            [
                "Classification replaces open generation with predefined labels.",
                "The linear head and the last token are the model's key pieces.",
                "Loss and imbalance determine what the classifier learns.",
                "The confusion matrix and threshold connect metrics to decisions.",
                "Test is reserved for an honest final evaluation.",
                "The quiz requires 80% and can be retaken without penalty.",
            ]
        ),
    ),
    key_points=(
        "A classifier is a generative model with a class head.",
        "Data, loss, metrics, and threshold form a chain of decisions.",
        "Accuracy alone is not enough with imbalanced classes.",
        "The threshold is chosen on validation according to the cost of error.",
        "The chapter quiz requires 80% and can be retaken.",
    ),
    quiz_id="quiz-capitulo-6",
)
