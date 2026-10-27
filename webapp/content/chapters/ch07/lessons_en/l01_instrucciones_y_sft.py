"""Lesson 1 · Instructions and supervised fine-tuning."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
)

LESSON = Lesson(
    number=1,
    slug="instrucciones-y-sft",
    title="Instructions and SFT",
    summary=(
        "Supervised instruction tuning teaches a pretrained model to answer concrete "
        "requests without abandoning next-token prediction."
    ),
    minutes=11,
    objectives=(
        "Define supervised instruction tuning and place it after pretraining.",
        "Explain what changes and what stays the same relative to pretraining.",
        "Recognise realistic goals and limits for a small SFT run.",
        "Distinguish full fine-tuning from parameter-efficient tuning.",
    ),
    blocks=(
        lead(
            "A pretrained model can continue text, but it does not necessarily obey. Ask it "
            "to turn a sentence into the passive voice and it may answer with more "
            "instructions, repeat the prompt, or invent a format. Supervised instruction "
            "tuning, or <strong>SFT</strong>, shows the model, through examples, what is "
            "expected when someone asks for something."
        ),
        p(
            "Pretraining optimises a very simple task: given a piece of text, predict the "
            "next token. With enough data and parameters, that task produces a model that "
            "knows grammar, styles, and part of the world. But the objective does not "
            "distinguish a question from an order or an ordinary paragraph. The model learns "
            "to continue, not to collaborate. SFT keeps exactly the same loss function and "
            "changes the data distribution: examples now take the form of a request followed "
            "by a desired response."
        ),
        h2("What supervised tuning adds"),
        p(
            "The book's experiment uses <strong>1,100 instruction-response pairs</strong>, "
            "split into 85% for training, 10% for testing, and 5% for validation. Each pair "
            "is formatted with a template, tokenised, and turned into a next-token example "
            "where the response tokens are the target. There is no new architecture and no "
            "different optimiser: there is a different dataset and a mask that decides which "
            "positions count. That continuity is the key to understanding both the method and "
            "its limits."
        ),
        p(
            "The effect is visible in practice. Before tuning, the book's medium GPT-2 "
            "generates a “Response” section that repeats the original sentence and copies "
            "part of the instruction again. After two epochs, it turns “The chef cooks the "
            "meal every day” into “The meal is cooked every day by the chef.” It has not "
            "learned the passive voice as an explicit grammar rule: it has adjusted its "
            "distribution so that, after that instruction and that format, a useful "
            "continuation becomes more likely. SFT shapes behaviour; it does not install a "
            "rule engine."
        ),
        callout(
            "warning",
            "SFT is not a guarantee of truth",
            "Tuning teaches <strong>format, style, and response patterns</strong>. It does not "
            "turn the model into a reliable database or remove hallucinations. A model can "
            "answer confidently and be wrong. Factual verification, data filtering, and "
            "evaluation remain essential.",
        ),
        h2("Goals and limits"),
        p(
            "A well-designed SFT run pursues four things: the model should recognise an "
            "instruction, produce a response in the expected format, learn to stop with the "
            "end-of-sequence token, and generalise to unseen requests. On its own, it does "
            "not guarantee truthfulness, safety, or up-to-date knowledge. Nor does it replace "
            "pretraining: it specialises it. The narrower the instruction set, the greater "
            "the risk that the model loses general abilities or overfits to one style."
        ),
        p(
            "Cost matters too. The book tunes medium GPT-2, with 355 million parameters, "
            "because the small 124-million model is too limited to produce qualitatively "
            "satisfactory results. On an A100 GPU, two epochs take about 0.86 minutes; on an "
            "Apple M3 CPU, about 15.78 minutes. These are figures from the book's experiment, "
            "not a promise for every machine. When the budget is tight, "
            "parameter-efficient tuning such as LoRA reduces the number of trainable weights "
            "and the memory cost."
        ),
        bullets(
            [
                "<strong>Data:</strong> clear, diverse pairs with correct responses; quality "
                "matters more than filling thousands of rows.",
                "<strong>Compute:</strong> full tuning updates every weight; LoRA trains small "
                "adapters and lowers the cost.",
                "<strong>Evaluation:</strong> a falling loss is not enough; read responses and "
                "compare them with references on a held-out set.",
            ]
        ),
        check(
            "What does SFT share with pretraining, and what changes?",
            "It shares the next-token loss and the optimiser. What changes is the data "
            "—instruction-response pairs— and the mask, which decides which response tokens "
            "contribute to the loss.",
        ),
        keypoints(
            [
                "Pretraining learns to continue text; SFT learns to answer requests.",
                "SFT does not change the architecture: it changes the data and the loss target.",
                "The book uses 1,100 pairs and a 355-million-parameter medium GPT-2.",
                "Format, style, and end-of-sequence behaviour are learned from examples.",
                "A small SFT run does not guarantee truth, safety, or fresh knowledge.",
                "LoRA lowers cost by training only a small fraction of the weights.",
            ]
        ),
    ),
    key_points=(
        "SFT adapts a pretrained model with instruction-response pairs.",
        "The task is still next-token prediction; the data and mask change.",
        "The goals are following instructions, keeping format, and knowing when to stop.",
        "Full tuning and LoRA differ in cost, not in the pedagogical idea.",
    ),
)
