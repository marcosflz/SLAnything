"""Lesson 3 · The training loop."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=3,
    slug="bucle-de-entrenamiento",
    title="The training loop",
    summary=(
        "Five operations repeated per batch —zero_grad, forward, loss, backward, and "
        "step— turn a random GPT into a model that starts to write."
    ),
    minutes=12,
    objectives=(
        "Order the operations of a training step correctly.",
        "Distinguish the batch loop from the epoch loop.",
        "Explain what backward does and what the optimizer updates.",
        "Interpret the training and validation losses in the book's example.",
    ),
    blocks=(
        lead(
            "A GPT does not learn by inspiration: it repeats a very short procedure "
            "thousands of times. Every batch goes through the same five operations, and each "
            "operation has an order. Changing that order is not a matter of style; it can "
            "stop the model from learning or let gradients accumulate without control."
        ),
        h2("The step, operation by operation"),
        p(
            "The cycle starts with <code>optimizer.zero_grad()</code>, which clears the "
            "gradients from the previous step. Then comes the <strong>forward</strong> pass: "
            "the model receives the input batch and produces logits. Logits and targets yield "
            "the cross-entropy loss. Next, <code>loss.backward()</code> walks the network "
            "backwards and leaves the loss gradient on every parameter. Finally, "
            "<code>optimizer.step()</code> uses those gradients to update the weights. The "
            "next batch starts again."
        ),
        figure(
            "img/ch05/bucle-entrenamiento.svg",
            "Circular diagram with the five training operations: batch, forward, backward, step, and zero_grad, inside the epoch loop.",
            "The inner loop walks over batches. When it ends, an epoch closes and the model is "
            "evaluated on data that did not take part in the update.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "The loss is a scalar, but it contains information from every position in the "
            "batch. <code>backward()</code> applies the chain rule from that scalar down to "
            "every weight. It updates nothing: it only computes derivatives. The update "
            "happens in <code>step()</code>, which reads the gradients and the learning rate. "
            "That separation lets you inspect or clip gradients before applying them."
        ),
        h2("Epochs, evaluation, and samples"),
        p(
            "The outer loop walks over <strong>epochs</strong>. An epoch is one complete pass "
            "through the training set. Inside each epoch, the loader delivers batches in order "
            "or shuffled. At the end of an epoch the model is usually evaluated and a text "
            "sample is generated to check whether numerical progress translates into something "
            "readable. In the book's example, the model trains for ten epochs with AdamW, a "
            "learning rate of 0.0004, and weight decay 0.1. Training loss falls from 9.781 to "
            "0.391; validation loss falls from 9.933 to 6.452 and stalls much earlier. The run "
            "takes about five minutes on a laptop."
        ),
        p(
            "Evaluation uses <code>model.eval()</code> inside <code>torch.no_grad()</code>. "
            "The first call disables dropout; the second avoids building the gradient graph, "
            "because nothing will be updated. During training, <code>model.train()</code> "
            "re-enables dropout. Forgetting the mode switch produces unstable, hard-to-"
            "reproduce results: the same batch can give different losses depending on the "
            "active mode."
        ),
        callout(
            "warning",
            "zero_grad goes first, not last",
            "If you forget <code>zero_grad()</code>, gradients from the previous batch add to "
            "the current ones. The effective step becomes larger and less predictable. PyTorch "
            "does not clear gradients automatically because accumulation is a legitimate "
            "technique; the loop owns that responsibility. The practical rule is to clear at "
            "the start of each iteration, unless you are accumulating on purpose."
        ),
        py(
            """
import math

vocabulary = ["blue", "green", "red"]
target = 1
logits = [2.0, 0.2, -0.5]
learning_rate = 0.8

def softmax(values):
    maximum = max(values)
    exponentials = [math.exp(v - maximum) for v in values]
    total = sum(exponentials)
    return [v / total for v in exponentials]

for step in range(1, 11):
    probabilities = softmax(logits)
    loss = -math.log(probabilities[target])
    gradients = probabilities[:]
    gradients[target] -= 1.0
    logits = [v - learning_rate * g for v, g in zip(logits, gradients)]
    if step in (1, 5, 10):
        print(
            f"Step {step:2d}: loss={loss:.3f} "
            f"p(green)={probabilities[target]:.3f}"
        )
""",
            caption=(
                "One gradient-descent step over three logits. It is the same idea as "
                "backward + step, without a neural network or PyTorch."
            ),
        ),
        p(
            "The example condenses the mechanism: the cross-entropy gradient with respect to "
            "the logits is <code>p − onehot(target)</code>. Subtracting that gradient, "
            "multiplied by the learning rate, raises the correct token's probability and "
            "lowers the others. In a transformer the same operation repeats for millions of "
            "parameters, but the logic is identical. What changes is scale and the cost of "
            "computing derivatives."
        ),
        h2("What to watch during training"),
        p(
            "A falling loss is not enough as a diagnosis. Compare the training curve with the "
            "validation curve and read a sample. If both fall, the model is learning. If "
            "training falls while validation stalls, overfitting appears. If the loss explodes "
            "or becomes <code>NaN</code>, check the learning rate, initialisation, and numerical "
            "stability. Periodic logging of metrics and samples is part of training, not a "
            "decoration added afterwards."
        ),
        check(
            "What is the difference between loss.backward() and optimizer.step()?",
            "backward() computes the loss gradients with respect to the parameters and stores "
            "them, but does not change the weights. step() reads those gradients, applies the "
            "optimizer rule, and updates the weights. First the direction is computed; then "
            "the step is taken."
        ),
        keypoints(
            [
                "Each batch follows zero_grad → forward → loss → backward → step.",
                "backward() computes gradients; step() updates the weights.",
                "An epoch is one complete pass through the training set.",
                "model.eval() and no_grad() are used to evaluate without dropout or gradients.",
                "In the book, training loss falls from 9.781 to 0.391 in ten epochs.",
                "Validation loss stalls at 6.452: a sign of overfitting.",
                "The loop should log metrics and samples, not just run steps.",
            ]
        ),
    ),
    key_points=(
        "The order of the training step matters: zero_grad before backward.",
        "The forward pass produces logits; cross entropy turns them into loss.",
        "backward computes gradients and step updates the weights.",
        "An epoch walks through every batch in the training set.",
        "Evaluation requires model.eval() and torch.no_grad().",
        "The gap between training and validation reveals overfitting.",
    ),
)
