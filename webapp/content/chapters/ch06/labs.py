"""Metadatos de los laboratorios del capítulo 6."""

LAB_META: dict[str, dict[str, str]] = {
    "classifier": {
        "title": "Clasificador interactivo",
        "description": (
            "Mueve el umbral y observa cómo cambian la matriz de confusión, la precisión, "
            "el recall y el F1."
        ),
        "icon": "target",
        "accent": "green",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "classifier": {
        "title": "Interactive classifier",
        "description": (
            "Move the threshold and watch the confusion matrix, precision, recall, and F1 "
            "change."
        ),
        "icon": "target",
        "accent": "green",
    },
}

LAB_IDS = frozenset({"classifier"})

# Alias usado por el contrato de exportación del paquete.
LAB_META_ES = LAB_META
