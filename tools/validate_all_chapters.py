"""Valida todos los capítulos integrados y sus colisiones globales.

Uso:

    uv run python tools/validate_all_chapters.py

Se ejecuta después de integrar los paquetes de los capítulos 2-7. Comprueba lo
que un validador por capítulo no puede ver: slugs, quizzes y términos de
glosario repetidos entre capítulos, además de los labs y las figuras.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp import config  # noqa: E402
from webapp.content import (  # noqa: E402
    COURSES,
    GLOSSARIES,
    QUIZZES_BY_LANG,
    validate_program,
)


def main() -> int:
    errors: list[str] = []

    for lang, program in COURSES.items():
        try:
            validate_program(
                program,
                QUIZZES_BY_LANG[lang],
                config.KNOWN_LABS,
                config.STATIC_DIR,
                GLOSSARIES[lang],
            )
        except ValueError as exc:
            errors.append(f"{lang}: {exc}")

        slugs = [lesson.slug for lesson in program.lessons]
        duplicates = {slug for slug in slugs if slugs.count(slug) > 1}
        if duplicates:
            errors.append(f"{lang}: slugs duplicados: {sorted(duplicates)}")

        terms = [term.term.casefold() for term in GLOSSARIES[lang]]
        repeated = {term for term in terms if terms.count(term) > 1}
        if repeated:
            errors.append(f"{lang}: términos de glosario repetidos: {sorted(repeated)}")

        quiz_ids = {quiz_id for quiz_id in QUIZZES_BY_LANG[lang] if quiz_id}
        linked = {lesson.quiz_id for lesson in program.lessons if lesson.quiz_id}
        unused = quiz_ids - linked
        if unused:
            errors.append(f"{lang}: quizzes sin lección: {sorted(unused)}")

        for lab_id in config.KNOWN_LABS:
            module = config.STATIC_DIR / "js" / "labs" / f"{lab_id}.js"
            if not module.is_file():
                errors.append(f"{lang}: falta el módulo JS del lab {lab_id}.")

    if errors:
        print(f"{len(errors)} problema(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    for lang, program in COURSES.items():
        print(
            f"{lang}: {program.chapter_count} capítulos · "
            f"{program.lesson_count} lecciones · {program.total_minutes} min · "
            f"{len(GLOSSARIES[lang])} términos · "
            f"{len(QUIZZES_BY_LANG[lang])} quizzes"
        )
    print(f"Labs: {len(config.KNOWN_LABS)} · {', '.join(sorted(config.KNOWN_LABS))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
