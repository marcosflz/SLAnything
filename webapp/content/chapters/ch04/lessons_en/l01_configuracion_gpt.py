"""Lesson 1 · Configuring a small GPT."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=1,
    slug="configuracion-gpt",
    title="Configuring a small GPT",
    summary=(
        "The seven keys of GPT-2 small, what each one controls, and where the 124 "
        "million parameters used as the book's working model come from."
    ),
    minutes=10,
    objectives=(
        "Read every key in the GPT_CONFIG_124M dictionary.",
        "Calculate the parameters of the embeddings, attention, and feed-forward network.",
        "Distinguish the 124 M model with weight tying from the 163 M model without it.",
        "Explain why a small GPT is enough to learn the architecture.",
    ),
    blocks=(
        lead(
            "A GPT does not start with an abstract idea but with a handful of numbers. The "
            "GPT-2 small configuration fits in a seven-key dictionary, yet it determines how "
            "many tokens the model can read, how many layers the information travels through, "
            "and how many parameters must be trained. In this lesson you will learn to read "
            "that configuration and to verify where the 124 million figure comes from."
        ),
        h2("Seven numbers that define the model"),
        p(
            "The book calls that dictionary <code>GPT_CONFIG_124M</code>. It is not a black "
            "box: every entry has a direct consequence for tensor shapes and cost. The table "
            "summarizes the seven keys and what each one controls. The values are those of "
            "GPT-2 small as described by Radford and colleagues; the book corrects the "
            "original 117 million figure and works with 124 million."
        ),
        table(
            ["Key", "Value", "What it controls"],
            [
                ["<code>vocab_size</code>", "50,257", "Distinct tokens the model can read and predict."],
                ["<code>context_length</code>", "1,024", "Maximum positions in the context window."],
                ["<code>emb_dim</code>", "768", "Components in each token vector."],
                ["<code>n_heads</code>", "12", "Attention heads working in parallel."],
                ["<code>n_layers</code>", "12", "Stacked transformer blocks."],
                ["<code>drop_rate</code>", "0.1", "Fraction of activations dropped during training."],
                ["<code>qkv_bias</code>", "False", "Whether Q, K, and V projections carry a bias."],
            ],
            caption="GPT-2 small's configuration, using the names from the book.",
            note=(
                "The per-head dimension is 768 / 12 = 64. It is not a separate key: it "
                "follows from emb_dim and n_heads."
            ),
        ),
        p(
            "The combination is not arbitrary. A dimension of 768 split across 12 heads "
            "leaves 64 components per head, enough for each head to specialize in one kind "
            "of relationship without exploding the cost. Twelve layers allow composed "
            "transformations, and 1,024 positions cover short texts or brief conversations. "
            "Dropout at 10% regularizes; <code>qkv_bias</code> starts disabled, as in many "
            "modern models, although the book revisits it when loading GPT-2 weights."
        ),
        h2("Where the 124 million come from"),
        p(
            "The figure is not memorized: it is calculated. Token embeddings take "
            "50,257 × 768 = 38,597,376 parameters; positional embeddings take "
            "1,024 × 768 = 786,432. Each block contains four 768 × 768 attention "
            "projections —three for Q, K, and V, one for the output—, a feed-forward network "
            "that expands to 3,072 and returns to 768, and two LayerNorms. The complete block "
            "is about 7.09 million parameters; twelve blocks, about 85.03 million. Adding the "
            "embeddings and the final normalization gives 124,412,160, provided the output "
            "head reuses the embedding matrix. The code below checks it step by step; this is "
            "our own calculation from the book's dimensions."
        ),
        py(
            """
VOCAB = 50_257
CONTEXT = 1_024
EMB = 768
LAYERS = 12

tok_emb = VOCAB * EMB
pos_emb = CONTEXT * EMB
qkv = 3 * EMB * EMB                 # qkv_bias=False
out_proj = EMB * EMB + EMB          # the output projection does have a bias
attn = qkv + out_proj
ffn = EMB * (4 * EMB) + 4 * EMB + (4 * EMB) * EMB + EMB
ln = 2 * EMB                        # scale and shift of one LayerNorm
block = attn + ffn + 2 * ln
tied = tok_emb + pos_emb + LAYERS * block + ln
head = VOCAB * EMB
untied = tied + head

print(f"Embeddings: {tok_emb:,} + {pos_emb:,} = {tok_emb + pos_emb:,}")
print(f"Attention per block: {attn:,} (QKV {qkv:,} + output {out_proj:,})")
print(f"FFN per block: {ffn:,}")
print(f"Complete block: {block:,}")
print(f"12 blocks + embeddings + final LN: {tied:,}")
print(f"Output head: {head:,}")
print(f"Without weight tying: {untied:,}")
print(f"fp32 memory without tying: {untied * 4 / 1024**2:.2f} MB")
""",
            caption=(
                "GPT-2 small parameter count. The last line assumes 4 bytes per parameter "
                "in 32-bit floating point."
            ),
        ),
        p(
            "The result matches the book: 124,412,160 parameters with weight tying and "
            "163,009,536 without it. The difference is exactly the 38,597,376 parameters of "
            "the output head, which duplicates the embedding table. In 32-bit floating point "
            "the untied model takes 621.83 MB; storing the weights alone is already a memory "
            "exercise. The book implements a separate head so it can train and compare, and "
            "leaves weight sharing for chapter 6, when it loads the pretrained weights."
        ),
        callout(
            "note",
            "124 M is not a round number",
            "The exact total is 124,412,160. If you see 163,009,536, it is not a mistake: "
            "it is the same model with an independent output head. The 38.6 M difference is "
            "the matrix that projects 768 dimensions into the vocabulary. Original GPT-2 "
            "reuses the embedding matrix to save memory and computation.",
        ),
        check(
            "If the output head has 38.6 M parameters, why is the model considered 124 M "
            "rather than 163 M?",
            "Because in the original GPT-2 architecture the output head shares its weights "
            "with the token embedding table. They are not 38.6 M additional parameters but "
            "the same matrix reused. Counting them separately, as the book's implementation "
            "does, produces 163 M.",
        ),
        keypoints(
            [
                "GPT-2 small's configuration fits in seven keys: vocabulary, context, dimension, heads, layers, dropout, and QKV bias.",
                "Each token is represented by 768 dimensions and each attention head works with 64.",
                "Token embeddings contribute 38,597,376 parameters; positional embeddings contribute 786,432.",
                "Attention and the FFN add about 7.09 M parameters per block; twelve blocks add about 85.03 M.",
                "With weight tying the total is 124,412,160; with a separate head it is 163,009,536.",
                "The small model is not a toy: it is the same architecture with manageable dimensions.",
            ]
        ),
    ),
    key_points=(
        "The configuration fixes vocabulary, context, dimension, heads, and layers.",
        "Token embeddings are the largest table in the model.",
        "Attention and the FFN repeat in each of the twelve blocks.",
        "The exact total with weight tying is 124,412,160 parameters.",
        "A separate head adds 38.6 M and brings the total to 163,009,536.",
        "A small GPT lets you understand and train the same architecture.",
    ),
)
