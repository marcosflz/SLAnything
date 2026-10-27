"""Lesson 2 · Special tokens and decoding."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    quote,
    table,
)

LESSON = Lesson(
    number=2,
    slug="tokens-especiales",
    title="Special tokens and decoding",
    summary=(
        "Vocabularies need pieces that are not words: one for the unknown, one to separate "
        "documents, and others to arrange batches. Here we see how they work and why decoding "
        "does not always return the original text."
    ),
    minutes=9,
    objectives=(
        "Explain the role of <|unk|> and <|endoftext|>.",
        "Distinguish beginning, end, and padding tokens.",
        "Describe the decoding process and its limits.",
        "Check when a text → IDs → text round-trip is faithful.",
    ),
    blocks=(
        lead(
            "In the previous lesson we built a vocabulary from the words in a corpus. What "
            "happens when a word that was not there arrives? A naive tokenizer stops with an "
            "error. A useful tokenizer needs a way out: a special token that says “I do not "
            "know this”."
        ),
        p(
            "The book demonstrates the failure with an innocent sentence: <code>“Hello, do you "
            "like tea?”</code>. The word “Hello” does not appear in <em>The Verdict</em>, so it "
            "has no ID and the dictionary lookup raises a <code>KeyError</code>. This is not a "
            "bug in the code: it is a consequence of building the vocabulary from a limited "
            "corpus. The practical lesson is twofold: train on diverse text and have a plan for "
            "whatever remains outside."
        ),
        h2("Two tokens that change the contract"),
        p(
            "The first tokenizer is extended with <strong><code>&lt;|unk|&gt;</code></strong> "
            "(for <em>unknown</em>) and <strong><code>&lt;|endoftext|&gt;</code></strong>. The "
            "first replaces any piece that is not in the vocabulary. The second marks a "
            "boundary: the end of one document and the start of another. When several sources "
            "are concatenated for training, these markers prevent the model from learning a "
            "continuity that does not exist."
        ),
        p(
            "Adding them takes the example vocabulary from 1,159 to <strong>1,161</strong> "
            "entries. In the English version of the chapter the two new tokens occupy IDs 1159 "
            "and 1160, at the end of the sorted list. The order is a convention, not magic: what "
            "matters is that the same map is used for training and inference."
        ),
        table(
            ["Token", "Purpose", "When it appears", "Risk if missing"],
            [
                [
                    "<code>&lt;|unk|&gt;</code>",
                    "Represents an unknown piece",
                    "A word or symbol outside the vocabulary",
                    "The encoder fails or loses the input",
                ],
                [
                    "<code>&lt;|endoftext|&gt;</code>",
                    "Separates documents or marks the end",
                    "Between two independent texts",
                    "The model blends sources without a boundary",
                ],
                [
                    "<code>[BOS]</code> / <code>[EOS]</code>",
                    "Beginning and end of a sequence",
                    "Tasks that need explicit delimiters",
                    "The model cannot tell where text starts or stops",
                ],
                [
                    "<code>[PAD]</code>",
                    "Pads sequences of different lengths",
                    "Batches with examples of unequal size",
                    "They cannot be stacked into a rectangular tensor",
                ],
            ],
            caption="Common special tokens. Not every model uses every one.",
            note=(
                "GPT-2 and the GPT family use a single special token, &lt;|endoftext|&gt;, with "
                "ID 50,256 in a vocabulary of 50,257 entries. Padding uses the same token, and an "
                "attention mask prevents the model from attending to it."
            ),
        ),
        p(
            "There is an important difference between the didactic tokenizer and GPT's. The "
            "first needs <code>&lt;|unk|&gt;</code> because its vocabulary is a closed list of "
            "words. The second uses BPE and can split any word into subwords or bytes, so it "
            "rarely runs out of representations. It still keeps <code>&lt;|endoftext|&gt;</code> "
            "as an explicit separator."
        ),
        h2("Decoding: the way back"),
        p(
            "Decoding means querying the inverse dictionary and joining the tokens. If the IDs "
            "are valid, the result should look very much like the original text. “Look like” "
            "does not mean “be identical”. The simple tokenizer joins with spaces and then "
            "removes spaces before punctuation; that post-processing improves readability but "
            "can change spacing details. And if any token was <code>&lt;|unk|&gt;</code>, the "
            "original word is lost for good."
        ),
        p(
            "That is why we talk about a <strong>round-trip</strong>. A tokenizer is faithful if "
            "<code>decode(encode(text)) == text</code> for the text in question. Byte-level "
            "tokenizers usually satisfy this property; tokenizers that lowercase, strip spaces, "
            "or replace unknown words do not. Before using a tokenizer in production, test "
            "sentences with accents, double punctuation, emoji, and invented words."
        ),
        quote(
            "The vocabulary defines what the model can name; special tokens define what it can "
            "do when something falls outside.",
            "Central idea of this lesson",
        ),
        callout(
            "warning",
            "The round-trip can fail without an error",
            "A decoding can return perfectly readable text that is still different from the "
            "original. If the tokenizer collapses two unknown words into the same "
            "<code>&lt;|unk|&gt;</code>, the model cannot recover which was which. The loss is "
            "silent: test it with examples instead of assuming it.",
        ),
        p(
            "Padding tokens deserve a separate comment. To train in batches, all sequences in a "
            "batch must have the same length. The usual solution is to append <code>[PAD]</code> "
            "to shorter sequences and attach a mask that marks which positions are real. Without "
            "that mask, the model would treat padding as text and the loss would penalise "
            "predictions on artificial positions."
        ),
        check(
            "You have the sentence “Hello, world” and the tokenizer returns <|unk|>, “,”, “world”. What happened and what was lost?",
            "“Hello” was not in the vocabulary and was replaced by the unknown token. Decoding "
            "returns something like “&lt;|unk|&gt;, world”. The IDs preserve the structure, but "
            "not the original word: the information was lost during encoding.",
        ),
        h2("Designing the input contract"),
        p(
            "Choosing special tokens is designing a contract. If the model will receive several "
            "documents, it needs a boundary. If it will process batches, it needs padding and a "
            "mask. If it will generate text and stop, it needs an end signal. Adding tokens that "
            "are never used does not help; it dilutes the vocabulary and occupies embedding rows "
            "that receive few gradients."
        ),
        p(
            "The rest of the chapter shows how BPE reduces reliance on "
            "<code>&lt;|unk|&gt;</code> and how ID sequences are grouped into windows for "
            "training. For now, keep the idea: a tokenizer does not merely split text; it decides "
            "what can be represented, what is lost, and how context is delimited."
        ),
        keypoints(
            [
                "&lt;|unk|&gt; represents pieces that are not in the vocabulary.",
                "&lt;|endoftext|&gt; separates documents and, in GPT, also marks the end.",
                "[BOS], [EOS], and [PAD] are common conventions, not obligations.",
                "Decoding requires an inverse dictionary from ID to token.",
                "A round-trip is faithful only if the tokenizer neither normalises nor loses information.",
                "An unknown token can make the return leg readable but not exact.",
            ]
        ),
    ),
    key_points=(
        "Special tokens cover situations that words do not cover.",
        "<|unk|> avoids failure with a closed vocabulary; BPE makes it almost unnecessary.",
        "<|endoftext|> separates sources and marks the end in GPT models.",
        "Decoding reconstructs text but does not guarantee an exact round-trip.",
    ),
    quiz_id=None,
)
