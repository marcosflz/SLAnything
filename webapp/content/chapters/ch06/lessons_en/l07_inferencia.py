"""Lesson 7 · Inference and thresholds."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=7,
    slug="inferencia-clasificador",
    title="Inference and thresholds",
    summary=(
        "The model returns probabilities; the threshold turns them into decisions and "
        "determines which kind of error we accept."
    ),
    minutes=10,
    objectives=(
        "Turn logits into probabilities and apply a decision threshold.",
        "Explain how moving the threshold affects precision and recall.",
        "Relate calibration to threshold selection.",
        "Choose a threshold from the cost of errors.",
    ),
    blocks=(
        lead(
            "In production, a classifier does not hand over a magic label: it hands over a "
            "score. Someone —a person or a rule— decides from which value to act. That value "
            "is the threshold, and it is not a minor technical detail. Moving it changes how "
            "much spam is detected, how many legitimate messages are blocked, and ultimately "
            "the cost of the system."
        ),
        h2("A probability is not a decision"),
        p(
            "The classification head produces two logits. Softmax turns them into "
            "probabilities that sum to 1. The default rule is to choose the class with the "
            "highest probability, which is equivalent to a threshold of <strong>0.5</strong> "
            "in the binary case. If the spam probability exceeds 0.5, the message is marked "
            "as spam; otherwise it is allowed through. But 0.5 is not sacred: it is simply the "
            "point where two symmetric classes balance."
        ),
        p(
            "<strong>Calibration</strong> describes whether probabilities mean what they seem "
            "to mean. A model may say 0.9 with much lower real confidence, or vice versa. "
            "Transformers are often overconfident, especially after a short finetuning run. "
            "That is why the threshold is chosen empirically on validation, comparing success "
            "and error rates at different points, rather than copied from another problem. "
            "The test set must not be used for this search: if it is, it stops being an "
            "independent estimate."
        ),
        h2("Moving the threshold changes the error type"),
        p(
            "Suppose ten messages with their spam probability and true label. With a 0.5 "
            "threshold, 3 of the 5 spam messages are detected, but 2 ham messages are marked "
            "as spam: 60% precision, 60% recall. If we lower the threshold to 0.3, all 5 spam "
            "messages are detected and there are no false negatives, although 3 false "
            "positives appear: 62.5% precision, 100% recall. If we raise it to 0.7, only 2 "
            "spam messages are detected and 1 ham message slips through: 66.7% precision, 40% "
            "recall. The same model, three different policies."
        ),
        table(
            ["Threshold", "TP", "FP", "FN", "Precision", "Recall", "F1"],
            [
                ["0.30", "5", "3", "0", "62.5%", "100%", "76.9%"],
                ["0.50", "3", "2", "2", "60.0%", "60.0%", "60.0%"],
                ["0.70", "2", "1", "3", "66.7%", "40.0%", "50.0%"],
            ],
            caption="Effect of three thresholds on the same ten example messages.",
        ),
        py(
            """
examples = [
    (0.90, 1), (0.80, 1), (0.75, 0), (0.60, 1), (0.55, 0),
    (0.45, 1), (0.40, 1), (0.30, 0), (0.20, 0), (0.10, 0),
]

for threshold in (0.30, 0.50, 0.70):
    tp = fp = fn = 0
    for probability, real in examples:
        prediction = 1 if probability >= threshold else 0
        if prediction == 1 and real == 1:
            tp += 1
        elif prediction == 1 and real == 0:
            fp += 1
        elif prediction == 0 and real == 1:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    print(
        f"Threshold {threshold:.2f}: TP={tp} FP={fp} FN={fn} "
        f"precision={precision:.3f} recall={recall:.3f} F1={f1:.3f}"
    )
""",
            caption=(
                "Threshold sweep over ten messages. Lowering the threshold usually raises "
                "recall and lowers precision."
            ),
        ),
        callout(
            "warning",
            "Accuracy can stay the same",
            "When the threshold moves, some errors are exchanged: a false negative becomes a "
            "true positive and a true negative becomes a false positive. The total number of "
            "successes may not change, even though the kind of failure does. That is why you "
            "must inspect the full matrix and the cost, not only accuracy."
        ),
        check(
            "You lower the threshold from 0.5 to 0.3. What do you expect to happen to recall "
            "and precision?",
            "Recall rises because more messages exceed the threshold and more real spam is "
            "detected. Precision usually falls because more ham messages are also marked as "
            "spam. It is the classic trade-off: coverage is gained at the expense of false "
            "positives.",
        ),
        keypoints(
            [
                "The model produces probabilities; the threshold produces decisions.",
                "0.5 is a convention, not a universal truth.",
                "Lowering the threshold raises recall and usually lowers precision.",
                "Raising the threshold protects precision and lets more positives through.",
                "Calibration determines whether a probability deserves trust.",
                "The threshold is chosen on validation according to the cost of each error.",
            ]
        ),
    ),
    key_points=(
        "A threshold turns a score into a system action.",
        "The default threshold is 0.5, but it is not always optimal.",
        "Precision and recall move in opposite directions as the threshold changes.",
        "Calibration affects how probabilities should be interpreted.",
        "The threshold is selected on validation and evaluated once on test.",
    ),
)
