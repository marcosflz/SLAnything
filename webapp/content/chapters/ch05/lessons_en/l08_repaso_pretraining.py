"""Lesson 8 · Pretraining review."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=8,
    slug="repaso-pretraining",
    title="Pretraining review",
    summary=(
        "A map of the eight lessons, the most common mistakes, and a checklist for "
        "explaining pretraining without reciting it."
    ),
    minutes=10,
    objectives=(
        "Reconnect loss, training, data, evaluation, sampling, and cost.",
        "Spot common conceptual mistakes before the self-assessment.",
        "Explain the chapter with formulas and tensor shapes.",
        "Use the quiz as a diagnosis, not as a final grade.",
    ),
    blocks=(
        lead(
            "Chapter 5 looks like a collection of recipes: a loss function, a loop, a loader, "
            "an optimizer, a sampling strategy, and a calculator. In fact it is one story: a "
            "model learns to assign probability to the next token, and everything else exists "
            "to make that learning measurable, stable, and affordable. This review checks that "
            "the pieces fit together."
        ),
        h2("The map in one table"),
        table(
            ["Question", "Short answer", "Lesson"],
            [
                ["What is optimised?", "Mean next-token cross entropy.", "1 and 2"],
                ["How are weights updated?", "zero_grad → forward → backward → step, by epochs.", "3 and 4"],
                ["What does the model see?", "Token windows grouped into batches.", "5"],
                ["How do we know it generalises?", "Validation loss and text samples.", "6"],
                ["How much does it cost?", "FLOPs ≈ 6 · N · D; GPU-hours and memory.", "7"],
            ],
            caption="The five questions that summarise pretraining.",
            note="If you can answer them with a numerical example, you understand the structure.",
        ),
        h2("Five mistakes to avoid"),
        bullets(
            [
                "<strong>Confusing loss with accuracy.</strong> A low loss does not guarantee "
                "true or useful text; it measures assigned probability, not factual correctness.",
                "<strong>Comparing losses across tokenizers.</strong> The baseline scale depends "
                "on ln(V). Change the vocabulary and the starting point changes.",
                "<strong>Forgetting zero_grad.</strong> Gradients accumulate and the effective step "
                "becomes unpredictable.",
                "<strong>Evaluating with dropout active.</strong> Without model.eval(), the "
                "validation metric is unstable and hard to compare.",
                "<strong>Believing one sample is an evaluation.</strong> A lucky generation does "
                "not compensate for a validation curve that is getting worse.",
            ]
        ),
        p(
            "There is a sixth, subtler mistake: looking only at the final number. Training loss "
            "can fall to almost zero while validation loss rises. Without both curves, the result "
            "looks like success. With both, overfitting is visible. The same applies to "
            "perplexity: it is useful for tracking an experiment, but it does not summarise text "
            "quality on its own. Evaluation combines metrics, held-out sets, and critical reading "
            "of samples."
        ),
        h2("Checklist"),
        bullets(
            [
                "I can write the shapes of logits, targets, and the batch loss.",
                "I can compute −ln p and exp(L) for a small example.",
                "I can order the five operations of a training step.",
                "I can explain the difference between Adam and AdamW without notes.",
                "I know why the split is 90/10 and why drop_last is only used in training.",
                "I can tell greedy decoding apart from sampling with temperature and top-k.",
                "I can estimate 6 · N · D and turn it into GPU-hours with effective throughput.",
                "I remember that data, not only the model, limits quality.",
            ],
            ordered=True,
        ),
        callout(
            "tip",
            "How to use the self-assessment",
            "Take the quiz without looking at your notes. If you miss a question, return to the "
            "relevant lesson and explain the mistake out loud. A score of 80 % does not mean you "
            "have memorised everything: it means you can move on without carrying a basic "
            "confusion. Retake it a day later; short-term memory inflates the result."
        ),
        p(
            "The chapter ends with a trained base model and the option to load GPT-2 weights. "
            "That load is not a trick to skip the learning: it is a way to check that the "
            "implemented architecture matches a real model. If the weights fit and the generated "
            "text is coherent, the pieces are connected correctly. Before moving on, make sure "
            "you can explain each step to someone else without reading the code. Finetuning in "
            "the following chapters starts from there."
        ),
        check(
            "Explain in three sentences why validation loss is more informative than training "
            "loss when deciding whether the model has learned something general.",
            "Training loss is computed on the same examples that update the weights, so it can "
            "always fall through memorisation. Validation loss uses unseen text and estimates "
            "whether the model generalises. When both fall there is useful learning; when only "
            "training falls, there is overfitting."
        ),
        keypoints(
            [
                "Loss measures the correct token's probability, not the truth of the text.",
                "The training loop applies gradients in a specific order.",
                "Data loaders turn text into reproducible windows and batches.",
                "Validation catches overfitting; samples catch qualitative problems.",
                "Temperature and top-k control generation variety.",
                "6 · N · D and 16 bytes per parameter estimate compute and memory.",
                "The quiz is a diagnosis; if it fails, return to the lesson, not to chance.",
            ]
        ),
    ),
    key_points=(
        "Loss, perplexity, training, data, evaluation, and cost form a system.",
        "Validation is the compass for generalisation.",
        "Loop order and evaluation mode change the result.",
        "Decoding controls variety, not learned quality.",
        "Cost estimates are order-of-magnitude bounds.",
        "The self-assessment helps locate the lesson to review.",
    ),
    quiz_id="quiz-capitulo-5",
)
