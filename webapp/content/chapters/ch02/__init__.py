"""Paquete de contenido del capítulo 2: trabajar con texto."""

from .chapter_en import CHAPTER as CHAPTER_EN
from .chapter_es import CHAPTER as CHAPTER_ES
from .glossary_en import GLOSSARY as GLOSSARY_EN
from .glossary_es import GLOSSARY as GLOSSARY_ES
from .labs import LAB_IDS, LAB_META as _LAB_META, LAB_META_EN
from .quiz_en import QUIZZES as QUIZZES_EN
from .quiz_es import QUIZZES as QUIZZES_ES

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

LAB_META_ES = _LAB_META
