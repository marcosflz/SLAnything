"""Lesson 1 · Tokens and vocabulary."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=1,
    slug="tokens-y-vocabulario",
    title="Tokens and vocabulary",
    summary=(
        "A model does not read letters: it receives numbers. The first step is deciding which "
        "unit of text counts as a token and building a vocabulary that maps each unit to an ID."
    ),
    minutes=10,
    objectives=(
        "Explain why an LLM cannot process raw text.",
        "Compare word, subword, and character tokenization.",
        "Build a vocabulary and assign an identifier to each token.",
        "Recognise the out-of-vocabulary problem.",
    ),
    blocks=(
        lead(
            "A language model looks as if it reads, but it actually receives a sequence of "
            "numbers. Between the text you type and the first mathematical operation there is "
            "a design decision that shapes everything else: <strong>which pieces of text count "
            "as units</strong>. Those pieces are tokens."
        ),
        p(
            "Neural networks add, multiply, and apply functions to vectors of real numbers. Text "
            "is categorical: the string “cat” cannot be added to “dog”. To bridge that gap we "
            "build a <strong>vocabulary</strong>: a finite list of units plus a mapping from each "
            "unit to an integer, the <strong>token ID</strong>. Tokenizing means splitting the "
            "text; encoding means translating each piece into its identifier."
        ),
        h2("Why splitting on spaces is not enough"),
        p(
            "The obvious approach is to treat every word as a token. The book begins that way "
            "with a short story by Edith Wharton, <em>The Verdict</em>: after separating words "
            "and punctuation, it obtains <strong>4,690 tokens</strong> from a text of "
            "<strong>20,479 characters</strong>. It is a useful starting point because it is "
            "easy to explain, but it has two problems."
        ),
        p(
            "The first is vocabulary size. A language has hundreds of thousands of words and "
            "inflected forms; if every one gets an identifier, the table grows without bound and "
            "many tokens appear only once. The second is the <strong>unknown word</strong>: if the "
            "model never saw “teleportation” during training, the tokenizer has no number to "
            "assign. This is the <em>out-of-vocabulary</em> (OOV) problem."
        ),
        table(
            ["Unit", "Benefit", "Cost", "Example"],
            [
                [
                    "<strong>Word</strong>",
                    "Readable tokens and short sequences",
                    "Huge vocabulary and unknown words",
                    "“cat”, “sleeps”, “.”",
                ],
                [
                    "<strong>Subword</strong>",
                    "Balance between size and coverage",
                    "Tokens that do not match whole words",
                    "“un”, “believ”, “able”",
                ],
                [
                    "<strong>Character</strong>",
                    "Minimal vocabulary and full coverage",
                    "Very long sequences and less meaning per step",
                    "“c”, “a”, “t”",
                ],
            ],
            caption="Three granularities for the same text. The choice changes vocabulary size and sequence length.",
        ),
        p(
            "Subword tokenization aims for the middle ground. A vocabulary of tens of thousands "
            "of pieces can represent new words by combining known fragments. “Tokenization”, for "
            "instance, can be split into “token” + “ization”. The model does not need to have seen "
            "the whole word to build a reasonable representation."
        ),
        h2("From text to identifier"),
        p(
            "Building a vocabulary is simpler than it sounds. Walk through the training texts, "
            "extract tokens, remove duplicates, and sort the result. Then assign an integer to "
            "each position. In the book's example the vocabulary is around <strong>1,159 "
            "tokens</strong>; after adding two special tokens it becomes <strong>1,161</strong>. "
            "That is tiny compared with a real model, but enough to understand the mechanism."
        ),
        figure(
            "img/ch02/tokenizacion.svg",
            "Diagram of a sentence split into tokens and then converted into numeric identifiers.",
            "Text is split into tokens; each token queries the vocabulary and returns an ID. "
            "The vocabulary is the bridge between the two worlds; the IDs in the figure are "
            "illustrative.",
            credit="Original diagram by Aula LLM.",
            wide=True,
        ),
        p(
            "Direction matters. <strong>Encoding</strong> goes from text to IDs; "
            "<strong>decoding</strong> walks the other way. Decoding needs an inverse dictionary, "
            "from ID to token. Without it, the model could produce correct numbers and we would "
            "not know how to turn them into words. The next lesson shows what happens when a "
            "token is missing from the vocabulary and how special pieces handle it."
        ),
        p(
            "One linguistic decision deserves conscious attention: whether to keep case and "
            "whitespace. The book keeps capitalisation because it helps distinguish proper nouns "
            "and learn punctuation; it removes spaces to simplify the example. A real tokenizer "
            "usually keeps spaces inside tokens because they carry structure."
        ),
        bullets(
            [
                "<strong>Text</strong>: the original string, with case and punctuation.",
                "<strong>Tokens</strong>: the units produced by the splitting rule.",
                "<strong>Vocabulary</strong>: the sorted set of unique tokens.",
                "<strong>IDs</strong>: the integers that represent those tokens.",
            ]
        ),
        callout(
            "tip",
            "A practical rule",
            "A small vocabulary lengthens sequences; a huge one grows the embedding matrix and "
            "leaves many rows undertrained. There is no universally correct granularity: only a "
            "trade-off between coverage, length, and cost.",
        ),
        check(
            "Why is character tokenization not the obvious solution, given that it covers every word?",
            "Because it multiplies sequence length and spreads meaning across many pieces. The "
            "model has to recompose words from minimal units, and every attention step costs "
            "more. Subwords keep meaningful fragments while keeping sequences manageable.",
        ),
        h2("What to remember"),
        p(
            "A vocabulary is not a list of meanings: it is a lookup table. Two tokens with nearby "
            "IDs are not necessarily similar; the number is just a key. Meaning appears later, "
            "when each ID becomes a vector and that vector is trained. Keeping these ideas apart "
            "prevents a common confusion: the ID encodes identity, not semantics."
        ),
        p(
            "Also remember that the tokenizer is chosen before training and then fixed. Changing "
            "it forces a new vocabulary and retraining of the embeddings. That is why models "
            "publish their tokenizer together with their weights: it is not an interchangeable "
            "detail but part of the input contract."
        ),
        keypoints(
            [
                "An LLM does not process raw text: it processes numeric identifiers.",
                "Tokenizing splits text; encoding assigns an ID to each token.",
                "Word, subword, and character granularities have different costs.",
                "A large vocabulary shortens sequences but grows embeddings and suffers from OOV.",
                "A token ID identifies a piece; it carries no meaning by itself.",
                "The tokenizer is part of the model and should not be changed casually.",
            ]
        ),
    ),
    key_points=(
        "An LLM needs numbers: the tokenizer turns text into IDs.",
        "Subword granularity balances vocabulary size and sequence length.",
        "A vocabulary is built from the unique tokens in the corpus.",
        "Out-of-vocabulary words are the OOV problem.",
    ),
    quiz_id=None,
)
