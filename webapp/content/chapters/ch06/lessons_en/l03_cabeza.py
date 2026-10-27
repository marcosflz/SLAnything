"""Lesson 3 · The classification head."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=3,
    slug="cabeza-clasificacion",
    title="The classification head",
    summary=(
        "A new linear layer turns the model's 768 dimensions into one score per class; "
        "the last token summarises the sequence."
    ),
    minutes=11,
    objectives=(
        "Explain how the vocabulary output layer is replaced by a class head.",
        "Interpret the shape of the output tensor and the logits for each class.",
        "Justify using the last token in a model with causal attention.",
        "Turn logits into probabilities with softmax and obtain the predicted class.",
    ),
    blocks=(
        lead(
            "Classifying does not require a different transformer. It requires changing the "
            "last projection: instead of spreading probability over 50,257 tokens, the "
            "network must spread it over a handful of classes. That new layer is the "
            "classification head, and its design explains why the model is still the same "
            "GPT-2 that used to generate text."
        ),
        h2("From vocabulary to classes"),
        p(
            "In small GPT-2, the <code>out_head</code> layer transforms a 768-dimensional "
            "vector into 50,257 scores, one per vocabulary token. For classification it is "
            "replaced by a linear layer of <strong>768 → 2</strong>: two outputs, one for "
            "“not spam” and one for “spam”. If the task had three classes —technology, "
            "sports, and politics, for example— the layer would have three outputs. The "
            "number of nodes matches the number of classes, not the vocabulary size."
        ),
        p(
            "The input is still a sequence of token identifiers. The output now has shape "
            "<code>[batch, tokens, classes]</code>. With a batch of 8 messages of 120 tokens "
            "and two classes, the resulting tensor is <code>[8, 120, 2]</code>. Every "
            "position in the sequence produces a prediction, but not all of them are equally "
            "useful. To classify the whole message, one position is selected and the others "
            "are ignored."
        ),
        figure(
            "img/ch06/cabeza-clasificacion.svg",
            "Diagram of GPT-2 with twelve blocks; the last block and final normalisation are trainable, and the vocabulary head is replaced by a projection to two classes.",
            "The classification head replaces the vocabulary projection with a linear layer "
            "from 768 to 2 classes. Only the last transformer block, the final normalisation, "
            "and the new head are trained.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("Why the last token"),
        p(
            "GPT uses causal attention: each token can only look at previous tokens and "
            "itself. The first token sees nothing of the future; the last token, by contrast, "
            "has been able to attend to the entire sequence. That is why the book concentrates "
            "classification on the last row of the output tensor, "
            "<code>outputs[:, -1, :]</code>. It is the position that accumulates the most "
            "information from the message and the one used to compute the loss and the "
            "prediction."
        ),
        p(
            "The two values in that row are <strong>logits</strong>: unnormalised scores. In "
            "the book's example, the last token produces <code>[-3.5983, 3.9902]</code>. "
            "Because the second score is higher, the predicted class is 1, “spam”. Applying "
            "softmax is optional for deciding, since the transformation preserves order; it "
            "is essential, however, if we want to interpret the result as a probability or "
            "choose a threshold other than 0.5."
        ),
        py(
            """
import math

logits = [-3.5983, 3.9902]
labels = ["not spam", "spam"]

# Stable softmax: subtract the maximum before exponentiating.
maximum = max(logits)
exponentials = [math.exp(value - maximum) for value in logits]
total = sum(exponentials)
probabilities = [value / total for value in exponentials]

for label, logit, probability in zip(labels, logits, probabilities):
    print(f"{label:8s} logit={logit:6.2f}  probability={probability:.4f}")

prediction = 0
for index in range(1, len(probabilities)):
    if probabilities[index] > probabilities[prediction]:
        prediction = index

print("Predicted class:", labels[prediction])
""",
            caption=(
                "Softmax over the last token's logits. The class with the highest "
                "probability matches the one with the highest logit."
            ),
        ),
        p(
            "The “Interactive classifier” lab turns these scores into decisions. With a list "
            "of example messages you can move the threshold and watch the confusion matrix, "
            "precision, recall, and F1 change. It is the best way to see that the head does "
            "not decide on its own: it produces scores, and the surrounding system fixes the "
            "rule."
        ),
        lab("classifier"),
        callout(
            "tip",
            "One head, many architectures",
            "The same pattern appears in BERT and other models: a contextual representation "
            "and a linear layer per class. The difference lies in which token or vector is "
            "used as the summary. GPT uses the last token because of the causal mask; a "
            "bidirectional encoder usually uses the <code>[CLS]</code> token or pooling over "
            "the sequence."
        ),
        check(
            "If the output tensor is [8, 120, 2], what does each dimension represent and why "
            "is position 119 selected?",
            "Eight is the batch size, 120 is the sequence length, and 2 is the number of "
            "classes. Position 119 is the last token; thanks to causal attention it has been "
            "able to look at the previous 119 tokens and summarises the whole message better.",
        ),
        keypoints(
            [
                "The classification head replaces the vocabulary projection.",
                "A linear layer from 768 to 2 produces one logit per class.",
                "The output has shape [batch, tokens, classes].",
                "The last token summarises the sequence because it sees all previous tokens.",
                "Softmax turns logits into probabilities but does not change the argmax.",
                "The head produces scores; the threshold and metrics decide.",
            ]
        ),
    ),
    key_points=(
        "The classification head is a linear layer with one output per class.",
        "The output tensor keeps the token dimension and adds the class dimension.",
        "The last token is the natural summary of a causal-attention sequence.",
        "Logits rank the same before and after softmax.",
        "The prediction is the argmax; the threshold is a later decision.",
    ),
)
