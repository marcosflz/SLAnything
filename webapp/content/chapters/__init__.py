"""Paquetes de contenido de los capítulos 2-7.

Cada subpaquete (``ch02``, ``ch03``, …) es autocontenido y exporta:

* ``CHAPTER_ES`` / ``CHAPTER_EN``: ``Chapter`` con 8 lecciones.
* ``QUIZZES_ES`` / ``QUIZZES_EN``: ``dict[str, Quiz]``.
* ``GLOSSARY_ES`` / ``GLOSSARY_EN``: tupla de ``GlossaryTerm``.
* ``LAB_META_ES`` / ``LAB_META_EN``: metadatos de los laboratorios nuevos.
* ``LAB_IDS``: conjunto de identificadores de laboratorio del capítulo.

La integración central (``webapp/content/course.py``, ``webapp/labs.py`` y
``webapp/content/__init__.py``) importa estos paquetes. Los agentes de contenido
no deben editar los archivos compartidos.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

_NAMES = tuple(f"ch{number:02d}" for number in range(2, 8))

# Se importan solo los paquetes que ya existen. Así la integración es incremental
# y un capítulo a medio escribir no impide validar los demás.
MODULES = tuple(
    import_module(f"{__name__}.{name}")
    for name in _NAMES
    if (Path(__file__).parent / name / "__init__.py").is_file()
)

__all__ = ["MODULES"]
