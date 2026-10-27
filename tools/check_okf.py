#!/usr/bin/env python
"""Validador del bundle OKF v0.2 de Aula LLM.

Comprueba conformidad estructural, enlaces internos, índices, log y metadatos
recomendados. No valida la veracidad del contenido.

Uso:
    uv run python tools/check_okf.py
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "okf"
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
ACTOR_RE = re.compile(
    r"^(?:human:[A-Za-z0-9_.-]+|process:[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)$"
)

errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    return path.relative_to(BUNDLE).as_posix()


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.append(f"{rel(path)}: YAML inválido: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{rel(path)}: el frontmatter debe ser un mapping YAML.")
        return None
    return data


def parse_time(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def check_time(path: Path, field: str, value: object) -> None:
    parsed = parse_time(value)
    if parsed is None or parsed.tzinfo is None:
        errors.append(f"{rel(path)}: `{field}` debe ser ISO 8601 con offset UTC.")


def resolve_link(source: Path, target: str) -> Path | None:
    target = target.strip()
    if not target or target.startswith(("#", "mailto:")):
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    clean = target.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    path = BUNDLE / clean.lstrip("/") if clean.startswith("/") else source.parent / clean
    return path.resolve()


def check_links(path: Path, text: str) -> None:
    for raw in LINK_RE.findall(text):
        resolved = resolve_link(path, raw)
        if resolved is None:
            continue
        if BUNDLE not in resolved.parents and resolved != BUNDLE:
            # Enlaces a documentación externa al bundle: se permiten si existen.
            if not resolved.exists():
                warnings.append(f"{rel(path)}: enlace externo al bundle no encontrado: {raw}")
            continue
        if not resolved.exists():
            errors.append(f"{rel(path)}: enlace roto: {raw}")


def check_index(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if path == BUNDLE / "index.md":
        data = parse_frontmatter(path)
        if data is None:
            errors.append("okf/index.md: falta el frontmatter con okf_version.")
            return
        if data.get("okf_version") != "0.2":
            errors.append("okf/index.md: okf_version debe ser '0.2'.")
        extra = set(data) - {"okf_version"}
        if extra:
            errors.append(
                "okf/index.md: el índice raíz solo admite okf_version; "
                f"claves extra: {', '.join(sorted(extra))}."
            )
    else:
        if FRONTMATTER_RE.match(text):
            errors.append(f"{rel(path)}: los index.md no deben llevar frontmatter.")
    if not LINK_RE.search(text):
        warnings.append(f"{rel(path)}: índice sin enlaces.")
    check_links(path, text)


def check_log(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    matches = DATE_RE.findall(text)
    if not matches:
        errors.append("okf/log.md: no contiene ninguna cabecera '## YYYY-MM-DD'.")
        return
    dates: list[datetime] = []
    for value in matches:
        try:
            dates.append(datetime.strptime(value, "%Y-%m-%d"))
        except ValueError:
            errors.append(f"okf/log.md: fecha inválida {value}.")
    if dates != sorted(dates, reverse=True):
        errors.append("okf/log.md: las fechas deben ir de más reciente a más antigua.")


def check_concept(path: Path) -> None:
    data = parse_frontmatter(path)
    if data is None:
        errors.append(f"{rel(path)}: falta frontmatter YAML parseable.")
        return
    if not isinstance(data.get("type"), str) or not data["type"].strip():
        errors.append(f"{rel(path)}: falta el campo obligatorio `type`.")
    for field in ("title", "description"):
        if not data.get(field):
            warnings.append(f"{rel(path)}: falta `{field}` recomendado.")
    if "generated" in data:
        generated = data["generated"]
        if not isinstance(generated, dict):
            errors.append(f"{rel(path)}: `generated` debe ser un mapping.")
        else:
            if not ACTOR_RE.match(str(generated.get("by", ""))):
                errors.append(
                    f"{rel(path)}: `generated.by` no sigue el convenio de actor: "
                    f"{generated.get('by')!r}."
                )
            check_time(path, "generated.at", generated.get("at"))
    else:
        warnings.append(f"{rel(path)}: falta `generated` (recomendado).")
    status = data.get("status")
    if status is not None and status not in {"draft", "stable", "deprecated"}:
        errors.append(f"{rel(path)}: status inválido {status!r}.")
    if "stale_after" in data:
        check_time(path, "stale_after", data["stale_after"])
    check_links(path, path.read_text(encoding="utf-8"))


def main() -> int:
    if not BUNDLE.is_dir():
        print("No existe el bundle okf/.", file=sys.stderr)
        return 1

    concept_paths: list[Path] = []
    index_paths: list[Path] = []
    log_paths: list[Path] = []

    for path in sorted(BUNDLE.rglob("*.md")):
        name = path.name
        if name == "index.md":
            index_paths.append(path)
        elif name == "log.md":
            log_paths.append(path)
        else:
            concept_paths.append(path)

    if not concept_paths:
        errors.append("El bundle no contiene conceptos.")

    for path in index_paths:
        check_index(path)
    for path in log_paths:
        check_log(path)
    for path in concept_paths:
        check_concept(path)

    # Cada concepto debería aparecer enlazado desde algún índice.
    linked: set[Path] = set()
    for path in index_paths:
        for raw in LINK_RE.findall(path.read_text(encoding="utf-8")):
            resolved = resolve_link(path, raw)
            if resolved is not None:
                linked.add(resolved)
    for path in concept_paths:
        if path.resolve() not in linked:
            warnings.append(f"{rel(path)}: no está enlazado desde ningún index.md.")

    # Cada directorio con conceptos debería tener su index.md.
    for directory in sorted({path.parent for path in concept_paths}):
        if directory == BUNDLE:
            continue
        if not (directory / "index.md").is_file():
            warnings.append(f"{directory.relative_to(BUNDLE).as_posix()}/: falta index.md.")

    print(f"OKF: {len(concept_paths)} conceptos, {len(index_paths)} índices, "
          f"{len(log_paths)} logs.")
    if warnings:
        print(f"\nAvisos ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print(f"\nErrores ({len(errors)}):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("\nBundle OKF conforme (v0.2).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
