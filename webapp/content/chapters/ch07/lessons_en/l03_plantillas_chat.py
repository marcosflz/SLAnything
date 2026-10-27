"""Lesson 3 · Chat templates."""

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
    number=3,
    slug="plantillas-chat",
    title="Chat templates",
    summary=(
        "A chat template turns roles and messages into a token sequence with markers. The "
        "model only sees text; the structure must be explicit and constant."
    ),
    minutes=12,
    objectives=(
        "Identify the system, user, and assistant roles in a conversation.",
        "Compare Alpaca and ChatML styles and their markers.",
        "Explain why training and inference must share a template.",
        "Build and review a template with a runnable example.",
    ),
    blocks=(
        lead(
            "A model does not see “roles”: it sees a token sequence. The chat template is "
            "the contract that translates a conversation into that sequence. It decides "
            "where each turn starts, who is speaking, where the response ends, and which text "
            "the model should learn. If the contract changes between training and real use, "
            "the model receives an input unlike the one it learned to interpret."
        ),
        p(
            "The book compares two styles. The <strong>Alpaca</strong> style uses plain-text "
            "sections: an instruction, an optional input, and a response, delimited by "
            "<code>### Instruction:</code>, <code>### Input:</code>, and "
            "<code>### Response:</code>. The <strong>Phi-3</strong> style uses special turn "
            "tokens, an idea similar to ChatML: they mark the start and end of each turn, for "
            "example "
            "&lt;|im_start|&gt; and &lt;|im_end|&gt;. Both approaches work; what matters is "
            "that the template is unambiguous and applied to every example in the same way."
        ),
        figure(
            "img/ch07/plantilla-chat.svg",
            "Diagram of a conversation with system, user, and assistant turns delimited by special tokens, with the response area marked as trainable.",
            "The template turns roles into markers. The green area is the part that usually "
            "contributes to the loss; the rest is context.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("Roles, markers, and format"),
        code(
            "text",
            """
<|im_start|>system
You are a concise, precise assistant.<|im_end|>
<|im_start|>user
Rewrite in the passive voice: "The chef cooks dinner."<|im_end|>
<|im_start|>assistant
Dinner is cooked by the chef.<|im_end|>
""",
            caption="A ChatML conversation. Special tokens separate turns, and the model learns to close its own.",
        ),
        p(
            "The conversation above has three roles. The system turn is not decoration: it "
            "sets the frame, tone, and limits of the answer. The user turn carries the task. "
            "The assistant turn produces the response to be taught. In ChatML, every turn "
            "opens and closes with a marker; in Alpaca, the <code>### Response:</code> heading "
            "marks where the learnable area begins. If the tokenizer does not recognise a "
            "marker as special, it will split it into several tokens and the model will see a "
            "different sequence; check the vocabulary before trusting the template."
        ),
        p(
            "In Alpaca, the instruction and response are separated by headings and blank "
            "lines. If the input field is empty, the <code>### Input:</code> section is "
            "omitted; including it empty adds noise and teaches a pattern that carries no "
            "information. In ChatML, the system turn sets the general behaviour, the user turn "
            "contains the request, and the assistant turn contains the response. The same "
            "dialogue can be represented in either style, but mixing them within one training "
            "run without a measured reason is not advisable."
        ),
        lab("chat-template"),
        h2("Consistency between training and inference"),
        p(
            "The template is as much part of the model as the weights. If you train with "
            "Alpaca and send ChatML in production, the model sees markers it never associated "
            "with a task; if you train without a system turn and later add a long one, you "
            "also change the distribution. The same applies to spaces, line breaks, and the "
            "end token: an apparently trivial difference can shift the response. Store the "
            "template next to the checkpoint, version it, and test it with reference cases "
            "before deployment. Write it down in the model card and compare a rendered example "
            "before and after any code change. A useful check is to render the same case with "
            "the old and new templates and compare the IDs; if they differ, the update is not "
            "harmless. Document the tokenizer version as well."
        ),
        py(
            """
INSTRUCTION = "Rewrite in the passive voice: \\"The chef cooks dinner every day.\\""
RESPONSE = "Dinner is cooked every day by the chef."

def chatml(instruction, response):
    return (
        "<|im_start|>system\\nYou are a concise assistant.\\n<|im_end|>\\n"
        "<|im_start|>user\\n" + instruction + "\\n<|im_end|>\\n"
        "<|im_start|>assistant\\n" + response + "\\n<|im_end|>"
    )

def alpaca(instruction, response):
    return (
        "Below is an instruction that describes a task. Write a response that completes it.\\n\\n"
        "### Instruction:\\n" + instruction + "\\n\\n"
        "### Response:\\n" + response
    )

for name, text in (("ChatML", chatml(INSTRUCTION, RESPONSE)),
                   ("Alpaca", alpaca(INSTRUCTION, RESPONSE))):
    print("=" * 10, name, "=" * 10)
    print(text)
    print()
""",
            caption=(
                "Two templates for the same pair. Change the instruction text and watch how "
                "the markers are preserved."
            ),
        ),
        callout(
            "tip",
            "The template is code too",
            "Treat it as a versioned function: it takes roles and returns text; it has tests "
            "for empty cases, accents, and long responses. If you build it with "
            "concatenation, check line breaks and do not let user text imitate system markers "
            "without escaping or validation. A template change without tests is a hidden model "
            "change.",
        ),
        check(
            "Why is it not enough for the inference template to “look similar” to the training one?",
            "Because the model learns exact associations between markers, spaces, and "
            "responses. A formatting difference changes the token sequence and can lead to "
            "worse answers even when the request content is the same.",
        ),
        keypoints(
            [
                "The template translates roles and messages into a token sequence.",
                "Alpaca uses headings; ChatML and Phi-3 use special turn tokens.",
                "The input section is omitted when the field is empty.",
                "Training and inference must use the same template and tokeniser.",
                "The template is versioned and tested like any other component.",
                "An ambiguous format lets user text imitate markers.",
            ]
        ),
    ),
    key_points=(
        "Roles do not exist for the model: only the markers that represent them.",
        "Alpaca and ChatML are different styles; mixing them without measurement adds noise.",
        "The template must be identical in training and inference.",
        "The template is a versioned, testable artefact.",
    ),
)
