"""Ingesta estructurada: documentos → secciones + fragmentos con id estable.

Sustituye al corte duro de 300 000 caracteres del motor anterior. Cada fuente
se convierte en una secuencia lineal de títulos y párrafos (con su página
cuando la hay); a partir de ella se construyen:

- ``sections``: árbol plano (nivel 1 y 2) que el usuario usa para elegir qué
  convertir. Cada sección de nivel 1 puede ser un capítulo de la unidad.
- ``chunks``: fragmentos de ~1 500 caracteres que nunca cruzan una sección, con
  id ``<fuente>:p<página>:c<n>``. Las lecciones citan estos ids y el
  verificador comprueba que existen y que el texto los respalda.

Detección de estructura por formato:

- PDF: marcadores (outline) del PDF; si no hay, títulos por patrón de línea.
- DOCX: estilos «Heading/Título N» y tablas en su posición.
- EPUB: orden del *spine* del OPF (no alfabético) y un título por documento.
- Markdown: ``#``/``##``. HTML: ``h1``/``h2``. TXT: patrones de línea.
"""

from __future__ import annotations

import html as html_lib
import json
import posixpath
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

from webapp.authoring.extract import SUPPORTED_EXTENSIONS, html_to_text

CHUNK_CHARS = 1500
SYNTHETIC_SECTION_CHARS = 14_000
MIN_SECTION_CHARS = 400

_HEADING_PATTERNS = (
    (1, re.compile(r"^(cap[ií]tulo|chapter|unidad|unit|tema|lecci[oó]n|parte|part)\s+[\w\dIVXLC]+\b.{0,80}$", re.I)),
    (1, re.compile(r"^\d{1,2}\s+[A-ZÁÉÍÓÚÑ][^.!?]{2,80}$")),
    (2, re.compile(r"^\d{1,2}\.\d{1,2}\s+[A-ZÁÉÍÓÚÑ][^.!?]{2,90}$")),
)


@dataclass
class Item:
    kind: str  # "heading" | "para"
    text: str
    level: int = 0
    page: int | None = None


@dataclass
class _Section:
    id: str
    title: str
    level: int
    source: str
    page_start: int | None
    page_end: int | None = None
    chunk_ids: list[str] = field(default_factory=list)
    chars: int = 0
    parent: str | None = None


# ---------------------------------------------------------------------------
# Lectura por formato → secuencia de Items
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("­", "")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", _clean(text))
    result = []
    for block in blocks:
        joined = re.sub(r"(?<![.!?:;])\n(?!\n)", " ", block).strip()
        if joined:
            result.append(joined)
    return result


def _line_heading(line: str) -> int:
    stripped = line.strip()
    if not 3 <= len(stripped) <= 100:
        return 0
    for level, pattern in _HEADING_PATTERNS:
        if pattern.match(stripped):
            return level
    return 0


def _items_from_plain(text: str, page: int | None = None) -> list[Item]:
    """Texto sin marcas: detecta títulos por patrón de línea."""
    items: list[Item] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            items.extend(Item("para", p, page=page) for p in _paragraphs("\n".join(buffer)))
            buffer.clear()

    # Línea a línea: en PDFs y TXT los títulos suelen ir en su propia línea,
    # sin línea en blanco alrededor.
    for line in _clean(text).split("\n"):
        level = _line_heading(line)
        if level:
            flush()
            items.append(Item("heading", line.strip(), level, page))
        else:
            buffer.append(line)
    flush()
    return items


def _pdf_items(path: Path) -> tuple[list[Item], int, list[str]]:
    from pypdf import PdfReader

    warnings: list[str] = []
    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"No se pudo abrir el PDF: {exc}") from exc
    if reader.is_encrypted:
        raise ValueError("El PDF está protegido con contraseña.")

    # Marcadores → {página: [(nivel, título)]}
    marks: dict[int, list[tuple[int, str]]] = {}

    def walk(nodes, depth: int) -> None:
        for node in nodes:
            if isinstance(node, list):
                walk(node, depth + 1)
                continue
            try:
                page = reader.get_destination_page_number(node) + 1
                title = str(node.title).strip()
            except Exception:  # noqa: BLE001
                continue
            if title and depth <= 2:
                marks.setdefault(page, []).append((depth, title))

    try:
        walk(reader.outline, 1)
    except Exception:  # noqa: BLE001
        marks = {}

    items: list[Item] = []
    empty_pages = 0
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001
            text = ""
        for level, title in marks.get(number, []):
            items.append(Item("heading", title, level, number))
        if not text.strip():
            empty_pages += 1
            continue
        if marks:
            items.extend(Item("para", p, page=number) for p in _paragraphs(text))
        else:
            items.extend(_items_from_plain(text, number))
    total = len(reader.pages)
    if empty_pages == total:
        raise ValueError(
            "El PDF no contiene texto extraíble. Si es un escaneo, aplica OCR antes de subirlo."
        )
    if empty_pages:
        warnings.append(
            f"{path.name}: {empty_pages} de {total} páginas sin texto (¿escaneadas?). "
            "Aplica OCR si contienen contenido importante."
        )
    if not marks:
        warnings.append(f"{path.name}: el PDF no tiene marcadores; los capítulos se han detectado por el texto.")
    return items, total, warnings


def _docx_items(path: Path) -> list[Item]:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    try:
        document = Document(str(path))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"No se pudo abrir el DOCX: {exc}") from exc
    items: list[Item] = []
    body = document.element.body
    for child in body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            paragraph = Paragraph(child, document)
            text = paragraph.text.strip()
            if not text:
                continue
            style = (paragraph.style.name if paragraph.style is not None else "") or ""
            match = re.search(r"(heading|t[ií]tulo)\s*(\d)", style, re.I)
            if match and int(match.group(2)) <= 2:
                items.append(Item("heading", text, int(match.group(2))))
            elif style.lower() == "title":
                items.append(Item("heading", text, 1))
            else:
                items.append(Item("para", text))
        elif tag == "tbl":
            table = Table(child, document)
            rows = []
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                items.append(Item("para", "\n".join(rows)))
    return items


def _epub_items(path: Path) -> list[Item]:
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"No se pudo abrir el EPUB: {exc}") from exc
    with archive:
        names = archive.namelist()
        order: list[str] = []
        try:
            container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
            rootfile = next(el for el in container.iter() if el.tag.endswith("rootfile"))
            opf_path = rootfile.attrib["full-path"]
            opf = ElementTree.fromstring(archive.read(opf_path))
            base = posixpath.dirname(opf_path)
            manifest = {
                el.attrib.get("id"): el.attrib.get("href")
                for el in opf.iter()
                if el.tag.endswith("item")
            }
            for ref in (el for el in opf.iter() if el.tag.endswith("itemref")):
                href = manifest.get(ref.attrib.get("idref"))
                if href:
                    order.append(posixpath.normpath(posixpath.join(base, href)))
        except (KeyError, StopIteration, ElementTree.ParseError):
            order = []
        if not order:
            order = sorted(n for n in names if n.lower().endswith((".xhtml", ".html", ".htm")))
        items: list[Item] = []
        for name in order:
            if name not in names:
                continue
            raw = archive.read(name).decode("utf-8", errors="replace")
            items.extend(_html_items(raw, default_title=True))
    if not items:
        raise ValueError("El EPUB no contiene texto legible.")
    return items


_HEADING_TAG = re.compile(r"<h([12])[^>]*>(.*?)</h\1>", re.I | re.S)


def _html_items(raw: str, default_title: bool = False) -> list[Item]:
    items: list[Item] = []
    position = 0
    found = False
    for match in _HEADING_TAG.finditer(raw):
        before = html_to_text(raw[position:match.start()])
        items.extend(Item("para", p) for p in _paragraphs(before))
        title = html_lib.unescape(re.sub(r"<[^>]+>", " ", match.group(2)))
        title = re.sub(r"\s+", " ", title).strip()
        if title:
            items.append(Item("heading", title[:160], int(match.group(1))))
            found = True
        position = match.end()
    rest = html_to_text(raw[position:])
    items.extend(Item("para", p) for p in _paragraphs(rest))
    if default_title and not found and items:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
        if title_match and len(rest) > MIN_SECTION_CHARS:
            items.insert(0, Item("heading", html_lib.unescape(title_match.group(1)).strip()[:160], 1))
    return items


def _markdown_items(text: str) -> list[Item]:
    items: list[Item] = []
    buffer: list[str] = []
    found = False

    def flush() -> None:
        if buffer:
            items.extend(Item("para", p) for p in _paragraphs("\n".join(buffer)))
            buffer.clear()

    for line in text.splitlines():
        match = re.match(r"^(#{1,2})\s+(.+?)\s*#*\s*$", line)
        if match:
            flush()
            items.append(Item("heading", match.group(2).strip()[:160], len(match.group(1))))
            found = True
        else:
            buffer.append(line)
    flush()
    return items if found else _items_from_plain(text)


def read_items(path: Path) -> tuple[list[Item], int | None, list[str]]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato no admitido en {path.name!r}.")
    if suffix == ".pdf":
        return _pdf_items(path)
    if suffix == ".docx":
        return _docx_items(path), None, []
    if suffix == ".epub":
        return _epub_items(path), None, []
    if suffix in {".html", ".htm", ".odt"}:
        if suffix == ".odt":
            from webapp.authoring.extract import extract_text

            return _items_from_plain(extract_text(path)), None, []
        return _html_items(path.read_text(encoding="utf-8", errors="replace")), None, []
    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix in {".md", ".markdown"}:
        return _markdown_items(text), None, []
    return _items_from_plain(text), None, []


# ---------------------------------------------------------------------------
# Secuencia → secciones y fragmentos
# ---------------------------------------------------------------------------

def _source_key(index: int) -> str:
    return f"d{index}"


def build_document(paths: Iterable[Path], max_chars: int | None = None) -> dict:
    """Construye ``document.json`` a partir de varias fuentes, en orden."""
    sources: list[dict] = []
    sections: list[_Section] = []
    chunks: list[dict] = []
    warnings: list[str] = []
    total_chars = 0
    truncated = False

    for index, path in enumerate(paths, start=1):
        key = _source_key(index)
        items, pages, item_warnings = read_items(path)
        warnings.extend(item_warnings)
        sources.append({"key": key, "name": path.name, "pages": pages})
        if not any(item.kind == "heading" and item.level == 1 for item in items):
            items = _synthetic_sections(items, path.stem)

        current_top: _Section | None = None
        current: _Section | None = None
        buffer: list[str] = []
        buffer_page: int | None = None
        counters: dict[int | None, int] = {}

        def flush() -> None:
            nonlocal buffer, buffer_page, total_chars, truncated
            if not buffer or current is None:
                buffer = []
                return
            text = "\n\n".join(buffer).strip()
            buffer = []
            if not text:
                return
            if max_chars and total_chars >= max_chars:
                truncated = True
                return
            page = buffer_page
            counters[page] = counters.get(page, 0) + 1
            chunk_id = f"{key}:p{page}:c{counters[page]}" if page else f"{key}:c{len(chunks) + 1}"
            chunks.append({"id": chunk_id, "source": key, "page": page, "section": current.id, "text": text})
            total_chars += len(text)
            targets = [current] if current is current_top else [current, current_top]
            for section in targets:
                if section is None:
                    continue
                section.chunk_ids.append(chunk_id)
                section.chars += len(text)
                if page:
                    section.page_end = max(section.page_end or page, page)

        for item in items:
            if item.kind == "heading":
                flush()
                section = _Section(
                    id=f"s{len(sections) + 1}",
                    title=item.text,
                    level=1 if item.level <= 1 or current_top is None else 2,
                    source=key,
                    page_start=item.page,
                    page_end=item.page,
                )
                if section.level == 1:
                    current_top = section
                else:
                    section.parent = current_top.id if current_top else None
                sections.append(section)
                current = section
                buffer_page = item.page
                continue
            if current is None:
                current = current_top = _Section(
                    id=f"s{len(sections) + 1}", title=path.stem, level=1, source=key,
                    page_start=item.page, page_end=item.page,
                )
                sections.append(current)
            if buffer and (
                sum(len(part) for part in buffer) + len(item.text) > CHUNK_CHARS
                or (item.page and buffer_page and item.page != buffer_page)
            ):
                flush()
            if not buffer:
                buffer_page = item.page
            buffer.append(item.text)
        flush()

    # Fusiona secciones de nivel 1 casi vacías (portadas, índices…) con la siguiente.
    tops = [section for section in sections if section.level == 1]
    for previous, following in zip(tops, tops[1:]):
        if previous.chars < MIN_SECTION_CHARS and previous.chunk_ids:
            following.chunk_ids = previous.chunk_ids + following.chunk_ids
            following.chars += previous.chars
            previous.chunk_ids, previous.chars = [], 0
    sections = [section for section in sections if section.chars > 0]

    if not chunks:
        raise ValueError("No se ha podido extraer texto suficiente de los documentos.")
    if truncated:
        warnings.append(
            f"Se han procesado los primeros {max_chars:,} caracteres; el resto se ha omitido."
        )
    return {
        "version": 1,
        "sources": sources,
        "sections": [
            {
                "id": s.id,
                "title": s.title,
                "level": s.level,
                "parent": s.parent,
                "source": s.source,
                "page_start": s.page_start,
                "page_end": s.page_end,
                "chunk_ids": s.chunk_ids,
                "chars": s.chars,
                "words": round(s.chars / 5.8),
            }
            for s in sections
        ],
        "chunks": chunks,
        "stats": {
            "chars": total_chars,
            "chunks": len(chunks),
            "sections": len([s for s in sections if s.level == 1]),
            "pages": sum(source["pages"] or 0 for source in sources) or None,
            "truncated": truncated,
        },
        "warnings": warnings,
    }


def _synthetic_sections(items: list[Item], stem: str) -> list[Item]:
    """Sin títulos detectables: crea partes de ~14 000 caracteres."""
    result: list[Item] = []
    size = 0
    part = 0
    for item in items:
        if item.kind == "heading" and item.level == 2:
            result.append(item)
            continue
        if size == 0 or size >= SYNTHETIC_SECTION_CHARS:
            part += 1
            page = f" (p. {item.page})" if item.page else ""
            result.append(Item("heading", f"{stem} · parte {part}{page}", 1, item.page))
            size = 0
        result.append(item)
        size += len(item.text)
    return result


def public_outline(document: dict) -> dict:
    """Versión ligera para la UI: secciones sin el texto de los fragmentos."""
    return {
        "sources": document["sources"],
        "sections": [
            {key: value for key, value in section.items() if key != "chunk_ids"}
            | {"chunks": len(section["chunk_ids"])}
            for section in document["sections"]
        ],
        "stats": document["stats"],
        "warnings": document["warnings"],
    }


def chunk_map(document: dict) -> dict[str, dict]:
    return {chunk["id"]: chunk for chunk in document["chunks"]}


def save(document: dict, path: Path) -> None:
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
