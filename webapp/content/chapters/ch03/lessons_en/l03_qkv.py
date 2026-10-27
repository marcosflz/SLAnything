"""Lesson 3 · Queries, keys, and values."""

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
    table,
)

LESSON = Lesson(
    number=3,
    slug="consultas-claves-valores",
    title="Queries, keys, and values",
    summary=(
        "Q, K, and V are three learned projections of the same token: what it seeks, what it "
        "offers, and what it contributes. Attention is a soft search among them."
    ),
    minutes=12,
    objectives=(
        "Distinguish the roles of query, key, and value.",
        "Explain how Wq, Wk, and Wv transform embeddings.",
        "Follow scores and weights with concrete dimensions.",
        "Relate GPT-2 dimensions to the split across heads.",
    ),
    blocks=(
        lead(
            "The names <strong>query</strong>, <strong>key</strong>, and <strong>value</strong> "
            "come from databases and information retrieval. Picture a library: you submit a "
            "query, look for keys that match it, and retrieve the associated values. Attention "
            "does something similar, but instead of selecting one record, it mixes all of them "
            "with a weight."
        ),
        p(
            "Each input token is projected into three different vectors by three learned "
            "matrices. The query (<em>q</em>) represents what that token is looking for; the key "
            "(<em>k</em>), what it offers to others; the value (<em>v</em>), the content it "
            "contributes if attended to. All three come from the same embedding, but they are not "
            "interchangeable: they play different roles and are trained separately."
        ),
        h2("Three projections, three roles"),
        p(
            "If the input is a matrix X with one row per token, the projections are Q = X · "
            "W<sub>q</sub>, K = X · W<sub>k</sub>, and V = X · W<sub>v</sub>. Each matrix has "
            "shape d<sub>in</sub> × d<sub>out</sub>. In modern transformers, input and output "
            "dimensions usually match —GPT-2 small uses 768— although toy examples reduce them so "
            "the arithmetic is easy to follow. The key dimension, d<sub>k</sub>, is the one that "
            "appears in the scaling of lesson 4."
        ),
        figure(
            "img/ch03/qkv.svg",
            "Diagram of the Q, K, and V projections from a token, followed by score computation, softmax, and a weighted sum of values.",
            "One token is projected into a query, a key, and a value. The query is compared with "
            "all keys; the resulting weights mix the values.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        lab("qkv"),
        h2("A soft search"),
        p(
            "Scores are computed from Q and K: each query is compared with every key through a dot "
            "product. Those scores are normalized with softmax and become attention weights. "
            "Finally, the context vector is the weighted sum of the values V. Unlike a database, "
            "there is no exact match: every value contributes, some more than others. That "
            "softness is what makes the mechanism trainable with gradient descent."
        ),
        p(
            "An example with a four-dimensional query: q = [0.8, 0.2, −0.4, 0.6]. Against three "
            "keys, the dot products are 0.50, 0.16, and 0.28. Dividing by √4 = 2 gives 0.25, 0.08, "
            "and 0.14; after softmax, the weights are approximately 0.365, 0.308, and 0.327. The "
            "first key is the closest match, but the other two keep considerable weight. If the "
            "associated values were v<sub>1</sub>, v<sub>2</sub>, and v<sub>3</sub>, the context "
            "would be 0.365 v<sub>1</sub> + 0.308 v<sub>2</sub> + 0.327 v<sub>3</sub>. These "
            "values are our own example for following the arithmetic."
        ),
        p(
            "Why not use the embeddings directly as queries and keys? Because the model needs to "
            "learn an asymmetric relation. What a token seeks need not match what it offers. By "
            "projecting into different subspaces, the network can specialize one direction for “I "
            "am looking for a subject” and another for “I offer a subject,” even though the original "
            "embedding is the same. The matrices W<sub>q</sub>, W<sub>k</sub>, and W<sub>v</sub> "
            "are parameters: they are adjusted during training and not written by hand."
        ),
        h2("Dimensions that matter"),
        p(
            "In the original transformer, the base model had 512 dimensions and 8 heads; each head "
            "worked with 64 dimensions. GPT-2 small has 768 dimensions, 12 heads, and a 1024-token "
            "window; GPT-2 large has 1600 dimensions and 25 heads. In all these cases, the "
            "dimension per head is 64. That is no accident: the design divides a fixed budget of "
            "dimensions among several heads so each one can specialize without multiplying the "
            "cost by the number of heads."
        ),
        table(
            ["Model", "model dimension", "heads", "dimension per head"],
            [
                ["Book toy example", "3 → 2", "1", "2"],
                ["Original transformer", "512", "8", "64"],
                ["GPT-2 small", "768", "12", "64"],
                ["GPT-2 large", "1600", "25", "64"],
            ],
            caption=(
                "The dimension budget is split across heads. In GPT-2 the total dimension is much "
                "larger than in the original transformer, but the dimension per head stays at 64."
            ),
            note="Architecture figures cited in the book; the toy example uses d_in = 3 and d_out = 2.",
        ),
        callout(
            "info",
            "Projections are not dictionaries",
            "W<sub>q</sub>, W<sub>k</sub>, and W<sub>v</sub> contain no definitions or symbolic "
            "rules. They are matrices of numbers adjusted to minimize the task loss. If a "
            "direction ends up correlating with a linguistic function, that is an emergent effect "
            "of training, not an instruction we wrote.",
        ),
        check(
            "Why does attention use three different matrices instead of comparing the original "
            "embeddings with each other?",
            "Because query, key, and value play different roles. The query expresses what the "
            "current token seeks; the key, what each candidate offers; the value, what content is "
            "mixed. With three learned projections, the model can specialize each role in a "
            "subspace and break the symmetry of comparing a vector with itself.",
        ),
        keypoints(
            [
                "Each token is projected into a query, a key, and a value.",
                "The query is compared with all keys to produce scores.",
                "Softmax turns scores into weights that sum to one.",
                "The context is the weighted sum of the values.",
                "Projections are learned parameters; attention weights are dynamic.",
                "GPT-2 small uses 768 dimensions, 12 heads, and 64 dimensions per head.",
            ]
        ),
    ),
    key_points=(
        "Query, key, and value are three learned projections of the same token.",
        "The query seeks, the key offers, and the value contributes content.",
        "Attention is a soft search: every value contributes with some weight.",
        "Dimensions per head divide the model's budget.",
        "GPT-2 small: 768 dimensions, 12 heads, 64 per head.",
    ),
)
