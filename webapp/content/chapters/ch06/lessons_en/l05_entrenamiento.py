"""Lesson 5 · Training without breaking the model."""

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
    number=5,
    slug="entrenamiento-clasificador",
    title="Training without breaking the model",
    summary=(
        "A low learning rate, few trainable layers, and validation-based stopping adapt "
        "the model without destroying what it already knew."
    ),
    minutes=11,
    objectives=(
        "Justify a low learning rate for finetuning.",
        "Interpret training and validation loss and accuracy curves.",
        "Apply early stopping and restore the best checkpoint.",
        "Recognise signs of overfitting and catastrophic forgetting.",
    ),
    blocks=(
        lead(
            "Finetuning is closer to tuning an instrument than to building a new one. The "
            "model already knows language; what we want is a limited correction. If we use a "
            "high learning rate or train every layer for too long, the classifier may improve "
            "on the training batches while losing general abilities we never needed to touch."
        ),
        h2("A fine adjustment, not a restart"),
        p(
            "The book trains with <strong>AdamW</strong>, a learning rate of <code>5e-5</code>, "
            "and weight decay of <code>0.1</code>. The batch size is 8 messages and the number "
            "of epochs is 5. The rate is low compared with many from-scratch trainings: the "
            "starting weights are already valuable, so they should move only a little at each "
            "step. Weight decay adds a penalty on large weights and acts as regularisation."
        ),
        p(
            "Only the new head, the last transformer block, and the final normalisation are "
            "updated. The rest stays frozen. This decision reduces the number of parameters "
            "receiving gradients, speeds up training, and limits the damage a noisy batch can "
            "do to early layers. The book takes about <strong>5.65 minutes</strong> on a "
            "MacBook Air with an M3 chip and less than half a minute on a V100 or A100 GPU. "
            "These are figures from the chapter, not a promise for any hardware."
        ),
        h2("Read the curves and stop in time"),
        p(
            "During training, the loss and accuracy of training and validation are recorded. "
            "At the end of the first epoch, the model is around 70% accuracy on training and "
            "72.5% on validation, with a loss that has already fallen sharply. By epoch 4 it "
            "reaches 100% on training and 97.5% on validation. The full evaluation, without "
            "limiting itself to five batches, gives <strong>97.21% on training, 97.32% on "
            "validation, and 95.67% on test</strong>."
        ),
        table(
            ["Epoch", "Train loss", "Val loss", "Train accuracy", "Val accuracy"],
            [
                ["1", "0.523", "0.557", "70.0%", "72.5%"],
                ["2", "0.409", "0.353", "82.5%", "85.0%"],
                ["3", "0.340", "0.306", "90.0%", "90.0%"],
                ["4", "0.222", "0.137", "100%", "97.5%"],
                ["5", "0.083", "0.074", "100%", "97.5%"],
            ],
            caption=(
                "Summary of the book's curves. Intermediate accuracies are estimated on five "
                "batches; the final evaluation uses the full dataset."
            ),
            note="Figures from Raschka, Build a Large Language Model (From Scratch), chapter 6.",
        ),
        p(
            "Five epochs is a sensible starting point for this dataset, not a universal "
            "constant. The right number depends on the amount of data, the difficulty of the "
            "task, and how quickly validation performance plateaus. If the validation curve "
            "is still falling, more epochs may help; if it turns upward while training loss "
            "keeps falling, the model is starting to memorise."
        ),
        p(
            "<strong>Early stopping</strong> means monitoring a validation metric and stopping "
            "training when it stops improving for several evaluations. It is not enough to "
            "keep the last state: save the checkpoint with the best validation loss or F1 and "
            "restore it at the end. In the book's example validation loss keeps falling until "
            "epoch 5, so there is no sign of overfitting; on another dataset, the curve could "
            "turn earlier."
        ),
        p(
            "Overfitting shows up as a growing gap: training loss falls while validation loss "
            "rises. <strong>Catastrophic forgetting</strong> is another risk: the model "
            "specialises so much that it loses general abilities. A low rate, fewer epochs, "
            "and frozen layers reduce both dangers, but do not eliminate them. If the "
            "classifier only sees messages from one domain, its effective vocabulary narrows."
        ),
        callout(
            "tip",
            "Keep the best, not the last",
            "A simple and robust practice: after each epoch, evaluate on validation and save "
            "a copy of the weights if the chosen metric improves. At the end, restore that "
            "copy. The number of epochs then becomes a maximum budget instead of a guess."
        ),
        check(
            "Training loss falls, but validation loss starts to rise. What is happening and "
            "what would you do?",
            "That is the typical sign of overfitting: the model memorises the training set and "
            "loses generalisation. I would stop training, restore the checkpoint with the best "
            "validation score, and try more regularisation, fewer epochs, or more data.",
        ),
        keypoints(
            [
                "Finetuning uses a low learning rate to preserve the pretrained weights.",
                "Freezing layers reduces compute and the risk of catastrophic forgetting.",
                "The book uses AdamW, lr=5e-5, weight_decay=0.1, batches of 8, and 5 epochs.",
                "Final accuracy in the book is 97.21% train, 97.32% val, and 95.67% test.",
                "Early stopping watches validation, not training.",
                "Restore the best checkpoint, not necessarily the last one.",
            ]
        ),
    ),
    key_points=(
        "Finetuning makes small changes to a model that already knows language.",
        "A low rate and frozen layers protect prior knowledge.",
        "Validation decides when to stop and which checkpoint to keep.",
        "A growing train–validation gap signals overfitting.",
        "The number of epochs is a budget, not a universal recipe.",
    ),
)
