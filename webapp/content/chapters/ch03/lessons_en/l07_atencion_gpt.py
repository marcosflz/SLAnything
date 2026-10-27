"""Lesson 7 · Attention inside GPT."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lab,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=7,
    slug="atencion-en-gpt",
    title="Attention inside GPT",
    summary=(
        "GPT stacks decoder-only blocks with causal attention, normalization, and feed-forward "
        "networks. That order explains both its capability and its quadratic cost."
    ),
    minutes=10,
    objectives=(
        "Place causal attention inside a decoder-only block.",
        "Describe the order of normalization, attention, residual, and feed-forward.",
        "Explain why attention costs O(n²) per layer and head.",
        "Compute the number of attention scores for a length and head count.",
    ),
    blocks=(
        lead(
            "In the previous chapter, attention was an isolated module. In GPT it is one piece "
            "inside a block that repeats dozens of times. Understanding where it sits —and what "
            "happens before and after— explains why the model can generate text and why long "
            "context is expensive."
        ),
        p(
            "GPT is <strong>decoder-only</strong>: it has no separate encoder and no cross-attention "
            "over another sequence. Each block processes the same sequence it receives. First it "
            "normalizes the representations; then it applies multi-head attention with a causal "
            "mask; it adds the original input through a residual connection; it normalizes again; "
            "it passes through a position-wise feed-forward network; and it adds another residual. "
            "GPT-2 small stacks 12 of these blocks and has 117 million parameters."
        ),
        h2("The decoder-only block"),
        p(
            "The exact order varies across families. GPT-2 uses <strong>pre-normalization</strong>: "
            "LayerNorm comes before attention and before feed-forward, and a residual connection "
            "wraps each sublayer. The original transformer used post-normalization: the residual "
            "sum came first and normalization after. Pre-normalization makes deep stacks easier to "
            "train because it keeps the scale of activations entering each sublayer stable."
        ),
        p(
            "Attention is the only operation in the block that mixes information across positions. "
            "Feed-forward is applied to each token separately and transforms its representation, "
            "but does not combine it with others. Residual connections let the original information "
            "reach later layers intact and give the gradient a direct path backward. Without them, "
            "stacking 12 or 96 blocks would be much harder."
        ),
        lab("transformer"),
        h2("From layer to prediction"),
        p(
            "After the last block, a final normalization prepares the representations and a linear "
            "head projects them to the vocabulary size. Those scores are the <strong>logits</strong>; "
            "softmax turns them into a distribution over the next token. The model does not choose "
            "a word directly: it produces a distribution, and the sampling procedure decides how "
            "to use it. During training, the loss compares that distribution with the token that "
            "actually followed in the corpus."
        ),
        p(
            "At inference time, generating one token at a time seems wasteful: if we have already "
            "processed the prompt, why recompute everything for the next token? The answer is the "
            "<strong>key-value cache</strong>. The K and V representations of previous positions do "
            "not change when we append a token at the end, so they are stored. The new token "
            "computes its query and appends its key and value to the cache; attention is computed "
            "over what is stored. That reduces work per step, although attention still compares "
            "against every stored position."
        ),
        h2("The price of looking"),
        p(
            "For a sequence of n tokens, each head builds an n × n score matrix: every position is "
            "compared with every position. That matrix is normalized and used to mix the values. "
            "Attention cost grows with n², and the memory needed to materialize the matrix does too. "
            "In a model with h heads and L layers, the number of scores per layer is h · n²; across "
            "all layers, L · h · n²."
        ),
        table(
            ["Length n", "Scores per head", "12 heads, one layer", "Approx."],
            [
                ["128", "16,384", "196,608", "0.2 M"],
                ["1024", "1,048,576", "12,582,912", "12.6 M"],
                ["4096", "16,777,216", "201,326,592", "201 M"],
                ["8192", "67,108,864", "805,306,368", "805 M"],
            ],
            caption=(
                "Attention scores for one layer with 12 heads. Doubling the length multiplies the "
                "number of comparisons by four."
            ),
            note="Our own calculation: n² scores per head, multiplied by 12 heads.",
        ),
        p(
            "With 1024 tokens —GPT-2's window— and 12 heads, a single layer generates about 12.6 "
            "million scores. With 4096 tokens, about 201 million. The difference is not linear: "
            "doubling the length quadruples attention work. That is why very long-context models "
            "need efficient attention, parallelism, and extra memory. Some kernels reduce memory "
            "use without changing the asymptotic order; other methods approximate or reorganize "
            "the computation."
        ),
        p(
            "Do not confuse attention cost with total model cost. The Q, K, and V projections, the "
            "feed-forward network, and the output head also cost, and for short sequences they may "
            "dominate. Attention becomes the bottleneck as n grows, because its quadratic term "
            "eventually wins. That is the practical reason why context length is an expensive "
            "resource, not an arbitrary number."
        ),
        callout(
            "warning",
            "O(n²) is per layer and per head",
            "Quadratic cost does not describe the whole model as one operation. It applies to the "
            "attention matrix of each head in each layer. A model with 12 layers and 12 heads "
            "repeats that pattern 144 times per sequence. O(n²) describes growth, not an absolute "
            "operation count.",
        ),
        check(
            "How many attention scores does one layer with 12 heads generate for 1024 tokens? Why "
            "is 1024 × 12 not enough?",
            "It generates 12 × 1024² = 12,582,912 scores, about 12.6 million. 1024 × 12 is not "
            "enough because each token is compared with all tokens, not just one: there are 1024 × "
            "1024 pairs per head, then multiplied by 12 heads.",
        ),
        keypoints(
            [
                "GPT is decoder-only: each block processes the same sequence with causal attention.",
                "GPT-2 small stacks 12 blocks, uses 12 heads of 64 dimensions, and has 117 M parameters.",
                "Attention mixes positions; feed-forward transforms each token separately.",
                "Residual connections and normalization make deep stacks viable.",
                "Attention costs O(n²) per layer and head: n tokens produce n² scores.",
                "The key-value cache speeds up generation but does not remove training's quadratic cost.",
            ]
        ),
    ),
    key_points=(
        "Causal attention lives inside a decoder-only block with residuals and feed-forward.",
        "GPT-2 small: 12 layers, 12 heads, 768 dimensions, 117 M parameters.",
        "The final representation is projected to the vocabulary and normalized with softmax.",
        "Attention produces n² scores per head and layer.",
        "The KV cache accelerates inference; training cost remains quadratic.",
    ),
)
