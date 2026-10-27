"""Lesson 5 · Predicting the next word."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=5,
    slug="predecir-la-siguiente-palabra",
    title="Predicting the next word",
    summary=(
        "GPT stands for Generative Pretrained Transformer. Behind the acronym is a very "
        "simple loop: predict a token, add it to the context, and repeat."
    ),
    minutes=15,
    objectives=(
        "Break down the GPT acronym and explain what each word contributes.",
        "Describe autoregressive generation step by step.",
        "Use an n-gram model as a mock-up of next-token prediction.",
        "Relate temperature and top-k to the variety and coherence of the generated text.",
    ),
    blocks=(
        lead(
            "GPT is three letters and a loop. <strong>G</strong>enerative, because it produces "
            "new text; <strong>P</strong>retrained, because it learned from an enormous corpus "
            "before you asked it anything; <strong>T</strong>ransformer, because of the "
            "architecture we saw in lesson 3. What unites them is a tiny task: given a "
            "context, predict the next token."
        ),
        p(
            "That loop is called <strong>autoregressive generation</strong>. The model receives "
            "an initial context —a sentence, a question, a document— and produces a probability "
            "distribution over all the tokens in its vocabulary. It picks one, adds it to the "
            "context, and starts again. It does not plan the whole paragraph: it makes a local "
            "decision, incorporates it, and recalculates. Global coherence is the result of "
            "chaining many local decisions. If the context is “The sky turned”, the model does "
            "not look for a rule in a dictionary: it assigns more probability to “orange” or "
            "“red” than to “window”, because it has seen similar patterns. Context is its "
            "working memory; anything that does not fit in it does not exist for the "
            "prediction."
        ),
        figure(
            "img/ch01/fig_1_8_autoregressive.png",
            "Diagram of an autoregressive model: each step's output becomes part of the next step's input.",
            "At each iteration, the generated token is appended to the sequence and the model "
            "predicts again. That closed circuit is autoregressive generation.",
            credit="Figure 1.8 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        p(
            "To make the mechanism tangible, the lesson includes a mock-up without a neural "
            "network: an <strong>n-gram model</strong>. A unigram looks only at the frequency of "
            "each word; a bigram conditions the next word on the previous one; a trigram uses "
            "the two previous ones. Our model uses up to three context tokens —that is, a "
            "4-gram— and falls back: if the long context does not appear in the corpus, it "
            "tries a shorter one and, ultimately, the global frequency. That backoff is a "
            "primitive form of generalization: when there is not enough evidence for the long "
            "context, use the evidence that does exist. The lab trains it in your browser on a "
            "public-domain fragment of <em>Don Quixote</em> and lets you change the context, the "
            "length, and the seed to see how generation changes."
        ),
        lab("ngram"),
        figure(
            "img/ch01/fig_1_7_next_word.png",
            "The sentence is split into tokens and the model predicts which one comes next.",
            "The only pretraining task: split text into tokens and learn to fill in the next "
            "one. There is no human label; the label is the text itself.",
            credit="Figure 1.7 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        h2("Temperature and top-k"),
        p(
            "The model does not always choose the most probable token. <strong>Temperature</strong> "
            "changes the shape of the distribution: below 1 it sharpens it and favours safe "
            "options; above 1 it flattens it and makes room for less probable candidates. A very "
            "low temperature produces repetitive, predictable text; a very high one produces "
            "more variety and also more incoherence. <strong>Top-k</strong> cuts the tail: it "
            "keeps only the <em>k</em> most probable candidates, renormalizes their "
            "probabilities, and samples among them. That prevents an absurd but lucky token from "
            "ruining the sentence. The two controls combine: top-k decides <em>among what</em> to "
            "choose and temperature decides <em>how much</em> to risk. At the limit, a "
            "temperature of 0 means always choosing the most probable candidate —greedy "
            "generation— and top-k stops mattering."
        ),
        py(
            """
import collections
import random
import re

CORPUS = '''In a village of La Mancha, the name of which I have no desire to recall,
there lived not long ago one of those gentlemen that keep a lance in the
lance-rack, an old buckler, a lean hack, and a greyhound for coursing. An
olla of rather more beef than mutton, a salad on most nights, scraps on
Saturdays, lentils on Fridays, and a pigeon extra on Sundays, made away with
three quarters of his income. The rest of it went in a doublet of fine cloth
and velvet breeches and shoes to match for holidays, while on week-days he
made a figure in a coat of the best homespun. He had a housekeeper past
forty, a niece under twenty, and a lad for the field and market-place. The
age of this gentleman of ours was bordering on fifty. He was of a hardy
habit, spare, gaunt-featured, a very early riser and a great sportsman. They
say he had the surname of Quixada or Quesada, for there is some difference
of opinion among the authors who write on the subject. With these words the
poor gentleman lost his wits, and he puzzled over them night and day. In
short, he so buried himself in his books that he spent the nights reading
from twilight till daybreak and the days from dawn till dusk.'''

TOKEN_RE = re.compile(r"\\w+|[^\\w\\s]", re.UNICODE)

def tokenize(text):
    return TOKEN_RE.findall(text.lower())

TOKENS = tokenize(CORPUS)
MAX_ORDER = 4
COUNTS = {n: collections.defaultdict(collections.Counter) for n in range(1, MAX_ORDER + 1)}
for i, token in enumerate(TOKENS):
    for n in range(1, MAX_ORDER + 1):
        if i >= n - 1:
            COUNTS[n][tuple(TOKENS[i - n + 1:i])][token] += 1

def distribution(context):
    for n in range(min(MAX_ORDER - 1, len(context)), 0, -1):
        key = tuple(context[-n:])
        if key in COUNTS[n + 1]:
            return COUNTS[n + 1][key]
    return COUNTS[1][()]

def generate(prompt, steps=24, seed=7):
    random.seed(seed)
    context = tokenize(prompt)
    for _ in range(steps):
        dist = distribution(context)
        candidates = dist.most_common(5)
        words = [word for word, _ in candidates]
        weights = [count for _, count in candidates]
        chosen = random.choices(words, weights=weights, k=1)[0]
        context.append(chosen)
        if chosen in ".!?":
            break
    return " ".join(context)

print(f"Corpus tokens: {len(TOKENS):,}")
print(generate("the knight", 24))
""",
            caption=(
                "A minimal autoregressive loop over an English corpus. Change the "
                "prompt, the length, or the seed. In a real GPT, the counts are "
                "replaced by the network's logits."
            ),
        ),
        callout(
            "warning",
            "What the mock-up does not do",
            "The n-gram only looks at three tokens: it does not understand meaning, it does "
            "not generalize to new contexts, and it memorizes fragments of the corpus. If you "
            "ask it to perform a task, it will not comply. An LLM replaces the counts with "
            "<strong>learned weights</strong> and uses attention to integrate much longer "
            "contexts. The task is the same; the architecture and scale change."
        ),
        check(
            "Which two operations repeat at every step of autoregressive generation?",
            "Predicting a distribution over the next token and adding the chosen token to the "
            "context. One step's output becomes the next step's input.",
        ),
        keypoints(
            [
                "GPT stands for Generative Pretrained Transformer and generates token by token.",
                "Autoregressive generation chains prediction, appending, and repetition.",
                "An n-gram model reproduces the loop with counts and backoff, without a neural network.",
                "Temperature regulates variety; top-k trims improbable candidates.",
                "The mock-up imitates the task, not the understanding: an LLM learns representations, not tables.",
            ]
        ),
    ),
    key_points=(
        "GPT is a pretrained generative transformer that predicts the next token.",
        "Generating is a loop: predict, add to the context, repeat.",
        "N-grams are a teaching mock-up, not a substitute for an LLM.",
        "Temperature and top-k control the balance between coherence and variety.",
    ),
)
