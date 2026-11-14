"""Estudio de autoría: documentos → unidades didácticas con agentes nas-adk.

* ``settings``: proveedor de IA de la plataforma.
* ``credentials``: proveedor propio de cada usuario (API key o suscripción).
* ``providers``: catálogo de proveedores y traducción a nas-adk.
* ``extract``: texto plano a partir de PDF, DOCX, EPUB, Markdown, HTML o TXT.
* ``package``: contrato JSON, saneado y construcción de objetos del catálogo.
* ``store``: trabajos y cursos generados.

La generación en sí vive en ``webapp/generation`` (ADR-017, ADR-023).
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
