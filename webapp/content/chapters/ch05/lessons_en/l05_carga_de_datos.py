"""Lesson 5 · Data loaders and batches."""

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
    slug="carga-de-datos",
    title="Data loaders and batches",
    summary=(
        "The loader turns continuous text into token windows and groups them into batches; "
        "stride, shuffling, and drop_last change what the model sees."
    ),
    minutes=9,
    objectives=(
        "Explain how input and target windows are built.",
        "Distinguish context length from stride and describe their effect.",
        "Choose drop_last and shuffle differently for training and validation.",
        "Interpret the shapes and batch counts of a small corpus.",
    ),
    blocks=(
        lead(
            "The model does not read a book from cover to cover like a person. The loader cuts "
            "the text into windows, groups them into batches, and delivers them in a controlled "
            "order. That preparation looks mechanical, but it decides how much information each "
            "step receives and how often the corpus repeats."
        ),
        h2("Windows and stride"),
        p(
            "A window is a sequence of <code>T</code> tokens. Its target is the same sequence "
            "shifted one position: if the window contains tokens 10 to 265, the target contains "
            "tokens 11 to 266. Every position in the window then teaches the model to predict "
            "the next one. The <strong>stride</strong> is how many tokens the start of one "
            "window advances to the next. In the book, context length and stride are both 256, "
            "so windows do not overlap. A smaller stride would produce more windows and more "
            "examples, at the cost of repeating text and increasing the cost per epoch."
        ),
        p(
            "Context length is not just a memory limit: it also defines how much context the "
            "model sees at each prediction. With 256 tokens, the model can condition the next "
            "token on the previous 256. Increasing length raises the cost of attention and "
            "activations. That is why the book's example reduces the GPT-2 configuration from "
            "1,024 to 256 tokens so training fits on a laptop. At the end of the chapter, when "
            "loading GPT-2 weights, it returns to 1,024."
        ),
        h2("The split and the batches"),
        p(
            "Before creating the loaders, the text is split into training and validation. The "
            "book uses 90 % for training and 10 % for validation. The short story <em>The "
            "Verdict</em> has 20,479 characters and 5,145 tokens; with 256-token windows and a "
            "batch size of 2, the training loader produces 9 batches and the validation loader "
            "1. These are small numbers because the goal is to run the example in minutes, not "
            "to reproduce the scale of a commercial LLM."
        ),
        table(
            ["Setting", "Training", "Validation", "Reason"],
            [
                ["batch_size", "2", "2", "Same tensor format in both"],
                ["max_length", "256", "256", "The model's context length"],
                ["stride", "256", "256", "Non-overlapping windows"],
                ["shuffle", "True", "False", "Mix in train; preserve order when evaluating"],
                ["drop_last", "True", "False", "Stable shapes in train; keep all val data"],
            ],
            caption="Data loader settings in chapter 5.",
            note=(
                "batch_size=2 is didactic. Production runs often use batches of 1,024 or "
                "more, depending on available memory."
            ),
        ),
        p(
            "<strong>Shuffling</strong> mixes the windows at the start of each epoch. Without "
            "it, a fixed order can introduce correlations between consecutive batches: the "
            "optimizer sees one chapter and then another, and the trajectory suffers. Validation "
            "is not shuffled, so evaluation is reproducible and comparable across epochs. "
            "<code>drop_last</code> is enabled in training to discard an incomplete final "
            "batch; every batch then has the same shape and no update is made with very few "
            "examples. In validation it is left <code>False</code> so that part of the corpus "
            "is not lost."
        ),
        callout(
            "note",
            "Text can also have variable lengths",
            "The book uses fixed-length windows for simplicity and efficiency. In practice, "
            "training with variable-length sequences can help generalise to more diverse "
            "inputs, provided the batch is padded or packed carefully. The decision affects "
            "throughput and quality; there is no single correct answer."
        ),
        h2("What can go wrong"),
        p(
            "A common mistake is building windows with misaligned targets: if the same "
            "sequence is used as input and target, the model learns to copy and the loss can "
            "fall deceptively. Another is mixing the validation set into training; the "
            "validation metric then stops measuring generalisation. It is also worth checking "
            "shapes: input and target should be <code>[B, T]</code>, and model logits "
            "<code>[B, T, V]</code>. A one-line check before training saves hours of debugging."
        ),
        p(
            "The loader's <code>num_workers</code> controls how many processes prepare batches "
            "in parallel. The example uses 0 because the corpus is tiny and creating processes "
            "would cost more than the useful work. On a large corpus, a few workers keep the GPU "
            "from waiting for data. The rule is to measure: if GPU utilisation drops between "
            "steps, the loader may be the bottleneck."
        ),
        check(
            "Why does the training loader use drop_last=True while the validation loader uses "
            "drop_last=False?",
            "In training we want every batch to have the same shape and avoid an update with a "
            "very small residual batch, so the incomplete final batch is discarded. In "
            "validation we want to evaluate the whole set, so that batch is kept even if it has "
            "fewer examples."
        ),
        keypoints(
            [
                "Each window holds a sequence and its target is the same sequence shifted.",
                "Stride decides the overlap between consecutive windows.",
                "The book splits the corpus 90 % for training and 10 % for validation.",
                "The Verdict has 20,479 characters and 5,145 tokens in the example.",
                "Shuffle is on for training and off for validation.",
                "drop_last=True avoids incomplete batches in training.",
                "Always check the [B, T] shapes of input and target.",
            ]
        ),
    ),
    key_points=(
        "Windows turn continuous text into input-target pairs.",
        "Stride controls overlap and the number of examples.",
        "Training and validation use different shuffle and drop_last settings.",
        "Input and target shapes must be [B, T].",
        "The loader must not leak validation data into training.",
        "num_workers is chosen by measuring batch preparation cost.",
    ),
)
