"""Lesson 7 · Embeddings and meaning."""

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
    table,
)

LESSON = Lesson(
    number=7,
    slug="embeddings-y-significado",
    title="Embeddings and meaning",
    summary=(
        "Vectors let us compare tokens geometrically: direction, distance, and cosine "
        "similarity. That geometry captures useful regularities, but also limits and biases "
        "worth knowing."
    ),
    minutes=11,
    objectives=(
        "Calculate cosine similarity between two vectors.",
        "Interpret the nearest neighbours of a token.",
        "Distinguish geometric proximity from synonymy.",
        "Recognise the biases and limits of static embeddings.",
    ),
    blocks=(
        lead(
            "Similar tokens should have similar vectors. That intuition turns the embedding "
            "matrix into a map: words that appear in similar contexts end up close, and the "
            "distance between vectors can be measured. The basic tool is <strong>cosine "
            "similarity</strong>."
        ),
        p(
            "Cosine similarity compares the direction of two vectors, not their length. It is "
            "the dot product divided by the product of their norms: "
            "<code>cos(a, b) = (a · b) / (||a|| ||b||)</code>. The result runs from −1 to 1. A "
            "value near 1 means similar directions; near 0, orthogonal directions; near −1, "
            "opposite directions. By ignoring magnitude, two vectors can be very similar even if "
            "one is much longer than the other."
        ),
        figure(
            "img/ch02/espacio-embeddings.svg",
            "A two-dimensional map with clusters of vectors for animals, vehicles, and food.",
            "A two-dimensional projection shows clusters, but it does not prove that the model "
            "“understands” concepts. It is a visualisation, not evidence.",
            credit="Original diagram by Aula LLM.",
            wide=True,
        ),
        p(
            "The following example uses six invented three-dimensional vectors so the calculation "
            "is transparent. The values are chosen by hand so that animals sit near each other, "
            "vehicles do too, and food forms its own group. In a real model the coordinates are "
            "learned and are not read one by one; what remains is the mathematical operation."
        ),
        py(
            """
import math

VECTORS = {
    "cat":    [0.90, 0.30, 0.10],
    "dog":    [0.85, 0.35, 0.15],
    "car":    [0.10, 0.90, 0.20],
    "bus":    [0.15, 0.85, 0.25],
    "pizza":  [0.70, 0.20, 0.60],
    "paella": [0.65, 0.25, 0.65],
}


def cosine(a, b):
    product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return product / (norm_a * norm_b)


def neighbours(query, vectors, limit=3):
    scores = []
    for word, vector in vectors.items():
        if word != query:
            scores.append((cosine(vectors[query], vector), word))
    return sorted(scores, reverse=True)[:limit]


for word in ("cat", "car", "pizza"):
    print(f"Neighbours of “{word}”:")
    for score, neighbour in neighbours(word, VECTORS):
        print(f"  {neighbour:8} cosine={score:.3f}")

print()
print(f"cosine(cat, dog) = {cosine(VECTORS['cat'], VECTORS['dog']):.3f}")
print(f"cosine(cat, car) = {cosine(VECTORS['cat'], VECTORS['car']):.3f}")
""",
            caption=(
                "Cosine similarity and nearest neighbours with didactic vectors. Change the "
                "coordinates and watch the neighbours reorder."
            ),
        ),
        lab("embedding"),
        h2("What neighbours mean"),
        p(
            "In a trained embedding, the neighbours of “cat” often include “dog”, “feline”, or "
            "“pet”. That does not mean the vector contains a definition: it means those tokens "
            "appear in similar contexts and the model has pulled them together to reduce loss. "
            "Proximity is a statistical regularity, not a guaranteed logical relation."
        ),
        p(
            "That is why cosine similarity is useful for exploration and for retrieval systems, "
            "but it is not an oracle. Two antonyms can appear in very similar contexts (“high” "
            "and “low” next to “building”) and end up close. Two related words can be far apart "
            "if the corpus uses them in different registers. Geometry summarises usage, not the "
            "dictionary."
        ),
        table(
            ["Phenomenon", "What is observed", "Why it happens", "Consequence"],
            [
                [
                    "Synonymy",
                    "Close neighbours",
                    "Interchangeable contexts",
                    "Useful for retrieval and clustering",
                ],
                [
                    "Antonymy",
                    "They can also be close",
                    "They appear in the same contexts",
                    "Distance does not distinguish opposition",
                ],
                [
                    "Polysemy",
                    "One vector blends senses",
                    "A static embedding ignores context",
                    "“Bank” does not distinguish bench from institution",
                ],
                [
                    "Bias",
                    "Associations from the corpus",
                    "The model learns social frequencies",
                    "It may reproduce stereotypes",
                ],
            ],
            caption="Common limits of token embeddings. Contextual models mitigate some, not all.",
        ),
        callout(
            "warning",
            "Close does not mean correct",
            "A cosine of 0.95 between two vectors proves neither synonymy nor that the "
            "association is desirable. Before using embeddings to make decisions —filtering "
            "candidates, recommending, moderating— measure and review real examples instead of "
            "trusting the score alone.",
        ),
        h2("Static versus contextual"),
        p(
            "The embedding matrix in this chapter assigns a fixed vector to each token. It is a "
            "<strong>static</strong> representation: “bank” has the same vector in “river bank” "
            "and “central bank”. Modern transformers also produce <strong>contextual</strong> "
            "representations: the output of a layer depends on neighbouring tokens, so the vector "
            "for “bank” changes with the sentence. The input embedding remains static; what "
            "becomes contextual is the representation flowing through the network."
        ),
        p(
            "This distinction explains why comparing first-layer embeddings has limits. It is "
            "useful for analysing vocabulary and for retrieval tasks, but it does not replace a "
            "contextual representation when meaning depends on the sentence. It also explains why "
            "modern retrieval models train embeddings of sentences or whole documents, not just "
            "tokens."
        ),
        check(
            "Two vectors have cosine 0.98 but one is twice as long as the other. Are they very similar according to cosine similarity?",
            "Yes. Cosine similarity normalises by the norms, so length does not matter. Only "
            "direction matters. If you want absolute distance, you need another metric, such as "
            "Euclidean distance.",
        ),
        h2("Using them with judgement"),
        p(
            "To explore a vocabulary, compute neighbours and review extreme cases. To compare "
            "models, use the same query set and measure with task metrics, not only cluster "
            "cohesion. To detect bias, look for systematic associations between attributes and "
            "groups, and complement the metric with qualitative review. Geometry is a powerful "
            "tool, but it does not interpret itself."
        ),
        p(
            "This closes the conceptual arc of the chapter: text, tokens, IDs, windows, pairs, "
            "and vectors. The last lesson organises the map and offers a self-assessment. If you "
            "can explain every transition and calculate a couple of figures, you have the "
            "foundation chapter 3 needs to enter attention."
        ),
        keypoints(
            [
                "Cosine similarity compares directions and runs from −1 to 1.",
                "Close neighbours reflect similar contexts, not definitions.",
                "Antonyms and polysemous words can end up close.",
                "Static embeddings do not distinguish senses by sentence.",
                "Corpus biases show up in the geometry.",
                "The metric is interpreted together with the task and qualitative review.",
            ]
        ),
    ),
    key_points=(
        "Cosine measures the angle between vectors, not their length.",
        "Neighbours indicate similar contexts, not guaranteed synonymy.",
        "Static embeddings blend the senses of polysemous words.",
        "Geometry inherits biases from the corpus.",
    ),
    quiz_id=None,
)
