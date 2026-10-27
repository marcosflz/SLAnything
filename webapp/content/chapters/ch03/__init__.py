"""Capítulo 3 · Atención.

Paquete autocontenido con las ocho lecciones, el quiz, el glosario y los metadatos del
laboratorio del capítulo. La integración central lo importa sin editar este archivo.
"""

from webapp.content.chapters.ch03.chapter_en import CHAPTER as CHAPTER_EN
from webapp.content.chapters.ch03.chapter_es import CHAPTER as CHAPTER_ES
from webapp.content.chapters.ch03.glossary_en import GLOSSARY as GLOSSARY_EN
from webapp.content.chapters.ch03.glossary_es import GLOSSARY as GLOSSARY_ES
from webapp.content.chapters.ch03.labs import LAB_IDS, LAB_META_EN, LAB_META_ES
from webapp.content.chapters.ch03.quiz_en import QUIZZES as QUIZZES_EN
from webapp.content.chapters.ch03.quiz_es import QUIZZES as QUIZZES_ES

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
