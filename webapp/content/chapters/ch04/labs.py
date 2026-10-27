"""Metadatos del laboratorio del capítulo 4."""

LAB_META_ES: dict[str, dict[str, str]] = {
    "gpt-block": {
        "title": "Bloque GPT interactivo",
        "description": (
            "Activa y desactiva LayerNorm, atención, feed-forward y residuales para "
            "ver qué aporta cada pieza y cómo se conserva la forma de los tensores."
        ),
        "icon": "layers",
        "accent": "violet",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "gpt-block": {
        "title": "Interactive GPT block",
        "description": (
            "Turn LayerNorm, attention, feed-forward, and residual connections on and "
            "off to see what each piece contributes and how tensor shapes are preserved."
        ),
        "icon": "layers",
        "accent": "violet",
    },
}

# Alias en español para consumidores que usan el nombre corto del capítulo 1.
LAB_META = LAB_META_ES

LAB_IDS = frozenset({"gpt-block"})
