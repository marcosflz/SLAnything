"""Verificación de una unidad generada contra su documento de origen.

- Citas válidas: cada id de ``sources`` existe en ``document.json``.
- Respaldo: el texto del bloque comparte vocabulario con los fragmentos que
  cita. Es una comprobación léxica (sin embeddings) que detecta bloques que se
  han ido del documento; no prueba que una frase sea cierta.
- Cobertura: qué parte de los bloques de contenido cita alguna fuente.
"""

from __future__ import annotations

import re
import unicodedata

CONTENT_BLOCKS = {"p", "callout", "list", "table"}
SUPPORT_THRESHOLD = 0.22
_STOP = set(
    "para como esta este estos estas pero sobre entre desde hasta donde cuando porque "
    "tambien también puede pueden tiene tienen sino según segun cada otro otra otros "
    "otras with that this from have which there their about into would could should "
    "these those other where when because while being after before document documento".split()
)


def _norm(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in text if not unicodedata.combining(char))


def _words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]{5,}", _norm(text)) if word not in _STOP}


def block_text(block: dict) -> str:
    parts = [str(block.get(key) or "") for key in ("html", "text", "title", "question", "answer")]
    for key in ("items", "headers"):
        parts.extend(str(item) for item in block.get(key) or [])
    for row in block.get("rows") or []:
        parts.extend(str(cell) for cell in row)
    return " ".join(parts)


def support_score(text: str, sources: list[str], chunks: dict[str, dict]) -> float:
    words = _words(text)
    if not words:
        return 1.0
    reference: set[str] = set()
    for source in sources:
        chunk = chunks.get(source)
        if chunk:
            reference |= _words(chunk["text"])
    if not reference:
        return 0.0
    return len(words & reference) / len(words)


def verify_package(package: dict, chunks: dict[str, dict]) -> dict:
    """Marca bloques sin respaldo (``unsupported``) y devuelve el informe."""
    languages = package.get("languages") or ["es"]
    primary = languages[0]
    content = cited = 0
    invalid: list[dict] = []
    unsupported: list[dict] = []
    lessons = 0
    for chapter in package.get("chapters", []):
        for lesson in chapter.get("lessons", []):
            lessons += 1
            blocks_by_lang = lesson.get("blocks") or {}
            for lang, blocks in (blocks_by_lang.items() if isinstance(blocks_by_lang, dict) else []):
                for index, block in enumerate(blocks):
                    if not isinstance(block, dict):
                        continue
                    sources = [s for s in block.get("sources") or [] if isinstance(s, str)]
                    bad = [s for s in sources if s not in chunks]
                    if bad:
                        invalid.append({"lesson": lesson.get("slug"), "lang": lang, "block": index, "refs": bad})
                        sources = [s for s in sources if s in chunks]
                        block["sources"] = sources
                    if block.get("type") not in CONTENT_BLOCKS:
                        continue
                    if lang == primary:
                        content += 1
                        if sources:
                            cited += 1
                    # El respaldo léxico solo es fiable en el idioma del documento.
                    if lang == primary and sources:
                        score = support_score(block_text(block), sources, chunks)
                        if score < SUPPORT_THRESHOLD:
                            block["unsupported"] = True
                            unsupported.append(
                                {
                                    "lesson": lesson.get("slug"),
                                    "block": index,
                                    "score": round(score, 2),
                                    "excerpt": re.sub(r"<[^>]+>", "", block_text(block))[:160],
                                }
                            )
                        else:
                            block.pop("unsupported", None)
    return {
        "lessons": lessons,
        "content_blocks": content,
        "cited_blocks": cited,
        "cited_pct": round(cited * 100 / content) if content else 0,
        "unsupported": unsupported,
        "invalid_refs": invalid,
    }
