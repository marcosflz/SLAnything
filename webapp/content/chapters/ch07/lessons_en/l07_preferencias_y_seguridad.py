"""Lesson 7 · Preferences, RLHF, and safety."""

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
    number=7,
    slug="preferencias-y-seguridad",
    title="Preferences, RLHF, and safety",
    summary=(
        "SFT imitates one answer; preferences compare two. RLHF and DPO optimise that "
        "signal, and safety requires negative examples, evaluation, and oversight."
    ),
    minutes=11,
    objectives=(
        "Explain what a preference signal adds over an imitated response.",
        "Compare RLHF with DPO and recognise the role of the reference model.",
        "Design negative examples and refusal criteria without over-refusing.",
        "Identify safety limits that tuning cannot guarantee.",
    ),
    blocks=(
        lead(
            "SFT teaches a correct answer, but it does not tell the model what to do when two "
            "answers are possible and one is clearly better. Preferences add that comparison: "
            "for the same request, the model sees a preferred answer and a rejected one. It is "
            "a harder signal to collect and a closer one to what we want the model to do in "
            "production."
        ),
        p(
            "An imitated response has a fixed target: the model learns to reproduce the "
            "reference tokens. A preference does not say “write exactly this”, but “between "
            "these two outputs, this one is better”. That difference matters because many "
            "tasks have no single correct answer. A summary can be clearer without being "
            "identical; an explanation can be more useful without being longer. Preference "
            "data captures criteria such as clarity, usefulness, tone, or safety that a single "
            "reference does not express well."
        ),
        h2("From rewards to preferences"),
        p(
            "Classic <strong>RLHF</strong> (reinforcement learning from human feedback) has two "
            "parts. First, a <strong>reward model</strong> is trained to score a response from "
            "human comparisons. Then the model's policy is optimised to maximise that reward, "
            "usually with PPO and a penalty that prevents it from drifting too far from a "
            "reference model. It is powerful but complex: several models are involved, training "
            "is unstable, and the policy can exploit flaws in the reward model."
        ),
        p(
            "<strong>DPO</strong> (direct preference optimisation) simplifies the process. "
            "Instead of training a separate reward model and running a reinforcement loop, it "
            "optimises the model directly on pairs of preferred and rejected responses, "
            "keeping a reference and a parameter that controls how far it may drift. It is "
            "easier to implement and reproduce, which is why it has become popular. It is not "
            "magic: it still depends on the quality of the preferences, the reference model, "
            "and the evaluation. The book presents it as an optional step after SFT and points "
            "to its DPO notebook in the companion repository."
        ),
        table(
            ["Approach", "Signal", "Main pieces", "Typical risk"],
            [
                ["SFT", "Reference response", "Model and data", "Imitating bias or errors"],
                ["RLHF", "Human comparisons", "Reward model, policy, reference", "Reward hacking"],
                ["DPO", "Preferred/rejected pairs", "Model, reference, beta", "Overfitting preferences"],
            ],
            caption="Three ways to teach behaviour. They are not exclusive: DPO usually follows an SFT run.",
            note="Data quality and evaluation remain the common factor.",
        ),
        h2("Safety and limits"),
        p(
            "Preferences can also teach what not to do. A pair can show an answer that refuses "
            "a harmful request and another that accepts it; the model learns to prefer the "
            "first. But negative examples are not enough. Coverage must span different kinds "
            "of harm, from illegal content to dangerous instructions, data exfiltration, or "
            "manipulation. And it must avoid teaching indiscriminate refusal: a model that "
            "refuses everything is safe only in appearance and useless in practice."
        ),
        p(
            "System safety does not end with the weights. An attacker can inject malicious "
            "instructions through a document, a web page, or the conversation history itself; "
            "this is known as prompt injection. They can also probe for bias, leak information, "
            "or elicit dangerous answers through unusual combinations. Defence combines data, "
            "training, input and output filters, tool permissions, monitoring, and human "
            "review. No single layer is sufficient, and none promises zero risk."
        ),
        p(
            "Evaluating safety is different from evaluating usefulness. It requires adversarial "
            "tests, a held-out case set, explicit criteria, and a person responsible for "
            "deciding what is acceptable. Measure both false negatives —harm that gets "
            "through— and false positives —unnecessary refusals—. Repeat the evaluation "
            "whenever the model, template, tools, or usage policy changes. Safety is a "
            "continuous process, not an adjective added at the end."
        ),
        callout(
            "danger",
            "Tuning is not a safety barrier",
            "Teaching refusals improves expected behaviour, but it does not make the model "
            "infallible. A responsible system needs threat modelling, penetration tests, "
            "permission limits, decision logs, and an escalation path to a human. Do not ship "
            "a model just because it “said nothing bad” in a ten-question test.",
        ),
        check(
            "What is the practical difference between RLHF and DPO?",
            "RLHF trains a reward model and optimises the policy with reinforcement learning; "
            "DPO optimises the model directly on preferred and rejected response pairs, using "
            "a reference. DPO is usually simpler, but both depend on preference quality.",
        ),
        keypoints(
            [
                "SFT imitates one answer; preferences compare two.",
                "RLHF uses a reward model and reinforcement optimisation.",
                "DPO learns directly from preferred/rejected pairs.",
                "Preference signals capture criteria without a single correct answer.",
                "Negative examples must cover harm without teaching blanket refusal.",
                "Safety includes data, filters, permissions, monitoring, and people.",
            ]
        ),
    ),
    key_points=(
        "Preferences add a comparison signal that SFT lacks.",
        "RLHF and DPO are different ways to optimise that signal.",
        "Safety is evaluated with adversarial cases and human oversight.",
        "No tuning run guarantees a safe system on its own.",
    ),
)
