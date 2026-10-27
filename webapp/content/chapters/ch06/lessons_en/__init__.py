"""Chapter 6 lessons in English, in order."""

from .l01_finetuning import LESSON as L01
from .l02_datos import LESSON as L02
from .l03_cabeza import LESSON as L03
from .l04_perdida import LESSON as L04
from .l05_entrenamiento import LESSON as L05
from .l06_metricas import LESSON as L06
from .l07_inferencia import LESSON as L07
from .l08_repaso import LESSON as L08

LESSONS = (L01, L02, L03, L04, L05, L06, L07, L08)

__all__ = ["LESSONS"]
