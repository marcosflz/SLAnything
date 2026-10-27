"""Lesson 2 · Cross entropy and perplexity."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=2,
    slug="entropia-cruzada",
    title="Cross entropy and perplexity",
    summary=(
        "Cross entropy turns the model's probabilities into a mean loss; perplexity "
        "returns it to a more intuitive scale."
    ),
    minutes=11,
    objectives=(
        "Compute cross entropy for one token and a small batch.",
        "Relate mean loss to perplexity through exp(L).",
        "Interpret perplexity as an effective number of candidates.",
        "Explain why the initial loss depends on vocabulary size.",
    ),
    blocks=(
        lead(
            "The loss of one token is easy to compute, but a model is trained on millions of "
            "tokens. We need an account that summarises them without losing their meaning. "
            "<strong>Cross entropy</strong> does that job, and <strong>perplexity</strong> "
            "translates it into a unit that can be explained without logarithms."
        ),
        h2("From a probability to a loss"),
        p(
            "At each position, the model produces a distribution over the vocabulary and the "
            "text tells us which token was correct. The cross entropy of that position is "
            "<code>−ln p(correct)</code>. The negative sign turns a negative logarithm into a "
            "positive loss: the smaller the probability assigned to the correct token, the "
            "larger the penalty. If the model is confident and right, <code>p = 1</code> and "
            "the loss is 0. If it spreads probability across the whole vocabulary, the loss "
            "approaches <code>ln V</code>."
        ),
        table(
            ["Probability of correct token", "Loss −ln p", "Reading"],
            [
                ["1.00", "0.000", "The model has no doubt, but that confidence may be excessive"],
                ["0.50", "0.693", "The right answer is most likely, without a large margin"],
                ["0.10", "2.303", "Other options are favoured much more strongly"],
                ["0.01", "4.605", "The correct token is almost ruled out"],
            ],
            caption="Loss grows non-linearly as probability approaches zero.",
            note="Natural logarithm. Changing the base would change the number, not the order.",
        ),
        h2("Averaging a batch"),
        p(
            "A training batch contains <code>B·T</code> positions. The batch loss is the mean "
            "of the individual losses: <code>L = (1 / (B·T)) · Σ −ln p<sub>i</sub></code>. "
            "Each token contributes a share of the total. That contribution reveals which "
            "examples dominate the signal: a probability of 0.01 contributes 4.605, while one "
            "of 0.90 contributes only 0.105. The model spends most of the gradient correcting "
            "the cases where it is badly wrong."
        ),
        p(
            "The mean has an important consequence: the loss does not behave like a sum as "
            "the number of tokens changes. Two batches of different sizes can be compared if "
            "both use the mean, but the noise will be larger in the small batch. It is also "
            "worth remembering that the mean is computed over positions, so a 256-token "
            "sequence weighs 256 times more than a one-token sequence."
        ),
        callout(
            "note",
            "Perplexity is not an error percentage",
            "A perplexity of 10 does not mean 10 % failures. It means the model is uncertain, "
            "on average, among about 10 effective candidates. A perplexity of 1 would be a "
            "perfectly certain distribution; one equal to the vocabulary size would be "
            "uniform. It is a relative scale, not a grade."
        ),
        h2("Perplexity"),
        p(
            "Perplexity is defined as <code>exp(L)</code>, the exponential of mean loss. Its "
            "appeal is that it undoes the logarithm: if the model assigns the same probability "
            "to <code>k</code> candidates, its perplexity is approximately <code>k</code>. In "
            "the book's example, a loss of 10.794 over a 50,257-token vocabulary gives a "
            "perplexity of 48,725.82. The initial model is close to spreading probability "
            "across the entire vocabulary. After training, loss falls and so does perplexity."
        ),
        p(
            "Perplexity inherits the vocabulary dependence. A model with 1,000 tokens may have "
            "a perplexity of 50 and another with 50,000 a perplexity of 5,000; that alone does "
            "not say which is better. To compare models, use the same tokenizer and the same "
            "evaluation set. Perplexity is useful for following progress within an experiment, "
            "not for confronting numbers from different configurations."
        ),
        table(
            ["Token", "p(correct)", "Loss", "Contribution to mean"],
            [
                ["1", "0.90", "0.105", "0.026"],
                ["2", "0.50", "0.693", "0.173"],
                ["3", "0.10", "2.303", "0.576"],
                ["4", "0.25", "1.386", "0.347"],
            ],
            caption=(
                "Four-token batch: mean loss 1.122 and perplexity exp(1.122) ≈ 3.07."
            ),
            note="The contributions add up to the mean batch loss.",
        ),
        py(
            """
import math

probabilities = [0.90, 0.50, 0.10, 0.25]
losses = [-math.log(p) for p in probabilities]
mean_loss = sum(losses) / len(losses)
perplexity = math.exp(mean_loss)

for i, (p, loss) in enumerate(zip(probabilities, losses), start=1):
    print(f"Token {i}: p={p:.2f}  loss={loss:.3f}")

print(f"Mean loss: {mean_loss:.3f}")
print(f"Perplexity: {perplexity:.2f}")
""",
            caption=(
                "Cross entropy and perplexity for a four-token batch. Change the "
                "probabilities to see how the mean responds."
            ),
        ),
        lab("loss"),
        p(
            "The loss lab turns this table into an interactive control. Each token has a "
            "probability assigned to its target; moving it changes the token's loss, the batch "
            "mean, and perplexity. Watch two things: the curve explodes as probability "
            "approaches zero, and the mean moves more slowly than any individual token. That "
            "difference between detail and summary is what you see during training."
        ),
        check(
            "One token receives probability 0.50 and another 0.10. Which contributes more to "
            "the batch loss, and what is perplexity if only those two tokens existed?",
            "The 0.10 token contributes 2.303 versus 0.693 for the first. Mean loss would be "
            "(0.693 + 2.303) / 2 = 1.498 and perplexity exp(1.498) ≈ 4.47. The mean is over "
            "the two tokens, not over their probabilities."
        ),
        keypoints(
            [
                "A token's cross entropy is −ln of the correct token's probability.",
                "A batch loss is the mean loss of its positions.",
                "Tokens with very low probability dominate the loss and the gradient.",
                "Perplexity is exp(L) and reads as effective candidates.",
                "Loss and perplexity depend on vocabulary size.",
                "To compare models, use the same tokenizer and the same set.",
            ]
        ),
    ),
    key_points=(
        "The mean batch loss is the cross entropy of its positions.",
        "−ln p turns probabilities into an additive, stable scale.",
        "Perplexity is exp(L) and expresses effective uncertainty.",
        "Errors with very low p contribute far more to the mean.",
        "The initial loss resembles ln(V) and depends on the vocabulary.",
    ),
)
