"""Lesson 6 · Residual connections."""

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
    number=6,
    slug="conexiones-residuales",
    title="Residual connections",
    summary=(
        "The x + f(x) sum that gives gradients a direct path, compared with a deep "
        "network without shortcuts and with a numerical simulation of the effect."
    ),
    minutes=10,
    objectives=(
        "Explain the vanishing-gradient problem in deep networks.",
        "Describe what a residual connection adds and what it requires.",
        "Interpret the book's gradient experiment.",
        "Relate residuals to the depth of GPT-2.",
    ),
    blocks=(
        lead(
            "A residual connection is one of the simplest operations in the whole model: "
            "add a layer's input to its output. It has no parameters, takes no memory, and "
            "fits in one line. Yet it is what lets GPT-2 stack twelve blocks without the "
            "gradient fading along the way. Understanding why requires looking backwards, "
            "at how the error propagates."
        ),
        h2("The gradient problem"),
        p(
            "During training, the network computes a loss and propagates its derivative "
            "backwards, layer by layer, to update the weights. Each layer multiplies the "
            "gradient by its local derivatives. If those factors are small, the gradient "
            "reaches the first layers almost at zero: this is the "
            "<strong>vanishing-gradient problem</strong>. If they are large, it explodes. In "
            "a five-layer network the effect may be moderate; in a stack of twelve or "
            "ninety-six, it accumulates."
        ),
        p(
            "The book illustrates it with a five-layer network and a squared loss. Without "
            "shortcuts, the mean absolute gradient falls from 0.00505 in the last layer to "
            "0.00020 in the first. With residual connections, the last layer still has the "
            "largest gradient, but the first keeps 0.22170 and the intermediate layers stay "
            "in a much more stable range. These are figures from an illustrative experiment "
            "with a particular seed, not a universal law; what they show is the mechanism, "
            "not a value to memorize."
        ),
        figure(
            "img/ch04/conexiones-residuales.svg",
            "Comparison of a deep network without residual connections, with vanishing gradients, and one with shortcuts that preserve a direct path.",
            "Without a residual, the gradient becomes tiny away from the output. With one, "
            "the identity offers a direct path and the gradient reaches the first layers at "
            "a much larger order of magnitude.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("An identity that crosses the block"),
        p(
            "The residual connection creates an alternative path. Instead of computing "
            "<code>x = f(x)</code>, the block computes <code>x = x + f(x)</code>. When "
            "differentiating, a constant term appears: the derivative of the identity is one. "
            "That one means that even if the derivative of <code>f</code> is small, the "
            "gradient always has a route back without being multiplied by every layer. The "
            "sublayer can learn a small transformation —even one close to zero— without "
            "blocking the flow of information."
        ),
        p(
            "The transformer block has two residuals: one around attention and one around "
            "the FFN. Both add onto the same 768-dimensional vector. That accumulation is "
            "often called the <strong>residual stream</strong>: a main path that crosses every "
            "block and receives contributions from each sublayer. Attention and the FFN do "
            "not replace that path; they write onto it. This architecture makes training "
            "easier and lets the input information travel far without degrading completely."
        ),
        py(
            """
# Our own scalar simulation: it does not reproduce the book's PyTorch experiment.
# Each layer multiplies the gradient by 0.5; the residual adds an identity path.
layer_derivative = 0.5
layers = 5

without_residual = layer_derivative ** layers
with_residual = (1 + layer_derivative) ** layers

print(f"Relative gradient without residual: {without_residual:.6f}")
print(f"Relative gradient with residual: {with_residual:.6f}")
print(f"Scale improvement: x{with_residual / without_residual:.1f}")

print()
gradient = 1.0
for layer in range(layers, 0, -1):
    gradient *= layer_derivative
    print(f"Layer {layer} without residual: {gradient:.6f}")

gradient = 1.0
for layer in range(layers, 0, -1):
    gradient *= (1 + layer_derivative)
    print(f"Layer {layer} with residual: {gradient:.6f}")
""",
            caption=(
                "A didactic example with constant derivatives. The residual does not remove "
                "the multiplication, but it adds a factor (1 + f') that prevents the "
                "exponential collapse of the gradient."
            ),
        ),
        p(
            "The simulation exaggerates the effect so it is visible: with five layers and a "
            "derivative of 0.5, the gradient without a residual shrinks to 0.03125; with the "
            "shortcut, it rises to 7.59375. In a real network the derivatives are not "
            "constant and the residual does not guarantee that everything trains well, but "
            "the mechanism is the same. The identity does not stop the sublayer from "
            "learning; it gives it a floor from which to do so. That is why residuals appear "
            "in practically every modern transformer."
        ),
        callout(
            "tip",
            "Adding is not concatenating",
            "A residual connection adds two tensors of the same shape; it does not paste "
            "them side by side. That is why attention and the FFN must return 768 "
            "dimensions. If they returned another shape, you would need to project before "
            "adding or change the block design.",
        ),
        check(
            "If a sublayer learned the zero function, what would the block do with a "
            "residual connection?",
            "It would return the input unchanged: <code>x + 0 = x</code>. That is the key "
            "property of the identity path. Without a residual, the output would be zero and "
            "the information would be lost. With one, the sublayer can contribute nothing at "
            "a given moment without destroying what was already there.",
        ),
        keypoints(
            [
                "Gradients vanish when multiplied by small derivatives layer after layer.",
                "A residual connection adds the sublayer's input to its output.",
                "The identity contributes a constant term that keeps a gradient path open.",
                "The book compares gradients with and without shortcuts in a five-layer network.",
                "GPT-2 has two residuals per block: one for attention and one for the FFN.",
                "The residual stream crosses every block and accumulates their contributions.",
            ]
        ),
    ),
    key_points=(
        "Residual connections mitigate vanishing gradients.",
        "The sum x + f(x) requires matching input and output shapes.",
        "The identity offers a direct path for gradients and information.",
        "The book's experiment shows much more stable gradients with shortcuts.",
        "Each transformer block has one residual for attention and one for the FFN.",
        "The residual stream is the main path across the stack.",
    ),
)
