"""Lesson 5 · Training on instructions."""

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
    slug="entrenamiento-instrucciones",
    title="Training on instructions",
    summary=(
        "Instruction tuning reuses the pretraining loop with batches, a low learning rate, "
        "and few epochs. The loss guides, but generated answers decide."
    ),
    minutes=11,
    objectives=(
        "Describe the configuration used in the book's experiment.",
        "Interpret training and validation loss curves.",
        "Spot overfitting and decide when to stop.",
        "Relate model size, batch size, and hardware to cost.",
    ),
    blocks=(
        lead(
            "With the dataset formatted and the batches masked, training looks a lot like "
            "pretraining: a loop, an optimiser, and a next-token loss. What changes is scale "
            "and caution. Instruction tuning usually needs few epochs, a low learning rate, "
            "and close attention to generated answers, not only to the loss number."
        ),
        p(
            "The book starts from medium GPT-2, with 355 million parameters, and tunes it for "
            "<strong>two epochs</strong> with AdamW, a learning rate of <strong>5 × 10⁻⁵</strong>, "
            "and weight decay 0.1. The batch size is 8 and the maximum length is limited to "
            "1024 tokens. Evaluation runs every five steps on five batches, and a validation "
            "response is generated for inspection. These values come from the book's "
            "experiment; they are not a universal recipe, but they are a reasonable starting "
            "point for a model of this size."
        ),
        h2("What to watch during training"),
        p(
            "Before training, the book measures the initial loss: about 3.83 on training and "
            "3.76 on validation. After two epochs, training loss falls to 0.300 and validation "
            "loss to 0.657. The fast initial drop indicates that the model is picking up the "
            "format and the task; the later gap between the curves is the signal to watch. A "
            "very low training loss with a validation loss that stops improving suggests that "
            "the model is memorising examples instead of generalising."
        ),
        table(
            ["Model", "Device", "Time for 2 epochs"],
            [
                ["GPT-2 medium (355 M)", "Apple M3 CPU", "15.78 min"],
                ["GPT-2 medium (355 M)", "NVIDIA L4 GPU", "1.83 min"],
                ["GPT-2 medium (355 M)", "NVIDIA A100 GPU", "0.86 min"],
                ["GPT-2 small (124 M)", "Apple M3 CPU", "5.74 min"],
                ["GPT-2 small (124 M)", "NVIDIA L4 GPU", "0.69 min"],
                ["GPT-2 small (124 M)", "NVIDIA A100 GPU", "0.39 min"],
            ],
            caption="Reference instruction-tuning times from the book.",
            note="These are measurements from one environment; actual time depends on hardware, sequence length, and software version.",
        ),
        p(
            "Loss is a guide, not the verdict. During training, generate responses to the same "
            "validation instruction and read them. In the book, by the end of the first epoch "
            "the model already produces a correct passive sentence; by the end of the second, "
            "the answer is cleaner and ends with the end-of-sequence token. That qualitative "
            "inspection catches problems hidden by an average: truncated answers, "
            "repetitions, incomplete formatting, or language switches. If you only watch the "
            "number, you may celebrate a model that has learned the dataset's style without "
            "solving the task."
        ),
        h2("Overfitting, epochs, and hardware"),
        p(
            "The book stops at two epochs because a third brings no clear improvement and may "
            "increase overfitting. In general, a small dataset and a relatively large model "
            "are a memorisation-prone combination. The defence is twofold: hold out "
            "validation and test data, and stop when validation stops improving. Reviewing "
            "data diversity also helps: if every response is long, the model learns to be "
            "long; if every answer starts with the same phrase, it repeats the phrase."
        ),
        p(
            "The learning rate has a visible effect. Too high and the loss may oscillate or "
            "diverge; too low and training takes longer, possibly leaving the model "
            "half-trained. Batch size changes memory and stability: if it does not fit, reduce "
            "the batch or the maximum length and compensate with gradient accumulation. The "
            "smaller 124-million model is an alternative when the hardware cannot handle the "
            "medium one, but the book warns that its capacity is more limited. The choice is a "
            "trade-off between quality, time, and resources, not a matter of pride."
        ),
        callout(
            "warning",
            "A low loss is not a good answer",
            "Loss measures the probability assigned to reference tokens, not the usefulness "
            "of the response. A model can achieve an excellent loss while producing "
            "repetitive or incorrect answers. Always combine the curve with generation, "
            "automated evaluation, and human review of a sample.",
        ),
        check(
            "Training loss keeps falling, but validation loss has plateaued. What would you do?",
            "Stop training or reduce the number of epochs, review a sample of generated "
            "responses, and check whether the validation set represents real requests. "
            "Continuing to lower training loss does not improve generalisation.",
        ),
        keypoints(
            [
                "The book tunes medium GPT-2 for two epochs with lr 5e-5 and batch 8.",
                "Initial loss is about 3.8; final loss is 0.300 train and 0.657 validation.",
                "The gap between curves signals overfitting, not a quality measure.",
                "Reading generated answers catches failures that loss does not show.",
                "Fewer epochs and early validation protect a small dataset.",
                "Hardware changes the time, not the experimental design.",
            ]
        ),
    ),
    key_points=(
        "Tuning reuses the pretraining loop with a low learning rate.",
        "Two epochs suffice in the book's experiment; more may overfit.",
        "Validation loss and generated answers are read together.",
        "Batch size and maximum length determine memory cost.",
    ),
)
