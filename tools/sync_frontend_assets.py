"""Sincroniza los assets compartidos entre Jinja y Next.js.

Durante la migración el CSS vive en `webapp/static/css/app.css` para que la
interfaz antigua y la nueva no diverjan. Next.js importa una copia local; este
script la actualiza.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "webapp" / "static" / "css" / "app.css"
TARGET = ROOT / "frontend" / "src" / "app" / "app.css"

BANNER = (
    "/* Copia generada por tools/sync_frontend_assets.py desde\n"
    "   webapp/static/css/app.css. No editar a mano durante la migración. */\n\n"
)


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(BANNER + SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"CSS sincronizado: {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
