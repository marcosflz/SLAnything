"""Estudio de autoría: documentos → unidades didácticas con OpenCode.

El paquete separa cuatro responsabilidades:

* ``settings``: credenciales y modelo del proveedor LLM.
* ``extract``: texto plano a partir de PDF, DOCX, EPUB, Markdown, HTML o TXT.
* ``package``: contrato JSON, saneado y construcción de objetos del catálogo.
* ``runner``: ejecución de OpenCode en un directorio aislado y validación.
"""

from __future__ import annotations

from webapp.authoring.package import ParsedPackage, parse_package
from webapp.authoring.settings import (
    engine_status,
    load_settings,
    public_settings,
    save_settings,
)

__all__ = [
    "ParsedPackage",
    "engine_status",
    "load_settings",
    "parse_package",
    "public_settings",
    "save_settings",
]
