"""Lesson 4 · Loss and class imbalance."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=4,
    slug="perdida-clasificacion",
    title="Loss and class imbalance",
    summary=(
        "Cross-entropy turns confidence into an optimisable error; imbalance forces us to "
        "weight classes or inspect per-class metrics."
    ),
    minutes=10,
    objectives=(
        "Compute cross-entropy for a binary prediction.",
        "Explain why accuracy is misleading with imbalanced classes.",
        "Compare undersampling and class weights as responses to imbalance.",
        "Relate the book's initial loss to model calibration.",
    ),
    blocks=(
        lead(
            "Accuracy counts successes, but it is not differentiable: we cannot compute its "
            "gradient to update weights. Training needs a smooth function that penalises "
            "wrong predictions and, above all, wrong predictions made with excessive "
            "confidence. That function is cross-entropy. With imbalanced classes, we must "
            "also prevent the model from learning to always pick the majority class."
        ),
        h2("The loss we can actually optimise"),
        p(
            "For binary classification, <strong>cross-entropy</strong> is "
            "<code>-log(p_true)</code>, where <code>p_true</code> is the probability the "
            "model assigns to the correct class. If the model gives 90% to the right label, "
            "the loss is <code>-ln(0.9) ≈ 0.105</code>. If it gives 50%, the loss rises to "
            "<code>0.693</code>, the value of a fair coin. If it gives only 10%, the loss "
            "reaches <code>2.303</code>. The curve grows very quickly when the correct answer "
            "receives little probability: that is the penalty for miscalibrated confidence."
        ),
        table(
            ["Probability of the correct class", "Cross-entropy", "Reading"],
            [
                ["0.90", "0.105", "Confident and correct"],
                ["0.50", "0.693", "A fair-coin level of doubt"],
                ["0.10", "2.303", "Confident and wrong"],
            ],
            caption="Values of -ln(p) for three confidence levels.",
        ),
        p(
            "Over a batch, the loss is the average of the individual values. The book "
            "computes the initial loss before any adjustment, estimated over five batches: "
            "3.095 on training, 2.583 on validation, and 2.322 on test. These values are well above 0.693 because the "
            "model, with its newly adapted head, spreads its probabilities poorly. The number "
            "does not measure “how much it knows” in the abstract: it measures how much the "
            "function penalises the current answers. After five epochs, training loss falls "
            "to 0.083 and validation loss to 0.074."
        ),
        h2("When 95% means nothing"),
        p(
            "Imagine a dataset with 95 ham messages and 5 spam messages. A model that always "
            "says “ham” gets 95 out of 100 right and reports 95% accuracy. Yet its spam "
            "recall is zero: it detects none of the five cases that matter. Global accuracy "
            "rewards the majority class and hides the failure. The same effect appears in the "
            "book's original dataset, where 86.6% of messages are ham: a trivial classifier "
            "would exceed 86% without learning anything useful."
        ),
        p(
            "There are two families of solutions. The first changes the data: the book "
            "undersamples the majority class until it matches 747 examples per class. The "
            "second changes the loss: a larger <strong>class weight</strong> is assigned to "
            "the minority class. A common formula is <code>w_c = N / (2 · N_c)</code>, which "
            "normalises the weights so their mean is 1. With 5% positives, the positive "
            "weight would be 10 and the negative weight 0.526: the model would have to work "
            "about 19 times harder to get a spam message right than a ham message. In the "
            "book's dataset, without undersampling, the spam weight would be approximately "
            "3.7 versus 0.58 for ham."
        ),
        p(
            "The weighted version is implemented by multiplying each example's term by its "
            "class weight before averaging the batch. A spam mistake then contributes more "
            "to the gradient than a ham mistake, so the model cannot get away with always "
            "predicting the frequent class. The price is that the loss is no longer a direct "
            "estimate of accuracy: it is an objective designed to make learning pay "
            "attention to what matters."
        ),
        callout(
            "warning",
            "Changing the loss does not change reality",
            "Weighting classes helps the model pay attention to the minority, but it does not "
            "invent information. If spam messages are ambiguous or mislabelled, a high weight "
            "only amplifies the noise. Before touching the loss, review labels, duplicates, "
            "and overlap between splits."
        ),
        check(
            "A model has 95% accuracy and 0% spam recall. What is happening and which metric "
            "would you inspect next?",
            "It is always predicting the majority class. The high accuracy reflects the "
            "imbalance, not the ability to detect spam. I would inspect the confusion matrix "
            "and the precision/recall of the positive class; probably also F1 and the cost of "
            "false negatives.",
        ),
        keypoints(
            [
                "Cross-entropy is -log of the probability assigned to the correct class.",
                "It strongly penalises wrong but confident predictions.",
                "The average loss over a batch is the objective being minimised.",
                "With imbalance, high accuracy can hide zero recall.",
                "Undersampling balances data; class weights balance the loss.",
                "The book's initial loss is above 2.3 because the new head is poorly calibrated.",
            ]
        ),
    ),
    key_points=(
        "Cross-entropy replaces accuracy because it is differentiable.",
        "Confident mistakes are penalised non-linearly.",
        "Global accuracy is not enough when classes are imbalanced.",
        "Undersampling and class weighting are complementary strategies.",
        "Initial loss measures calibration, not domain knowledge.",
    ),
)
