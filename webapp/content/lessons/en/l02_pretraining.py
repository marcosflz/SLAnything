"""Lesson 2 · The two stages."""

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
    number=2,
    slug="pretraining-y-finetuning",
    title="The two stages",
    summary=(
        "Pretraining teaches the language with unlabeled text; finetuning "
        "specializes the model with smaller, labeled data."
    ),
    minutes=10,
    objectives=(
        "Explain next-token prediction and why it is self-supervised.",
        "Distinguish the base model from the specialized model obtained by finetuning.",
        "Differentiate finetuning from prompt engineering: changing weights versus changing context.",
        "Build input→target pairs from a sequence of tokens.",
    ),
    blocks=(
        lead(
            "Almost every modern LLM is built in two stages: one expensive and general, "
            "another comparatively cheap and specific. Understanding what the model learns "
            "in each stage avoids two common mistakes: believing it already “knows” how to "
            "follow instructions from day one, and confusing adjusting weights with writing "
            "a good prompt."
        ),
        h2("The first stage: pretraining"),
        p(
            "During pretraining, the model goes through an enormous corpus —web pages, books, "
            "Wikipedia, code— and is trained for a single task: predicting the next token. "
            "No human labels each sentence. If the sequence is “The cat sleeps on the sofa”, "
            "the input is “The cat sleeps on the” and the target is “sofa”. The label is the "
            "text itself: input and target come from the same sequence, just shifted by one "
            "position. This is <strong>self-supervised learning</strong>: the data brings its "
            "own answer. In practice, the model does not process one sentence at a time but "
            "long sequences, and computes a prediction at every position simultaneously; a "
            "causal mask prevents it from looking at future tokens. Each passage yields a "
            "huge number of examples at no labeling cost. The result is a <strong>base "
            "model</strong> or <em>foundation model</em>: it can complete text and has absorbed "
            "grammar, styles, and a considerable amount of factual knowledge, but it is not "
            "yet a reliable assistant. To succeed in diverse contexts, the network must learn "
            "regularities that go far beyond the immediate token: prediction is the excuse, "
            "representation is the prize."
        ),
        figure(
            "img/ch01/fig_1_3_pretraining_finetuning.png",
            "Diagram of the two stages: pretraining with unlabeled text and finetuning with a labeled dataset.",
            "Pretraining uses unlabeled text and next-token prediction. Finetuning starts "
            "from that base model and uses a smaller labeled dataset.",
            credit="Figure 1.3 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        p(
            "<strong>Finetuning</strong> adjusts the base model's weights with a smaller, "
            "labeled dataset. There are two common variants. <em>Instruction tuning</em> uses "
            "instruction–response pairs —“Summarize this report” → correct summary— and teaches "
            "the model to follow orders. Classification uses text and a label —an email and "
            "“spam” or “not spam”— and specializes it in a specific category. In both cases "
            "the weights change; the model does not simply read examples in the prompt. In "
            "practice you do not start from scratch: open weights are reused and adapted, "
            "which is much cheaper than pretraining. ChatGPT also adds an alignment process "
            "with human feedback (RLHF), which we will see later."
        ),
        callout(
            "info",
            "Do not confuse three things",
            "<strong>Pretraining</strong> learns the language from massive data and free "
            "labels. <strong>Finetuning</strong> specializes with small data and expensive "
            "labels. <strong>Prompt engineering</strong> —including few-shot— does not touch "
            "the weights: it places instructions and examples in the context to condition the "
            "response. In few-shot, the model “learns” only for the duration of the "
            "conversation; when it closes, no trace remains in the weights. We will see it in "
            "lesson 6."
        ),
        table(
            ["Dimension", "Pretraining", "Finetuning", "Prompt engineering"],
            [
                ["What changes", "The weights, from scratch", "The weights, from a base model", "Nothing: only the context"],
                ["Data", "Huge unlabeled corpus", "Small labeled dataset", "Instructions and examples in the prompt"],
                ["Goal", "Predict the next token", "Follow instructions or classify", "Solve the task on the spot"],
                ["Cost", "Very high", "Moderate", "Almost zero"],
            ],
            caption="Three ways to adapt a model. Only the first two modify the weights.",
        ),
        py(
            """
tokens = ["The", "cat", "sleeps", "on", "the", "sofa", "."]

pairs = []
for position in range(1, len(tokens)):
    input_tokens = tokens[:position]
    target = tokens[position]
    pairs.append((input_tokens, target))

for input_tokens, target in pairs[:3]:
    print(" ".join(input_tokens), "->", target)
print(f"\\n{len(pairs)} pairs built from a single sentence.")
""",
            caption=(
                "Each position generates a pair; the target was already in the text. "
                "Run the example and change the sentence."
            ),
        ),
        p(
            "In the “Labels” lab you will build those pairs by hand. You choose a sentence, "
            "mark which token acts as the target, and check that the input is everything "
            "before it. The exercise makes visible what usually stays hidden: pretraining "
            "does not need annotators because supervision travels inside the text itself."
        ),
        lab("labels"),
        check(
            "Why do we say pretraining is self-supervised if nobody labels the corpus?",
            "Because the label comes from the data itself: the token that follows in the "
            "sequence. Input and target are the same sentence shifted by one position, so "
            "every text fragment generates examples without human annotation.",
        ),
        keypoints(
            [
                "Pretraining predicts the next token over a huge, unlabeled corpus.",
                "The label is the text itself: input and target come from the same sequence.",
                "Finetuning adjusts the weights with smaller labeled data to specialize the model.",
                "Few-shot and prompt engineering do not change the weights; finetuning does.",
            ]
        ),
    ),
    key_points=(
        "Pretraining is self-supervised: the label is the next token of the text itself.",
        "The base model learns language; finetuning specializes it with labeled data.",
        "Finetuning changes weights; prompt engineering only conditions the context.",
        "Few-shot is not training: the examples disappear when the conversation ends.",
    ),
)
