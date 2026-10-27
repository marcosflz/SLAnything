"""Lesson 1 · From a base model to a classifier."""

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
    number=1,
    slug="finetuning-clasificacion",
    title="From a base model to a classifier",
    summary=(
        "Classification finetuning reuses a generative model and specialises it in a "
        "closed set of labels."
    ),
    minutes=10,
    objectives=(
        "Distinguish classification finetuning from instruction finetuning.",
        "Explain why a base model cannot solve a task with a prompt alone.",
        "Describe which layers are frozen and which are adjusted when a classification head is added.",
        "Place classification within the three stages of building an LLM.",
    ),
    blocks=(
        lead(
            "A base model can continue a text, but it cannot make a decision. It may write "
            "“spam” after a sentence if the context invites it, yet it may also follow an "
            "instruction literally and repeat it. Turning the model into a classifier takes "
            "more than a good prompt: its output must change and part of its weights must be "
            "adjusted with labelled examples."
        ),
        h2("Specialising is not the same as asking"),
        p(
            "<strong>Classification finetuning</strong> trains a model to assign one of "
            "several predefined labels. In the chapter's example, each text message is "
            "classified as <em>spam</em> or <em>not spam</em>. The model does not choose "
            "freely among all the words in its vocabulary: its final layer produces one "
            "score per class, and the prediction is the class with the highest score. That "
            "restriction is both an advantage and a limit. It is an advantage because the "
            "task becomes predictable and easy to evaluate; it is a limit because the model "
            "can only answer with the labels it saw during training."
        ),
        p(
            "The book places this technique next to <strong>instruction finetuning</strong>, "
            "which is covered in the following chapter. The latter teaches the model to "
            "follow varied orders and keeps considerable flexibility; the former turns it "
            "into a specialist. Building a specialist is usually simpler and cheaper than "
            "building a generalist that performs well on everything. The trade-off is clear: "
            "a spam classifier cannot translate or summarise, even if the model it starts "
            "from can."
        ),
        table(
            ["Approach", "What it adds", "What you get"],
            [
                [
                    "Prompting a base model",
                    "Instructions and examples in the context",
                    "A conditioned response, with no new weights",
                ],
                [
                    "Classification finetuning",
                    "A class head and adjusted weights",
                    "A fixed label for each input",
                ],
                [
                    "Instruction finetuning",
                    "Instruction–response pairs",
                    "A versatile model that follows orders",
                ],
            ],
            caption="Three ways to adapt a model. Only the last two change the weights.",
        ),
        h2("What gets frozen and what gets adjusted"),
        p(
            "The starting point is a small GPT-2 with 124 million parameters, the same "
            "architecture the book built in previous chapters, with weights loaded from "
            "OpenAI. The procedure has three "
            "moves. First, all parameters are <strong>frozen</strong>: they are marked as not "
            "requiring gradients and stop updating. Then the output layer, which projected "
            "768 dimensions onto the 50,257-token vocabulary, is replaced by a linear layer "
            "from 768 to 2 classes. Finally, the new head, the last transformer block and the "
            "final normalisation are <strong>unfrozen</strong>. The rest of the model stays "
            "untouched."
        ),
        p(
            "The reason is that lower layers capture general language structure —morphology, "
            "syntax, frequent associations— that is useful for many tasks. Higher layers are "
            "more specific and sit closer to the decision. Adjusting only a subset reduces "
            "cost and the risk of destroying what was already learned. The book notes that "
            "training the head alone already works, but that adding the last transformer block "
            "and its normalisation improves the result noticeably. This is not a universal "
            "recipe: it is a reasonable compromise between adaptation and cost."
        ),
        callout(
            "warning",
            "A prompt is not training",
            "When the book asks the base GPT-2 “Is this text spam? Answer yes or no”, it gets "
            "a repetition of the instruction rather than an answer. The model is not broken: "
            "it lacks the training that teaches it to obey. Finetuning is not about writing a "
            "longer prompt; it changes weights and the shape of the output."
        ),
        check(
            "Why can a spam classifier only answer “spam” or “not spam”?",
            "Because its final layer has one output per class and it was trained with those "
            "two labels. The prediction is the index with the highest score, not a free "
            "sequence of tokens. Answering anything else would require another set of classes "
            "or a different kind of finetuning.",
        ),
        keypoints(
            [
                "Classification finetuning specialises a generative model in predefined labels.",
                "The model can only predict classes seen during training.",
                "The model is frozen, the head is replaced, and the last layers are unfrozen.",
                "Lower layers hold general language; higher layers adapt to the task.",
                "Instruction finetuning is more flexible and needs more data and compute.",
                "A prompt conditions generation, but it does not replace training.",
            ]
        ),
    ),
    key_points=(
        "Classifying means choosing among known labels, not generating free text.",
        "The classification head replaces the projection to the vocabulary.",
        "Freezing layers preserves general knowledge and reduces cost.",
        "Instruction and classification finetuning pursue different goals.",
        "A base model needs training, not only instructions, to classify.",
    ),
)
