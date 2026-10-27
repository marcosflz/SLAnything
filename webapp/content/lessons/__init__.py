"""Lecciones del capítulo 1.

Cada módulo exporta `LESSON`. El orden de esta lista es el orden del curso.
"""

from webapp.content.lessons import (
    l01_que_es,
    l02_pretraining,
    l03_transformer,
    l04_escala,
    l05_siguiente_palabra,
    l06_prompting,
    l07_construccion,
    l08_repaso,
)

LESSONS = (
    l01_que_es.LESSON,
    l02_pretraining.LESSON,
    l03_transformer.LESSON,
    l04_escala.LESSON,
    l05_siguiente_palabra.LESSON,
    l06_prompting.LESSON,
    l07_construccion.LESSON,
    l08_repaso.LESSON,
)
