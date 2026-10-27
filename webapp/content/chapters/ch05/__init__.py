"""Paquete de contenido del capítulo 5."""

from __future__ import annotations

from .chapter_en import CHAPTER_EN
from .chapter_es import CHAPTER_ES
from .glossary_en import GLOSSARY_EN
from .glossary_es import GLOSSARY_ES
from .labs import LAB_IDS, LAB_META_EN, LAB_META_ES
from .quiz_en import QUIZZES_EN
from .quiz_es import QUIZZES_ES

__all__ = [
    "CHAPTER_ES",
    "CHAPTER_EN",
    "QUIZZES_ES",
    "QUIZZES_EN",
    "GLOSSARY_ES",
    "GLOSSARY_EN",
    "LAB_META_ES",
    "LAB_META_EN",
    "LAB_IDS",
]
