"""Lesson 1 · The problem of fixed memory."""

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
    slug="por-que-atencion",
    title="The problem of fixed memory",
    summary=(
        "Before attention, an encoder compressed the whole sentence into a single vector. "
        "That bottleneck explains why attention mechanisms emerged."
    ),
    minutes=10,
    objectives=(
        "Explain why word-by-word translation does not work.",
        "Describe the bottleneck of a recurrent encoder-decoder.",
        "Understand attention as selective access to the input, not infinite memory.",
        "Place self-attention within the 2017 transformer.",
    ),
    blocks=(
        lead(
            "Translation is not word substitution. Verb order, pronouns, and agreement change "
            "across languages, and a word only makes sense inside its sentence. Early neural "
            "translation models tried to solve this by compressing the entire input into one "
            "vector; attention was born to break that bottleneck."
        ),
        p(
            "Imagine translating a German sentence into English. In German, the main verb may "
            "appear at the end; in English, we expect it before the object. If you translate "
            "word by word from left to right, by the time you reach the verb you may already "
            "have made decisions you need to undo. The classic solution was an "
            "<strong>encoder-decoder</strong>: one network reads the full sentence, summarizes "
            "it, and another generates the translation from that summary. Before transformers, "
            "the usual architecture for this was a recurrent neural network (RNN)."
        ),
        p(
            "An RNN processes the sequence step by step and updates a <strong>hidden state</strong> "
            "at every word. When it finishes, that state is supposed to contain the meaning of "
            "the whole input. The decoder receives that single vector and starts generating. The "
            "problem is obvious: the entire sentence must fit in a fixed-size space. The longer "
            "and more complex the input, the more information competes for the same handful of "
            "numbers. Details from the first words fade and long dependencies are lost."
        ),
        h2("A hidden state is not infinite memory"),
        p(
            "The bottleneck is a consequence of the design. The decoder cannot go back to the "
            "original input; it only has the summary passed by the encoder. In the sentence “The "
            "lawyer who represented the company that bought the building arrived late,” the link "
            "between “lawyer” and “late” crosses several clauses. A fixed vector may preserve the "
            "general topic, but it does not guarantee every relevant link. Training RNNs also "
            "becomes difficult when dependencies are long: the gradient must travel through many "
            "steps and tends to vanish or explode."
        ),
        p(
            "Larger states, gates, and intermediate summaries improved the situation, but they "
            "still forced compression. The question that opened another path was: what if the "
            "decoder could look directly at the input instead of settling for a summary? It does "
            "not need to copy the whole sentence at every step; it only needs to decide which "
            "parts matter for the word being generated."
        ),
        h2("Attention: looking without compressing"),
        p(
            "In 2014, the Bahdanau mechanism introduced that idea to neural translation. At each "
            "generation step, the decoder scores every input position and distributes attention "
            "across them. Useful positions receive more weight; the rest receive less. The result "
            "is a context vector recomputed at every step, combining information from several "
            "words at once. This is especially valuable for <strong>alignment</strong>: the model "
            "can relate an output word to one or more input words even when their positions do "
            "not match."
        ),
        p(
            "What does “looking” mean here? Attention is not a database or a perfect memory. It is "
            "a mathematical operation: representations are compared, weights that sum to one are "
            "produced, and contents are mixed. The mixture is soft, differentiable, and learned "
            "with the rest of the network. There are no symbolic rules or explicit pointers, only "
            "vectors adjusted so that the mixture becomes useful."
        ),
        table(
            ["Aspect", "Recurrent encoder-decoder", "Attention in the transformer"],
            [
                [
                    "Access to input",
                    "The decoder receives a final hidden state.",
                    "Each position can consult the others in every layer.",
                ],
                [
                    "Long dependencies",
                    "They must survive compressed into one vector.",
                    "They are modeled through direct connections and weights.",
                ],
                [
                    "Parallelization",
                    "Limited by step-by-step recurrence.",
                    "Positions are processed in parallel during training.",
                ],
            ],
            caption=(
                "The change was not only about accuracy but about how the work is organized. "
                "Attention removes the need to compress the whole input before generating."
            ),
            note="Conceptual comparison.",
        ),
        h2("From RNNs to the transformer"),
        p(
            "The 2017 transformer pushed the idea further: it removed recurrence and organized the "
            "model around <strong>self-attention</strong>. Each token in a sequence relates to the "
            "other tokens in that same sequence. The original transformer kept an encoder and a "
            "decoder; GPT keeps only the decoder and stacks it into many layers. That choice fits "
            "the generative task: predict the next token by looking only at the past."
        ),
        p(
            "Attention also has a price. Comparing every token with every token produces an n × n "
            "matrix, and that cost grows with the square of the length. A context window is not "
            "free, which is why efficient kernels and caching techniques exist. Attention solves "
            "the fixed-summary bottleneck, but it does not remove the limits of context: it moves "
            "them."
        ),
        callout(
            "warning",
            "More context does not mean full understanding",
            "Attention lets the model consult previous positions, but it still has a maximum "
            "window and a cost that grows with length. A high weight is not a causal explanation "
            "of a decision either: it is a clue about where information was mixed. Attention "
            "interpretability is useful, but not automatic.",
        ),
        check(
            "Why does a recurrent encoder-decoder lose information in long sentences?",
            "Because the decoder only receives the final hidden state, a fixed-size vector that "
            "must summarize the whole input. As length grows, more information competes for the "
            "same space and distant dependencies can be diluted. Attention avoids that mandatory "
            "step by letting the decoder consult input positions directly.",
        ),
        keypoints(
            [
                "A recurrent encoder-decoder compresses the whole input into one fixed vector.",
                "That bottleneck loses long dependencies and makes training harder.",
                "Bahdanau attention let the decoder consult the input selectively.",
                "Self-attention relates each token to the other tokens in the same sequence.",
                "Attention reduces the summary problem but keeps context and cost limits.",
            ]
        ),
    ),
    key_points=(
        "A fixed hidden state motivated attention mechanisms.",
        "Attention distributes weights over the input and builds context.",
        "Self-attention compares positions within one sequence.",
        "The transformer removed recurrence and parallelized training.",
        "Context windows and quadratic cost remain.",
    ),
)
