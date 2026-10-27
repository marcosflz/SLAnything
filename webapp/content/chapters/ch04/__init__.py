"""Paquete de contenido del capítulo 4 · Arquitectura GPT.

El paquete es autocontenido: reúne las ocho lecciones en español e inglés, el
quiz de autoevaluación, el glosario y los metadatos del laboratorio nuevo.
"""

from webapp.content.chapters.ch04.chapter_en import CHAPTER_EN
from webapp.content.chapters.ch04.chapter_es import CHAPTER_ES
from webapp.content.chapters.ch04.glossary_en import GLOSSARY_EN
from webapp.content.chapters.ch04.glossary_es import GLOSSARY_ES
from webapp.content.chapters.ch04.labs import LAB_IDS, LAB_META_EN, LAB_META_ES
from webapp.content.chapters.ch04.quiz_en import QUIZZES_EN
from webapp.content.chapters.ch04.quiz_es import QUIZZES_ES

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
