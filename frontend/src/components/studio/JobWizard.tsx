"use client";

import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  Check,
  CheckCircle2,
  FileSearch,
  Loader2,
  Plus,
  RotateCcw,
  Sparkles,
  Trash2,
  Wand2,
  XCircle,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input, NativeSelect, Textarea } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { Progress } from "@/components/ui/progress";
import { apiGetClient, apiPost, apiPut } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AiChoice, AuthoringJob, CourseOutline, DocumentOutline, JobEvent, OutlineLesson } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ModelPicker } from "./ModelPicker";
import { STEPS, StatusPill, loc, stepFor, stepLabel } from "./shared";

const WORKING = new Set(["queued", "extracting", "outlining", "generating", "validating"]);

export function JobWizard({ initial, csrf, lang }: { initial: AuthoringJob; csrf: string; lang: Lang }) {
  const [job, setJob] = useState(initial);
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [error, setError] = useState("");
  const working = WORKING.has(job.status);
  // Modelo con el que se lanzan las siguientes etapas (empieza por el del trabajo, ADR-025).
  const [choice, setChoice] = useState<AiChoice | null>(() => {
    const saved = (initial.config as { ai?: AiChoice } | undefined)?.ai;
    return saved && saved.source && saved.provider && saved.model ? saved : null;
  });

  const refresh = useCallback(async () => {
    setJob(await apiGetClient<AuthoringJob>(`/api/v1/authoring/jobs/${initial.id}`));
  }, [initial.id]);

  // Historial inicial + progreso en directo por SSE (con polling de respaldo).
  useEffect(() => {
    let source: EventSource | null = null;
    let timer: number | undefined;
    apiGetClient<{ events: JobEvent[] }>(`/api/v1/authoring/jobs/${initial.id}/history`)
      .then((data) => setEvents(data.events))
      .catch(() => undefined);
    if (!working) return;
    const seen = new Set<string>();
    try {
      source = new EventSource(`/api/v1/authoring/jobs/${initial.id}/events`);
      source.addEventListener("log", (message) => {
        const event = JSON.parse((message as MessageEvent).data) as JobEvent;
        const key = `${event.ts}|${event.message}`;
        if (seen.has(key)) return;
        seen.add(key);
        setEvents((list) => (list.some((item) => `${item.ts}|${item.message}` === key) ? list : [...list, event]));
      });
      source.addEventListener("job", () => void refresh());
      source.onerror = () => {
        source?.close();
        timer = window.setInterval(() => void refresh(), 3000);
      };
    } catch {
      timer = window.setInterval(() => void refresh(), 3000);
    }
    return () => {
      source?.close();
      if (timer) window.clearInterval(timer);
    };
  }, [initial.id, working, refresh]);

  async function act(path: string, body: Record<string, unknown> = {}) {
    setError("");
    try {
      const payload = choice && path !== "cancel" ? { ...body, ai: choice } : body;
      await apiPost(`/api/v1/authoring/jobs/${job.id}/${path}`, payload, csrf);
      // Recarga completa: reinicia la suscripción SSE si el trabajo vuelve a correr.
      setJob(await apiGetClient<AuthoringJob>(`/api/v1/authoring/jobs/${job.id}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  const current = job.status === "failed" || job.status === "cancelled" ? null : stepFor(job.status);
  const currentIndex = current ? STEPS.indexOf(current) : -1;

  return (
    <div className="grid gap-6">
      <nav aria-label={pick(lang, "Pasos", "Steps")} className="overflow-x-auto scrollbar-thin">
        <ol className="m-0 flex min-w-max list-none items-center gap-2 p-0">
          {STEPS.map((step, index) => {
            const done = index < currentIndex || job.status === "ready";
            const active = index === currentIndex && job.status !== "ready";
            return (
              <li key={step} className="flex items-center gap-2">
                <span
                  aria-current={active ? "step" : undefined}
                  className={cn(
                    "flex items-center gap-2 rounded-full border px-3 py-1 text-[13px]",
                    done && "border-success/40 bg-success-soft text-success",
                    active && "border-primary bg-primary-soft font-medium text-primary",
                    !done && !active && "border-border text-muted-foreground"
                  )}
                >
                  <span className="grid size-5 place-items-center rounded-full bg-current/10 text-[11px]">
                    {done ? <Check className="size-3" /> : index + 1}
                  </span>
                  {stepLabel(step, lang)}
                </span>
                {index < STEPS.length - 1 ? <span className="h-px w-4 bg-border" aria-hidden="true" /> : null}
              </li>
            );
          })}
        </ol>
      </nav>

      {error ? <p className="m-0 rounded-md bg-destructive-soft px-3 py-2 text-sm text-destructive">{error}</p> : null}

      {!working && job.status !== "ready" ? <ModelPicker lang={lang} value={choice} onChange={setChoice} id="job-model" /> : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0">
          {job.status === "awaiting_scope" ? (
            <ScopeStep job={job} lang={lang} onSubmit={(body) => act("plan", body)} />
          ) : job.status === "awaiting_outline" ? (
            <OutlineStep job={job} csrf={csrf} lang={lang} onGenerate={() => act("generate")} onBack={refresh} />
          ) : job.status === "ready" ? (
            <ReadyStep job={job} lang={lang} />
          ) : job.status === "failed" || job.status === "cancelled" ? (
            <Card className="p-6">
              <div className="flex items-start gap-3">
                <XCircle className="mt-0.5 size-5 shrink-0 text-destructive" />
                <div className="min-w-0">
                  <p className="m-0 font-medium">
                    {job.status === "failed" ? pick(lang, "La generación se ha detenido", "Generation stopped") : pick(lang, "Generación cancelada", "Generation cancelled")}
                  </p>
                  {job.error ? <p className="m-0 mt-1 text-sm break-words text-muted-foreground">{job.error}</p> : null}
                  <p className="m-0 mt-2 text-sm text-muted-foreground">
                    {pick(lang, "Al reintentar se conserva todo lo ya generado.", "Retrying keeps everything already generated.")}
                  </p>
                  <Button className="mt-4" onClick={() => act("retry")}>
                    <RotateCcw /> {pick(lang, "Reintentar", "Retry")}
                  </Button>
                </div>
              </div>
            </Card>
          ) : (
            <WorkingStep job={job} events={events} lang={lang} onCancel={() => act("cancel")} />
          )}
        </div>

        <aside className="grid content-start gap-4">
          <Card className="p-4">
            <div className="mb-3 flex items-center justify-between gap-2">
              <span className="text-sm font-medium">{pick(lang, "Estado", "Status")}</span>
              <StatusPill status={job.status} lang={lang} />
            </div>
            <dl className="m-0 grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
              <dt className="text-muted-foreground">{pick(lang, "Documentos", "Documents")}</dt>
              <dd className="m-0 truncate text-right">{job.source_names.length}</dd>
              {job.progress.pages ? (
                <>
                  <dt className="text-muted-foreground">{pick(lang, "Páginas", "Pages")}</dt>
                  <dd className="tabular m-0 text-right">{job.progress.pages}</dd>
                </>
              ) : null}
              {job.progress.sections ? (
                <>
                  <dt className="text-muted-foreground">{pick(lang, "Secciones", "Sections")}</dt>
                  <dd className="tabular m-0 text-right">{job.progress.sections}</dd>
                </>
              ) : null}
              {job.progress.lessons_total ? (
                <>
                  <dt className="text-muted-foreground">{pick(lang, "Lecciones", "Lessons")}</dt>
                  <dd className="tabular m-0 text-right">
                    {job.progress.lessons_done ?? 0}/{job.progress.lessons_total}
                  </dd>
                </>
              ) : null}
              <dt className="text-muted-foreground">Tokens</dt>
              <dd className="tabular m-0 text-right">{(job.tokens_in + job.tokens_out).toLocaleString()}</dd>
              <dt className="text-muted-foreground">{pick(lang, "Modelo", "Model")}</dt>
              <dd className="m-0 truncate text-right" title={job.model}>
                {job.model}
              </dd>
            </dl>
          </Card>
          <Card className="p-4">
            <p className="m-0 mb-2 text-sm font-medium">{pick(lang, "Actividad", "Activity")}</p>
            <ol className="m-0 grid max-h-80 list-none gap-2 overflow-y-auto p-0 text-xs scrollbar-thin" aria-live="polite">
              {events.length ? (
                [...events].reverse().slice(0, 60).map((event, index) => (
                  <li key={`${event.ts}-${index}`} className="flex gap-2">
                    <span
                      className={cn(
                        "mt-1 size-1.5 shrink-0 rounded-full",
                        event.type === "error" ? "bg-destructive" : event.type === "warning" ? "bg-warning" : event.type === "ready" || event.type === "done" ? "bg-success" : event.type === "tool" ? "bg-border-strong" : "bg-primary"
                      )}
                      aria-hidden="true"
                    />
                    <span className="min-w-0">
                      <span className={cn("block", event.type === "tool" ? "text-muted-foreground" : "text-foreground")}>{event.message}</span>
                      <span className="text-muted-foreground">{new Date(event.ts).toLocaleTimeString(lang === "en" ? "en-GB" : "es-ES")}</span>
                    </span>
                  </li>
                ))
              ) : (
                <li className="text-muted-foreground">{pick(lang, "Sin actividad todavía.", "No activity yet.")}</li>
              )}
            </ol>
          </Card>
        </aside>
      </div>
    </div>
  );
}

function WorkingStep({ job, events, lang, onCancel }: { job: AuthoringJob; events: JobEvent[]; lang: Lang; onCancel: () => void }) {
  const total = job.progress.lessons_total ?? 0;
  const done = job.progress.lessons_done ?? 0;
  const last = [...events].reverse().find((event) => event.type === "stage" || event.type === "progress");
  const title = {
    queued: pick(lang, "En cola…", "Queued…"),
    extracting: pick(lang, "Analizando la estructura del documento", "Analyzing the document structure"),
    outlining: pick(lang, "Diseñando el temario", "Designing the outline"),
    generating: pick(lang, "Escribiendo las lecciones", "Writing the lessons"),
    validating: pick(lang, "Validando y verificando citas", "Validating and checking citations"),
  }[job.status as "queued"] ?? job.status_label;
  return (
    <Card className="p-6">
      <div className="flex items-start gap-4">
        <span className="grid size-11 shrink-0 place-items-center rounded-full bg-primary-soft text-primary">
          <Loader2 className="size-5 animate-spin" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="m-0 text-lg font-semibold">{title}</p>
          <p className="m-0 mt-1 text-sm text-muted-foreground">{last?.message ?? pick(lang, "Preparando…", "Preparing…")}</p>
          {job.status === "generating" && total ? (
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                <span>{pick(lang, "Lecciones", "Lessons")}</span>
                <span className="tabular">
                  {done}/{total}
                </span>
              </div>
              <Progress value={(done * 100) / total} label={pick(lang, "Progreso de generación", "Generation progress")} />
            </div>
          ) : null}
          <p className="m-0 mt-4 text-xs text-muted-foreground">
            {pick(lang, "Puedes cerrar esta página: el trabajo continúa en el servidor y se reanuda si se reinicia.", "You can close this page: the job continues on the server and resumes after a restart.")}
          </p>
          <Button variant="ghost" size="sm" className="mt-3" onClick={onCancel}>
            {pick(lang, "Cancelar", "Cancel")}
          </Button>
        </div>
      </div>
    </Card>
  );
}

type PlanOptions = {
  scope: string[];
  level: string;
  lessons_per_chapter: number | null;
  minutes_per_lesson: number;
  questions_per_chapter: number;
  question_kinds: string[];
  code_examples: boolean;
  auto_approve: boolean;
  notes: string;
};

function ScopeStep({ job, lang, onSubmit }: { job: AuthoringJob; lang: Lang; onSubmit: (body: PlanOptions) => void }) {
  const [outline, setOutline] = useState<DocumentOutline | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [options, setOptions] = useState<Omit<PlanOptions, "scope">>({
    level: "Intermedio",
    lessons_per_chapter: null,
    minutes_per_lesson: 12,
    questions_per_chapter: 10,
    question_kinds: ["single", "multiple", "true_false"],
    code_examples: false,
    auto_approve: false,
    notes: String(job.config?.notes ?? ""),
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    apiGetClient<DocumentOutline>(`/api/v1/authoring/jobs/${job.id}/document`).then((data) => {
      setOutline(data);
      setSelected(data.sections.filter((s) => s.level === 1).slice(0, 3).map((s) => s.id));
    });
  }, [job.id]);

  if (!outline) {
    return (
      <Card className="flex items-center gap-3 p-6 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" /> {pick(lang, "Cargando estructura…", "Loading structure…")}
      </Card>
    );
  }
  const tops = outline.sections.filter((section) => section.level === 1);
  const children = (id: string) => outline.sections.filter((section) => section.parent === id);
  const words = tops.filter((s) => selected.includes(s.id)).reduce((sum, s) => sum + s.words, 0);
  const toggle = (id: string) => setSelected((list) => (list.includes(id) ? list.filter((item) => item !== id) : [...list, id]));
  const kinds = [
    ["single", pick(lang, "Opción única", "Single choice")],
    ["multiple", pick(lang, "Respuesta múltiple", "Multiple answer")],
    ["true_false", pick(lang, "Verdadero/falso", "True/false")],
  ] as const;

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileSearch className="size-4" /> {pick(lang, "¿Qué quieres convertir?", "What do you want to convert?")}
            </CardTitle>
            <CardDescription>
              {pick(lang, "Cada sección marcada será un capítulo con sus lecciones, autoevaluación y glosario.", "Each selected section becomes a chapter with lessons, self-assessment and glossary.")}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="ghost" onClick={() => setSelected(tops.map((s) => s.id))}>
              {pick(lang, "Todo", "All")}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setSelected([])}>
              {pick(lang, "Nada", "None")}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {outline.warnings.length ? (
            <ul className="m-0 mb-3 grid list-none gap-1 rounded-md bg-warning-soft p-3 text-xs text-warning">
              {outline.warnings.map((warning) => (
                <li key={warning} className="flex gap-2">
                  <AlertTriangle className="size-3.5 shrink-0" /> {warning}
                </li>
              ))}
            </ul>
          ) : null}
          <ul className="m-0 grid max-h-[460px] list-none gap-1.5 overflow-y-auto p-0 scrollbar-thin">
            {tops.map((section) => {
              const checked = selected.includes(section.id);
              const subs = children(section.id);
              return (
                <li key={section.id}>
                  <label
                    className={cn(
                      "flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2.5 transition",
                      checked ? "border-primary/50 bg-primary-soft/50" : "border-border hover:bg-muted/40"
                    )}
                  >
                    <input type="checkbox" className="mt-1" checked={checked} onChange={() => toggle(section.id)} />
                    <span className="min-w-0 flex-1">
                      <span className="block text-sm font-medium">{section.title}</span>
                      <span className="block text-xs text-muted-foreground">
                        {section.page_start ? `${pick(lang, "págs.", "pp.")} ${section.page_start}–${section.page_end} · ` : ""}
                        {section.words.toLocaleString()} {pick(lang, "palabras", "words")}
                        {subs.length ? ` · ${subs.map((s) => s.title).slice(0, 4).join(" · ")}${subs.length > 4 ? "…" : ""}` : ""}
                      </span>
                    </span>
                  </label>
                </li>
              );
            })}
          </ul>
          <p className="m-0 mt-3 text-xs text-muted-foreground">
            {selected.length} {pick(lang, "capítulos seleccionados", "chapters selected")} · ~{words.toLocaleString()} {pick(lang, "palabras de origen", "source words")}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>{pick(lang, "Cómo debe ser la unidad", "Shape of the unit")}</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <Field label={pick(lang, "Nivel", "Level")} htmlFor="level">
              <NativeSelect id="level" className="w-full" value={options.level} onChange={(e) => setOptions({ ...options, level: e.target.value })}>
                {["Principiante", "Intermedio", "Avanzado"].map((level) => (
                  <option key={level} value={level}>
                    {lang === "en" ? { Principiante: "Beginner", Intermedio: "Intermediate", Avanzado: "Advanced" }[level] : level}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field label={pick(lang, "Lecciones por capítulo", "Lessons per chapter")} htmlFor="lessons">
              <NativeSelect
                id="lessons"
                className="w-full"
                value={options.lessons_per_chapter ?? ""}
                onChange={(e) => setOptions({ ...options, lessons_per_chapter: e.target.value ? Number(e.target.value) : null })}
              >
                <option value="">{pick(lang, "Automático", "Automatic")}</option>
                {[2, 3, 4, 5, 6, 8, 10].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field label={pick(lang, "Preguntas por capítulo", "Questions per chapter")} htmlFor="questions">
              <Input
                id="questions"
                type="number"
                min={4}
                max={20}
                value={options.questions_per_chapter}
                onChange={(e) => setOptions({ ...options, questions_per_chapter: Number(e.target.value) })}
              />
            </Field>
          </div>
          <Field label={pick(lang, "Tipos de pregunta", "Question types")}>
            <div className="flex flex-wrap gap-4">
              {kinds.map(([value, label]) => (
                <label key={value} className="flex items-center gap-1.5 text-sm">
                  <input
                    type="checkbox"
                    checked={options.question_kinds.includes(value)}
                    onChange={(e) =>
                      setOptions({
                        ...options,
                        question_kinds: e.target.checked
                          ? [...options.question_kinds, value]
                          : options.question_kinds.length > 1
                            ? options.question_kinds.filter((k) => k !== value)
                            : options.question_kinds,
                      })
                    }
                  />
                  {label}
                </label>
              ))}
            </div>
          </Field>
          <div className="flex flex-wrap gap-6 text-sm">
            <label className="flex items-center gap-1.5">
              <input type="checkbox" checked={options.code_examples} onChange={(e) => setOptions({ ...options, code_examples: e.target.checked })} />
              {pick(lang, "Incluir ejemplos de código ejecutables", "Include runnable code examples")}
            </label>
            <label className="flex items-center gap-1.5">
              <input type="checkbox" checked={options.auto_approve} onChange={(e) => setOptions({ ...options, auto_approve: e.target.checked })} />
              {pick(lang, "Generar sin revisar el temario", "Generate without reviewing the outline")}
            </label>
          </div>
          <Field label={pick(lang, "Indicaciones", "Instructions")} htmlFor="plan-notes">
            <Textarea id="plan-notes" rows={2} value={options.notes} onChange={(e) => setOptions({ ...options, notes: e.target.value })} maxLength={2000} />
          </Field>
          <div className="flex justify-end">
            <Button
              disabled={!selected.length || busy}
              onClick={() => {
                setBusy(true);
                onSubmit({ ...options, scope: tops.filter((s) => selected.includes(s.id)).map((s) => s.id) });
              }}
            >
              <Wand2 /> {pick(lang, "Diseñar el temario", "Design the outline")}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function OutlineStep({
  job,
  csrf,
  lang,
  onGenerate,
}: {
  job: AuthoringJob;
  csrf: string;
  lang: Lang;
  onGenerate: () => void;
  onBack: () => void;
}) {
  const [outline, setOutline] = useState<CourseOutline | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const primary = (job.languages[0] ?? "es") as string;
  const dirty = useRef(false);

  useEffect(() => {
    apiGetClient<CourseOutline>(`/api/v1/authoring/jobs/${job.id}/outline`).then(setOutline);
  }, [job.id]);

  if (!outline) {
    return (
      <Card className="flex items-center gap-3 p-6 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" /> {pick(lang, "Cargando temario…", "Loading outline…")}
      </Card>
    );
  }

  function update(next: CourseOutline) {
    dirty.current = true;
    setOutline(next);
  }

  function setLessonField(c: number, l: number, field: "title" | "summary", value: string) {
    const chapters = outline!.chapters.map((chapter, ci) =>
      ci !== c
        ? chapter
        : {
            ...chapter,
            lessons: chapter.lessons.map((lesson, li) =>
              li !== l ? lesson : { ...lesson, [field]: { ...lesson[field], [primary]: value } }
            ),
          }
    );
    update({ ...outline!, chapters });
  }

  function moveLesson(c: number, l: number, delta: number) {
    const chapters = outline!.chapters.map((chapter, ci) => {
      if (ci !== c) return chapter;
      const lessons = [...chapter.lessons];
      const target = l + delta;
      if (target < 0 || target >= lessons.length) return chapter;
      [lessons[l], lessons[target]] = [lessons[target], lessons[l]];
      return { ...chapter, lessons };
    });
    update({ ...outline!, chapters });
  }

  function removeLesson(c: number, l: number) {
    const chapters = outline!.chapters.map((chapter, ci) =>
      ci !== c ? chapter : { ...chapter, lessons: chapter.lessons.filter((_, li) => li !== l) }
    );
    update({ ...outline!, chapters: chapters.filter((chapter) => chapter.lessons.length) });
  }

  function addLesson(c: number) {
    const chapter = outline!.chapters[c];
    const blank: OutlineLesson = {
      slug: `nueva-${chapter.lessons.length + 1}`,
      title: Object.fromEntries(job.languages.map((code) => [code, pick(lang, "Nueva lección", "New lesson")])),
      summary: Object.fromEntries(job.languages.map((code) => [code, ""])),
      objectives: [],
      chunk_ids: chapter.lessons[chapter.lessons.length - 1]?.chunk_ids.slice(-2) ?? [],
    };
    const chapters = outline!.chapters.map((item, ci) => (ci !== c ? item : { ...item, lessons: [...item.lessons, blank] }));
    update({ ...outline!, chapters });
  }

  async function save() {
    setSaving(true);
    setMessage("");
    try {
      setOutline(await apiPut<CourseOutline>(`/api/v1/authoring/jobs/${job.id}/outline`, { outline }, csrf));
      dirty.current = false;
      return true;
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
      return false;
    } finally {
      setSaving(false);
    }
  }

  const lessons = outline.chapters.reduce((sum, chapter) => sum + chapter.lessons.length, 0);
  return (
    <div className="grid gap-4">
      <Card className="flex flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <p className="m-0 font-medium">{loc(outline.course.title, primary, job.title)}</p>
          <p className="m-0 text-sm text-muted-foreground">
            {outline.chapters.length} {pick(lang, "capítulos", "chapters")} · {lessons} {pick(lang, "lecciones", "lessons")} ·{" "}
            {pick(lang, "edita títulos y resúmenes, reordena o quita lecciones", "edit titles and summaries, reorder or drop lessons")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {message ? <span className="text-sm text-destructive">{message}</span> : null}
          <Button variant="outline" disabled={saving} onClick={save}>
            {pick(lang, "Guardar", "Save")}
          </Button>
          <Button
            disabled={saving}
            onClick={async () => {
              if (dirty.current && !(await save())) return;
              onGenerate();
            }}
          >
            <Sparkles /> {pick(lang, "Generar unidad", "Generate unit")}
          </Button>
        </div>
      </Card>
      {outline.chapters.map((chapter, c) => (
        <Card key={`${chapter.slug}-${c}`}>
          <CardHeader>
            <div className="min-w-0 flex-1">
              <p className="m-0 text-xs font-medium tracking-wide text-primary uppercase">
                {pick(lang, "Capítulo", "Chapter")} {c + 1}
              </p>
              <Input
                className="mt-1 h-auto border-transparent px-0 text-base font-semibold shadow-none focus-visible:border-input focus-visible:px-2"
                value={loc(chapter.title, primary)}
                aria-label={pick(lang, "Título del capítulo", "Chapter title")}
                onChange={(e) =>
                  update({
                    ...outline,
                    chapters: outline.chapters.map((item, ci) => (ci !== c ? item : { ...item, title: { ...item.title, [primary]: e.target.value } })),
                  })
                }
              />
              {chapter.objectives.length ? (
                <div className="mt-2 flex flex-wrap gap-1">
                  {chapter.objectives.map((objective) => (
                    <Pill key={objective.id} variant="outline">
                      {loc(objective.text, primary)}
                    </Pill>
                  ))}
                </div>
              ) : null}
            </div>
          </CardHeader>
          <CardContent>
            <ol className="m-0 grid list-none gap-2 p-0">
              {chapter.lessons.map((lesson, l) => (
                <li key={`${lesson.slug}-${l}`} className="grid grid-cols-[1.75rem_1fr_auto] items-start gap-3 rounded-lg border border-border p-3">
                  <span className="grid size-7 place-items-center rounded-md bg-muted text-xs font-semibold">{l + 1}</span>
                  <div className="grid min-w-0 gap-1.5">
                    <Input value={loc(lesson.title, primary)} aria-label={pick(lang, "Título de la lección", "Lesson title")} onChange={(e) => setLessonField(c, l, "title", e.target.value)} />
                    <Textarea
                      rows={2}
                      className="min-h-0 text-[13px]"
                      value={loc(lesson.summary, primary)}
                      aria-label={pick(lang, "Resumen", "Summary")}
                      onChange={(e) => setLessonField(c, l, "summary", e.target.value)}
                    />
                    <span className="text-xs text-muted-foreground">
                      {lesson.chunk_ids.length} {pick(lang, "fragmentos del documento", "document fragments")}
                    </span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <Button size="icon-sm" variant="ghost" onClick={() => moveLesson(c, l, -1)} disabled={l === 0} aria-label={pick(lang, "Subir", "Move up")}>
                      <ArrowUp />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => moveLesson(c, l, 1)} disabled={l === chapter.lessons.length - 1} aria-label={pick(lang, "Bajar", "Move down")}>
                      <ArrowDown />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => removeLesson(c, l)} aria-label={pick(lang, "Quitar", "Remove")}>
                      <Trash2 />
                    </Button>
                  </div>
                </li>
              ))}
            </ol>
            <Button variant="ghost" size="sm" className="mt-2" onClick={() => addLesson(c)}>
              <Plus /> {pick(lang, "Añadir lección", "Add lesson")}
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function ReadyStep({ job, lang }: { job: AuthoringJob; lang: Lang }) {
  return (
    <Card className="p-6">
      <div className="flex items-start gap-4">
        <span className="grid size-11 shrink-0 place-items-center rounded-full bg-success-soft text-success">
          <CheckCircle2 className="size-5" />
        </span>
        <div>
          <p className="m-0 text-lg font-semibold">{pick(lang, "Unidad lista para revisar", "Unit ready for review")}</p>
          <p className="m-0 mt-1 text-sm text-muted-foreground">
            {pick(lang, "Revisa cada lección junto a sus fuentes, corrige lo que haga falta y publícala para tu espacio.", "Review every lesson next to its sources, fix what you need and publish it to your workspace.")}
          </p>
          {job.course_slug ? (
            <Button asChild className="mt-4">
              <Link href={`/estudio/cursos/${job.course_slug}`}>{pick(lang, "Abrir la revisión", "Open review")}</Link>
            </Button>
          ) : null}
        </div>
      </div>
    </Card>
  );
}
