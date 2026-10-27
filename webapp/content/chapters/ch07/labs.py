"""Metadatos de los laboratorios del capítulo 7."""

LAB_META_ES: dict[str, dict[str, str]] = {
    "chat-template": {
        "title": "Plantilla de chat",
        "description": (
            "Edita una instrucción y una respuesta, elige ChatML o Alpaca y observa los "
            "tokens especiales y la máscara de pérdida."
        ),
        "icon": "message",
        "accent": "violet",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "chat-template": {
        "title": "Chat template",
        "description": (
            "Edit an instruction and a response, pick ChatML or Alpaca, and inspect the "
            "special tokens and the loss mask."
        ),
        "icon": "message",
        "accent": "violet",
    },
}

LAB_IDS = frozenset({"chat-template"})

__all__ = ["LAB_META_ES", "LAB_META_EN", "LAB_IDS"]
