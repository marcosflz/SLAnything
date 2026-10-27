"""Lesson 3 · Transformer and attention."""

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
    table,
)

LESSON = Lesson(
    number=3,
    slug="transformer-y-atencion",
    title="Transformer and attention",
    summary=(
        "Encoder, decoder, and self-attention: the architecture that changed language "
        "processing and the two families that adapted it."
    ),
    minutes=12,
    objectives=(
        "Describe the two modules of the original transformer and the asymmetry between them.",
        "Explain why GPT keeps only the decoder.",
        "Understand self-attention as contextual weighting, not a bag of words.",
        "Compare BERT and GPT by architecture, objective, and typical use.",
    ),
    blocks=(
        lead(
            "In 2017, the paper “Attention Is All You Need” introduced an architecture that "
            "dispensed with recurrence and organized everything around attention. GPT, BERT, "
            "and most of the models we use today descend from that design."
        ),
        h2("From encoder to decoder"),
        p(
            "The novelty was not inventing attention —it already existed— but building the "
            "whole architecture around it, without recurrence; that allows tokens to be "
            "processed in parallel during training. The original transformer was built for "
            "translation and had two modules. The <strong>encoder</strong> read the complete "
            "input sentence and built a contextual representation of each token. The "
            "<strong>decoder</strong> generated the translation token by token, looking at the "
            "encoder's representation and its own partial output. That asymmetry is key: the "
            "encoder sees the whole input; the decoder only sees the past of what it is "
            "generating, which is why generation is autoregressive. The paper stacked six "
            "encoder and six decoder blocks. GPT keeps only the decoder because its task is "
            "exactly that: continuing a sequence forward. GPT-3 took the same family to 96 "
            "layers and 175 billion parameters. Not every transformer is an LLM: it is also "
            "used in vision and audio. The “Transformer” lab lets you walk through the stages "
            "in the figure."
        ),
        figure(
            "img/ch01/fig_1_4_transformer.png",
            "Diagram of the original transformer: the encoder processes the input sentence and the decoder generates the translation step by step.",
            "The encoder processes the whole sentence; the decoder generates the translation "
            "word by word and reuses its own output.",
            credit="Figure 1.4 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        lab("transformer"),
        h2("Self-attention"),
        p(
            "<strong>Self-attention</strong> is the mechanism that lets each token weight the "
            "relevance of the others. To represent “tired” in “The cat did not cross the "
            "street because it was tired”, the model can give a lot of weight to “cat” and "
            "little to “street”: the connection goes beyond distance and surface order. It is "
            "not a bag of words: tokens are compared with each other and position also "
            "matters, so “the dog bites the cat” is not represented the same as “the cat bites "
            "the dog”. Internally, each token is projected into three vectors: a "
            "<em>query</em> (what it seeks), a <em>key</em> (what it offers), and a "
            "<em>value</em> (what content it contributes). Comparing queries and keys produces "
            "the weights; the values are combined with them. That representation changes with "
            "context: the same word does not weigh the same in two different sentences. In "
            "each layer, several attention heads (<em>multi-head</em>) observe different "
            "relationships in parallel; residual connections and normalization help "
            "information flow and keep training stable. You do not need to memorize the "
            "formulas: remember that attention builds contextual representations, not "
            "dictionaries of isolated words. The “Attention” lab lets you choose a word and "
            "see which others it weights most."
        ),
        lab("attention"),
        py(
            """
import matplotlib.pyplot as plt

SENTENCE = ["The", "cat", "did", "not", "cross", "the", "street", "because", "it", "was", "tired"]
WEIGHTS = [0.01, 0.20, 0.01, 0.02, 0.04, 0.01, 0.03, 0.02, 0.09, 0.04, 0.53]

total = sum(WEIGHTS)
weights = [weight / total for weight in WEIGHTS]
order = sorted(range(len(weights)), key=lambda i: weights[i])
labels = [SENTENCE[i] for i in order]
values = [weights[i] for i in order]
colors = ["#C77800" if label == "tired" else "#9DB7F5" for label in labels]

fig, ax = plt.subplots(figsize=(8, 3.6))
bars = ax.barh(labels, values, color=colors)
ax.set_xlabel("attention weight")
ax.set_title("What does “tired” attend to?")
for bar, value in zip(bars, values):
    ax.text(value + 0.005, bar.get_y() + bar.get_height() / 2, f"{value:.0%}", va="center")
plt.tight_layout()
plt.show()

strongest = SENTENCE[weights.index(max(weights))]
print(f"“tired” pays most attention to “{strongest}”.")
""",
            caption=(
                "Illustrative attention weights, normalized to sum to 1. Change the "
                "weights and watch the chart move."
            ),
        ),
        table(
            ["Aspect", "BERT", "GPT"],
            [
                [
                    "Architecture",
                    "Encoder-only: sees the whole sentence in both directions.",
                    "Decoder-only: looks only at the past and generates left to right.",
                ],
                [
                    "Objective",
                    "Fill in masked words (<em>masked language modeling</em>).",
                    "Predict the next token (<em>causal language modeling</em>).",
                ],
                [
                    "Typical use",
                    "Classification, information extraction, and sentiment analysis.",
                    "Text generation, dialogue, code, and assistants.",
                ],
            ],
            caption=(
                "BERT and GPT: two ways of using the transformer. BERT understands a closed "
                "text; GPT continues it."
            ),
            note="Figure 1.5 summarizes the two objectives.",
        ),
        figure(
            "img/ch01/fig_1_5_bert_vs_gpt.png",
            "Comparison between BERT, which fills in masked words, and GPT, which predicts the next token.",
            "BERT fills gaps and looks in both directions; GPT completes text from left to "
            "right using only the past.",
            credit="Figure 1.5 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        callout(
            "warning",
            "Not every transformer is an LLM",
            "The transformer architecture is also used in vision, audio, and multimodal "
            "models. An LLM is a <strong>generative</strong> transformer trained at scale to "
            "process and produce language. The architecture is the same family; the objective "
            "and the data change.",
        ),
        check(
            "Why does GPT use only the decoder and not need an encoder?",
            "Because it is trained to continue text: given a prefix, it predicts the next "
            "token and keeps appending its own output. The decoder, with causal attention, "
            "can already look at the whole past; a separate encoder that read the complete "
            "sentence would not fit a task that must move forward without seeing the future.",
        ),
        keypoints(
            [
                "The original transformer combines an encoder that reads the whole input and a decoder that generates token by token.",
                "GPT is decoder-only because its task is to continue text from left to right.",
                "Self-attention weights the relevance of other tokens and connects distant information.",
                "It is not a bag of words: relationships and positions matter.",
                "BERT and GPT adapt the transformer to different goals: filling gaps versus predicting the next token.",
            ]
        ),
    ),
    key_points=(
        "The original transformer has an encoder and a decoder; GPT keeps only the decoder.",
        "The decoder generates autoregressively and only looks at the past.",
        "Self-attention builds contextual representations and connects distant tokens.",
        "Multi-head attention, residual connections, and normalization make the architecture more expressive and stable.",
        "BERT uses the encoder to understand; GPT uses the decoder to generate.",
    ),
)
