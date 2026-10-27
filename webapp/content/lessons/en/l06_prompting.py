"""Lesson 6 · Zero-shot and few-shot."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    code,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=6,
    slug="zero-shot-y-few-shot",
    title="Zero-shot and few-shot",
    summary=(
        "How to ask for new tasks without touching the weights: the instruction and the "
        "examples in the prompt condition the model's response."
    ),
    minutes=10,
    objectives=(
        "Distinguish zero-shot, one-shot, and few-shot.",
        "Explain why examples in the prompt are not equivalent to training.",
        "Build a prompt with instructions and solved examples.",
        "Relate emergent behaviour to scale and data diversity.",
    ),
    blocks=(
        lead(
            "A base model is not born knowing how to obey. But it can solve a task it has "
            "never seen if we phrase it in the prompt: an instruction, a few examples, and an "
            "input. The key is that context conditions the next prediction."
        ),
        p(
            "Asking for a task <strong>zero-shot</strong> means describing it without any "
            "examples: “Classify the sentiment of this review”. <strong>One-shot</strong> adds "
            "one solved example and <strong>few-shot</strong> a few. In all three cases the "
            "mechanism is identical: the prompt text enters the context window and shifts the "
            "probability distribution toward the desired format. There is no gradient descent "
            "and no weight update. It is <em>in-context</em> learning, temporary: if you close "
            "the conversation, it disappears. An everyday example: asking “translate this "
            "sentence” without more is zero-shot; showing two translations before the target "
            "sentence is few-shot. One-shot is the intermediate case, with a single example. "
            "The boundary between one-shot and few-shot is fuzzy; what matters is how many "
            "examples the model sees, not the label."
        ),
        figure(
            "img/ch01/fig_1_6_zero_few_shot.png",
            "Comparison between completing text, solving a zero-shot task, and solving it with few-shot examples.",
            "In few-shot, the examples live inside the input itself. The model is not "
            "retrained: what changes is what it sees before answering.",
            credit="Figure 1.6 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        callout(
            "warning",
            "Few-shot is not finetuning",
            "In few-shot the model <strong>does not modify its weights</strong>. The examples "
            "occupy the context window and condition the probability of the next response. "
            "Finetuning, by contrast, trains on labeled data and changes the weights "
            "permanently. Confusing the two leads you to expect a memory that the prompt does "
            "not provide. Finetuning requires data, compute, and evaluation; few-shot only "
            "requires space in the context."
        ),
        h2("Building the prompt"),
        code(
            "text",
            """
# Zero-shot
Classify the sentiment as positive, negative, or neutral.
Review: "The product arrived broken and support did not respond."
Sentiment:

# Few-shot
Classify the sentiment as positive, negative, or neutral.
Review: "I love this product."
Sentiment: positive
Review: "It does not work and arrived late."
Sentiment: negative
Review: "It is a normal product."
Sentiment: neutral
Review: "The product arrived broken and support did not respond."
Sentiment:
""",
            caption="The same task with zero examples and with three. The output format is learned from the pattern itself.",
        ),
        lab("prompt"),
        py(
            """
INSTRUCTION = "Classify the sentiment as positive, negative, or neutral."
EXAMPLES = [
    ("I love this product.", "positive"),
    ("It does not work and arrived late.", "negative"),
    ("It is a normal product.", "neutral"),
]
INPUT = "Shipping was fast, but the box arrived broken."

lines = [f"Instruction: {INSTRUCTION}"]
for i, (review, label) in enumerate(EXAMPLES, start=1):
    lines.append(f"\\nExample {i}:\\nReview: {review}\\nSentiment: {label}")
lines.append(f"\\nReview: {INPUT}\\nSentiment:")
prompt = "\\n".join(lines).strip()

print(prompt)
print(f"\\nApproximate prompt tokens: {len(prompt.split())}")
""",
            caption=(
                "Build a few-shot prompt. Try removing examples, changing the "
                "instruction, or adding a mislabeled example."
            ),
        ),
        p(
            "A good prompt fixes the output format, gives representative examples, and avoids "
            "ambiguous instructions. Order also matters: examples most similar to the target "
            "input usually help more. Put the instruction first, leave the target input last, "
            "and mark clearly where the response starts, for example with “Output:”. There is "
            "also a practical limit: every example consumes context-window tokens, so more is "
            "not always better; at some point the cost grows and the signal dilutes. A "
            "mislabeled example also teaches the error. With long documents, it is sometimes "
            "better to summarize or retrieve only the relevant fragments before building the "
            "prompt."
        ),
        h2("Emergent behaviour"),
        p(
            "GPT was trained to predict text, not to translate. However, when the model is "
            "large enough and has seen enough multilingual text, translation "
            "<strong>emerges</strong> as a capability nobody explicitly programmed. The same "
            "happens with summarizing, spelling correction, or solving simple problems. "
            "Emergent does not mean magic: the capability appears as a consequence of scale "
            "and data diversity. Being hard to predict does not make it inexplicable, and many "
            "“emergent” capabilities depend on how they are evaluated; the boundary is still "
            "debated. This is the observation that popularized GPT-3: a single model, without "
            "retraining, can solve new tasks with a few examples. It is not unlimited: it "
            "depends on data quality and model size. Instead of programming one task for each "
            "goal, general language representations are used. The practical consequence is "
            "enormous: one model can solve very different tasks without a different model for "
            "each one."
        ),
        check(
            "What is the difference between few-shot and finetuning?",
            "Few-shot adds examples to the context and does not alter the weights; the effect "
            "lasts as long as the conversation. Finetuning trains on labeled data and changes "
            "the weights permanently.",
        ),
        keypoints(
            [
                "Zero-shot gives only the instruction; one-shot and few-shot add examples.",
                "Examples condition the context; they do not update the weights.",
                "Few-shot is temporary; finetuning is a permanent change to the weights.",
                "Emergent behaviour arises from scale and diverse data, not from a programmed task.",
                "More examples consume more context and do not guarantee better answers.",
            ]
        ),
    ),
    key_points=(
        "Zero-shot, one-shot, and few-shot differ in the number of examples in the prompt.",
        "Few-shot does not train: it conditions the next prediction with context.",
        "Finetuning does change the weights and persists outside the conversation.",
        "Scale and multilingual data explain emergent capabilities such as translation.",
    ),
)
