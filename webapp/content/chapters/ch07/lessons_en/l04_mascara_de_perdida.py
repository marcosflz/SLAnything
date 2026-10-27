"""Lesson 4 · Masking the loss."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=4,
    slug="mascara-de-perdida",
    title="Masking the loss",
    summary=(
        "In a batch, sequences are padded and targets are shifted. The mask decides which "
        "positions contribute to the loss and which are ignored with -100."
    ),
    minutes=11,
    objectives=(
        "Explain why a batch is padded to its longest sequence.",
        "Build shifted targets and locate padding positions.",
        "Justify the value -100 and the retention of one end token.",
        "Distinguish padding masking from instruction masking.",
    ),
    blocks=(
        lead(
            "One instruction sequence has a different length from the next. To process them "
            "together, the batch is padded to its longest member, but the model must not "
            "learn to predict padding. The solution is a mask: padding positions are replaced "
            "with a value that the loss function ignores."
        ),
        p(
            "The book's process has five steps: apply the template, tokenise, pad the batch, "
            "create shifted targets, and replace padding with <code>-100</code>. The shift is "
            "the same as in pretraining: if the input is [A, B, C], the target is [B, C, EOS]. "
            "The model learns to predict each token from the previous ones. What is new is "
            "that there are several sequences per batch and that some end earlier than others."
        ),
        h2("Which position enters the loss"),
        p(
            "Imagine a batch with a three-token sequence and a five-token sequence. The first "
            "is padded with two extra positions. Before masking, its targets might be "
            "<code>[B, C, EOS, EOS, EOS]</code>. The first EOS is informative: it teaches the "
            "model to end the response. The next two are only padding. If they counted, the "
            "model would learn to emit EOS again and again, and the loss would be diluted by "
            "positions that are not part of the response."
        ),
        figure(
            "img/ch07/mascara-perdida.svg",
            "Diagram of a sequence with masked context, an active response, and padding positions marked -100.",
            "In the response-only variant, only the green positions contribute. The "
            "instruction may be masked or not; the first EOS is kept and later padding is "
            "ignored with -100.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "The value <strong>-100</strong> is not arbitrary: it is the default "
            "<code>ignore_index</code> of <code>cross_entropy</code> in PyTorch. The loss "
            "function discards any target equal to -100, so the number of active positions "
            "varies between batches. This explains an apparent collision: GPT-2 uses the same "
            "ID, 50256, for end-of-sequence and for padding. The collision is deliberate and "
            "is resolved in the targets: one EOS is kept and the rest are masked. In the "
            "input, padding remains 50256 so that the model can process the batch."
        ),
        h2("Instruction masking: optional and debated"),
        p(
            "Padding masking is necessary. Instruction masking is something else: it means "
            "setting the request tokens to -100 as well, so the loss is computed only on the "
            "response. The intuition is reasonable: we want the model to learn to answer, not "
            "to memorise the question. The book does not apply it by default and leaves it as "
            "an exercise. Research is not conclusive: some work argues for masking, while "
            "other results favour training on the instruction too, because the model then "
            "learns the full relationship between request and response."
        ),
        p(
            "Measure before choosing. If you mask the instruction, the loss reflects only the "
            "response and may reduce overfitting to particular phrasings; if you do not, the "
            "loss includes the request and gives the model a richer signal, although one that "
            "is also easier to memorise. There is no universal answer: it depends on the "
            "dataset, the model size, and the evaluation. What is mandatory is that the mask "
            "is consistent with the template and documented. A small ablation on the "
            "validation set is usually more informative than a long argument; log the choice "
            "next to the checkpoint."
        ),
        py(
            """
import math

PAD = 50256
IGNORE = -100

def prepare_targets(targets):
    seen = 0
    output = []
    for token in targets:
        if token == PAD:
            seen += 1
            output.append(PAD if seen == 1 else IGNORE)
        else:
            output.append(token)
    return output

def mean_loss(probabilities, targets):
    active = []
    for i, (p, y) in enumerate(zip(probabilities, targets), start=1):
        if y == IGNORE:
            print(f"position {i}: target {y:>6}  -> ignored")
        else:
            value = -math.log(p)
            active.append(value)
            print(f"position {i}: target {y:>6}  -> loss {value:.4f}")
    return sum(active) / len(active)

targets = prepare_targets([120, 340, PAD, PAD, PAD])
probabilities = [0.80, 0.50, 0.01, 0.01, 0.01]
print("prepared targets:", targets)
print(f"mean loss: {mean_loss(probabilities, targets):.4f}")
""",
            caption=(
                "A demonstration with didactic losses: the first EOS is kept and later "
                "padding is ignored. Change the values and check the mean."
            ),
        ),
        callout(
            "note",
            "A mask is not a truncation",
            "The length limit, for example 1024 tokens for GPT-2, cuts sequences that do not "
            "fit. The mask does not cut: it decides which positions already present "
            "contribute to the loss. They are two different controls and should be recorded "
            "separately.",
        ),
        check(
            "Why keep one EOS token in the targets instead of masking all of them?",
            "Because the model must learn to end the response. If every EOS were replaced by "
            "-100, it would receive no signal to close generation and could continue "
            "indefinitely.",
        ),
        keypoints(
            [
                "Each batch is padded to its longest sequence, not to the dataset maximum.",
                "Targets are shifted one position to the right.",
                "The first EOS is kept; later padding is marked -100.",
                "cross_entropy ignores -100 by default, so only active positions count.",
                "The EOS/padding collision is resolved in the target tensor.",
                "Instruction masking is optional, debated, and must be measured.",
            ]
        ),
    ),
    key_points=(
        "Padding must not contribute to the loss: it is marked -100.",
        "The first EOS is kept so the model learns to stop.",
        "Padding masking is mandatory; instruction masking is an experimental choice.",
        "Masking and truncation are different controls.",
    ),
)
