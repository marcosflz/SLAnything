"""Lesson 6 · Accuracy, precision, and recall."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=6,
    slug="metricas",
    title="Accuracy, precision, and recall",
    summary=(
        "The confusion matrix separates successes and errors by class; precision, recall, "
        "and F1 summarise different aspects of performance."
    ),
    minutes=11,
    objectives=(
        "Build a binary confusion matrix from predictions and labels.",
        "Compute accuracy, precision, recall, and F1.",
        "Choose the right metric according to the cost of each error.",
        "Interpret a 2×2 matrix with a numerical example.",
    ),
    blocks=(
        lead(
            "A classifier can look excellent by a single number and be useless for the real "
            "problem. Accuracy mixes all successes, but does not distinguish whether the "
            "model detects spam or simply gets legitimate messages right. To decide with "
            "judgement we must open the box: count true positives, false positives, false "
            "negatives, and true negatives."
        ),
        h2("The confusion matrix"),
        p(
            "In binary classification, every prediction falls into one of four cells. A "
            "<strong>true positive</strong> (TP) is spam that the model marks as spam. A "
            "<strong>false positive</strong> (FP) is a legitimate message marked as spam. A "
            "<strong>false negative</strong> (FN) is spam that slips through as legitimate. A "
            "<strong>true negative</strong> (TN) is a legitimate message classified as such. "
            "The 2×2 matrix orders these counts and makes the two kinds of error visible, "
            "which accuracy adds together without distinction."
        ),
        figure(
            "img/ch06/matriz-confusion.svg",
            "2×2 confusion matrix with true positives, false positives, false negatives, and true negatives, plus the formulas for accuracy, precision, recall, and F1.",
            "The confusion matrix separates successes and errors by class. The derived "
            "metrics answer different questions about the same count.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "Take an example with 200 messages: 40 detected spam (TP), 10 legitimate messages "
            "marked as spam (FP), 20 spam that go unnoticed (FN), and 130 legitimate messages "
            "correctly classified (TN). There are 60 real spam messages and 140 real ham "
            "messages. The model gets 170 out of 200 right. These figures are invented for the "
            "exercise, but the structure is the same as in the chapter."
        ),
        h2("Four ways to summarise"),
        p(
            "<strong>Accuracy</strong> is <code>(TP + TN) / total</code>: 170/200 = "
            "<strong>85.0%</strong>. <strong>Precision</strong> answers “of everything I "
            "marked as spam, how much really was spam?”: <code>TP / (TP + FP)</code> = "
            "40/50 = <strong>80.0%</strong>. <strong>Recall</strong> answers “of all real "
            "spam, how much did I detect?”: <code>TP / (TP + FN)</code> = 40/60 = "
            "<strong>66.7%</strong>. <strong>F1</strong> is the harmonic mean of precision and "
            "recall: <code>2 · P · R / (P + R)</code> ≈ <strong>72.7%</strong>. The harmonic "
            "mean penalises low values, so a high F1 requires both metrics to be reasonable."
        ),
        table(
            ["Metric", "Formula", "Example", "Question it answers"],
            [
                ["Accuracy", "(TP + TN) / total", "85.0%", "How many predictions did I get right overall?"],
                ["Precision", "TP / (TP + FP)", "80.0%", "How much of what I flagged as spam was spam?"],
                ["Recall", "TP / (TP + FN)", "66.7%", "How much of the real spam did I detect?"],
                ["F1", "2PR / (P + R)", "72.7%", "How do I balance precision and recall?"],
            ],
            caption="The four metrics over the matrix TP=40, FP=10, FN=20, TN=130.",
        ),
        py(
            """
labels = [1] * 60 + [0] * 140   # 60 spam and 140 ham
predictions = [1] * 40 + [0] * 20 + [1] * 10 + [0] * 130

tp = sum(1 for real, pred in zip(labels, predictions) if real == 1 and pred == 1)
fp = sum(1 for real, pred in zip(labels, predictions) if real == 0 and pred == 1)
fn = sum(1 for real, pred in zip(labels, predictions) if real == 1 and pred == 0)
tn = sum(1 for real, pred in zip(labels, predictions) if real == 0 and pred == 0)

total = len(labels)
accuracy = (tp + tn) / total
precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

print(f"TP={tp}  FP={fp}  FN={fn}  TN={tn}")
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1:        {f1:.3f}")
""",
            caption=(
                "Computing the confusion matrix and the four metrics without external "
                "libraries."
            ),
        ),
        callout(
            "note",
            "The metric depends on the cost",
            "If a false positive makes you lose an important message, prioritise precision. "
            "If a false negative lets a threat through, prioritise recall. F1 is a useful "
            "summary when both errors weigh similarly, but it does not replace a cost matrix "
            "when the consequences are very different."
        ),
        check(
            "With TP=40, FP=10, and FN=20, why is recall 66.7% rather than 80%?",
            "Because recall divides true positives by all real positives, which include false "
            "negatives: 40 / (40 + 20) = 0.667. The 80% figure is precision, which divides by "
            "positive predictions: 40 / (40 + 10).",
        ),
        keypoints(
            [
                "The confusion matrix separates TP, FP, FN, and TN.",
                "Accuracy can hide poor performance on the minority class.",
                "Precision measures the purity of positive predictions.",
                "Recall measures coverage of real positives.",
                "F1 combines precision and recall with a harmonic mean.",
                "The chosen metric should reflect the cost of each error type.",
            ]
        ),
    ),
    key_points=(
        "Accuracy, precision, and recall answer different questions.",
        "The confusion matrix is the basis of all binary metrics.",
        "Precision penalises false positives; recall penalises false negatives.",
        "F1 summarises the balance between precision and recall.",
        "The cost of error decides which metric to prioritise.",
    ),
)
