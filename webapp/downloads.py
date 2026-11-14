"""Helpers para generar los ficheros .py descargables de una lección."""

from __future__ import annotations



def python_header(lesson, index: int, total: int, lang: str) -> str:
    if lang == "en":
        title = f"# {lesson.title} · runnable example {index} of {total}"
        hint = (
            "# You can run this file with: python nombre-del-archivo.py\n"
            "# Some examples may need: pip install matplotlib pandas numpy\n"
        )
    else:
        title = f"# {lesson.title} · ejemplo ejecutable {index} de {total}"
        hint = (
            "# Puedes ejecutar este archivo con: python nombre-del-archivo.py\n"
            "# Algunos ejemplos pueden necesitar: pip install matplotlib pandas numpy\n"
        )
    return f"{title}\n{hint}\n"


def example_position(lesson, index: int) -> int:
    for position, (block_index, _) in enumerate(lesson.python_blocks, start=1):
        if block_index == index:
            return position
    return index


def python_code(lesson, index: int, block: dict, lang: str) -> str:
    total = len(lesson.python_blocks)
    position = example_position(lesson, index)
    parts = [python_header(lesson, position, total, lang)]
    if block.get("caption"):
        parts.append(f"# {block['caption']}\n\n")
    parts.append(block["code"].rstrip() + "\n")
    return "".join(parts)
