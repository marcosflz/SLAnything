"""Lesson 2 · Data, labels, and splits."""

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
    number=2,
    slug="datos-etiquetados",
    title="Data, labels, and splits",
    summary=(
        "Classifier quality starts with the dataset: clear labels, balanced classes, and "
        "an honest separation between training, validation, and test."
    ),
    minutes=10,
    objectives=(
        "Describe the composition of the SMS Spam Collection used in the book.",
        "Explain the role of training, validation, and test sets.",
        "Detect data leakage before training.",
        "Justify class balancing and sequence formatting.",
    ),
    blocks=(
        lead(
            "A classifier learns from examples and labels. If labels are ambiguous, if the "
            "test set is contaminated by training data, or if one class appears almost every "
            "time, the model can score brilliantly on paper and fail exactly where it "
            "matters. Preparing the dataset is the first design decision in this chapter, "
            "not a preliminary chore."
        ),
        h2("A real dataset: SMS Spam Collection"),
        p(
            "The book works with text messages labelled as <em>ham</em> (not spam) or "
            "<em>spam</em>. The original dataset has <strong>5,572</strong> messages: "
            "<strong>4,825</strong> ham and <strong>747</strong> spam. That is, 86.6% ham and "
            "only 13.4% spam. This proportion reflects real life —we receive far more "
            "legitimate messages than fraudulent ones— and creates a problem: a model that "
            "always says “ham” would be right almost nine times out of ten."
        ),
        p(
            "To keep training manageable and educational, the book reduces the majority "
            "class. It keeps all 747 spam messages and randomly samples 747 ham messages. The "
            "result is <strong>1,494</strong> balanced messages, 747 of each class. The text "
            "labels are then converted to numbers: <code>ham → 0</code> and "
            "<code>spam → 1</code>. The change resembles turning words into identifiers, but "
            "here the label vocabulary has only two symbols. Other techniques exist for "
            "handling imbalance —class weights, resampling, synthetic data—; the book chooses "
            "undersampling for simplicity."
        ),
        h2("Training, validating, and testing"),
        p(
            "The balanced dataset is shuffled and split into three parts: <strong>70% for "
            "training, 10% for validation, and 20% for testing</strong>. With 1,494 examples, "
            "the code's split produces approximately 1,045, 149, and 300 messages. Each part "
            "has a different job. Training updates the weights; validation is used to make "
            "decisions —number of epochs, threshold, architecture—; test is reserved for a "
            "final estimate and should not guide successive adjustments."
        ),
        table(
            ["Split", "Proportion", "Approx. examples", "What it is for"],
            [
                ["Training", "70%", "1,045", "Update the weights"],
                ["Validation", "10%", "149", "Choose epochs, threshold, and settings"],
                ["Test", "20%", "300", "Estimate final performance once"],
            ],
            caption="Split of the balanced dataset of 1,494 messages.",
            note="Exact numbers depend on the code's rounding; the book uses 70/10/20.",
        ),
        h2("Data leakage and other traps"),
        p(
            "<strong>Data leakage</strong> happens when information from the test set sneaks "
            "into training. A typical case is splitting at random without removing "
            "duplicates: the same message, or a near-identical variant, appears in both train "
            "and test, and the model seems to memorise better than it generalises. Leakage "
            "also occurs if normalisation or feature selection uses the whole dataset before "
            "the split, or if messages from the same sender are spread across parts. The rule "
            "is simple: test data should be information the model has never seen."
        ),
        p(
            "Imbalance deserves a check per split, not only globally. After undersampling the "
            "classes are balanced, but a careless split could leave validation with very few "
            "spam messages. Stratify or, at the very least, verify the proportions. It is also "
            "worth checking text length: the longest message in the training set has "
            "<strong>120 tokens</strong>, well below the model's 1,024-token window. That is "
            "why the book pads shorter sequences with the <code>&lt;|endoftext|&gt;</code> "
            "token, whose id is <strong>50256</strong>, up to the training maximum length."
        ),
        callout(
            "warning",
            "Split before you look",
            "If you compute statistics, fit the tokenizer, or remove duplicates using the "
            "whole corpus and only then split, you have already contaminated the test set. "
            "Separation must happen before any data-dependent decision. In this chapter the "
            "tokenizer is fixed, but the principle still applies."
        ),
        check(
            "You have 10,000 messages and 90% are ham. Why is 90% accuracy not enough?",
            "Because a trivial classifier that always predicts “ham” would obtain the same "
            "score without detecting a single spam message. Global accuracy hides performance "
            "on the minority class; you need precision, recall, or a confusion matrix that "
            "separates the kinds of success and error.",
        ),
        keypoints(
            [
                "The original dataset has 5,572 messages: 4,825 ham and 747 spam.",
                "The book undersamples ham to 747 to balance the classes.",
                "Labels are encoded as 0 (ham) and 1 (spam).",
                "The split is 70% training, 10% validation, and 20% test.",
                "Leakage inflates metrics and is avoided by splitting before processing.",
                "Sequences are padded to 120 tokens with token id 50256.",
            ]
        ),
    ),
    key_points=(
        "Labels turn an open task into a classification problem.",
        "Imbalance demands looking beyond global accuracy.",
        "Training, validation, and test sets serve different purposes.",
        "Leakage is prevented by splitting before processing and removing duplicates.",
        "Padding lets variable-length sequences form batches.",
    ),
)
