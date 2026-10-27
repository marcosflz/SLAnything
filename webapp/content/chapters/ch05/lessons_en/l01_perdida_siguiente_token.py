"""Lesson 1 · The next-token loss."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=1,
    slug="perdida-siguiente-token",
    title="The next-token loss",
    summary=(
        "A GPT produces a vector of logits at every position. The loss measures how much "
        "probability the correct token receives and reduces that account to one number."
    ),
    minutes=11,
    objectives=(
        "Describe the shape of logits and targets in a batch.",
        "Explain how softmax yields the probability of the correct token.",
        "Interpret the loss of one position and the mean of a batch.",
        "Avoid comparing losses across different vocabularies.",
    ),
    blocks=(
        lead(
            "Training a GPT is, at bottom, raising the probability of the token that actually "
            "appears in the text. To know whether the model is improving we need a numerical "
            "measure of how close it gets to that answer. That measure is the "
            "<strong>next-token loss</strong>, the compass for this whole chapter."
        ),
        h2("What comes out of the model"),
        p(
            "Every position in the sequence produces a vector of <strong>logits</strong>, one "
            "per vocabulary token. If the vocabulary has 50,257 entries, the vector has "
            "50,257 unnormalised numbers. A high logit means the model favours that token, but "
            "it is not a probability: values can be negative and do not sum to 1. The "
            "<strong>softmax</strong> function turns them into a distribution by exponentiating "
            "each logit and dividing by the sum of all exponentials. The result is a vector of "
            "positive probabilities that sums to 1."
        ),
        figure(
            "img/ch05/perdida.svg",
            "Next-token probability distribution with the correct token highlighted and the loss formula.",
            "The loss does not look at the whole vector equally: it selects the probability "
            "of the correct token, applies −ln, and averages over the batch.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "The training goal is to push that probability towards 1. If the correct token is "
            "“sky” and the model assigns it 0.60, the loss at that position is −ln(0.60) ≈ "
            "0.511. If it assigns 0.05, the loss rises to −ln(0.05) ≈ 3.00. The account "
            "punishes small probabilities hard: moving from 0.60 to 0.90 cuts the loss from "
            "0.511 to 0.105, whereas moving from 0.05 to 0.10 only takes it from 3.00 to 2.30. "
            "That asymmetry is useful: the model learns most from the cases where it is badly "
            "wrong."
        ),
        h2("The shape of a batch"),
        p(
            "In practice we do not train on one sentence and one position at a time. A batch "
            "holds several sequences, and each sequence contributes several positions. Logits "
            "have shape <code>[B, T, V]</code>: batch size, sequence length, and vocabulary "
            "size. Targets have shape <code>[B, T]</code>, because for each position we only "
            "store the id of the correct token. The loss is computed over every position in "
            "the batch, not as an average of independent sentences."
        ),
        table(
            ["Tensor", "Shape", "What it contains"],
            [
                ["Logits", "<code>[B, T, V]</code>", "One score per vocabulary token and position"],
                ["Targets", "<code>[B, T]</code>", "The token that comes next at each position"],
                ["Flattened logits", "<code>[B·T, V]</code>", "Batch positions as independent rows"],
                ["Loss", "Scalar", "Mean of −ln p over the B·T positions"],
            ],
            caption="Usual shapes while computing the loss.",
            note=(
                "The loss is averaged over positions, not sequences. A long sequence "
                "contributes more positions than a short one."
            ),
        ),
        p(
            "Targets are built by shifting the input one position. If the sequence is “The "
            "sky is cloudy”, the inputs are “The sky is” and the targets “sky is cloudy”. The "
            "model sees the same text on both sides: the label was already there. This is why "
            "pretraining needs no annotators. The loss of a batch is the mean of the losses of "
            "all positions, so a batch of 256-token sequences provides 256 times more signal "
            "than a single prediction."
        ),
        p(
            "The book's 124-million-parameter model, with a vocabulary of 50,257 tokens, "
            "starts with a loss close to 10.99 on the short story <em>The Verdict</em>. That "
            "value is near a uniform distribution: ln(50,257) ≈ 10.825. This is no accident. "
            "Before training, the weights are random and the model spreads probability over "
            "almost the whole vocabulary. A high loss does not mean it “knows nothing”: it "
            "means it does not yet concentrate probability on the correct token."
        ),
        callout(
            "warning",
            "Loss is not a percentage score",
            "A loss of 2.0 does not mean 2 % accuracy. It is the negative logarithm of the "
            "mean probability of the correct token. Nor can losses be compared naively across "
            "models with different vocabularies: a 50,000-token vocabulary starts from a much "
            "higher baseline than a 1,000-token one. To compare, use the same tokenizer or "
            "look at perplexity and task metrics."
        ),
        check(
            "Why is the loss computed position by position and then averaged, instead of "
            "comparing only the last word of each sentence?",
            "Because during pretraining the model learns from every position: each token in "
            "the sequence is a potential target. Averaging all positions uses far more of the "
            "text and yields a more stable signal than looking only at the end of each "
            "sentence."
        ),
        keypoints(
            [
                "Logits are unnormalised scores; softmax turns them into probabilities.",
                "The loss at a position is −ln of the probability assigned to the correct token.",
                "Targets are the input shifted one position, not human annotations.",
                "In a batch, logits have shape [B, T, V] and targets [B, T].",
                "The batch loss averages every position, not just the last one.",
                "A loss near ln(V) indicates a nearly uniform model, such as the initial one.",
            ]
        ),
    ),
    key_points=(
        "The loss measures the correct token's probability with −ln and averages it.",
        "Softmax turns logits into a distribution that sums to 1.",
        "Targets are the input sequence shifted one position.",
        "A batch loss is the mean over all positions.",
        "The scale of the loss depends on vocabulary size.",
    ),
)
