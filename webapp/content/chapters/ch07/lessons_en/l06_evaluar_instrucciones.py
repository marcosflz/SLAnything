"""Lesson 6 · Evaluating responses."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=6,
    slug="evaluar-instrucciones",
    title="Evaluating responses",
    summary=(
        "Classification accuracy does not work for open-ended answers. Usefulness, "
        "faithfulness, and format are evaluated with references, people, and judge models."
    ),
    minutes=10,
    objectives=(
        "Explain why open-text evaluation is multidimensional.",
        "Compare benchmarks, human evaluation, and automated LLM judging.",
        "Interpret an average score and its limits.",
        "Compute exact match and token F1 on a small set.",
    ),
    blocks=(
        lead(
            "In the previous chapter, an answer was spam or not, and accuracy settled the "
            "question. Here an answer can be correct but long, useful but badly formatted, or "
            "fluent but false. Evaluating instructions requires deciding what “good” means "
            "and accepting that no single metric answers that question."
        ),
        p(
            "The book reserves 110 examples for testing. For each one it generates up to 256 "
            "tokens, removes the instruction text, and stores the model's response next to the "
            "reference. In the first three cases, manual inspection shows one clear success, "
            "one partially correct answer, and another success. That reading is valuable but "
            "does not scale: reviewing hundreds of responses one by one takes time and is hard "
            "to repeat with the same criteria."
        ),
        h2("Three families of evaluation"),
        bullets(
            [
                "<strong>Short-answer or multiple-choice benchmarks:</strong> they measure "
                "knowledge and reasoning with a checkable answer, such as MMLU. They are easy "
                "to score but do not capture an open conversation.",
                "<strong>Human comparison:</strong> people read answers and rate them or prefer "
                "one model over another. It is the reference pattern, although expensive, slow, "
                "and subject to annotator variability.",
                "<strong>Automated evaluation with another LLM:</strong> a larger model acts as "
                "a judge with a rubric. It is cheap and repeatable, but it approximates human "
                "judgement and inherits biases.",
            ]
        ),
        p(
            "The book chooses the third route to quantify the full set. It uses Llama 3 with 8 "
            "billion parameters, run locally with Ollama, and asks for a score from 0 to 100 "
            "for each response, compared with the reference. The tuned model's result is an "
            "average of <strong>54.16</strong>. For context, the base Llama 3 without tuning "
            "scores 58.51 with the same methodology, and Llama 3 instruct, tuned on a general "
            "dataset, reaches 82.6. These are figures from the book; they help compare "
            "configurations, not declare that a model is “good” in the abstract. The score is "
            "a signal, not a certification. A single number cannot carry that context by "
            "itself."
        ),
        h2("Usefulness, faithfulness, format, and limits"),
        p(
            "A useful rubric separates dimensions. <strong>Usefulness</strong> asks whether the "
            "answer solves the task. <strong>Faithfulness</strong> checks whether its claims "
            "are supported by the input or a reliable source. <strong>Format</strong> verifies "
            "that the requested structure is respected and generation stops. "
            "<strong>Safety</strong> adds a layer: refusing what should be refused without "
            "falling into excessive refusals. A single judge returning one number compresses "
            "all these dimensions and may reward verbosity or style even when the answer is "
            "wrong."
        ),
        p(
            "Classic automatic metrics remain useful. Exact match compares the normalised "
            "answer with the reference; token F1 measures partial overlap and forgives small "
            "surface differences. Neither understands synonyms or factual correctness. In "
            "addition, an LLM judge is not deterministic, may vary between runs, and tends to "
            "prefer longer answers or output from its own model family. A judge can also "
            "reward an answer that sounds confident but is unsupported. That is why it is "
            "calibrated against a human sample, the rubric is fixed, and measurements are "
            "repeated when the decision matters. Report the rubric and the number of examples "
            "alongside the average, or the number invites false comparisons. Keep the raw "
            "responses for audit."
        ),
        py(
            """
from collections import Counter

def normalise(text):
    table = str.maketrans("áéíóúüñ", "aeiouun", ".,;:!?¿¡\\"'()")
    return " ".join(text.lower().translate(table).split())

def exact_match(prediction, reference):
    return float(normalise(prediction) == normalise(reference))

def token_f1(prediction, reference):
    p = normalise(prediction).split()
    r = normalise(reference).split()
    if not p or not r:
        return 0.0
    hits = sum((Counter(p) & Counter(r)).values())
    if hits == 0:
        return 0.0
    precision = hits / len(p)
    recall = hits / len(r)
    return 2 * precision * recall / (precision + recall)

examples = [
    ("Dinner is cooked every day by the chef.",
     "Dinner is cooked every day by the chef."),
    ("Cumulus.", "Cumulonimbus."),
    ("The author is Jane Austen.", "Jane Austen."),
]

for i, (prediction, reference) in enumerate(examples, start=1):
    em = exact_match(prediction, reference)
    f1 = token_f1(prediction, reference)
    print(f"Example {i}: exact_match={em:.2f}  f1={f1:.4f}")

mean_em = sum(exact_match(p, r) for p, r in examples) / len(examples)
mean_f1 = sum(token_f1(p, r) for p, r in examples) / len(examples)
print(f"Mean: exact_match={mean_em:.4f}  f1={mean_f1:.4f}")
""",
            caption=(
                "Normalisation, exact match, and token F1. The second example shares no "
                "tokens with the reference; the third gets partial F1."
            ),
        ),
        callout(
            "warning",
            "The judge is not the court",
            "An average of 54 out of 100 does not mean the model is “average” in absolute "
            "terms: it means that this judge, with this rubric and this set, scored it that "
            "way. Changing the judge prompt, the answer order, or the judge model can move "
            "the result. Document the setup and validate with people.",
        ),
        check(
            "What two checks would you run before trusting an automated evaluation?",
            "Calibrate it against a sample rated by people and check its stability by repeating "
            "the evaluation or changing the answer order. I would also check that the rubric "
            "measures usefulness, faithfulness, and format, not just style.",
        ),
        keypoints(
            [
                "Open-text evaluation is not reducible to accuracy.",
                "Usefulness, faithfulness, format, and safety are distinct dimensions.",
                "The book uses 110 test examples and a Llama 3 8B judge.",
                "The tuned model averages 54.16; the instruct reference reaches 82.6.",
                "Exact match and token F1 measure overlap, not understanding.",
                "Every LLM judge needs human calibration and bias control.",
            ]
        ),
    ),
    key_points=(
        "Open answers are evaluated across several dimensions and sources.",
        "Benchmarks, people, and automated judges answer different questions.",
        "An average score describes a specific set and rubric.",
        "Automated evaluation is calibrated with human review.",
    ),
)
