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
)

LESSON = Lesson(
    number=8,
    slug="repaso",
    title="Review and self-assessment",
    summary=(
        "Eight ideas to take with you and a ten-question quiz to check what you learned "
        "before moving on to chapter 2."
    ),
    minutes=10,
    objectives=(
        "Review the eight key ideas of the chapter.",
        "Connect the concepts from the seven previous lessons.",
        "Check your learning with a self-assessment.",
    ),
    blocks=(
        lead(
            "You have completed chapter 1. It is time to consolidate: fewer isolated "
            "definitions and more connections between them. If you can explain these eight "
            "ideas in your own words, you have the mental map you need to build. This is not "
            "an exam: it is an opportunity to spot which idea needs a second visit."
        ),
        p(
            "The chapter began with an unfinished sentence and ends with a complete pipeline. "
            "In between came parameters, the corpus, the transformer, attention, autoregressive "
            "generation, and prompts. This review puts them in order. Do not try to memorize "
            "the list: use it as a checking network."
        ),
        h2("The eight ideas you take with you"),
        bullets(
            [
                "<strong>An LLM predicts the next token.</strong> That task, sustained by the "
                "scale of parameters and data, produces general capabilities.",
                "<strong>“Large” means two things:</strong> many parameters and an enormous, "
                "diverse corpus. Neither is enough on its own.",
                "<strong>Pretraining is self-supervised:</strong> the label is the text itself, "
                "specifically the token that follows. No human annotators are needed.",
                "<strong>Finetuning specializes</strong> the base model with labeled data, "
                "whether to follow instructions or to classify.",
                "<strong>The original transformer has an encoder and a decoder.</strong> BERT "
                "uses the encoder; GPT uses the decoder. They are different ways of solving tasks.",
                "<strong>Self-attention weights relevance</strong> across tokens and connects "
                "distant information.",
                "<strong>GPT generates autoregressively:</strong> its previous output becomes "
                "the input of the next step.",
                "<strong>Zero-shot and few-shot do not change the weights:</strong> they place "
                "instructions and examples in the context. Finetuning does change the weights.",
            ],
            ordered=True,
        ),
        p(
            "If you had to keep a single sentence, it would be this: an LLM is a network trained "
            "to predict the next token, and almost everything else —translating, summarizing, "
            "programming, conversing— emerges from that task when the model and the data are "
            "large enough. Temperature and top-k do not change what the model knows; they only "
            "change how it chooses among its candidates. Likewise, a prompt does not change its "
            "weights: it changes the context from which it predicts."
        ),
        p(
            "Three pairs not to confuse: parameters versus tokens (network capacity versus "
            "text units); pretraining versus finetuning (learning the language versus "
            "specializing in a task); and few-shot versus finetuning (context versus weights). "
            "Attention, for its part, is not a store of facts: it weights the relevance of the "
            "tokens present in the context. If you can explain each pair in one sentence, you "
            "have understood the structure of the chapter."
        ),
        p(
            "Before moving on, try to draw the pipeline from memory: text → tokens → "
            "embeddings → transformer → probabilities → next token → repeat. If you get stuck "
            "at a step, go back to the corresponding lesson. The drawing fits on a napkin and "
            "summarizes the whole chapter. You do not need to memorize every formula: just know "
            "what goes in and what comes out at each stage."
        ),
        h2("Checking what you learned"),
        p(
            "The chapter self-assessment has <strong>ten multiple-choice questions</strong>. "
            "Each answer comes with an explanation, and at the end you can review which lesson "
            "covers each idea. There is no time limit and no penalty for retrying: the goal is "
            "to find gaps, not to pass by luck. If you are torn between two options, ask "
            "yourself what changes and what does not: almost every question in the chapter "
            "revolves around that distinction."
        ),
        check(
            "Explain in two sentences why few-shot is not the same as finetuning.",
            "Few-shot adds examples to the prompt and conditions the prediction without "
            "touching the weights; the effect disappears when the conversation ends. "
            "Finetuning trains on labeled data and changes the weights permanently.",
        ),
        callout(
            "success",
            "Now it's your turn",
            "Open the <strong>chapter self-assessment</strong>: ten questions and an "
            "explanation for each answer. You need <strong>80%</strong> —eight out of ten— to "
            "consider the chapter passed. You can retake it as many times as you want; if you "
            "miss one, go back to the relevant lesson and try again."
        ),
        keypoints(
            [
                "Predicting the next token is the task that sustains an LLM.",
                "Parameters and data are the two dimensions of scale.",
                "Transformer, attention, and autoregressive generation form the technical core.",
                "Few-shot conditions the context; finetuning changes the weights.",
                "The quiz requires 80% and can be retaken without penalty.",
            ]
        ),
    ),
    key_points=(
        "An LLM predicts the next token; scale and data explain its capabilities.",
        "Pretraining learns the language; finetuning specializes the model.",
        "GPT uses the decoder and generates autoregressively.",
        "Few-shot does not train: it conditions the context without touching the weights.",
    ),
    quiz_id="quiz-capitulo-1",
)
