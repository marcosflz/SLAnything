"""Saneado del HTML que puede llegar desde el Estudio de autoría.

El contenido del curso de referencia se escribe a mano y es de confianza. El
contenido generado por un modelo no lo es: aunque el agente solo escriba datos,
un documento de origen puede contener instrucciones maliciosas. Antes de guardar
un paquete se limpia todo el HTML con una lista blanca de etiquetas y atributos.
"""

from __future__ import annotations

import html
from html.parser import HTMLParser

ALLOWED_TAGS = {
    "a",
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "h4",
    "i",
    "li",
    "mark",
    "ol",
    "p",
    "pre",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "u",
    "ul",
}

VOID_TAGS = {"br"}

ALLOWED_ATTRS = {
    "a": {"href", "title"},
    "code": {"class"},
    "span": {"class"},
}

SKIP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed"}


def _safe_href(value: str) -> str | None:
    value = value.strip()
    lowered = value.lower()
    if lowered.startswith(("http://", "https://", "mailto:")):
        return value
    if value.startswith(("/", "#")):
        return value
    return None


class _Sanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in SKIP_CONTENT_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag not in ALLOWED_TAGS:
            return
        cleaned: list[str] = []
        allowed = ALLOWED_ATTRS.get(tag, set())
        for name, value in attrs:
            if name not in allowed or value is None:
                continue
            if name == "href":
                value = _safe_href(value)
                if value is None:
                    continue
            if name == "class":
                # Solo clases inocuas de resaltado; nunca estilos ni eventos.
                if not value.replace("-", "").replace("_", "").replace(" ", "").isalnum():
                    continue
            cleaned.append(f' {name}="{html.escape(value, quote=True)}"')
        attrs_text = "".join(cleaned)
        if tag in VOID_TAGS:
            self._parts.append(f"<{tag}{attrs_text}>")
        else:
            self._parts.append(f"<{tag}{attrs_text}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_CONTENT_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in ALLOWED_TAGS and tag not in VOID_TAGS:
            self._parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._parts.append(html.escape(data, quote=False))

    def handle_comment(self, data: str) -> None:
        return

    def result(self) -> str:
        return "".join(self._parts).strip()


def sanitize_html(value: str, max_length: int = 12_000) -> str:
    """Devuelve HTML seguro y recortado a ``max_length`` caracteres."""
    if not isinstance(value, str):
        raise ValueError("El HTML debe ser una cadena.")
    value = value[:max_length]
    parser = _Sanitizer()
    parser.feed(value)
    parser.close()
    return parser.result()
