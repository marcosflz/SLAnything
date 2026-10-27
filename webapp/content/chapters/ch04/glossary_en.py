"""Chapter 4 glossary (English)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_EN: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="LayerNorm",
        definition=(
            "A normalization that centers and scales each token's activations along the "
            "embedding dimension. It uses a per-vector mean and variance plus a learnable "
            "shift and scale."
        ),
        lesson="layer-normalization",
    ),
    GlossaryTerm(
        term="GELU",
        definition=(
            "A smooth activation, Gaussian Error Linear Unit, that weights each input by "
            "the Gaussian cumulative distribution. GPT-2 uses a tanh approximation of it "
            "inside the feed-forward network."
        ),
        lesson="gelu",
    ),
    GlossaryTerm(
        term="feed-forward network (FFN)",
        definition=(
            "The transformer subnetwork made of two linear projections and an activation. "
            "It expands each token's dimension, applies GELU, and projects back to the "
            "original dimension without mixing tokens."
        ),
        lesson="feed-forward",
    ),
    GlossaryTerm(
        term="transformer block",
        definition=(
            "The unit that combines LayerNorm, multi-head attention, a feed-forward "
            "network, and two residual connections. GPT-2 small stacks twelve blocks with "
            "the same shape but different weights."
        ),
        lesson="bloque-transformer",
    ),
    GlossaryTerm(
        term="residual connection",
        definition=(
            "The sum of a sublayer's input and output, x + f(x), which creates a direct path "
            "for information and gradients. It requires the input and output to have the "
            "same shape."
        ),
        lesson="conexiones-residuales",
    ),
    GlossaryTerm(
        term="Pre-LN",
        definition=(
            "The arrangement that applies LayerNorm before attention and before the "
            "feed-forward network. GPT-2 uses it, and it usually gives more stable training "
            "dynamics than Post-LN."
        ),
        lesson="bloque-transformer",
    ),
    GlossaryTerm(
        term="Post-LN",
        definition=(
            "The original transformer arrangement in which LayerNorm is applied after each "
            "sublayer rather than before it. It can be harder to train in deep stacks."
        ),
        lesson="layer-normalization",
    ),
    GlossaryTerm(
        term="weight tying",
        definition=(
            "A technique that reuses the token embedding matrix as the output head matrix. "
            "In GPT-2 small it avoids duplicating 38,597,376 parameters and explains the "
            "difference between 124 and 163 million."
        ),
        lesson="cabeza-de-salida",
    ),
    GlossaryTerm(
        term="output head",
        definition=(
            "The final linear layer that projects each 768-dimensional context vector into "
            "the vocabulary size and produces the next-token logits. In GPT-2 it has no "
            "bias."
        ),
        lesson="cabeza-de-salida",
    ),
    GlossaryTerm(
        term="embedding dimension (emb_dim)",
        definition=(
            "The number of components in each vector that represents a token; in GPT-2 "
            "small it is 768. It determines the size of the projections and a large part of "
            "the model's cost."
        ),
        lesson="configuracion-gpt",
    ),
    GlossaryTerm(
        term="QKV projection",
        definition=(
            "The three linear transformations that turn each token into a query, a key, and "
            "a value for attention. In GPT-2 small each one projects 768 dimensions to 768."
        ),
        lesson="bloque-transformer",
    ),
    GlossaryTerm(
        term="residual stream",
        definition=(
            "The main path that runs through every block, adding each sublayer's output as "
            "it goes. It is the usual metaphor for how information is accumulated and "
            "preserved in a deep transformer."
        ),
        lesson="conexiones-residuales",
    ),
)
