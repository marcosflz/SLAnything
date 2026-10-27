"""Exporta las traducciones de interfaz de FastAPI al frontend Next.js.

FastAPI sigue siendo la fuente única durante la migración. Cuando el frontend
sea la única interfaz, este script se puede sustituir por un fichero TypeScript
propio sin tocar los componentes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp.i18n import EN  # noqa: E402
TARGET = ROOT / "frontend" / "src" / "lib" / "messages.json"


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(EN, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Exportadas {len(EN)} traducciones a {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
