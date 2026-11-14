"use client";

import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BookA,
  CheckCircle2,
  ClipboardCheck,
  Eye,
  FileText,
  Globe2,
  Loader2,
  Pencil,
  Plus,
  RefreshCw,
  Save,
  Trash2,
  Undo2,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { BlockRenderer } from "@/components/BlockRenderer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input, NativeSelect, Textarea } from "@/components/ui/form";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/overlay";
import { Pill } from "@/components/ui/pill";
import { Progress } from "@/components/ui/progress";
import { apiGetClient, apiPost, apiPut } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AuthoringCourse, Block, CoursePackage, PackageBlock, PackageQuestion } from "@/lib/types";
import { cn } from "@/lib/utils";
import { loc } from "./shared";

type Selection = { chapter: number; kind: "lesson" | "quiz" | "glossary"; lesson: number };

export function pageOf(source: string): string {
  const match = /:p(\d+)/.exec(source);
  return match ? `p. ${match[1]}` : source;
}

export function CourseReview({
  initial,
  csrf,
  lang,
  canPublishPublic,
}: {
  initial: AuthoringCourse;
  csrf: string;
  lang: Lang;
  canPublishPublic: boolean;
}) {
  const [course, setCourse] = useState(initial);
  const [pkg, setPkg] = useState<CoursePackage>(initial.package!);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<{ tone: "ok" | "error"; text: string } | null>(null);
  const [sel, setSel] = useState<Selection>({ chapter: 0, kind: "lesson", lesson: 0 });
  const [contentLang, setContentLang] = useState(pkg.languages[0]);
  const [visibility, setVisibility] = useState<"workspace" | "public">(initial.visibility ?? "workspace");
  const report = course.report ?? {};
  const unsupportedCount = report.unsupported?.length ?? 0;

  useEffect(() => {
    const warn = (event: BeforeUnloadEvent) => {
      if (dirty) event.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  function mutate(fn: (draft: CoursePackage) => void) {
    const draft = structuredClone(pkg);
    fn(draft);
    setPkg(draft);
    setDirty(true);
  }

  async function save(): Promise<boolean> {
    setBusy(true);
    setNotice(null);
    try {
      const updated = await apiPut<AuthoringCourse>(`/api/v1/authoring/courses/${course.slug}/package`, { package: pkg }, csrf);
      setCourse(updated);
      setPkg(updated.package!);
      setDirty(false);
      setNotice({ tone: "ok", text: pick(lang, "Cambios guardados.", "Changes saved.") });
      return true;
    } catch (err) {
      setNotice({ tone: "error", text: err instanceof Error ? err.message : String(err) });
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function publish(publish: boolean) {
    if (dirty && !(await save())) return;
    setBusy(true);
    try {
      const updated = publish
        ? await apiPost<AuthoringCourse>(`/api/v1/authoring/courses/${course.slug}/publish`, { visibility }, csrf)
        : await apiPost<AuthoringCourse>(`/api/v1/authoring/courses/${course.slug}/unpublish`, {}, csrf);
      setCourse({ ...course, ...updated });
      setNotice({
        tone: "ok",
        text: publish ? pick(lang, "Unidad publicada.", "Unit published.") : pick(lang, "Unidad retirada.", "Unit unpublished."),
      });
    } catch (err) {
      setNotice({ tone: "error", text: err instanceof Error ? err.message : String(err) });
    } finally {
      setBusy(false);
    }
  }

  const chapter = pkg.chapters[sel.chapter];
  const firstLesson = pkg.chapters[0]?.lessons[0]?.slug;

  return (
    <div className="grid gap-5">
      <Card className="flex flex-wrap items-center gap-4 p-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="truncate text-lg font-semibold">{loc(pkg.course.title, contentLang, course.title)}</h2>
            {course.status === "published" ? (
              <Pill variant="success">
                {course.visibility === "public" ? <Globe2 /> : null} {pick(lang, "Publicada", "Published")}
              </Pill>
            ) : (
              <Pill variant="secondary">{pick(lang, "Borrador", "Draft")}</Pill>
            )}
            {dirty ? <Pill variant="warning">{pick(lang, "Cambios sin guardar", "Unsaved changes")}</Pill> : null}
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span>
              {pkg.chapters.length} {pick(lang, "capítulos", "chapters")} · {pkg.chapters.reduce((n, c) => n + c.lessons.length, 0)} {pick(lang, "lecciones", "lessons")}
            </span>
            {typeof report.cited_pct === "number" ? (
              <span className="flex items-center gap-2">
                {pick(lang, "Con cita", "Cited")}
                <Progress value={report.cited_pct} className="w-20" tone={report.cited_pct >= 70 ? "success" : "warning"} label={pick(lang, "Bloques con cita", "Cited blocks")} />
                <span className="tabular">{report.cited_pct}%</span>
              </span>
            ) : null}
            {unsupportedCount ? (
              <span className="flex items-center gap-1 text-warning">
                <AlertTriangle className="size-3.5" /> {unsupportedCount} {pick(lang, "bloques a revisar", "blocks to check")}
              </span>
            ) : typeof report.cited_pct === "number" ? (
              <span className="flex items-center gap-1 text-success">
                <CheckCircle2 className="size-3.5" /> {pick(lang, "Sin alertas de respaldo", "No support alerts")}
              </span>
            ) : null}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {pkg.languages.length > 1 ? (
            <Tabs value={contentLang} onValueChange={setContentLang}>
              <TabsList>
                {pkg.languages.map((code) => (
                  <TabsTrigger key={code} value={code}>
                    {code.toUpperCase()}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          ) : null}
          <Button variant="outline" disabled={!dirty || busy} onClick={save}>
            {busy ? <Loader2 className="animate-spin" /> : <Save />} {pick(lang, "Guardar", "Save")}
          </Button>
          {course.status === "published" ? (
            <>
              {firstLesson ? (
                <Button asChild variant="ghost">
                  <Link href={`/cursos/${course.slug}`}>
                    <Eye /> {pick(lang, "Ver", "View")}
                  </Link>
                </Button>
              ) : null}
              <Button variant="secondary" disabled={busy} onClick={() => publish(false)}>
                <Undo2 /> {pick(lang, "Retirar", "Unpublish")}
              </Button>
            </>
          ) : (
            <>
              {canPublishPublic ? (
                <NativeSelect value={visibility} onChange={(e) => setVisibility(e.target.value as "workspace" | "public")} aria-label={pick(lang, "Visibilidad", "Visibility")}>
                  <option value="workspace">{pick(lang, "Solo este espacio", "This workspace only")}</option>
                  <option value="public">{pick(lang, "Catálogo abierto", "Open catalog")}</option>
                </NativeSelect>
              ) : null}
              <Button disabled={busy} onClick={() => publish(true)}>
                <CheckCircle2 /> {pick(lang, "Publicar", "Publish")}
              </Button>
            </>
          )}
        </div>
        {notice ? (
          <p className={cn("m-0 w-full rounded-md px-3 py-2 text-sm", notice.tone === "ok" ? "bg-success-soft text-success" : "bg-destructive-soft text-destructive")}>
            {notice.text}
          </p>
        ) : null}
      </Card>

      <div className="grid gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
        <Card className="h-fit p-2 lg:sticky lg:top-20">
          <nav aria-label={pick(lang, "Contenido de la unidad", "Unit contents")} className="max-h-[70vh] overflow-y-auto scrollbar-thin">
            {pkg.chapters.map((item, c) => (
              <div key={item.slug} className="mb-2">
                <p className="m-0 px-2 py-1.5 text-[11px] font-semibold tracking-wide text-muted-foreground uppercase">
                  {c + 1}. {loc(item.title, contentLang)}
                </p>
                {item.lessons.map((lesson, l) => {
                  const flagged = (report.unsupported ?? []).some((u) => u.lesson === lesson.slug);
                  return (
                    <NavItem key={lesson.slug} active={sel.chapter === c && sel.kind === "lesson" && sel.lesson === l} onClick={() => setSel({ chapter: c, kind: "lesson", lesson: l })}>
                      <FileText /> <span className="min-w-0 flex-1 truncate">{loc(lesson.title, contentLang)}</span>
                      {flagged ? <AlertTriangle className="!text-warning" /> : null}
                    </NavItem>
                  );
                })}
                <NavItem active={sel.chapter === c && sel.kind === "quiz"} onClick={() => setSel({ chapter: c, kind: "quiz", lesson: 0 })}>
                  <ClipboardCheck /> {pick(lang, "Autoevaluación", "Self-assessment")}
                  <span className="ml-auto text-xs text-muted-foreground">{item.quiz.questions.length}</span>
                </NavItem>
                <NavItem active={sel.chapter === c && sel.kind === "glossary"} onClick={() => setSel({ chapter: c, kind: "glossary", lesson: 0 })}>
                  <BookA /> {pick(lang, "Glosario", "Glossary")}
                  <span className="ml-auto text-xs text-muted-foreground">{item.glossary.length}</span>
                </NavItem>
              </div>
            ))}
          </nav>
        </Card>

        <div className="min-w-0">
          {sel.kind === "lesson" ? (
            <LessonEditor
              key={`${sel.chapter}-${sel.lesson}-${contentLang}`}
              pkg={pkg}
              chapterIndex={sel.chapter}
              lessonIndex={sel.lesson}
              contentLang={contentLang}
              lang={lang}
              csrf={csrf}
              mutate={mutate}
              courseSlug={course.slug}
              canRegenerate={Boolean(course.job_id)}
              dirty={dirty}
              onRegenerated={async () => {
                const fresh = await apiGetClient<AuthoringCourse>(`/api/v1/authoring/courses/${course.slug}`);
                setCourse(fresh);
                setPkg(fresh.package!);
                setDirty(false);
              }}
            />
          ) : sel.kind === "quiz" ? (
            <QuizEditor chapterIndex={sel.chapter} pkg={pkg} contentLang={contentLang} lang={lang} mutate={mutate} />
          ) : (
            <Card>
              <CardHeader>
                <div>
                  <CardTitle>{pick(lang, "Glosario del capítulo", "Chapter glossary")}</CardTitle>
                  <CardDescription>{loc(chapter.title, contentLang)}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="grid gap-3">
                {chapter.glossary.map((term, index) => (
                  <div key={index} className="grid gap-2 rounded-lg border border-border p-3 sm:grid-cols-[200px_1fr_auto]">
                    <Input
                      value={loc(term.term, contentLang)}
                      aria-label={pick(lang, "Término", "Term")}
                      onChange={(e) => mutate((d) => (d.chapters[sel.chapter].glossary[index].term[contentLang] = e.target.value))}
                    />
                    <Textarea
                      rows={2}
                      className="min-h-0"
                      value={loc(term.definition, contentLang)}
                      aria-label={pick(lang, "Definición", "Definition")}
                      onChange={(e) => mutate((d) => (d.chapters[sel.chapter].glossary[index].definition[contentLang] = e.target.value))}
                    />
                    <Button
                      size="icon-sm"
                      variant="ghost"
                      aria-label={pick(lang, "Quitar", "Remove")}
                      onClick={() => mutate((d) => d.chapters[sel.chapter].glossary.splice(index, 1))}
                    >
                      <Trash2 />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function NavItem({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? "true" : undefined}
      className={cn(
        "flex w-full cursor-pointer items-center gap-2 rounded-md border-0 bg-transparent px-2 py-1.5 text-left text-[13px] text-soft-foreground hover:bg-muted [&_svg]:size-3.5 [&_svg]:shrink-0 [&_svg]:text-muted-foreground",
        active && "bg-primary-soft font-medium text-primary hover:bg-primary-soft"
      )}
    >
      {children}
    </button>
  );
}

const TEXT_FIELDS: Record<string, string[]> = {
  lead: ["html"],
  p: ["html"],
  h2: ["text"],
  h3: ["text"],
  callout: ["title", "html"],
  check: ["question", "answer"],
  quote: ["text", "source"],
};

function LessonEditor({
  pkg,
  chapterIndex,
  lessonIndex,
  contentLang,
  lang,
  csrf,
  mutate,
  courseSlug,
  canRegenerate,
  dirty,
  onRegenerated,
}: {
  pkg: CoursePackage;
  chapterIndex: number;
  lessonIndex: number;
  contentLang: string;
  lang: Lang;
  csrf: string;
  mutate: (fn: (draft: CoursePackage) => void) => void;
  courseSlug: string;
  canRegenerate: boolean;
  dirty: boolean;
  onRegenerated: () => Promise<void>;
}) {
  const lesson = pkg.chapters[chapterIndex].lessons[lessonIndex];
  const blocks = lesson.blocks[contentLang] ?? [];
  const [editing, setEditing] = useState<number | null>(null);
  const [instructions, setInstructions] = useState("");
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState("");
  const path = (d: CoursePackage) => d.chapters[chapterIndex].lessons[lessonIndex];

  async function regenerate() {
    if (dirty && !window.confirm(pick(lang, "Hay cambios sin guardar que se perderán. ¿Continuar?", "Unsaved changes will be lost. Continue?"))) return;
    setRegenerating(true);
    setError("");
    try {
      const before = JSON.stringify(lesson.blocks);
      const { job_id } = await apiPost<{ job_id: string }>(
        `/api/v1/authoring/courses/${courseSlug}/regenerate`,
        { chapter: chapterIndex + 1, lesson: lessonIndex + 1, instructions },
        csrf
      );
      // Espera a que el worker sustituya la lección (máx. ~5 min).
      for (let i = 0; i < 150; i += 1) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const fresh = await apiGetClient<{ package: CoursePackage }>(`/api/v1/authoring/courses/${courseSlug}`);
        const updated = fresh.package.chapters[chapterIndex].lessons[lessonIndex];
        if (JSON.stringify(updated.blocks) !== before) break;
        const history = await apiGetClient<{ events: { type: string; message: string }[] }>(`/api/v1/authoring/jobs/${job_id}/history`);
        const last = history.events[history.events.length - 1];
        if (last?.type === "error") throw new Error(last.message);
      }
      await onRegenerated();
      setInstructions("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRegenerating(false);
    }
  }

  return (
    <div className="grid gap-4">
      <Card>
        <CardContent className="grid gap-3 pt-5">
          <Field label={pick(lang, "Título", "Title")} htmlFor="lesson-title">
            <Input id="lesson-title" value={loc(lesson.title, contentLang)} onChange={(e) => mutate((d) => (path(d).title[contentLang] = e.target.value))} />
          </Field>
          <Field label={pick(lang, "Resumen", "Summary")} htmlFor="lesson-summary">
            <Textarea id="lesson-summary" rows={2} value={loc(lesson.summary, contentLang)} onChange={(e) => mutate((d) => (path(d).summary[contentLang] = e.target.value))} />
          </Field>
          {canRegenerate ? (
            <details className="rounded-lg border border-border p-3">
              <summary className="cursor-pointer text-sm font-medium">
                <RefreshCw className="mr-1 inline size-3.5" /> {pick(lang, "Regenerar esta lección con IA", "Regenerate this lesson with AI")}
              </summary>
              <div className="mt-3 grid gap-2">
                <Textarea
                  rows={2}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder={pick(lang, "Ej.: más ejemplos prácticos, nivel más básico, añade una tabla comparativa…", "E.g. more practical examples, simpler level, add a comparison table…")}
                  aria-label={pick(lang, "Instrucciones", "Instructions")}
                />
                {error ? <p className="m-0 text-sm text-destructive">{error}</p> : null}
                <div className="flex justify-end">
                  <Button variant="secondary" disabled={regenerating} onClick={regenerate}>
                    {regenerating ? <Loader2 className="animate-spin" /> : <RefreshCw />} {pick(lang, "Regenerar", "Regenerate")}
                  </Button>
                </div>
              </div>
            </details>
          ) : null}
        </CardContent>
      </Card>

      <div className="grid gap-2">
        {blocks.map((block, index) => (
          <div
            key={index}
            className={cn(
              "group relative rounded-xl border bg-card p-4 pr-12 shadow-card",
              block.unsupported ? "border-warning/60" : "border-border"
            )}
          >
            <div className="absolute top-2 right-2 flex flex-col gap-1 opacity-60 transition group-hover:opacity-100 group-focus-within:opacity-100">
              <Button size="icon-sm" variant="ghost" aria-label={pick(lang, "Editar", "Edit")} onClick={() => setEditing(editing === index ? null : index)}>
                <Pencil />
              </Button>
              <Button size="icon-sm" variant="ghost" aria-label={pick(lang, "Subir", "Move up")} disabled={index === 0} onClick={() => mutate((d) => swap(path(d).blocks[contentLang], index, index - 1))}>
                <ArrowUp />
              </Button>
              <Button size="icon-sm" variant="ghost" aria-label={pick(lang, "Bajar", "Move down")} disabled={index === blocks.length - 1} onClick={() => mutate((d) => swap(path(d).blocks[contentLang], index, index + 1))}>
                <ArrowDown />
              </Button>
              <Button size="icon-sm" variant="ghost" aria-label={pick(lang, "Quitar", "Remove")} onClick={() => mutate((d) => path(d).blocks[contentLang].splice(index, 1))}>
                <Trash2 />
              </Button>
            </div>
            <div className="mb-2 flex flex-wrap items-center gap-1.5">
              <Pill variant="outline" className="font-mono text-[11px]">
                {block.type}
              </Pill>
              {(block.sources ?? []).map((source) => (
                <Pill key={source} variant="secondary" title={source}>
                  {pageOf(source)}
                </Pill>
              ))}
              {block.unsupported ? (
                <Pill variant="warning">
                  <AlertTriangle /> {pick(lang, "Poco respaldo en la fuente", "Weak source support")}
                </Pill>
              ) : null}
            </div>
            {editing === index ? (
              <BlockForm block={block} lang={lang} onChange={(next) => mutate((d) => (path(d).blocks[contentLang][index] = next))} />
            ) : (
              <div className="prose prose-preview">
                <BlockRenderer block={block as Block} index={index} lessonSlug={lesson.slug} labMeta={{}} csrf="" lang={lang} />
              </div>
            )}
          </div>
        ))}
        <Button
          variant="ghost"
          className="justify-self-start"
          onClick={() =>
            mutate((d) => {
              const list = path(d).blocks[contentLang];
              list.splice(Math.max(1, list.length - 1), 0, { type: "p", html: pick(lang, "Nuevo párrafo.", "New paragraph.") });
            })
          }
        >
          <Plus /> {pick(lang, "Añadir párrafo", "Add paragraph")}
        </Button>
      </div>
    </div>
  );
}

function swap<T>(list: T[], a: number, b: number) {
  [list[a], list[b]] = [list[b], list[a]];
}

function BlockForm({ block, lang, onChange }: { block: PackageBlock; lang: Lang; onChange: (next: PackageBlock) => void }) {
  const fields = TEXT_FIELDS[block.type];
  const [raw, setRaw] = useState(() => JSON.stringify(block, null, 2));
  const [invalid, setInvalid] = useState(false);
  if (fields) {
    return (
      <div className="grid gap-2">
        {fields.map((field) => (
          <Field key={field} label={field} htmlFor={`f-${field}`}>
            <Textarea
              id={`f-${field}`}
              rows={field === "html" || field === "answer" ? 5 : 2}
              value={String(block[field] ?? "")}
              onChange={(e) => onChange({ ...block, [field]: e.target.value })}
            />
          </Field>
        ))}
        <p className="m-0 text-xs text-muted-foreground">
          {pick(lang, "HTML permitido: strong, em, code, a, br, ul, ol, li, span, sub, sup.", "Allowed HTML: strong, em, code, a, br, ul, ol, li, span, sub, sup.")}
        </p>
      </div>
    );
  }
  if (block.type === "list" || block.type === "keypoints") {
    const items = (block.items as string[]) ?? [];
    return (
      <Field label={pick(lang, "Un elemento por línea", "One item per line")} htmlFor="f-items">
        <Textarea id="f-items" rows={Math.max(3, items.length + 1)} value={items.join("\n")} onChange={(e) => onChange({ ...block, items: e.target.value.split("\n").filter((line) => line.trim()) })} />
      </Field>
    );
  }
  return (
    <Field label="JSON" htmlFor="f-json" hint={invalid ? pick(lang, "JSON no válido", "Invalid JSON") : undefined}>
      <Textarea
        id="f-json"
        rows={10}
        className={cn("font-mono text-xs", invalid && "border-destructive")}
        value={raw}
        onChange={(e) => {
          setRaw(e.target.value);
          try {
            onChange(JSON.parse(e.target.value));
            setInvalid(false);
          } catch {
            setInvalid(true);
          }
        }}
      />
    </Field>
  );
}

function QuizEditor({
  chapterIndex,
  pkg,
  contentLang,
  lang,
  mutate,
}: {
  chapterIndex: number;
  pkg: CoursePackage;
  contentLang: string;
  lang: Lang;
  mutate: (fn: (draft: CoursePackage) => void) => void;
}) {
  const quiz = pkg.chapters[chapterIndex].quiz;
  const questions = (d: CoursePackage) => d.chapters[chapterIndex].quiz.questions;
  const kindLabel = useMemo(
    () => ({
      single: pick(lang, "Opción única", "Single choice"),
      multiple: pick(lang, "Respuesta múltiple", "Multiple answer"),
      true_false: pick(lang, "Verdadero/falso", "True/false"),
    }),
    [lang]
  );
  return (
    <div className="grid gap-3">
      <Card className="p-4">
        <p className="m-0 font-medium">{loc(quiz.title, contentLang)}</p>
        <p className="m-0 mt-1 text-sm text-muted-foreground">
          {quiz.questions.length} {pick(lang, "preguntas · aprobado con", "questions · pass mark")} {quiz.pass_score}% ·{" "}
          {pick(lang, "las respuestas correctas se aplican a todos los idiomas", "correct answers apply to all languages")}
        </p>
      </Card>
      {quiz.questions.map((question: PackageQuestion, qi) => {
        const kind = question.kind ?? "single";
        const correct = Array.isArray(question.correct) ? question.correct : [question.correct];
        const options = question.options[contentLang] ?? [];
        return (
          <Card key={question.id} className="p-4">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span className="grid size-6 place-items-center rounded-md bg-muted text-xs font-semibold">{qi + 1}</span>
              <Pill variant="violet">{kindLabel[kind]}</Pill>
              {question.difficulty ? <Pill variant="outline">{question.difficulty}</Pill> : null}
              {question.source ? <Pill variant="secondary">{pageOf(question.source)}</Pill> : null}
              <Button size="icon-sm" variant="ghost" className="ml-auto" aria-label={pick(lang, "Quitar pregunta", "Remove question")} onClick={() => mutate((d) => questions(d).splice(qi, 1))}>
                <Trash2 />
              </Button>
            </div>
            <Textarea
              rows={2}
              value={loc(question.prompt, contentLang)}
              aria-label={pick(lang, "Enunciado", "Prompt")}
              onChange={(e) => mutate((d) => (questions(d)[qi].prompt[contentLang] = e.target.value))}
            />
            <fieldset className="m-0 mt-3 grid gap-2 border-0 p-0">
              <legend className="mb-1 text-xs text-muted-foreground">{pick(lang, "Marca la(s) correcta(s)", "Mark the correct one(s)")}</legend>
              {options.map((option, oi) => (
                <div key={oi} className="flex items-center gap-2">
                  <input
                    type={kind === "multiple" ? "checkbox" : "radio"}
                    name={`q-${question.id}`}
                    checked={correct.includes(oi)}
                    aria-label={`${pick(lang, "Correcta", "Correct")} ${oi + 1}`}
                    onChange={(e) =>
                      mutate((d) => {
                        const q = questions(d)[qi];
                        if (kind === "multiple") {
                          const set = new Set(Array.isArray(q.correct) ? q.correct : [q.correct]);
                          if (e.target.checked) set.add(oi);
                          else set.delete(oi);
                          q.correct = [...set].sort((a, b) => a - b);
                        } else {
                          q.correct = oi;
                        }
                      })
                    }
                  />
                  <Input
                    value={option}
                    aria-label={`${pick(lang, "Opción", "Option")} ${oi + 1}`}
                    onChange={(e) => mutate((d) => (questions(d)[qi].options[contentLang][oi] = e.target.value))}
                  />
                </div>
              ))}
            </fieldset>
            <Field label={pick(lang, "Explicación", "Explanation")} htmlFor={`exp-${question.id}`} className="mt-3">
              <Textarea
                id={`exp-${question.id}`}
                rows={2}
                value={loc(question.explanation, contentLang)}
                onChange={(e) => mutate((d) => (questions(d)[qi].explanation[contentLang] = e.target.value))}
              />
            </Field>
          </Card>
        );
      })}
    </div>
  );
}
