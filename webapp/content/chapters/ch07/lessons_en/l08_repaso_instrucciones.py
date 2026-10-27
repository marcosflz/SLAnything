"""Lesson 8 · Review and self-assessment."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=8,
    slug="repaso-instrucciones",
    title="Review and self-assessment",
    summary=(
        "Eight steps to organise the chapter, three confusions to clear up, and a ten-question "
        "quiz to check what you have learned."
    ),
    minutes=10,
    objectives=(
        "Rebuild the instruction-tuning pipeline from start to finish.",
        "Distinguish SFT, masking, templates, and evaluation.",
        "Find gaps with a ten-question self-assessment.",
        "Connect the chapter to the next step: preferences.",
    ),
    blocks=(
        lead(
            "You have travelled from a model that completes text to a model that answers "
            "requests. It is not an architecture change: it is a change of data, format, and "
            "signal. This review orders the pieces and helps you find the idea that needs a "
            "second visit before you move on."
        ),
        p(
            "The chapter starts with a distinction and ends with a measurement. In between "
            "come a dataset, a template, a masked batch, a training loop, and a judge. If you "
            "can explain what goes in and what comes out of each stage, you have the map. If "
            "one stage sounds familiar but you could not draw it, return to the corresponding "
            "lesson: the quiz rewards understanding, not memorisation. The order is not "
            "decorative: a mistake in the template or the mask propagates to every later stage, "
            "so test each step with a tiny batch before spending compute. A small batch is "
            "enough to expose a broken template or a mask that is off by one."
        ),
        h2("The pipeline in eight steps"),
        bullets(
            [
                "<strong>1. Define the goal.</strong> A pretrained model does not reliably "
                "follow instructions; SFT specialises it with examples.",
                "<strong>2. Collect pairs.</strong> Instruction, optional input, and response. "
                "Quality, diversity, licence, and privacy are checked before training.",
                "<strong>3. Format.</strong> Alpaca or ChatML turn roles into text and markers. "
                "The same template must be used for training and inference.",
                "<strong>4. Tokenise and batch.</strong> The batch is padded to its longest "
                "sequence; targets are shifted one position.",
                "<strong>5. Mask.</strong> Padding is marked -100; one EOS is kept. Masking the "
                "instruction is optional and decided by measurement.",
                "<strong>6. Train.</strong> Few epochs, a low rate, and validation. A low loss "
                "does not prove good answers.",
                "<strong>7. Generate and evaluate.</strong> Hold out a test set, read responses, "
                "and combine metrics with human judgement.",
                "<strong>8. Iterate.</strong> Adjust data, format, hyperparameters, or model "
                "size based on observed errors, not intuition.",
            ],
            ordered=True,
        ),
        p(
            "Three common confusions. First, believing that SFT “installs” knowledge. Most "
            "knowledge comes from pretraining; SFT shapes how it is used. Second, confusing "
            "padding masking with instruction masking. The first is mandatory to avoid "
            "training on empty positions; the second is an experimental decision about which "
            "part of the sequence receives signal. Third, treating a judge's score as truth. "
            "It is an approximate measure, useful for comparing configurations, but it needs "
            "calibration and context."
        ),
        table(
            ["Question", "Short answer"],
            [
                ["What does SFT change?", "The data and the mask; not the architecture."],
                ["What does the loss ignore?", "Positions marked -100."],
                ["What do training and inference share?", "The template, tokeniser, and format."],
                ["What does an LLM judge measure?", "Approximate quality under a rubric, not absolute truth."],
            ],
            caption="Four quick checks before closing the chapter.",
        ),
        h2("Check what you have learned"),
        p(
            "The chapter self-assessment has <strong>ten multiple-choice questions</strong>, "
            "with an explanation for every answer. You need <strong>80%</strong> —eight out of "
            "ten— to consider the chapter passed. You can retake it without penalty. If you "
            "miss one, do not just memorise the correct option: return to the lesson, rebuild "
            "the reasoning, and try explaining it aloud. That effort is what consolidates the "
            "idea."
        ),
        callout(
            "success",
            "Your turn",
            "Open the <strong>Chapter 7 self-assessment</strong>. It covers all eight lessons "
            "and mixes definitions with application cases. If you get all ten, excellent; if "
            "you miss one, you now know where to look. The goal is not the score, but arriving "
            "at the next chapter with the ideas connected.",
        ),
        check(
            "Explain in two sentences why an excellent validation loss does not guarantee a good assistant.",
            "Loss measures the probability of reference tokens, not whether the answer is "
            "useful, true, or safe. A model can fit the dataset's style very well and still "
            "fail on new requests or produce plausible but incorrect answers.",
        ),
        keypoints(
            [
                "SFT specialises a pretrained model with instruction-response pairs.",
                "Template, tokeniser, and format must match in training and inference.",
                "Padding is masked with -100; the first EOS is kept.",
                "Validation loss and response reading are interpreted together.",
                "Evaluation combines metrics, judges, and human review.",
                "Preferences and DPO are the next step, not a requirement of SFT.",
                "The quiz requires 80% and can be retaken without penalty.",
            ]
        ),
    ),
    key_points=(
        "The pipeline runs from formatted pairs to masked batches, training, and evaluation.",
        "Padding masking, instruction masking, and truncation are distinct controls.",
        "A judge score is an approximation calibrated with people.",
        "The chapter closes with a ten-question self-assessment.",
    ),
    quiz_id="quiz-capitulo-7",
)
