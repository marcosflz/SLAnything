"""Lesson 4 · AdamW and the learning rate."""

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
    slug="optimizador-y-lr",
    title="AdamW and the learning rate",
    summary=(
        "AdamW adapts each weight's step and separates regularisation; the learning rate "
        "decides how far the model moves on each update."
    ),
    minutes=10,
    objectives=(
        "Explain what Adam's moments store.",
        "Distinguish AdamW's weight decay from classic Adam's.",
        "Relate the learning rate to training stability.",
        "Describe what warmup and cosine decay are for.",
    ),
    blocks=(
        lead(
            "Choosing an optimizer is not a search for a magic formula. It is deciding how to "
            "distribute the update step among parameters with very different gradients. "
            "<strong>AdamW</strong> handles the adaptive part and regularisation; the "
            "<strong>learning rate</strong> sets the scale of the move. Together they explain "
            "much of why a training run converges or goes out of control."
        ),
        h2("Adam in two moments"),
        p(
            "Adam keeps two estimates per weight: the first moment, a moving average of the "
            "gradient, and the second, a moving average of the squared gradient. The first "
            "gives direction; the second measures recent magnitude and lets the step be "
            "divided by a scale adapted to each parameter. The usual coefficients are 0.9 for "
            "the first moment and 0.999 for the second. At the start the averages are biased "
            "towards zero, so Adam applies a bias correction before using them. The result is "
            "a step that behaves similarly for parameters with large and small gradients."
        ),
        p(
            "That adaptation speeds up convergence, but it can also amplify noise when the "
            "second moment is very small. Frameworks therefore add a small stability constant, "
            "<code>eps</code>, to the denominator. In a transformer, embeddings, attention "
            "matrices, and feed-forward layers receive gradients of very different magnitudes; "
            "Adam partially balances those differences and prevents some weights from moving "
            "much more than others merely because of their gradient scale."
        ),
        h2("Why AdamW"),
        p(
            "Weight decay is a regularisation that pushes weights towards zero to limit their "
            "size. In classic Adam, that term is added to the gradient and becomes mixed with "
            "the adaptive moments: the effect of regularisation depends on gradient scale. "
            "<strong>AdamW</strong> applies it in a decoupled way, directly to the weight, "
            "after the adaptive step. The decay keeps its meaning and does not interfere with "
            "the moment estimates. This is the variant the book uses to pretrain the small GPT."
        ),
        table(
            ["Hyperparameter", "Book value", "What it controls"],
            [
                ["Optimizer", "AdamW", "Adaptive steps with decoupled decay"],
                ["Learning rate", "0.0004", "Initial step size"],
                ["Weight decay", "0.1", "Pressure towards small weights"],
                ["Epochs", "10", "Complete passes over the corpus"],
                ["Evaluation", "every 5 steps", "Frequency of metrics"],
            ],
            caption="Configuration of the chapter 5 pretraining example.",
            note=(
                "These are values for a didactic experiment, not a universal recipe. Batch "
                "size, architecture, and corpus change the optimum."
            ),
        ),
        h2("Tuning the learning rate"),
        p(
            "The learning rate multiplies the optimizer's step. If it is too high, the loss "
            "oscillates, explodes, or becomes <code>NaN</code>: the model jumps outside the "
            "region where the local gradient approximation is valid. If it is too low, "
            "training proceeds but needs many more iterations and may settle in a poor area. "
            "A rate of 0.0004 is reasonable for the book's 124 M model with small batches; it "
            "does not transfer unchanged to a larger model or another batch size."
        ),
        p(
            "Two common techniques improve the trajectory. <strong>Warmup</strong> starts "
            "with a very small rate and raises it during the first steps, so Adam's moments "
            "stabilise before large moves. <strong>Cosine decay</strong> then lowers the rate "
            "along a smooth curve towards zero, so the end of training makes fine adjustments. "
            "Sometimes <strong>gradient clipping</strong> is added: if the gradient norm "
            "exceeds a threshold, it is rescaled to avoid disproportionate updates. The book "
            "presents these variants in appendix D; the chapter's basic loop uses a constant "
            "rate."
        ),
        callout(
            "tip",
            "A rate is not an eternal constant",
            "If the loss becomes noisy, try lowering it or adding warmup. If it falls very "
            "slowly and the gradient is stable, try raising it carefully. Log the gradient "
            "norm and the loss per step: without those curves, changing hyperparameters is "
            "guessing. A good starting point is to reproduce the book's configuration first "
            "and change one variable at a time."
        ),
        check(
            "What does AdamW's decoupled weight decay provide compared with adding it to the "
            "gradient?",
            "It keeps regularisation separate from the adaptive moments. The weight shrinks by "
            "its own factor, independent of gradient scale, while Adam's step keeps using the "
            "moments. That makes the effect of weight decay more predictable and prevents it "
            "from being amplified or diluted per parameter."
        ),
        keypoints(
            [
                "Adam estimates gradient mean and variance to adapt the step per weight.",
                "Bias correction prevents the initial moments from being too small.",
                "AdamW applies weight decay decoupled from the gradient.",
                "The book uses AdamW with lr 0.0004, weight decay 0.1, and ten epochs.",
                "Too high a rate destabilises; too low a rate slows training down.",
                "Warmup, cosine decay, and gradient clipping stabilise training.",
            ]
        ),
    ),
    key_points=(
        "Adam adapts the step with moving averages of the gradient and its square.",
        "AdamW separates weight decay from the adaptive update.",
        "The learning rate controls step size and stability.",
        "Warmup smooths the start; cosine decay refines the end.",
        "Gradient clipping limits disproportionate updates.",
        "The book's hyperparameters are a starting point, not a universal recipe.",
    ),
)
