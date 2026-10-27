"""Chapter 3 glossary (EN)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="attention",
        definition=(
            "A mechanism that computes weights over sequence positions and mixes their "
            "representations according to their relevance to a query. In LLMs it replaces the "
            "single summary of recurrent models."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="query",
        definition=(
            "A token projection that expresses what information it seeks in other positions. It "
            "is compared with keys through a dot product to produce scores."
        ),
        lesson="consultas-claves-valores",
    ),
    GlossaryTerm(
        term="key",
        definition=(
            "A token projection that indicates what it offers to other tokens' queries. Keys are "
            "compared with each query and determine how attention is distributed."
        ),
        lesson="consultas-claves-valores",
    ),
    GlossaryTerm(
        term="value",
        definition=(
            "A token projection containing the content mixed when the token receives attention. "
            "The context vector is a weighted sum of values, not of keys."
        ),
        lesson="consultas-claves-valores",
    ),
    GlossaryTerm(
        term="dot product",
        definition=(
            "An operation that multiplies two vectors component by component and sums the "
            "products. In attention it measures alignment between a query and a key: larger "
            "values mean closer directions."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="scaled dot-product",
        definition=(
            "An attention variant that divides QKᵀ scores by the square root of the key dimension "
            "before softmax. It prevents scores from growing with dimension and the distribution "
            "from saturating."
        ),
        lesson="producto-escalado",
    ),
    GlossaryTerm(
        term="softmax",
        definition=(
            "A function that turns a row of scores into positive weights that sum to one. In "
            "attention it is applied after scaling and, for causal models, after masking."
        ),
        lesson="producto-escalado",
    ),
    GlossaryTerm(
        term="causal mask",
        definition=(
            "A restriction that prevents each position from attending to future tokens. It is "
            "implemented by replacing future scores with −∞ before softmax, so their weight is "
            "exactly zero."
        ),
        lesson="mascara-causal",
    ),
    GlossaryTerm(
        term="attention weight",
        definition=(
            "A normalized value that indicates how much one position contributes to another's "
            "context. It is computed for each input and changes with the sentence; it is not a "
            "trainable model parameter."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="attention score",
        definition=(
            "The unnormalized result of comparing a query with a key, usually a dot product. It "
            "is scaled and passed through softmax to obtain the weights."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="attention head",
        definition=(
            "One of the parallel attentions in a multi-head block. Each head has its own Q, K, "
            "and V projections and works with d_model / h dimensions."
        ),
        lesson="multi-head-attention",
    ),
    GlossaryTerm(
        term="context vector",
        definition=(
            "A token representation built as a weighted sum of the sequence's values. It replaces "
            "the isolated embedding in later transformer layers."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="alignment",
        definition=(
            "A correspondence between positions in two sequences, for example between the words "
            "of a sentence and its translation. Attention supports soft alignments without a "
            "one-to-one word mapping."
        ),
        lesson="por-que-atencion",
    ),
    GlossaryTerm(
        term="quadratic cost",
        definition=(
            "The growth of attention work proportional to n², because each of the n tokens is "
            "compared with all n tokens. It is counted per head and per layer."
        ),
        lesson="atencion-en-gpt",
    ),
)
