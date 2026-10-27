"""Lesson 7 · How an LLM is built."""

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
    number=7,
    slug="como-se-construye",
    title="How an LLM is built",
    summary=(
        "The book's map: tokenization, embeddings, attention, GPT architecture, "
        "pretraining, classification, and instructions, with cost as a compass."
    ),
    minutes=8,
    objectives=(
        "Walk through the stages of building an LLM.",
        "Place each chapter of the book in the complete pipeline.",
        "Explain why we start with a small model.",
        "Estimate training cost with the rule FLOPs ≈ 6 · N · D.",
    ),
    blocks=(
        lead(
            "The book does not start with a 175 billion parameter model. It starts with a "
            "small version that fits on a laptop and can be understood line by line. Scale "
            "comes later; first, the pieces."
        ),
        p(
            "The goal is to build a GPT with about <strong>124 million parameters</strong>, a "
            "size comparable to GPT-2 small. It is not a final product: it is a "
            "<strong>teaching vehicle</strong>. It has the same components as a large model "
            "—tokenization, embeddings, attention, transformer blocks, and an output head— but "
            "it can be trained and debugged on consumer hardware. Understanding each piece "
            "matters more than reproducing GPT-3's cost. When you need capacity, you can load "
            "already-trained open weights."
        ),
        figure(
            "img/ch01/fig_1_9_roadmap.png",
            "The three stages of the book: build the architecture and prepare the data, pretrain the base model, and specialize it with finetuning.",
            "Build, pretrain, and specialize: the three stages that organize chapters 2 to 7.",
            credit="Figure 1.9 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        h2("The plan, chapter by chapter"),
        table(
            ["Ch.", "Question it answers", "What you take away"],
            [
                ["<strong>1</strong>", "What is an LLM and how does everything fit?", "The mental map of this chapter"],
                ["<strong>2</strong>", "How do we turn text into numbers?", "Tokenizer, embeddings, and sliding window"],
                ["<strong>3</strong>", "How does the model look at context?", "Self-attention, causal attention, and multi-head"],
                ["<strong>4</strong>", "How is GPT assembled?", "Complete architecture and text generation"],
                ["<strong>5</strong>", "How is it trained?", "Training loop, evaluation, and base model"],
                ["<strong>6</strong>", "How do we classify text?", "Finetuning for classification"],
                ["<strong>7</strong>", "How does it follow instructions?", "Instruction tuning and alignment"],
            ],
            caption="The book's roadmap, from data to instructions.",
            note=(
                "Chapters 2 to 4 prepare data and architecture; chapter 5 runs pretraining; "
                "chapters 6 and 7 specialize the base model."
            ),
        ),
        p(
            "The order is not accidental. Without a tokenizer there are no numbers; without "
            "embeddings there are no representations; without attention there is no context; "
            "without a complete GPT block there is nothing to train. Pretraining produces a "
            "<strong>base model</strong> capable of completing text. Classification and "
            "instruction tuning specialize it for concrete tasks. Each stage reuses the work "
            "of the previous one. Each chapter produces an executable piece, not just notes."
        ),
        lab("cost"),
        py(
            """
N = 175e9
D = 300e9
FLOPs = 6 * N * D
GPUS = {
    "A100 (40 effective TFLOPS)": 40,
    "H100 (150 effective TFLOPS)": 150,
}
GPU_HOUR_PRICE = 2.0

print(f"Training FLOPs: {FLOPs:.2e}")
for gpu, tflops in GPUS.items():
    hours = FLOPs / (tflops * 1e12 * 3600)
    print(f"{gpu:30} {hours:>12,.0f} GPU-hours  ${hours * GPU_HOUR_PRICE:,.0f}")
print("Rule of thumb: FLOPs ≈ 6 · N · D; these are order-of-magnitude estimates.")
""",
            caption=(
                "The 6 · N · D rule in action. Change N, D, or the price to see how "
                "quickly the bill grows."
            ),
        ),
        p(
            "Training cost is estimated with <strong>FLOPs ≈ 6 · N · D</strong>, where "
            "<em>N</em> is the number of parameters and <em>D</em> the number of tokens. With "
            "that rule, GPT-3 (175 billion parameters, 300 billion tokens) is around 2.2 "
            "million GPU-hours on A100s and about 4.4 million dollars. The educational model "
            "(124 million parameters, 1 billion tokens) fits in about 7 GPU-hours on an RTX "
            "4090 and about 3.5 dollars. These are order-of-magnitude estimates, not budgets: "
            "real utilization, interconnection, and energy prices change the bill."
        ),
        p(
            "To follow the book you do not need a datacenter GPU. The first chapters and small "
            "finetuning work on a laptop; a GPU speeds up training, but it is not essential to "
            "understand the code. What you do need is persistence and critical curiosity: an "
            "LLM produces plausible text, not necessarily true text. The lab calculator lets "
            "you change model, tokens, hardware, and price to see the effect of each variable."
        ),
        callout(
            "warning",
            "Do not try this on your laptop",
            "Training GPT-3 from scratch requires thousands of GPUs for weeks and millions of "
            "dollars. The book trains small models so you can run the code and understand each "
            "piece. If you need a capable model without paying for pretraining, load open "
            "weights (Llama, Mistral, GPT-2) and finetune."
        ),
        check(
            "Why does the book build a ~124M parameter model instead of reproducing GPT-3?",
            "Because the goal is to understand the complete pipeline with a model that can be "
            "trained and debugged on affordable hardware. The architecture is the same; later "
            "you can load open weights to avoid the cost of large-scale pretraining.",
        ),
        keypoints(
            [
                "The book builds a small GPT (~124M) to understand each component.",
                "The pipeline goes from tokens and embeddings to attention and GPT architecture.",
                "Pretraining produces a base model; finetuning specializes it.",
                "Cost grows with parameters and tokens: FLOPs ≈ 6 · N · D.",
                "To use a capable model without training from scratch, reuse open weights.",
            ]
        ),
    ),
    key_points=(
        "You learn by building a small GPT, not by reproducing GPT-3.",
        "Tokenization, embeddings, attention, and architecture precede pretraining.",
        "Classification and instructions are finetuning stages.",
        "Training cost scales with parameters and tokens (6 · N · D).",
    ),
)
