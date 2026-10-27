"""Lesson 4 · From token to vector."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=4,
    slug="vocabulario-y-embeddings",
    title="From token to vector",
    summary=(
        "An identifier has no geometry. For the network to operate, each token becomes a row "
        "in a matrix: its embedding. Here we count rows, columns, and parameters."
    ),
    minutes=11,
    objectives=(
        "Explain why IDs are not enough as network input.",
        "Describe an embedding matrix as a lookup table.",
        "Compare one-hot encoding with a dense representation.",
        "Calculate the parameters of an embedding layer.",
    ),
    blocks=(
        lead(
            "We already know how to turn text into integers. But an integer is a label, not a "
            "position in a space. The network needs dense, learnable vectors. The layer that "
            "performs this conversion is the <strong>embedding layer</strong>, and its size "
            "shapes memory and model capacity."
        ),
        p(
            "Imagine a vocabulary of six tokens and vectors of three dimensions. The embedding "
            "layer is a 6 × 3 matrix: one row per token, one column per dimension. The token "
            "with ID 3 returns the fourth row —remember that Python counts from zero—. There is "
            "no mysterious operation: it is a table lookup. The table starts with small values "
            "and is optimised during training."
        ),
        p(
            "In the book, the minimal example uses exactly that: <code>vocab_size = 6</code> and "
            "<code>output_dim = 3</code>. Passing ID 3 through the layer returns "
            "<code>[-0.4015, 0.9666, -1.1481]</code>, which matches the fourth row of the "
            "matrix. Passing four IDs at once returns a 4 × 3 matrix. The output shape adds a "
            "dimension to the batch: if a tensor of shape <code>(batch, context)</code> goes in, "
            "a tensor <code>(batch, context, dimension)</code> comes out."
        ),
        h2("One-hot versus dense"),
        p(
            "A classical alternative is <strong>one-hot</strong> encoding: a vector as long as "
            "the vocabulary, with a 1 at the token's position and zeros elsewhere. For a "
            "vocabulary of 50,257, every token would occupy a vector of 50,257 numbers, almost "
            "all zero. Multiplying that vector by a weight matrix produces precisely the "
            "corresponding row. The embedding layer does the same without building the sparse "
            "vector: it selects the row directly. This is an implementation optimisation, not a "
            "conceptual change."
        ),
        p(
            "The dense representation has another advantage: each dimension can specialise in a "
            "learned aspect. You should not read each column as “gender” or “number”; in practice "
            "the directions are combinations and their meaning is discovered after training. "
            "What matters is that the whole vector is updated by gradients and can encode "
            "contextual regularities."
        ),
        table(
            ["Model", "Vocabulary", "Dimension", "Matrix parameters", "Calculation"],
            [
                ["Book toy example", "6", "3", "18", "6 × 3"],
                ["GPT-2 small", "50,257", "768", "38,597,376", "50,257 × 768"],
                ["GPT-3 175B", "50,257", "12,288", "617,558,016", "50,257 × 12,288"],
            ],
            caption=(
                "Parameters of a single token matrix. Real models add positional embeddings and "
                "many other layers."
            ),
            note=(
                "GPT-2 small and GPT-3 are figures quoted in the book for vocabulary and "
                "dimension. The products are our arithmetic to show order of magnitude; they do "
                "not include biases or positional embeddings."
            ),
        ),
        callout(
            "info",
            "A matrix that learns",
            "At initialisation, rows are noise. After training, tokens that appear in similar "
            "contexts tend to have similar vectors. The similarity is not programmed: it emerges "
            "from minimising the prediction loss.",
        ),
        p(
            "The parameter count is <code>V × d</code>, where <code>V</code> is vocabulary size "
            "and <code>d</code> is dimension. Doubling the dimension doubles this layer's "
            "parameters; doubling the vocabulary does too. In large models the embedding matrix "
            "can hold hundreds of millions of parameters, although it remains a fraction of the "
            "total. In GPT-3, for example, 617 million against 175 billion parameters for the "
            "whole model."
        ),
        p(
            "One subtlety is worth anticipating: the same word receives the same vector in any "
            "position. The embedding layer does not know whether “cat” is the first or last word. "
            "That information is added later with positional embeddings, which we will see at the "
            "end of the chapter. First we need to build training sequences; the next two lessons "
            "handle that."
        ),
        check(
            "A vocabulary has 10,000 tokens and the dimension is 128. How many parameters does the embedding matrix have?",
            "10,000 × 128 = 1,280,000 parameters. With biases, add 10,000; positional embeddings "
            "are a separate matrix. The basic count is always vocabulary × dimension.",
        ),
        h2("Why this layer matters"),
        p(
            "The embedding matrix is the first representation of language inside the model. "
            "Everything that follows —attention, feed-forward, residual layers— operates on "
            "these vectors. If the vocabulary is poorly built, the matrix spends rows on rare "
            "tokens and leaves little data for frequent ones. If the dimension is too small, the "
            "model lacks room to distinguish nuances; if it is too large, it pays memory and "
            "compute with no guarantee of improvement."
        ),
        p(
            "In GPT models, the embedding dimension matches the transformer's hidden dimension. "
            "GPT-2 small uses 768; GPT-3 uses 12,288. The match is not accidental: it lets the "
            "embedding output enter the attention layers directly without an extra projection. "
            "It is an architectural decision preserved across the family."
        ),
        keypoints(
            [
                "An ID is a label; an embedding is a dense, learnable vector.",
                "The embedding layer is a lookup in a V × d matrix.",
                "One-hot plus matrix multiplication is equivalent to selecting a row.",
                "Matrix parameters equal vocabulary × dimension.",
                "The dimension matches the transformer's hidden dimension in GPT.",
                "Every token gets the same vector in any position; position is added separately.",
            ]
        ),
    ),
    key_points=(
        "The embedding layer turns each ID into a row of a V × d matrix.",
        "It is equivalent to one-hot followed by multiplication, but more efficient.",
        "Its parameters are vocabulary × dimension.",
        "Vectors are learned and carry no position by themselves.",
    ),
    quiz_id=None,
)
