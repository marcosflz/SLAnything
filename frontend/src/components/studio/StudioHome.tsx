"use client";

import {
  ArrowRight,
  BookOpen,
  Bot,
  FileText,
  FileUp,
  Globe2,
  KeyRound,
  Layers,
  Loader2,
  Settings2,
  Sparkles,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

import { EmptyState } from "@/components/charts/Kpi";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input, NativeSelect, Textarea } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { Progress } from "@/components/ui/progress";
import { apiDelete, apiGetClient, apiPut, apiUpload } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AuthoringCourse, AuthoringJob, AuthoringPayload, AuthoringSettings } from "@/lib/types";
import { cn, relativeDays } from "@/lib/utils";
import { StatusPill } from "./shared";

const ACCEPT = ".pdf,.docx,.epub,.odt,.md,.markdown,.txt,.html,.htm";

export function StudioHome({ initial, csrf, lang }: { initial: AuthoringPayload; csrf: string; lang: Lang }) {
  const router = useRouter();
  const [data, setData] = useState(initial);
  const [files, setFiles] = useState<File[]>([]);
  const [title, setTitle] = useState("");
  const [languages, setLanguages] = useState<string[]>(["es"]);
  const [notes, setNotes] = useState("");
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const input = useRef<HTMLInputElement>(null);
  const active = data.jobs.some((job) => job.active);

  useEffect(() => {
    if (!active) return;
    const timer = window.setInterval(async () => {
      try {
        setData(await apiGetClient<AuthoringPayload>("/api/v1/authoring"));
      } catch {
        // Reintento en el siguiente ciclo.
      }
    }, 5000);
    return () => window.clearInterval(timer);
  }, [active]);

  function addFiles(list: FileList | null) {
    if (!list) return;
    const next = [...files, ...Array.from(list)].slice(0, data.limits.max_files);
    setFiles(next);
    if (!title && next[0]) setTitle(next[0].name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " "));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!files.length) {
      setError(pick(lang, "Añade al menos un documento.", "Add at least one document."));
      return;
    }
    setBusy(true);
    setError("");
    const body = new FormData();
    body.set("title", title);
    body.set("notes", notes);
    languages.forEach((code) => body.append("languages", code));
    files.forEach((file) => body.append("files", file));
    try {
      const job = await apiUpload<AuthoringJob>("/api/v1/authoring/jobs", body, csrf);
      router.push(`/estudio/trabajos/${job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  async function removeCourse(course: AuthoringCourse) {
    if (!window.confirm(pick(lang, "¿Borrar «{t}»? No se puede deshacer.", "Delete “{t}”? This cannot be undone.").replace("{t}", course.title))) return;
    await apiDelete(`/api/v1/authoring/courses/${course.slug}`, csrf);
    setData(await apiGetClient<AuthoringPayload>("/api/v1/authoring"));
  }

  const quota = data.quota;
  return (
    <div className="grid gap-6">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="size-4 text-primary" /> {pick(lang, "Nueva unidad didáctica", "New learning unit")}
              </CardTitle>
              <CardDescription>
                {pick(
                  lang,
                  "Sube apuntes, un libro o un capítulo. Detectamos su estructura, eliges qué convertir, revisas el temario y obtienes lecciones con citas, autoevaluación y glosario.",
                  "Upload notes, a book or a chapter. We detect its structure, you choose what to convert, review the outline and get lessons with citations, self-assessment and glossary."
                )}
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={submit} className="grid gap-4">
              <div
                role="button"
                tabIndex={0}
                onClick={() => input.current?.click()}
                onKeyDown={(event) => (event.key === "Enter" || event.key === " ") && input.current?.click()}
                onDragOver={(event) => {
                  event.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(event) => {
                  event.preventDefault();
                  setDragging(false);
                  addFiles(event.dataTransfer.files);
                }}
                className={cn(
                  "flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed border-border-strong px-6 py-8 text-center transition",
                  dragging ? "border-primary bg-primary-soft" : "hover:border-primary/60 hover:bg-muted/50"
                )}
              >
                <span className="grid size-11 place-items-center rounded-full bg-primary-soft text-primary">
                  <UploadCloud className="size-5" aria-hidden="true" />
                </span>
                <p className="m-0 text-sm font-medium">
                  {pick(lang, "Arrastra aquí tus documentos o haz clic para elegirlos", "Drop your documents here or click to choose")}
                </p>
                <p className="m-0 text-xs text-muted-foreground">
                  PDF · DOCX · EPUB · ODT · Markdown · HTML · TXT — {pick(lang, "hasta", "up to")} {data.limits.max_files} ×{" "}
                  {data.limits.max_upload_mb} MB
                </p>
                <input
                  ref={input}
                  type="file"
                  multiple
                  accept={ACCEPT}
                  className="sr-only"
                  onChange={(event) => addFiles(event.target.files)}
                  aria-label={pick(lang, "Documentos", "Documents")}
                />
              </div>
              {files.length ? (
                <ul className="m-0 grid list-none gap-1.5 p-0">
                  {files.map((file, index) => (
                    <li key={`${file.name}-${index}`} className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm">
                      <FileText className="size-4 text-muted-foreground" aria-hidden="true" />
                      <span className="min-w-0 flex-1 truncate">{file.name}</span>
                      <span className="tabular text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(1)} MB</span>
                      <button
                        type="button"
                        className="grid size-6 cursor-pointer place-items-center rounded border-0 bg-transparent text-muted-foreground hover:bg-muted"
                        onClick={() => setFiles(files.filter((_, i) => i !== index))}
                        aria-label={pick(lang, "Quitar", "Remove")}
                      >
                        <X className="size-3.5" />
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label={pick(lang, "Título de la unidad", "Unit title")} htmlFor="unit-title">
                  <Input id="unit-title" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
                </Field>
                <Field label={pick(lang, "Idiomas", "Languages")}>
                  <div className="flex h-9 items-center gap-4">
                    {(["es", "en"] as const).map((code) => (
                      <label key={code} className="flex items-center gap-1.5 text-sm">
                        <input
                          type="checkbox"
                          checked={languages.includes(code)}
                          onChange={(e) =>
                            setLanguages(
                              e.target.checked
                                ? [...languages, code]
                                : languages.length > 1
                                  ? languages.filter((l) => l !== code)
                                  : languages
                            )
                          }
                        />
                        {code === "es" ? "Español" : "English"}
                      </label>
                    ))}
                  </div>
                </Field>
              </div>
              <Field
                label={pick(lang, "Indicaciones para la IA (opcional)", "Instructions for the AI (optional)")}
                htmlFor="unit-notes"
                hint={pick(lang, "Público, enfoque, qué evitar… Podrás afinar más al elegir el contenido.", "Audience, focus, what to avoid… You can refine later.")}
              >
                <Textarea id="unit-notes" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} maxLength={2000} />
              </Field>
              <p className="m-0 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                <Bot className="size-3.5" aria-hidden="true" />
                {data.ai.source === "user"
                  ? pick(lang, "Generarás con tu proveedor:", "You will generate with your provider:")
                  : pick(lang, "Generarás con el proveedor de la plataforma:", "You will generate with the platform provider:")}
                {" "}
                <span className="font-medium text-foreground">
                  {data.ai.provider_label + (data.ai.model ? ` · ${data.ai.model}` : "")}
                </span>
                <Link href="/cuenta#proveedor-ia" className="ml-1">
                  {pick(lang, "Cambiar", "Change")}
                </Link>
              </p>
              {error ? <p className="m-0 rounded-md bg-destructive-soft px-3 py-2 text-sm text-destructive">{error}</p> : null}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="text-xs text-muted-foreground">
                  {pick(lang, "Este mes: {u} de {l} generaciones", "This month: {u} of {l} generations")
                    .replace("{u}", String(quota.used))
                    .replace("{l}", String(quota.limit))}
                </span>
                <Button type="submit" disabled={busy || quota.remaining <= 0}>
                  {busy ? <Loader2 className="animate-spin" /> : <FileUp />}
                  {pick(lang, "Analizar documentos", "Analyze documents")}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="grid content-start gap-6">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>{pick(lang, "Cómo funciona", "How it works")}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <ol className="m-0 grid list-none gap-3 p-0 text-sm">
                {[
                  [pick(lang, "Analizamos la estructura", "We analyze the structure"), pick(lang, "Capítulos, secciones y páginas del documento.", "Chapters, sections and pages.")],
                  [pick(lang, "Eliges qué convertir", "You choose what to convert"), pick(lang, "Un capítulo o el libro entero, con nivel y tipos de pregunta.", "One chapter or the whole book, with level and question types.")],
                  [pick(lang, "Revisas el temario", "You review the outline"), pick(lang, "Renombra, reordena o quita lecciones antes de generar.", "Rename, reorder or drop lessons before generating.")],
                  [pick(lang, "Revisas y publicas", "You review and publish"), pick(lang, "Cada bloque cita su página; editas lo que quieras.", "Every block cites its page; edit anything.")],
                ].map(([head, text], index) => (
                  <li key={head} className="flex gap-3">
                    <span className="grid size-6 shrink-0 place-items-center rounded-full bg-primary-soft text-xs font-semibold text-primary">{index + 1}</span>
                    <span>
                      <span className="block font-medium">{head}</span>
                      <span className="text-muted-foreground">{text}</span>
                    </span>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>
          {data.can_configure ? <ProviderSettings initial={data.settings} csrf={csrf} lang={lang} /> : null}
        </div>
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <Layers className="size-4" /> {pick(lang, "Proyectos", "Projects")}
            </CardTitle>
            <CardDescription>{pick(lang, "Documentos en proceso y su estado", "Documents in progress and their status")}</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          {data.jobs.length ? (
            <ul className="m-0 grid list-none gap-2 p-0">
              {data.jobs.map((job) => (
                <JobRow key={job.id} job={job} lang={lang} />
              ))}
            </ul>
          ) : (
            <EmptyState icon={FileText} title={pick(lang, "Aún no hay proyectos", "No projects yet")} description={pick(lang, "Sube tu primer documento para empezar.", "Upload your first document to start.")} />
          )}
        </CardContent>
      </Card>

      <section>
        <h3 className="mb-3 flex items-center gap-2 text-base font-semibold">
          <BookOpen className="size-4" /> {pick(lang, "Unidades generadas", "Generated units")}
        </h3>
        {data.courses.length ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {data.courses.map((course) => (
              <Card key={course.slug} className="flex flex-col p-4">
                <div className="mb-2 flex items-start justify-between gap-2">
                  <Link href={`/estudio/cursos/${course.slug}`} className="line-clamp-2 font-medium text-foreground no-underline hover:text-primary hover:no-underline">
                    {course.title}
                  </Link>
                  {course.status === "published" ? (
                    <Pill variant="success">
                      {course.visibility === "public" ? <Globe2 /> : null}
                      {pick(lang, "Publicada", "Published")}
                    </Pill>
                  ) : (
                    <Pill variant="secondary">{pick(lang, "Borrador", "Draft")}</Pill>
                  )}
                </div>
                <p className="m-0 mb-3 text-xs text-muted-foreground">
                  {course.summary.chapter_count} {pick(lang, "capítulos", "chapters")} · {course.summary.lesson_count} {pick(lang, "lecciones", "lessons")} ·{" "}
                  {course.summary.languages.join("/").toUpperCase()}
                </p>
                {typeof course.report?.cited_pct === "number" ? (
                  <div className="mb-3">
                    <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                      <span>{pick(lang, "Bloques con cita", "Blocks with citation")}</span>
                      <span className="tabular">{course.report.cited_pct}%</span>
                    </div>
                    <Progress value={course.report.cited_pct} tone={course.report.cited_pct >= 70 ? "success" : "warning"} label={pick(lang, "Bloques con cita", "Blocks with citation")} />
                  </div>
                ) : null}
                <div className="mt-auto flex items-center gap-2">
                  <Button asChild size="sm" variant="secondary" className="flex-1">
                    <Link href={`/estudio/cursos/${course.slug}`}>
                      {pick(lang, "Revisar", "Review")} <ArrowRight />
                    </Link>
                  </Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => removeCourse(course)} aria-label={pick(lang, "Borrar", "Delete")}>
                    <Trash2 />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState icon={BookOpen} title={pick(lang, "Todavía no hay unidades", "No units yet")} />
        )}
      </section>
    </div>
  );
}

function JobRow({ job, lang }: { job: AuthoringJob; lang: Lang }) {
  const total = job.progress?.lessons_total ?? 0;
  const done = job.progress?.lessons_done ?? 0;
  const legacy = job.engine === "opencode";
  const href = !legacy ? `/estudio/trabajos/${job.id}` : job.course_slug ? `/estudio/cursos/${job.course_slug}` : null;
  const content = (
    <>
      <FileText className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium text-foreground">{job.title}</span>
        <span className="block truncate text-xs text-muted-foreground">
          {job.source_names.join(", ")} · {relativeDays(job.created_at, lang)}
          {legacy ? pick(lang, " · motor anterior", " · previous engine") : ""}
        </span>
        {job.error ? <span className="block truncate text-xs text-destructive">{job.error}</span> : null}
      </span>
      {job.status === "generating" && total ? (
        <span className="hidden w-32 sm:block">
          <Progress value={(done * 100) / total} label={`${done}/${total}`} />
        </span>
      ) : null}
      <StatusPill status={job.status} lang={lang} />
      {href ? <ArrowRight className="size-4 text-muted-foreground" aria-hidden="true" /> : null}
    </>
  );
  const className = "flex items-center gap-3 rounded-lg border border-border px-3 py-2.5 no-underline transition hover:no-underline";
  return (
    <li>
      {href ? (
        <Link href={href} className={cn(className, "hover:border-border-strong hover:bg-muted/40")}>
          {content}
        </Link>
      ) : (
        <div className={className}>{content}</div>
      )}
    </li>
  );
}

export function ProviderSettings({ initial, csrf, lang }: { initial: AuthoringSettings; csrf: string; lang: Lang }) {
  const [settings, setSettings] = useState(initial);
  const [apiKey, setApiKey] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const provider = useMemo(() => settings.providers.find((item) => item.id === settings.provider), [settings]);

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const updated = await apiPut<AuthoringSettings>(
        "/api/v1/authoring/settings",
        { provider: settings.provider, model: settings.model, base_url: settings.base_url, api_key: apiKey || null },
        csrf
      );
      setSettings({ ...settings, ...updated });
      setApiKey("");
      setMessage(pick(lang, "Guardado.", "Saved."));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle className="flex items-center gap-2">
            <Settings2 className="size-4" /> {pick(lang, "Proveedor de IA de la plataforma", "Platform AI provider")}
          </CardTitle>
          <CardDescription>
            {pick(
              lang,
              "Lo usa quien no configura su propio proveedor. Los agentes funcionan con nas-adk {v}.",
              "Used by anyone without their own provider. Agents run on nas-adk {v}."
            ).replace("{v}", settings.engine?.version ?? "")}
          </CardDescription>
        </div>
        {settings.key_configured ? (
          <Pill variant="success">
            <KeyRound /> {settings.key_hint}
          </Pill>
        ) : null}
      </CardHeader>
      <CardContent>
        <form onSubmit={save} className="grid gap-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label={pick(lang, "Proveedor", "Provider")} htmlFor="provider">
              <NativeSelect
                id="provider"
                className="w-full"
                value={settings.provider}
                onChange={(e) => {
                  const next = settings.providers.find((item) => item.id === e.target.value);
                  setSettings({ ...settings, provider: e.target.value, model: next?.models[0] ?? "", base_url: next?.default_base_url ?? "" });
                }}
              >
                {settings.providers.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field label={pick(lang, "Modelo", "Model")} htmlFor="model">
              <Input id="model" list="models" value={settings.model} onChange={(e) => setSettings({ ...settings, model: e.target.value })} />
              <datalist id="models">
                {provider?.models.map((model) => <option key={model} value={model} />)}
              </datalist>
            </Field>
          </div>
          {provider?.base_url_editable ? (
            <Field label="Base URL" htmlFor="base-url" hint={provider?.notes}>
              <Input id="base-url" value={settings.base_url} onChange={(e) => setSettings({ ...settings, base_url: e.target.value })} placeholder={provider?.default_base_url ?? ""} />
            </Field>
          ) : (
            <p className="m-0 text-xs text-muted-foreground">{provider?.notes}</p>
          )}
          <Field label="API key" htmlFor="api-key">
            <Input id="api-key" type="password" autoComplete="off" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder={settings.key_configured ? "••••••••" : ""} />
          </Field>
          <div className="flex items-center justify-end gap-3">
            {message ? <span className="text-sm text-muted-foreground">{message}</span> : null}
            <Button type="submit" variant="secondary" disabled={busy}>
              {pick(lang, "Guardar", "Save")}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
