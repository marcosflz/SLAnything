"""Lesson 6 · Evaluation and generation."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
)

LESSON = Lesson(
    number=6,
    slug="evaluacion-y-generacion",
    title="Evaluation and generation",
    summary=(
        "Validation loss catches overfitting; decoding strategies control how much variety "
        "the text produced by the model has."
    ),
    minutes=11,
    objectives=(
        "Compare training loss with validation loss.",
        "Recognise overfitting and propose ways to reduce it.",
        "Distinguish numerical evaluation from qualitative inspection.",
        "Explain greedy decoding, temperature, and top-k.",
    ),
    blocks=(
        lead(
            "A model can improve its training loss while getting worse on new text. Good "
            "evaluation needs two views: a validation curve that cannot fool itself and a "
            "generated sample that can be read. The first catches overfitting; the second "
            "reveals what kind of text the model produces."
        ),
        h2("Two curves, one decision"),
        p(
            "Training loss is computed on the same data that updates the weights. Validation "
            "loss is computed on text the model has not seen. At first both fall: the model "
            "learns useful regularities. When training loss keeps falling but validation loss "
            "stalls or rises, the model starts memorising details of the corpus. In the book's "
            "example, after ten epochs training loss is 0.391 and validation loss is 6.452. "
            "The gap is huge because the corpus is tiny and the model has seen it many times."
        ),
        p(
            "Evaluation uses <code>model.eval()</code> to disable dropout and "
            "<code>torch.no_grad()</code> to avoid building gradients. You can also limit the "
            "number of evaluated batches with <code>num_batches</code>, which speeds up "
            "monitoring during training. That partial estimate is noisy but sufficient to "
            "detect trends. At the end, evaluate every batch in the validation set."
        ),
        p(
            "In the book, validation loss stalls from the second epoch onwards. That does not "
            "mean the model is useless: it means it no longer generalises better with more "
            "passes over that corpus. Validation perplexity, exp(6.452) ≈ 633, is still high, "
            "but far below the initial value. The practical conclusion is that data size and "
            "variety matter as much as the number of epochs."
        ),
        h2("What to do when validation stalls"),
        p(
            "The first measure is more data or more variety. The second is reducing effective "
            "capacity: fewer parameters, more dropout, or stronger weight decay. You can also "
            "apply <em>early stopping</em>: keep the checkpoint with the best validation loss "
            "and stop when it has not improved for several evaluations. On large corpora one "
            "epoch may be enough; on a small one, ten epochs almost guarantee memorisation."
        ),
        p(
            "Do not choose hyperparameters by looking at the validation set again and again. "
            "If you tune on it, it becomes contaminated and stops being an honest estimate. "
            "For important decisions, hold out a third test set and use it once at the end. "
            "Validation guides decisions during development; test reports the final result."
        ),
        h2("Generating is not evaluating"),
        p(
            "Loss measures the probability of the correct token, but it does not say whether "
            "generated text is useful, original, or safe. To generate, the model starts from a "
            "context, picks a token, appends it, and repeats. The simplest strategy is "
            "<strong>greedy decoding</strong>: always choose the most likely token with "
            "<code>argmax</code>. It is deterministic and tends to produce repetitive text "
            "because it never explores alternatives. The model trained on <em>The Verdict</em> "
            "ends up copying passages verbatim when greedy decoding is used."
        ),
        p(
            "<strong>Temperature</strong> divides the logits before softmax. Below 1 the "
            "distribution sharpens and the model becomes conservative; above 1 it flattens and "
            "less likely options appear. <strong>Top-k</strong> trims the tail: it keeps the "
            "<code>k</code> largest logits, sets the rest to negative infinity, and "
            "renormalises. This avoids sampling an absurd token with a tiny probability. In the "
            "book, temperature 1.4 with top-k 25 produces text different from the memorised "
            "passage, more varied and also riskier."
        ),
        callout(
            "warning",
            "A pretty sample does not prove the model is good",
            "You can find a lucky generation and conclude that the model has learned. That is "
            "a sample of size one. Serious evaluation combines loss on a held-out set, several "
            "generations with the same configuration, and, when possible, a task with an "
            "objective criterion. Perplexity does not measure truth, usefulness, or safety "
            "either: it only measures how much probability the model gives to real tokens."
        ),
        check(
            "Training loss falls from 1.2 to 0.3, but validation loss rises from 2.1 to 2.8. "
            "What is happening and what would you do?",
            "The model is overfitting: it improves on the data it sees and loses "
            "generalisation. I would review corpus size and variety, reduce epochs or apply "
            "early stopping, and try more dropout or weight decay. I would also check for data "
            "leakage between training and validation."
        ),
        keypoints(
            [
                "Validation loss measures generalisation; training loss measures fit.",
                "A growing gap between them is the classic sign of overfitting.",
                "In the book, validation stalls at 6.452 while training falls to 0.391.",
                "More data, dropout, weight decay, and early stopping fight overfitting.",
                "Greedy decoding is deterministic but tends to repeat and memorise.",
                "Temperature and top-k control variety and risk during sampling.",
                "A single generation does not replace systematic evaluation.",
            ]
        ),
    ),
    key_points=(
        "Training and validation measure different things: fit and generalisation.",
        "Diverging curves indicate overfitting.",
        "Evaluation requires model.eval() and torch.no_grad().",
        "Greedy, temperature, and top-k are decoding strategies, not training methods.",
        "Perplexity does not measure truth or usefulness.",
        "One lucky sample is not enough evidence.",
    ),
)
