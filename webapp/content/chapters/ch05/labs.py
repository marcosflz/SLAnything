"""Metadatos de los laboratorios del capítulo 5."""

LAB_META_ES: dict[str, dict[str, str]] = {
    "loss": {
        "title": "Laboratorio de pérdida",
        "description": (
            "Mueve la probabilidad del token correcto y observa la entropía cruzada, "
            "la perplejidad y la contribución de cada token al lote."
        ),
        "icon": "chart",
        "accent": "amber",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "loss": {
        "title": "Loss lab",
        "description": (
            "Move the probability of the correct token and watch cross entropy, "
            "perplexity, and each token's contribution to the batch."
        ),
        "icon": "chart",
        "accent": "amber",
    },
}

LAB_IDS = frozenset({"loss"})
