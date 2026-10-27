"""Lesson 3 · GELU and activations."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=3,
    slug="gelu",
    title="GELU and activations",
    summary=(
        "Why GPT's feed-forward network does not simply use ReLU: GELU's smooth curve, "
        "its tanh approximation, and its effect on training."
    ),
    minutes=9,
    objectives=(
        "Compare ReLU and GELU by shape and by behavior on negative values.",
        "Write the GELU approximation used by GPT-2.",
        "Explain why a smooth activation can help optimization.",
        "Place GELU inside the transformer block's feed-forward network.",
    ),
    blocks=(
        lead(
            "An activation decides how much of a neuron's signal passes through. ReLU "
            "answers with a corner: positive inputs pass, negative inputs become zero. GELU "
            "answers with a curve. That difference, small at first sight, changes the "
            "optimization landscape of a deep network and is the one GPT-2 adopts in its "
            "feed-forward network."
        ),
        h2("ReLU and its limits"),
        p(
            "ReLU is popular because it is cheap and works: <code>max(0, x)</code>. Its "
            "derivative is one for positive values and zero for negative ones. That "
            "simplicity has a price. At zero there is a corner the function cannot smooth "
            "out, and a neuron that always falls in the negative region stops receiving "
            "gradient: it shuts down. In very deep networks, accumulating inactive neurons "
            "can make learning harder. This does not make ReLU bad —it is used in a great "
            "many models— but it leaves room for alternatives."
        ),
        h2("The GELU curve"),
        p(
            "GELU, Gaussian Error Linear Unit, is defined as <code>x · Φ(x)</code>, where "
            "<code>Φ</code> is the cumulative distribution function of a standard Gaussian. "
            "The idea is to weight each input by the probability that a standard normal is "
            "below it: strongly negative values fade almost to zero, positive values pass "
            "almost intact, and the transition is smooth. Computing <code>Φ</code> exactly is "
            "expensive, so GPT-2 uses the approximation "
            "<code>0.5 · x · (1 + tanh(√(2/π) · (x + 0.044715 · x³)))</code>. It is the same "
            "one implemented in the book and the one used when loading pretrained weights."
        ),
        py(
            """
import math

def gelu(x):
    return 0.5 * x * (1 + math.tanh(
        math.sqrt(2 / math.pi) * (x + 0.044715 * x ** 3)
    ))

def relu(x):
    return max(0.0, x)

print(f"{'x':>5} {'ReLU':>9} {'GELU':>9}")
for x in (-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0):
    print(f"{x:>5.1f} {relu(x):>9.4f} {gelu(x):>9.4f}")
""",
            caption=(
                "Numerical comparison of ReLU and GELU with GPT-2's approximation. Notice "
                "that GELU does not reach zero for negative values."
            ),
        ),
        p(
            "GELU's curve resembles ReLU in the positive region and approaches zero in the "
            "negative one, but without cutting off. That smoothness has two consequences. "
            "First, the derivative changes continuously, giving the optimizer finer "
            "information near zero. Second, a neuron with a negative input can keep a small "
            "output and gradient instead of shutting down completely. The book summarizes it "
            "this way: GELU allows more nuanced parameter adjustments and tends to behave "
            "better in deep, complex architectures. It is not a universal guarantee but an "
            "empirical choice that worked for GPT-2."
        ),
        p(
            "Inside the block, GELU does not act alone: it lives between the two projections "
            "of the feed-forward network. The first projection expands each token from 768 "
            "to 3,072 dimensions; GELU introduces non-linearity; the second projection brings "
            "the vector back to 768. Without a non-linear activation, the two matrices would "
            "collapse into a single linear transformation and the network would lose "
            "capacity. GELU is therefore a small but essential piece of the block repeated "
            "twelve times in GPT-2 small. More recent models use variants such as SwiGLU, but "
            "the logic is the same: a smooth non-linearity between projections."
        ),
        callout(
            "warning",
            "Smooth does not mean magic",
            "Being differentiable everywhere does not guarantee that a model trains better "
            "in every case. The choice of activation interacts with initialization, "
            "normalization, depth, and data. In the book, GELU is the piece that accompanies "
            "GPT-2's FFN; the comparison with ReLU is there to explain the design, not to "
            "declare an absolute winner.",
        ),
        check(
            "What does a neuron gain with GELU over ReLU when it receives a negative input?",
            "GELU leaves a small, non-zero output and therefore a non-zero gradient. That "
            "neuron can keep contributing to learning, albeit less than a positive one. With "
            "ReLU, a negative input produces zero and blocks the gradient in that unit.",
        ),
        keypoints(
            [
                "ReLU is piecewise linear, cheap, and zeroes every negative value.",
                "GELU weights the input by the Gaussian cumulative distribution.",
                "GPT-2 uses a tanh approximation with the 0.044715 · x³ term.",
                "GELU's smoothness provides finer gradients near zero.",
                "GELU lets negative inputs keep a small signal.",
                "Inside the FFN, GELU supplies the non-linearity between projections.",
            ]
        ),
    ),
    key_points=(
        "ReLU has a corner at zero and fully shuts down negative values.",
        "GELU is a smooth curve based on the normal distribution.",
        "GPT-2 and the book use the tanh approximation.",
        "Smoothness gives the optimizer more information.",
        "Neurons with negative inputs do not fully switch off under GELU.",
        "GELU sits in the middle of the feed-forward network.",
    ),
)
