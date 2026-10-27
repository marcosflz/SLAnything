"""Metadatos de los laboratorios interactivos.

El identificador debe coincidir con el nombre del módulo en
`webapp/static/js/labs/` y con `config.KNOWN_LABS`. Los capítulos 2-7 aportan
sus propios metadatos desde `webapp/content/chapters/`.
"""

from webapp.content.chapters import MODULES

LAB_META: dict[str, dict[str, str]] = {
    "memory": {
        "title": "Explorador de memoria",
        "description": "Compara pesos, cuantización y memoria de entrenamiento.",
        "icon": "cpu",
        "accent": "blue",
    },
    "labels": {
        "title": "Fábrica de etiquetas",
        "description": "Convierte una frase en pares entrada → objetivo.",
        "icon": "tag",
        "accent": "violet",
    },
    "transformer": {
        "title": "Dentro del transformer",
        "description": "Recorre encoder, decoder y atención paso a paso.",
        "icon": "layers",
        "accent": "amber",
    },
    "attention": {
        "title": "Mapa de atención",
        "description": "Descubre a qué tokens mira cada palabra.",
        "icon": "eye",
        "accent": "teal",
    },
    "ngram": {
        "title": "Generador de n-gramas",
        "description": "Entrena con El Quijote, ajusta temperatura y genera texto.",
        "icon": "sparkles",
        "accent": "blue",
    },
    "prompt": {
        "title": "Constructor de prompts",
        "description": "Monta ejemplos zero-shot y few-shot y cópialos.",
        "icon": "message",
        "accent": "violet",
    },
    "cost": {
        "title": "Calculadora de entrenamiento",
        "description": "Estima memoria, tiempo y coste según escala.",
        "icon": "calculator",
        "accent": "amber",
    },
}

LAB_META_EN: dict[str, dict[str, str]] = {
    "memory": {
        "title": "Memory explorer",
        "description": "Compare weights, quantization, and training memory.",
        "icon": "cpu",
        "accent": "blue",
    },
    "labels": {
        "title": "Label factory",
        "description": "Turn a sentence into input → target pairs.",
        "icon": "tag",
        "accent": "violet",
    },
    "transformer": {
        "title": "Inside the transformer",
        "description": "Walk through encoder, decoder, and attention step by step.",
        "icon": "layers",
        "accent": "amber",
    },
    "attention": {
        "title": "Attention map",
        "description": "Discover which tokens each word looks at.",
        "icon": "eye",
        "accent": "teal",
    },
    "ngram": {
        "title": "N-gram generator",
        "description": "Train on Don Quixote, adjust temperature, and generate text.",
        "icon": "sparkles",
        "accent": "blue",
    },
    "prompt": {
        "title": "Prompt builder",
        "description": "Assemble zero-shot and few-shot examples and copy them.",
        "icon": "message",
        "accent": "violet",
    },
    "cost": {
        "title": "Training calculator",
        "description": "Estimate memory, time, and cost at different scales.",
        "icon": "calculator",
        "accent": "amber",
    },
}


for _module in MODULES:
    LAB_META.update(_module.LAB_META_ES)
    LAB_META_EN.update(_module.LAB_META_EN)


def lab_meta_for(lang: str = "es") -> dict[str, dict[str, str]]:
    return LAB_META_EN if lang == "en" else LAB_META
