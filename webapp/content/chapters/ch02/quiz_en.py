"""Chapter 2 self-assessment (EN)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-2": Quiz(
        id="quiz-capitulo-2",
        title="Self-assessment · Chapter 2",
        description=(
            "Ten questions on tokens, BPE, windows, pairs, and embeddings. You need 80% to pass "
            "the chapter; you can retake the quiz without penalty."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="What is the difference between a token and a token ID?",
                options=(
                    "The token is the piece of text; the ID is its numeric key in the vocabulary.",
                    "The token is a number and the ID is a word.",
                    "They are synonyms: both name the same string.",
                    "The ID is the dense vector and the token is its position.",
                ),
                correct=0,
                explanation=(
                    "A token is the text unit produced by the tokenizer. The ID is the integer "
                    "with which the vocabulary represents that unit. The vector comes later, with "
                    "the embedding layer."
                ),
            ),
            Question(
                id="q2",
                prompt="What main advantage does subword tokenization have over word tokenization?",
                options=(
                    "It removes the need for a vocabulary entirely.",
                    "It represents new words by combining known fragments.",
                    "It guarantees that every token has a single meaning.",
                    "It reduces every word to a single character.",
                ),
                correct=1,
                explanation=(
                    "A subword vocabulary can split unseen terms into pieces it already knows. "
                    "That is why BPE almost eliminates OOV without needing an <|unk|> for every "
                    "new word."
                ),
            ),
            Question(
                id="q3",
                prompt="Why is the <|unk|> token added to a closed vocabulary?",
                options=(
                    "To mark the end of every document.",
                    "To pad batches of different lengths.",
                    "To represent pieces that were not in the training corpus.",
                    "To increase the embedding dimension.",
                ),
                correct=2,
                explanation=(
                    "Without <|unk|>, an unknown word raises a vocabulary lookup error. The "
                    "unknown token provides an emergency representation, although the original "
                    "word can no longer be recovered when decoding."
                ),
            ),
            Question(
                id="q4",
                prompt="What is the role of <|endoftext|> in GPT-2's tokenizer?",
                options=(
                    "It tells the model to translate the sentence.",
                    "It separates documents and has ID 50,256 in a vocabulary of 50,257 tokens.",
                    "It replaces every rare word.",
                    "It adds positional information to each token.",
                ),
                correct=1,
                explanation=(
                    "GPT-2 uses a single special token to mark the end of a text or separate "
                    "sources. Its BPE vocabulary has 50,257 entries and <|endoftext|> is the last "
                    "one, with ID 50,256."
                ),
            ),
            Question(
                id="q5",
                prompt="In BPE, what happens at each training iteration?",
                options=(
                    "The least frequent token is removed from the corpus.",
                    "The most frequent adjacent symbol pair is merged.",
                    "A random vector is assigned to each word.",
                    "Every word is split into letters and the process stops.",
                ),
                correct=1,
                explanation=(
                    "BPE counts adjacent pairs weighted by word frequency and merges the most "
                    "frequent one. Each merge adds a new token to the vocabulary and the process "
                    "repeats."
                ),
            ),
            Question(
                id="q6",
                prompt="A vocabulary has 10,000 tokens and the embedding dimension is 128. How many parameters does the token matrix have?",
                options=(
                    "128,000",
                    "1,280,000",
                    "10,128",
                    "12,800,000",
                ),
                correct=1,
                explanation=(
                    "The matrix has one row per token and one column per dimension: "
                    "10,000 × 128 = 1,280,000 parameters. Biases and positional embeddings, if "
                    "present, are counted separately."
                ),
            ),
            Question(
                id="q7",
                prompt="A sequence has 1,000 tokens, the context is 100, and the stride is 50. How many windows with a complete target are produced?",
                options=(
                    "10",
                    "18",
                    "19",
                    "20",
                ),
                correct=1,
                explanation=(
                    "Using floor((N − L − 1) / S) + 1: floor((1000 − 100 − 1) / 50) + 1 = "
                    "17 + 1 = 18 windows with a complete target. Each shares 50 tokens with the "
                    "next one."
                ),
            ),
            Question(
                id="q8",
                prompt="If a window input is x = [10, 20, 30, 40], what is the target y for next-token prediction?",
                options=(
                    "[10, 20, 30, 40]",
                    "[20, 30, 40, 50]",
                    "[9, 19, 29, 39]",
                    "[40, 30, 20, 10]",
                ),
                correct=1,
                explanation=(
                    "The target is the input shifted by one position: y[i] = x[i + 1]. The last "
                    "position must predict the token after 40 in the original sequence, shown here "
                    "as 50."
                ),
            ),
            Question(
                id="q9",
                prompt="Two embeddings have a cosine similarity of 0.95. What does that mean exactly?",
                options=(
                    "Their vectors point in very similar directions.",
                    "One vector is much longer than the other.",
                    "The tokens are synonyms in every context.",
                    "The Euclidean distance between them is 0.95.",
                ),
                correct=0,
                explanation=(
                    "Cosine measures the angle between vectors and normalises by their norms. A "
                    "high value indicates similar directions, not lengths or guaranteed synonymy."
                ),
            ),
            Question(
                id="q10",
                prompt="What is the correct order of the chapter's text-preparation pipeline?",
                options=(
                    "Text → IDs → tokens → windows → embeddings → pairs.",
                    "Text → tokens → IDs → windows → pairs → embeddings.",
                    "Tokens → text → embeddings → IDs → windows → pairs.",
                    "Text → embeddings → tokens → pairs → IDs → windows.",
                ),
                correct=1,
                explanation=(
                    "First the text is tokenized, then tokens are encoded as IDs, windows are cut, "
                    "x/y pairs are built, and finally IDs are converted into embedding vectors."
                ),
            ),
        ),
    ),
}
