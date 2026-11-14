"""Generación por etapas con agentes nas-adk (ADR-017, ADR-023).

    queued → extracting → awaiting_scope → outlining → awaiting_outline
           → generating → validating → ready | failed | cancelled

Cada etapa guarda su resultado en el directorio del trabajo, así que un
reinicio retoma desde la última etapa completada sin volver a pagar las
llamadas ya hechas:

    document.json        ingesta estructurada (secciones + fragmentos)
    outline.json         temario editable por el usuario
    lessons/cN-lM.json   cada lección generada
    assess/cN.json       quiz + glosario de cada capítulo
    course.json          paquete final validado
    report.json          verificación de citas y avisos
    events.jsonl         progreso para la UI (SSE)

Cada llamada al modelo es un agente nas-adk (``runtime.run_agent``) con
herramientas propias (``tools.JobToolbox``) que entrega con ``submit_*``. Las
credenciales son siempre las de quien lanzó la acción (``credentials.resolve``).
"""

from __future__ import annotations

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from webapp import config
from webapp.authoring import credentials, store
from webapp.authoring.package import parse_package, slugify
from webapp.db import utcnow
from webapp.generation import document as doc
from webapp.generation import models, prompts, runtime, verify
from webapp.generation.tools import JobToolbox

logger = logging.getLogger("aula.generation")

FRAGMENT_BUDGET = 14_000  # caracteres de documento por lección
OUTLINE_EXCERPT = 240


Cancelled = runtime.Cancelled


# ---------------------------------------------------------------------------
# Utilidades de ficheros y progreso
# ---------------------------------------------------------------------------

def job_path(job_id: str, *parts: str) -> Path:
    return store.job_dir(job_id).joinpath(*parts)


def _read(job_id: str, name: str) -> Any:
    return json.loads(job_path(job_id, name).read_text(encoding="utf-8"))


def _write(job_id: str, name: str, data: Any) -> None:
    path = job_path(job_id, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


def emit(job_id: str, kind: str, message: str, **data: Any) -> None:
    """Añade un evento de progreso (lo lee el endpoint SSE)."""
    event = {"ts": utcnow(), "type": kind, "message": message, **data}
    path = job_path(job_id, "events.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_events(job_id: str, offset: int = 0) -> tuple[list[dict], int]:
    path = job_path(job_id, "events.jsonl")
    if not path.is_file():
        return [], offset
    with path.open("r", encoding="utf-8") as handle:
        handle.seek(offset)
        lines = handle.readlines()
        position = handle.tell()
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events, position


def _progress(job_id: str, **values: Any) -> None:
    job = store.get_job(job_id, with_log=False) or {}
    progress = dict(job.get("progress") or {})
    progress.update(values)
    store.update_job(job_id, progress_json=json.dumps(progress, ensure_ascii=False))


def _check(job_id: str) -> None:
    job = store.get_job(job_id, with_log=False)
    if job is None or job["status"] == "cancelled":
        raise Cancelled()


def _options(job_id: str) -> dict:
    job = store.get_job(job_id, with_log=False) or {}
    options = dict(job.get("config") or {})
    options.setdefault("languages", job.get("languages") or ["es"])
    return options


def _settings(job_id: str, actor_id: int | None = None) -> dict:
    """Proveedor con el que trabaja este paso: el de quien lanzó la acción."""
    job = store.get_job(job_id, with_log=False) or {}
    user_id = actor_id or job.get("actor_id") or job.get("owner_id")
    return credentials.resolve(int(user_id) if user_id else None)


_usage_lock = __import__("threading").Lock()


def _record_usage(job_id: str, tokens_in: int, tokens_out: int) -> None:
    with _usage_lock:
        job = store.get_job(job_id, with_log=False) or {}
        store.update_job(
            job_id,
            tokens_in=int(job.get("tokens_in") or 0) + int(tokens_in or 0),
            tokens_out=int(job.get("tokens_out") or 0) + int(tokens_out or 0),
        )


def _cancelled(job_id: str) -> bool:
    job = store.get_job(job_id, with_log=False)
    return job is None or job["status"] == "cancelled"


def _agent(job_id: str, toolbox: JobToolbox, message: str, settings: dict, stage: str) -> dict:
    """Ejecuta un agente de la tarea y devuelve lo que entregó."""
    result = runtime.run_agent(
        toolbox,
        settings,
        message,
        is_cancelled=lambda: _cancelled(job_id),
        on_tool=lambda text: emit(job_id, "tool", text, stage=stage),
    )
    _record_usage(job_id, result.input_tokens, result.output_tokens)
    return result.data


def _fail(job_id: str, exc: Exception) -> None:
    message = str(exc) or exc.__class__.__name__
    logger.exception("Generación %s fallida", job_id)
    emit(job_id, "error", message)
    store.update_job(job_id, status="failed", error=message[:2000], finished_at=utcnow())


# ---------------------------------------------------------------------------
# Etapa 1 · Ingesta estructurada
# ---------------------------------------------------------------------------

def analyze(job_id: str) -> None:
    try:
        store.update_job(job_id, status="extracting", stage="analyze", started_at=utcnow(), error=None)
        emit(job_id, "stage", "Analizando la estructura de los documentos…", stage="analyze")
        uploads = sorted(job_path(job_id, "uploads").glob("*"))
        document = doc.build_document(uploads, max_chars=config.GEN_MAX_CHARS)
        doc.save(document, job_path(job_id, "document.json"))
        stats = document["stats"]
        emit(
            job_id,
            "done",
            f"{stats['sections']} secciones y {stats['chunks']} fragmentos detectados.",
            stage="analyze",
        )
        for warning in document["warnings"]:
            emit(job_id, "warning", warning)
        _progress(job_id, sections=stats["sections"], chunks=stats["chunks"], pages=stats["pages"])
        store.update_job(job_id, status="awaiting_scope", stage="scope")
    except Exception as exc:  # noqa: BLE001
        _fail(job_id, exc)


# ---------------------------------------------------------------------------
# Etapa 2 · Temario
# ---------------------------------------------------------------------------

def _excerpts(document: dict, chunk_ids: list[str], limit: int = OUTLINE_EXCERPT) -> list[dict]:
    chunks = doc.chunk_map(document)
    return [
        {"id": cid, "page": chunks[cid]["page"], "text": chunks[cid]["text"][:limit]}
        for cid in chunk_ids
        if cid in chunks
    ]


def _fragments(document: dict, chunk_ids: list[str], budget: int = FRAGMENT_BUDGET) -> list[dict]:
    chunks = doc.chunk_map(document)
    result, used = [], 0
    for cid in chunk_ids:
        chunk = chunks.get(cid)
        if chunk is None:
            continue
        if used and used + len(chunk["text"]) > budget:
            break
        result.append({"id": cid, "page": chunk["page"], "text": chunk["text"]})
        used += len(chunk["text"])
    return result


def plan(job_id: str) -> None:
    """Un temario por sección elegida + la ficha del curso."""
    try:
        store.update_job(job_id, status="outlining", stage="outline", error=None)
        options = _options(job_id)
        document = doc.load(job_path(job_id, "document.json"))
        sections = {section["id"]: section for section in document["sections"]}
        scope = [sid for sid in options.get("scope", []) if sid in sections]
        if not scope:
            raise ValueError("Elige al menos una sección del documento.")
        settings = _settings(job_id)
        languages = options["languages"]
        chapters: list[dict] = []
        emit(job_id, "stage", f"Diseñando el temario de {len(scope)} capítulo(s)…", stage="outline", total=len(scope))
        for number, sid in enumerate(scope, start=1):
            _check(job_id)
            section = sections[sid]
            subsections = [s["title"] for s in document["sections"] if s.get("parent") == sid]
            result = _agent(
                job_id,
                JobToolbox(task="outline", document=document, languages=languages, scope_chunk_ids=section["chunk_ids"]),
                prompts.outline(
                    section=section,
                    excerpts=_excerpts(document, section["chunk_ids"]),
                    subsections=subsections,
                    options=options,
                    chapter_number=number,
                ),
                settings,
                "outline",
            )
            chapters.append(_normalize_outline(result, section, number))
            emit(job_id, "progress", f"Temario del capítulo {number}: {section['title']}", stage="outline", done=number, total=len(scope))

        course = _agent(
            job_id,
            JobToolbox(task="course", document=document, languages=languages),
            prompts.course(
                chapters=[{"title": c["title"], "description": c["description"]} for c in chapters],
                options=options,
                source_names=[s["name"] for s in document["sources"]],
            ),
            settings,
            "outline",
        )
        _write(job_id, "outline.json", {"course": course, "chapters": _unique_slugs(chapters)})
        lessons = sum(len(c["lessons"]) for c in chapters)
        _progress(job_id, chapters=len(chapters), lessons_total=lessons, lessons_done=0)
        emit(job_id, "done", f"Temario listo: {len(chapters)} capítulos y {lessons} lecciones.", stage="outline")
        if options.get("auto_approve"):
            store.update_job(job_id, status="generating", stage="generate")
            generate(job_id)
        else:
            store.update_job(job_id, status="awaiting_outline", stage="review_outline")
    except Cancelled:
        emit(job_id, "cancelled", "Generación cancelada.")
    except Exception as exc:  # noqa: BLE001
        _fail(job_id, exc)


def _unique_slugs(chapters: list[dict]) -> list[dict]:
    """Slugs de lección y capítulo únicos en todo el curso."""
    seen_lessons: set[str] = set()
    seen_chapters: set[str] = set()
    for chapter in chapters:
        base = slugify(chapter.get("slug") or f"capitulo-{chapter['number']}", f"capitulo-{chapter['number']}", 50)
        slug, n = base, 2
        while slug in seen_chapters:
            slug, n = f"{base}-{n}", n + 1
        seen_chapters.add(slug)
        chapter["slug"] = slug
        for index, lesson in enumerate(chapter.get("lessons", []), start=1):
            base = slugify(lesson.get("slug") or f"leccion-{index}", f"leccion-{index}", 50)
            slug, n = base, 2
            while slug in seen_lessons:
                slug, n = f"{base}-{n}", n + 1
            seen_lessons.add(slug)
            lesson["slug"] = slug
    return chapters


def _normalize_outline(result: dict, section: dict, number: int) -> dict:
    lessons = []
    seen: set[str] = set()
    for index, item in enumerate(result.get("lessons") or [], start=1):
        if not isinstance(item, dict):
            continue
        slug = slugify(item.get("slug") or f"leccion-{index}", f"leccion-{index}", 50)
        while slug in seen:
            slug = f"{slug}-{index}"
        seen.add(slug)
        chunk_ids = [c for c in item.get("chunk_ids") or [] if c in section["chunk_ids"]]
        lessons.append(
            {
                "slug": slug,
                "title": item.get("title") or {"es": f"Lección {index}"},
                "summary": item.get("summary") or item.get("title") or {},
                "objectives": [str(o) for o in item.get("objectives") or []],
                "chunk_ids": chunk_ids,
            }
        )
    if not lessons:
        raise ValueError(f"El temario del capítulo {number} no tiene lecciones.")
    # Fragmentos que el modelo no asignó: al final de la lección más cercana.
    assigned = {cid for lesson in lessons for cid in lesson["chunk_ids"]}
    for position, cid in enumerate(section["chunk_ids"]):
        if cid not in assigned:
            target = lessons[min(len(lessons) - 1, position * len(lessons) // max(1, len(section["chunk_ids"])))]
            target["chunk_ids"].append(cid)
    return {
        "number": number,
        "section_id": section["id"],
        "slug": slugify(section["title"], f"capitulo-{number}", 50),
        "title": result.get("title") or {"es": section["title"]},
        "subtitle": result.get("subtitle") or result.get("title") or {"es": section["title"]},
        "description": result.get("description") or {},
        "objectives": [o for o in result.get("objectives") or [] if isinstance(o, dict)],
        "lessons": lessons,
    }


def load_outline(job_id: str) -> dict:
    return _read(job_id, "outline.json")


def save_outline(job_id: str, outline: dict) -> dict:
    """Guarda el temario editado por el usuario (renombrar, reordenar, borrar)."""
    current = load_outline(job_id)
    chapters = []
    for chapter in outline.get("chapters") or []:
        lessons = [lesson for lesson in chapter.get("lessons") or [] if isinstance(lesson, dict)]
        if lessons:
            chapters.append({**chapter, "number": len(chapters) + 1, "lessons": lessons})
    if not chapters:
        raise ValueError("El temario debe conservar al menos un capítulo con lecciones.")
    current["chapters"] = _unique_slugs(chapters)
    if isinstance(outline.get("course"), dict):
        current["course"] = {**current.get("course", {}), **outline["course"]}
    _write(job_id, "outline.json", current)
    # Las lecciones ya generadas con un plan distinto dejan de valer.
    lessons_dir = job_path(job_id, "lessons")
    if lessons_dir.is_dir():
        for file in lessons_dir.glob("*.json"):
            file.unlink()
    _progress(job_id, lessons_total=sum(len(c["lessons"]) for c in chapters), lessons_done=0)
    return current


# ---------------------------------------------------------------------------
# Etapa 3 · Lecciones y evaluación (en paralelo, reanudable)
# ---------------------------------------------------------------------------

def _lesson_file(chapter: int, lesson: int) -> str:
    return f"lessons/c{chapter}-l{lesson}.json"


def _objective_texts(chapter: dict, ids: list[str], lang: str) -> list[str]:
    texts = []
    for objective in chapter.get("objectives", []):
        if objective.get("id") in ids:
            text = objective.get("text")
            texts.append(text.get(lang) if isinstance(text, dict) else str(text))
    return [t for t in texts if t]


def generate_lesson(
    job_id: str,
    settings: dict,
    document: dict,
    chapter: dict,
    index: int,
    options: dict,
    *,
    instructions: str = "",
    previous_error: str = "",
) -> dict:
    lesson_plan = dict(chapter["lessons"][index - 1])
    lesson_plan["objective_texts"] = _objective_texts(
        chapter, lesson_plan.get("objectives", []), options["languages"][0]
    )
    fragments = _fragments(document, lesson_plan.get("chunk_ids", []))
    toolbox = JobToolbox(
        task="lesson",
        document=document,
        languages=options["languages"],
        scope_chunk_ids=[cid for lesson in chapter["lessons"] for cid in lesson.get("chunk_ids", [])],
        lesson_slug=lesson_plan["slug"],
    )
    result = _agent(
        job_id,
        toolbox,
        prompts.lesson(
            chapter=chapter,
            lesson_plan=lesson_plan,
            lesson_number=index,
            lesson_count=len(chapter["lessons"]),
            fragments=fragments,
            options=options,
            instructions=instructions,
            previous_error=previous_error,
        ),
        settings,
        "generate",
    )
    result["slug"] = lesson_plan["slug"]
    result["number"] = index
    _write(job_id, _lesson_file(chapter["number"], index), result)
    return result


def generate(job_id: str) -> None:
    try:
        store.update_job(job_id, status="generating", stage="generate", error=None)
        options = _options(job_id)
        outline = load_outline(job_id)
        document = doc.load(job_path(job_id, "document.json"))
        settings = _settings(job_id)
        # Una suscripción personal va por el CLI local: una lección cada vez.
        workers = 1 if models.is_subscription(settings) else max(1, config.GEN_CONCURRENCY)
        pending = [
            (chapter, index)
            for chapter in outline["chapters"]
            for index in range(1, len(chapter["lessons"]) + 1)
            if not job_path(job_id, _lesson_file(chapter["number"], index)).is_file()
        ]
        total = sum(len(c["lessons"]) for c in outline["chapters"])
        done = total - len(pending)
        emit(job_id, "stage", f"Escribiendo {len(pending)} lecciones…", stage="generate", done=done, total=total)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(generate_lesson, job_id, settings, document, chapter, index, options): (chapter, index)
                for chapter, index in pending
            }
            for future in as_completed(futures):
                chapter, index = futures[future]
                future.result()
                done += 1
                title = chapter["lessons"][index - 1]["title"]
                label = title.get(options["languages"][0]) if isinstance(title, dict) else str(title)
                emit(job_id, "progress", f"Lección lista: {label}", stage="generate", done=done, total=total)
                _progress(job_id, lessons_done=done)
                _check(job_id)

        emit(job_id, "stage", "Creando autoevaluaciones y glosario…", stage="assess")
        for chapter in outline["chapters"]:
            _check(job_id)
            name = f"assess/c{chapter['number']}.json"
            if job_path(job_id, name).is_file():
                continue
            lessons = [
                {"slug": lesson["slug"], "title": lesson.get("title"), "summary": lesson.get("summary")}
                for lesson in chapter["lessons"]
            ]
            chunk_ids = [cid for lesson in chapter["lessons"] for cid in lesson.get("chunk_ids", [])]
            result = _agent(
                job_id,
                JobToolbox(
                    task="assessment",
                    document=document,
                    languages=options["languages"],
                    scope_chunk_ids=chunk_ids,
                    lesson_slugs=[lesson["slug"] for lesson in lessons],
                ),
                prompts.assessment(
                    chapter=chapter,
                    lessons=lessons,
                    fragments=_fragments(document, chunk_ids[:: max(1, len(chunk_ids) // 12)], 9000),
                    options=options,
                ),
                settings,
                "assess",
            )
            _write(job_id, name, result)
            emit(job_id, "progress", f"Autoevaluación del capítulo {chapter['number']} lista", stage="assess")
        assemble(job_id)
    except Cancelled:
        emit(job_id, "cancelled", "Generación cancelada.")
    except Exception as exc:  # noqa: BLE001
        _fail(job_id, exc)


# ---------------------------------------------------------------------------
# Etapa 4 · Ensamblado, validación y verificación
# ---------------------------------------------------------------------------

def build_package(job_id: str) -> dict:
    options = _options(job_id)
    outline = load_outline(job_id)
    languages = options["languages"]
    course = outline.get("course") or {}
    chapters = []
    for chapter in outline["chapters"]:
        lessons = []
        for index in range(1, len(chapter["lessons"]) + 1):
            lesson = _read(job_id, _lesson_file(chapter["number"], index))
            lesson["number"] = index
            lessons.append(lesson)
        assess = _read(job_id, f"assess/c{chapter['number']}.json")
        quiz = assess.get("quiz") or {}
        quiz["id"] = f"{chapter['slug']}-quiz"
        valid_slugs = {lesson["slug"] for lesson in lessons}
        glossary = []
        for term in assess.get("glossary") or []:
            if isinstance(term, dict):
                if term.get("lesson") not in valid_slugs:
                    term = {**term, "lesson": None}
                glossary.append(term)
        chapters.append(
            {
                "number": chapter["number"],
                "slug": chapter["slug"],
                "title": chapter["title"],
                "subtitle": chapter.get("subtitle") or chapter["title"],
                "description": chapter.get("description") or chapter["title"],
                "level": course.get("level") or {lang: options.get("level") or "Intermedio" for lang in languages},
                "lessons": lessons,
                "quiz": quiz,
                "glossary": glossary[:24],
            }
        )
    job = store.get_job(job_id, with_log=False) or {}
    return {
        "schema_version": 2,
        "languages": languages,
        "slug": options.get("slug") or slugify(job.get("title") or "unidad"),
        "course": {
            "title": course.get("title") or {lang: job.get("title") or "Unidad" for lang in languages},
            "subtitle": course.get("subtitle") or course.get("title") or {},
            "description": course.get("description") or {},
            "level": course.get("level") or {lang: options.get("level") or "Intermedio" for lang in languages},
            "accent": options.get("accent") or "violet",
            "tags": course.get("tags") or [],
            "source": course.get("source") or {},
        },
        "chapters": chapters,
    }


def assemble(job_id: str) -> None:
    store.update_job(job_id, status="validating", stage="validate")
    emit(job_id, "stage", "Validando y verificando citas…", stage="validate")
    options = _options(job_id)
    document = doc.load(job_path(job_id, "document.json"))
    chunks = doc.chunk_map(document)
    settings = None
    repaired: list[str] = []
    for attempt in range(3):
        package = build_package(job_id)
        report = verify.verify_package(package, chunks)
        try:
            parsed = parse_package(package)
            break
        except ValueError as exc:
            error = str(exc)
            # Reparación dirigida: se regenera solo la lección que falla.
            target = _failing_lesson(package, error)
            if target is None or attempt == 2:
                raise
            chapter_number, index = target
            outline = load_outline(job_id)
            chapter = next(c for c in outline["chapters"] if c["number"] == chapter_number)
            settings = settings or _settings(job_id)
            emit(job_id, "warning", f"Reparando la lección {chapter_number}.{index}: {error[:160]}")
            generate_lesson(job_id, settings, document, chapter, index, options, previous_error=error)
            repaired.append(f"{chapter_number}.{index}")
    job = store.get_job(job_id, with_log=False) or {}
    existing = job.get("course_slug")
    slug = existing or store.unique_course_slug(parsed.slug)
    if slug != parsed.slug:
        parsed = parse_package(package, slug_override=slug)
    report.update(
        {
            "warnings": document.get("warnings", []),
            "repaired_lessons": repaired,
            "chapters": parsed.summary["chapter_count"],
            "questions": sum(len(q.questions) for q in parsed.quizzes[parsed.languages[0]].values()),
            "generated_at": utcnow(),
        }
    )
    _write(job_id, "course.json", package)
    _write(job_id, "report.json", report)
    store.save_generated_course(
        slug=parsed.slug,
        owner_id=int(job.get("owner_id") or 0),
        job_id=job_id,
        title=parsed.summary["titles"].get(parsed.languages[0], job.get("title") or "Unidad"),
        package=package,
        status="draft",
        report=report,
    )
    store.update_job(job_id, status="ready", stage="review", course_slug=parsed.slug, finished_at=utcnow())
    emit(
        job_id,
        "ready",
        f"Unidad lista para revisar: {report['lessons']} lecciones, {report['cited_pct']} % de bloques con cita.",
        course_slug=parsed.slug,
    )


def _failing_lesson(package: dict, error: str) -> tuple[int, int] | None:
    match = re.search(r"chapter\[(\d+)\]\.lesson\[(\d+)\]", error)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.search(r"(gen-[a-z0-9-]+)", error)
    if match:
        slug = match.group(1)
        for chapter in package["chapters"]:
            for lesson in chapter["lessons"]:
                if slug.endswith(lesson["slug"]):
                    return chapter["number"], lesson["number"]
    return None


def regenerate_lesson(
    job_id: str,
    chapter_number: int,
    lesson_number: int,
    instructions: str,
    actor_id: int | None = None,
) -> None:
    """Regenera una lección y la sustituye en el borrador actual.

    Se parte del paquete guardado (con las ediciones manuales del revisor), no
    de los ficheros de la generación: solo cambia la lección pedida.
    """
    try:
        job = store.get_job(job_id, with_log=False) or {}
        slug = job.get("course_slug")
        stored = store.get_course(slug, with_package=True) if slug else None
        if stored is None:
            raise ValueError("La unidad ya no existe.")
        package = stored["package"]
        options = _options(job_id)
        outline = load_outline(job_id)
        document = doc.load(job_path(job_id, "document.json"))
        chapter = next(c for c in outline["chapters"] if c["number"] == chapter_number)
        # La persona que pide la regeneración paga con su credencial (o la de la plataforma).
        settings = _settings(job_id, actor_id)
        emit(job_id, "stage", f"Regenerando la lección {chapter_number}.{lesson_number}…", stage="regenerate")
        lesson = generate_lesson(job_id, settings, document, chapter, lesson_number, options, instructions=instructions)
        target = package["chapters"][chapter_number - 1]["lessons"]
        lesson["number"] = lesson_number
        lesson["slug"] = target[lesson_number - 1]["slug"]
        target[lesson_number - 1] = lesson
        report = verify.verify_package(package, doc.chunk_map(document))
        parse_package(package, slug_override=slug)
        store.save_generated_course(
            slug=slug,
            owner_id=int(stored["owner_id"]),
            job_id=job_id,
            title=stored["title"],
            package=package,
            report={**(stored.get("report") or {}), **report, "generated_at": utcnow()},
        )
        emit(job_id, "ready", f"Lección {chapter_number}.{lesson_number} regenerada.", course_slug=slug)
    except Exception as exc:  # noqa: BLE001
        logger.exception("No se pudo regenerar la lección")
        emit(job_id, "error", f"No se pudo regenerar la lección: {exc}")
