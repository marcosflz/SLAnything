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
    slug="repaso-texto",
    title="Review and self-assessment",
    summary=(
        "The whole chapter on one map: from a string of text to the tensor that enters the "
        "transformer. Eight ideas, a table of connections, and a ten-question quiz."
    ),
    minutes=10,
    objectives=(
        "Reorder the text-preparation pipeline without consulting the lessons.",
        "Connect tokenization, BPE, windows, pairs, and embeddings.",
        "Identify which step needs a second visit.",
        "Check your understanding with the chapter self-assessment.",
    ),
    blocks=(
        lead(
            "You have travelled through chapter 2. At the start, text was a string of "
            "characters; at the end, it is a tensor of shape "
            "<code>(batch, context, dimension)</code> that a transformer can process. This "
            "review adds no new concepts: it organises the ones you have and points out the "
            "connections that usually break."
        ),
        p(
            "The full pipeline fits in one line: <strong>text → tokens → IDs → windows → x/y "
            "pairs → embeddings → input tensor</strong>. Every arrow is a decision. Tokenizing by "
            "words or subwords changes the vocabulary. Choosing a stride changes the number of "
            "examples. Choosing a dimension changes memory. If you can justify each arrow, you "
            "can explain the chapter."
        ),
        h2("The eight ideas in this chapter"),
        bullets(
            [
                "<strong>An LLM does not process raw text.</strong> It needs IDs and vectors; the "
                "tokenizer is the first piece of the model.",
                "<strong>Granularity matters.</strong> Word, subword, and character balance "
                "coverage, length, and vocabulary size.",
                "<strong>Special tokens fill gaps.</strong> <code>&lt;|unk|&gt;</code>, "
                "<code>&lt;|endoftext|&gt;</code>, and <code>[PAD]</code> handle situations that "
                "words cannot.",
                "<strong>BPE builds subwords by frequency.</strong> It merges frequent pairs and "
                "can represent new words.",
                "<strong>The sliding window creates examples.</strong> Context and stride "
                "determine how many fragments appear and how much they overlap.",
                "<strong>The target is the shifted input.</strong> An L-token window produces L "
                "predictions, not one.",
                "<strong>An embedding is a matrix lookup.</strong> The ID's row is the vector; the "
                "matrix is learned.",
                "<strong>Geometry is not semantics.</strong> Cosine and neighbours are useful, but "
                "they inherit biases and do not guarantee synonymy.",
            ],
            ordered=True,
        ),
        p(
            "Three pairs worth keeping apart. First, <strong>token versus ID</strong>: the token "
            "is the text piece; the ID is its numeric key. Second, <strong>training window versus "
            "context window</strong>: the first is the fragment used in one step; the second is "
            "the maximum the model can process. Third, <strong>static embedding versus contextual "
            "representation</strong>: the first is a fixed row; the second depends on the "
            "sentence and is produced by the transformer."
        ),
        h2("The pipeline in a table"),
        table(
            ["Step", "Input", "Output", "Control question"],
            [
                ["Tokenize", "Text", "Token list", "Which units did I choose?"],
                ["Encode", "Tokens", "IDs", "Does the vocabulary cover the domain?"],
                ["Window", "IDs", "L-token fragments", "How much do they overlap?"],
                ["Pair", "Fragment", "Shifted x and y", "How many predictions result?"],
                ["Embed", "IDs", "Matrix of vectors", "How many parameters are there?"],
                ["Position", "Vectors", "Ordered vectors", "How does the model know where a token is?"],
            ],
            caption="The pipeline and a question to check each transition.",
        ),
        p(
            "The last row deserves a comment. The embedding layer assigns the same vector to a "
            "token wherever it is. For the model to distinguish “cat eats fish” from “fish eats "
            "cat”, it needs positional information. GPT models add a position embedding to the "
            "token one; both have the same dimension and are summed. In chapter 3, attention will "
            "use that sum as its starting point."
        ),
        check(
            "Explain in two sentences why a 256-token window produces 256 predictions, not one.",
            "Because the transformer output has one position per input token and each position "
            "produces a distribution over the vocabulary. The loss compares every position with "
            "the next token, so all 256 positions are used in a single forward pass.",
        ),
        callout(
            "success",
            "Your turn",
            "Open the <strong>chapter 2 self-assessment</strong>: ten questions with "
            "explanations. You need <strong>80%</strong> —eight out of ten— to consider the "
            "chapter complete. If you miss one, return to the relevant lesson; the quiz can be "
            "retaken without penalty.",
        ),
        p(
            "Before pressing start, do one last mental exercise. Imagine the corpus “The cat "
            "sleeps. The dog sleeps.” and walk the pipeline: tokens, IDs, a six-token window, "
            "shifted pairs, an embedding matrix of vocabulary × dimension. If you can write the "
            "tensor shapes and justify the shift, you are ready for chapter 3. If something "
            "resists, do not move on: return to that lesson. The next chapter assumes all of this."
        ),
        p(
            "Chapter 3 starts exactly where this one ends: with a tensor of embeddings and an open "
            "question, how the model decides which tokens to attend to. Data preparation is not a "
            "formality; it is half the work. A clear pipeline makes model errors debuggable. An "
            "opaque pipeline turns every strange result into a black box."
        ),
        keypoints(
            [
                "The pipeline is text → tokens → IDs → windows → pairs → embeddings.",
                "Each tokenization decision changes vocabulary, length, and cost.",
                "The training target is the input shifted by one token.",
                "The training window is not the model's maximum context.",
                "Static embeddings are complemented by positional and contextual information.",
                "The quiz requires 80% and can be retaken without penalty.",
            ]
        ),
    ),
    key_points=(
        "The chapter turns raw text into tensors ready for the transformer.",
        "Tokenization, BPE, and windows are decisions with measurable consequences.",
        "x/y pairs make the next-token task explicit.",
        "An embedding is a learned lookup; position is added separately.",
    ),
    quiz_id="quiz-capitulo-2",
)
