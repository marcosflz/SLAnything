"""Laboratorios del capítulo 2."""

LAB_META: dict[str, dict[str, str]] = {
    "tokenizer": {
        "title": "Tokenizador BPE",
        "description": "Divide un texto en subpalabras y observa cómo cambian las fusiones.",
        "icon": "tag",
        "accent": "blue",
    },
    "window": {
        "title": "Ventana deslizante",
        "description": "Ajusta contexto y stride y cuenta las ventanas que salen.",
        "icon": "layers",
        "accent": "violet",
    },
    "embedding": {
        "title": "Mapa de embeddings",
        "description": "Mueve vectores y compara vecinos con similitud coseno.",
        "icon": "eye",
        "accent": "teal",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "tokenizer": {
        "title": "BPE tokenizer",
        "description": "Split text into subwords and watch how merges change the result.",
        "icon": "tag",
        "accent": "blue",
    },
    "window": {
        "title": "Sliding window",
        "description": "Adjust context and stride and count the resulting windows.",
        "icon": "layers",
        "accent": "violet",
    },
    "embedding": {
        "title": "Embedding map",
        "description": "Move vectors and compare neighbours with cosine similarity.",
        "icon": "eye",
        "accent": "teal",
    },
}

LAB_IDS = frozenset({"tokenizer", "window", "embedding"})
