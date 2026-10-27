"""Metadatos de los laboratorios del capítulo 3."""

LAB_META_ES: dict[str, dict[str, str]] = {
    "qkv": {
        "title": "Consultas, claves y valores",
        "description": (
            "Elige un token y observa cómo su consulta reparte la atención entre claves y "
            "valores."
        ),
        "icon": "layers",
        "accent": "amber",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "qkv": {
        "title": "Queries, keys, and values",
        "description": (
            "Pick a token and watch its query distribute attention across keys and values."
        ),
        "icon": "layers",
        "accent": "amber",
    },
}

LAB_IDS = frozenset({"qkv"})
