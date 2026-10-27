"""Lesson 3 · BPE step by step."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=3,
    slug="byte-pair-encoding",
    title="BPE step by step",
    summary=(
        "Byte pair encoding builds a subword vocabulary by merging the most frequent pairs of "
        "symbols. It is the method behind GPT-2, GPT-3, and many current models."
    ),
    minutes=12,
    objectives=(
        "Describe the training loop of BPE.",
        "Explain why merges depend on corpus frequencies.",
        "Tokenize a new word with the learned merges.",
        "Relate BPE to GPT-2's 50,257-token vocabulary.",
    ),
    blocks=(
        lead(
            "Word tokenization breaks on a new word. Character tokenization covers any text but "
            "lengthens sequences. BPE resolves the dilemma with a simple idea: start from "
            "characters and merge the most frequent pairs until the pieces reach a useful size."
        ),
        p(
            "The algorithm trains in two phases. First, every word in the corpus is decomposed "
            "into characters and its end is marked; the code example omits that marker to keep "
            "the output readable. Second, all adjacent symbol pairs are counted; the most "
            "frequent pair is merged into a new symbol and the process repeats. Each iteration "
            "adds one entry to the vocabulary. After many iterations, frequent symbols represent "
            "morphemes or whole words, while rare ones remain fragments."
        ),
        table(
            ["Iteration", "Most frequent pair", "Merge", "Effect"],
            [
                ["0", "—", "—", "Vocabulary of characters"],
                ["1", "l + o", "lo", "Appears in “low”, “lower”, “lowest”"],
                ["2", "lo + w", "low", "The fragment groups the root"],
                ["3", "n + e", "ne", "Appears in “new”, “newer”, “newest”"],
                ["4", "ne + w", "new", "A complete word becomes a token"],
            ],
            caption=(
                "A didactic example with a small corpus. Real merges depend on the corpus and "
                "on the configured number of operations."
            ),
            note=(
                "The table is an illustration, not output from GPT-2's tokenizer. The exact "
                "order changes with the corpus and the tie-breaking rule."
            ),
        ),
        h2("The loop, precisely"),
        p(
            "Training BPE repeats three steps until the target vocabulary size is reached. "
            "<strong>One:</strong> represent every word as a sequence of symbols. "
            "<strong>Two:</strong> count adjacent pairs, weighted by word frequency. "
            "<strong>Three:</strong> merge the most frequent pair in all its occurrences and "
            "record the rule. If two pairs tie, a stable criterion —for example, lexicographic "
            "order— is needed so the result is reproducible."
        ),
        p(
            "The number of merges is a hyperparameter. More merges produce longer tokens, "
            "shorter sequences, and a larger vocabulary. Fewer merges produce small fragments "
            "and long sequences. GPT-2 fixes its vocabulary at <strong>50,257 tokens</strong>; "
            "<code>&lt;|endoftext|&gt;</code> occupies the last ID, 50,256. That size is not a "
            "law of nature: it is the result of a trade-off between coverage, computational "
            "cost, and observed quality."
        ),
        h2("A miniature BPE"),
        p(
            "The following example trains BPE on eight invented words. It does not try to "
            "reproduce GPT's tokenizer: it shows the complete mechanism in a few lines. Watch "
            "the order of the merges and try changing the number of operations or adding words "
            "to the corpus. Then tokenize a word that was not in the training data."
        ),
        py(
            """
from collections import Counter

# Simplified BPE: no end marker, so the output is easier to read.
CORPUS = ["low", "low", "lower", "lowest", "new", "newer", "newest", "wide", "slow"]


def count_pairs(tokens):
    return Counter(zip(tokens, tokens[1:]))


def merge(tokens, pair):
    a, b = pair
    output = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and tokens[i] == a and tokens[i + 1] == b:
            output.append(a + b)
            i += 2
        else:
            output.append(tokens[i])
            i += 1
    return output


def train(words, operations):
    vocabulary = {tuple(word) for word in words}
    rules = []
    for _ in range(operations):
        counts = Counter()
        for tokens in vocabulary:
            counts.update(count_pairs(tokens))
        if not counts:
            break
        pair, frequency = counts.most_common(1)[0]
        if frequency < 2:
            break
        vocabulary = {tuple(merge(list(tokens), pair)) for tokens in vocabulary}
        rules.append((pair, frequency, "".join(pair)))
    return rules


def tokenize(word, rules):
    tokens = list(word)
    for pair, _, _ in rules:
        tokens = merge(tokens, pair)
    return tokens


rules = train(CORPUS, operations=6)
print("Learned merges:")
for number, ((a, b), frequency, result) in enumerate(rules, start=1):
    print(f"  {number}. {a} + {b} -> {result}  (frequency {frequency})")

for word in ("slowly", "newest", "wider"):
    pieces = tokenize(word, rules)
    print(f"{word:10} -> {pieces}  ({len(pieces)} tokens)")
""",
            caption=(
                "Didactic BPE: count pairs, merge the most frequent, and apply the rules to new "
                "words. Change the corpus or the number of operations."
            ),
        ),
        p(
            "One detail usually surprises learners: the word “slowly” can share the root “low” "
            "with words it has seen and leave “ly” as a fragment. The tokenizer does not know "
            "that “-ly” is a suffix; it only applies frequency rules. That blindness is also its "
            "strength: it works across languages, proper nouns, and code without a morphological "
            "analyser."
        ),
        p(
            "The result also depends on the minimum frequency required. If pairs that appear only "
            "once are allowed to merge, the vocabulary fills with accidental combinations and "
            "stops compressing. That is why many training runs require a pair to exceed a "
            "threshold before merging it. It is another decision that changes the final "
            "tokenizer, and it explains why two BPE implementations can disagree even with the "
            "same corpus."
        ),
        lab("tokenizer"),
        callout(
            "info",
            "Why BPE almost eliminates OOV",
            "If a word is not in the vocabulary, BPE splits it into pieces that are. At the "
            "limit, any text can be represented as bytes or characters. The book checks this "
            "with “someunknownPlace”: GPT's tokenizer splits it into several subwords and "
            "decoding returns the exact word.",
        ),
        check(
            "Two different corpora produce different merges. Does that mean one of the tokenizers is wrong?",
            "No. BPE is a frequency-driven procedure: the result depends on the data. Two "
            "tokenizers can both be valid and split the same text differently. What matters is "
            "that each model uses the tokenizer it was trained with and that its vocabulary "
            "covers the domain well.",
        ),
        h2("What BPE does not solve"),
        p(
            "BPE does not understand meaning. A frequent merge may join fragments that belong to "
            "different morphemes, and a rare word may be split into unintuitive pieces. It does "
            "not remove corpus bias either: if a term appears rarely, its representation will be "
            "more fragmented and receive less training. It is a tool for compression and "
            "coverage, not a linguistic theory."
        ),
        p(
            "At this point we can turn text into IDs robustly. The next step is to give each ID a "
            "vector representation. Before that, we will see how many dimensions that "
            "representation has and where its parameters come from."
        ),
        keypoints(
            [
                "BPE starts from characters and iteratively merges frequent pairs.",
                "Each merge adds one new token to the vocabulary.",
                "The number of merges controls the balance between coverage and length.",
                "GPT-2 uses a BPE vocabulary of 50,257 tokens.",
                "New words are tokenized by applying the learned merges.",
                "BPE does not guarantee interpretable tokens: it guarantees coverage.",
            ]
        ),
    ),
    key_points=(
        "BPE learns merges from the frequency of adjacent pairs.",
        "The vocabulary grows by one entry per merge.",
        "GPT-2 uses 50,257 BPE tokens; <|endoftext|> is 50,256.",
        "Unknown words are decomposed into subwords.",
        "BPE depends on the corpus and does not encode meaning.",
    ),
    quiz_id=None,
)
