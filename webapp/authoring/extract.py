"""Extracción de texto de los documentos que se suben al Estudio.

El agente no recibe PDFs binarios: recibe Markdown troceado con marcas de página.
Así el modelo puede citar el origen y el backend controla tamaño y formato.
"""

from __future__ import annotations

import html
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".markdown", ".txt", ".html", ".htm", ".epub", ".odt"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "head"}:
            self._skip += 1
        elif tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "blockquote"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "head"} and self._skip:
            self._skip -= 1
        elif tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "blockquote"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_to_text(source: str) -> str:
    parser = _TextExtractor()
    parser.feed(source)
    parser.close()
    return _clean(html.unescape(parser.text()))


def _pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depende del entorno
        raise ValueError("Falta pypdf para leer PDFs.") from exc
    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise ValueError(f"No se pudo abrir el PDF: {exc}") from exc
    if reader.is_encrypted:
        raise ValueError("El PDF está protegido con contraseña.")
    parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            parts.append(f"\n\n--- Página {index} ---\n\n{text}")
    if not parts:
        raise ValueError(
            "El PDF no contiene texto extraíble. Si es un escaneo, aplica OCR antes de subirlo."
        )
    return _clean("".join(parts))


def _docx_text(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover
        raise ValueError("Falta python-docx para leer DOCX.") from exc
    try:
        document = Document(str(path))
    except Exception as exc:
        raise ValueError(f"No se pudo abrir el DOCX: {exc}") from exc
    parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return _clean("\n\n".join(parts))


def _epub_text(path: Path) -> str:
    parts: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = sorted(
                name
                for name in archive.namelist()
                if name.lower().endswith((".xhtml", ".html", ".htm"))
            )
            for name in names:
                raw = archive.read(name).decode("utf-8", errors="replace")
                text = html_to_text(raw)
                if text:
                    parts.append(f"\n\n--- Sección: {name} ---\n\n{text}")
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"No se pudo abrir el EPUB: {exc}") from exc
    if not parts:
        raise ValueError("El EPUB no contiene texto legible.")
    return _clean("".join(parts))


def _odt_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            raw = archive.read("content.xml").decode("utf-8", errors="replace")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise ValueError(f"No se pudo abrir el ODT: {exc}") from exc
    return html_to_text(raw)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Formato no admitido en {path.name!r}. Usa PDF, DOCX, EPUB, ODT, "
            "Markdown, HTML o TXT."
        )
    if suffix == ".pdf":
        text = _pdf_text(path)
    elif suffix == ".docx":
        text = _docx_text(path)
    elif suffix == ".epub":
        text = _epub_text(path)
    elif suffix == ".odt":
        text = _odt_text(path)
    elif suffix in {".html", ".htm"}:
        text = html_to_text(path.read_text(encoding="utf-8", errors="replace"))
    else:
        text = _clean(path.read_text(encoding="utf-8", errors="replace"))
    if len(text.strip()) < 40:
        raise ValueError(f"{path.name!r} no contiene suficiente texto para una unidad.")
    return text


def chunk_text(text: str, max_chars: int, chunk_chars: int = 45_000) -> tuple[list[str], bool]:
    """Trocea el texto en partes legibles y avisa si se ha recortado."""
    truncated = len(text) > max_chars
    text = text[:max_chars]
    parts: list[str] = []
    cursor = 0
    while cursor < len(text):
        end = min(len(text), cursor + chunk_chars)
        if end < len(text):
            # Corta en un párrafo o una línea para no romper frases.
            boundary = text.rfind("\n\n", cursor, end)
            if boundary > cursor + chunk_chars // 2:
                end = boundary
        parts.append(text[cursor:end].strip())
        cursor = end
    return [part for part in parts if part], truncated


def write_source_parts(text: str, destination: Path, max_chars: int) -> dict:
    """Escribe ``source/*.md`` y devuelve metadatos para el agente."""
    destination.mkdir(parents=True, exist_ok=True)
    parts, truncated = chunk_text(text, max_chars)
    written = []
    for index, part in enumerate(parts, start=1):
        path = destination / f"source-{index:02d}.md"
        path.write_text(
            f"# Documento de origen · parte {index} de {len(parts)}\n\n{part}\n",
            encoding="utf-8",
        )
        written.append(path.name)
    return {
        "parts": written,
        "part_count": len(written),
        "characters": len(text),
        "truncated": truncated,
    }
