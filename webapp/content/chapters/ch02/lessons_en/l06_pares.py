"""Lesson 6 · Input → target pairs."""

from webapp.content.schema import (
    Lesson,
    bullets,
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
    number=6,
    slug="pares-entrada-objetivo",
    title="Input → target pairs",
    summary=(
        "Each window becomes two sequences: the input and the target shifted by one token. "
        "The model learns to predict, at every position, the token that comes next."
    ),
    minutes=10,
    objectives=(
        "Build the pair x → y from a sequence of IDs.",
        "Explain why the target is the input shifted by one position.",
        "Describe the shape of a batch and the role of the causal mask.",
        "Interpret cross-entropy loss in this setting.",
    ),
    blocks=(
        lead(
            "We have windows of IDs. Now we must turn them into the pair training needs: an "
            "input <code>x</code> and a target <code>y</code>. The rule is so simple it almost "
            "feels like cheating: <strong>y is x shifted one token to the left</strong>. The text "
            "supplies the label without human annotation."
        ),
        p(
            "The book shows it with four tokens. If the input is <code>[290, 4920, 2241, 287]</code>, "
            "the target is <code>[4920, 2241, 287, 257]</code>. The first position learns to "
            "predict 4920 from 290; the second, to predict 2241 from 290 and 4920; and so on. In "
            "text: “and” → “established”; “and established” → “himself”; “and established "
            "himself” → “in”. Every prefix is a valid input and the next token is its label."
        ),
        bullets(
            [
                "<strong>x</strong>: the IDs the model sees in one step.",
                "<strong>y</strong>: the IDs it should predict, one per position.",
                "<strong>Shift</strong>: y[i] = x[i + 1] within the window.",
                "<strong>Window</strong>: the context fragment cut from the corpus.",
                "<strong>Batch</strong>: several windows stacked for joint processing.",
            ]
        ),
        h2("One window, many predictions"),
        p(
            "It is tempting to think that a 256-token window produces a single training example. "
            "It does not: it produces <strong>256 predictions</strong>, one per position. The "
            "full input goes through the transformer and the output has the same length. At each "
            "position there is a vector of logits over the vocabulary, and the loss compares that "
            "vector with the correct token. The total loss is the mean of the per-position losses."
        ),
        p(
            "That design is what makes training efficient. Instead of cutting the text into 256 "
            "one-token examples, it processes one sequence and reuses the computation. The causal "
            "mask prevents position <code>i</code> from looking at future positions: if it could "
            "see <code>x[i+1]</code>, the task would be copying rather than predicting. Attention "
            "only looks backwards."
        ),
        table(
            ["Element", "Shape", "Example", "Contents"],
            [
                ["Input IDs", "(batch, context)", "(8, 4)", "8 windows of 4 tokens"],
                ["Target IDs", "(batch, context)", "(8, 4)", "The same, shifted"],
                ["Embeddings", "(batch, context, d)", "(8, 4, 256)", "One vector per token"],
                ["Logits", "(batch, context, V)", "(8, 4, 50,257)", "One score per vocabulary token"],
                ["Loss", "scalar", "2.31", "Mean over the batch's 32 positions"],
            ],
            caption="Typical shapes in a training batch. The last dimension is the vocabulary.",
            note=(
                "The example uses batch 8, context 4, and dimension 256, as in the book. The "
                "50,257 and the loss of 2.31 are illustrative."
            ),
        ),
        h2("The code that builds the pairs"),
        p(
            "The following example starts from a list of IDs and generates windows with their "
            "targets. It then counts how many predictions each window contributes. Change the "
            "context, the stride, or the sequence and watch the shapes change. PyTorch is not "
            "needed: lists are enough to understand the mechanism."
        ),
        py(
            """
IDS = [40, 367, 2885, 1464, 1807, 3619, 402, 271, 10899]
CONTEXT = 4
STRIDE = 2


def windows(ids, context, stride):
    pairs = []
    for start in range(0, len(ids) - context + 1, stride):
        x = ids[start:start + context]
        y = ids[start + 1:start + context + 1]
        pairs.append((x, y))
    return pairs


pairs = windows(IDS, CONTEXT, STRIDE)
print(f"Sequence of {len(IDS)} IDs, context {CONTEXT}, stride {STRIDE}")
print(f"Complete windows: {len(pairs)}")
for number, (x, y) in enumerate(pairs, start=1):
    print(f"  {number}. x={x}  y={y}")

predictions = sum(len(y) for _, y in pairs)
print(f"Total predictions: {predictions}")

# Cross-entropy loss for one prediction.
import math

probability = 0.8
loss = -math.log(probability)
print(f"If p(correct token)=0.8, loss={loss:.3f}")
print(f"If p(correct token)=0.1, loss={-math.log(0.1):.3f}")
""",
            caption=(
                "Building x → y pairs and computing the loss for one prediction. Try context 2, "
                "4, or 8 and stride 1 or 2."
            ),
        ),
        lab("labels"),
        callout(
            "info",
            "The label is not a human judgement",
            "The target does not say whether a sentence is good, true, or appropriate: it says "
            "which token came next in the corpus. The model learns statistical regularities of "
            "the text, including its biases. That is why corpus quality and filtering matter so "
            "much.",
        ),
        p(
            "The usual loss is <strong>cross-entropy</strong>. For each position, the model "
            "produces a probability distribution over the vocabulary and the loss is "
            "<code>−log p(correct token)</code>. If it assigns probability 0.8 to the correct "
            "token, the loss is 0.223; if it assigns 0.1, it rises to 2.303. The mean over all "
            "positions in the batch produces a single number used to update the weights. These "
            "are example values, not results from a trained model."
        ),
        h2("Batches and stability"),
        p(
            "A batch of eight four-token windows produces an 8 × 4 matrix of IDs and, after "
            "embeddings, an 8 × 4 × 256 tensor. The loss is computed over all 32 positions. With "
            "larger batches, the gradient is less noisy but more memory is required. The book "
            "reminds us that batch size is a hyperparameter: there is no universal value, and "
            "small batches can produce noisier updates."
        ),
        p(
            "It is also wise to drop the last batch if it is incomplete. If the corpus does not "
            "divide exactly, a smaller batch can cause a loss spike and destabilise training. "
            "That is why many implementations use <code>drop_last=True</code>. It is an "
            "engineering detail, but it affects reproducibility and tensor shapes."
        ),
        check(
            "If x = [10, 20, 30, 40], what is y with context 4 and what does the last position predict?",
            "y = [20, 30, 40, next]. The last position of x is 40; the model must predict the "
            "token that follows 40 in the original sequence. That token is not in x: it is at "
            "position i+1 of the window, which is why the target is shifted.",
        ),
        h2("From pair to practice"),
        p(
            "With the pairs built, the data pipeline is almost complete: text → tokens → IDs → "
            "windows → x/y pairs. Only the conversion of IDs into vectors and the addition of "
            "position remain. Those two operations are the bridge to the transformer and occupy "
            "the last two lessons of the chapter."
        ),
        p(
            "Before moving on, check that you can explain why a four-token window generates four "
            "predictions rather than one. If the answer is “because the model produces one output "
            "per position and all of them are compared with the next token”, you have understood "
            "the central mechanism of pretraining."
        ),
        keypoints(
            [
                "The target y is the input x shifted by one token.",
                "Every position in the window generates a prediction.",
                "The causal mask prevents looking at future tokens.",
                "Loss is the mean of −log p(correct token) over positions.",
                "A batch stacks windows and adds a dimension to the tensor.",
                "The label comes from the text, not from human annotation.",
            ]
        ),
    ),
    key_points=(
        "x and y are the same sequence shifted by one position.",
        "An L-token window produces L predictions.",
        "The causal mask stops the model from seeing the future.",
        "Cross-entropy measures the probability assigned to the correct token.",
        "Batch size balances memory and gradient stability.",
    ),
    quiz_id=None,
)
