"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import type {
  AuthoringCourse,
  AuthoringJob,
  AuthoringPayload,
  AuthoringSettings,
  Lang,
} from "@/lib/types";
import {
  ApiClientError,
  apiDelete,
  apiGetClient,
  apiPost,
  apiPut,
  apiUpload,
} from "@/lib/client";
import { t } from "@/lib/messages";
import { Icon } from "@/components/ui";

const STATUS_TONE: Record<string, string> = {
  ready: "badge-success",
  failed: "badge-danger",
  cancelled: "badge-neutral",
  queued: "badge-info",
  extracting: "badge-warning",
  generating: "badge-warning",
  validating: "badge-warning",
};

function fmt(value: string | null, lang: Lang): string {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString(lang === "en" ? "en-GB" : "es-ES", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export function StudioPanel({
  initial,
  csrf,
  lang,
}: {
  initial: AuthoringPayload;
  csrf: string;
  lang: Lang;
}) {
  const [settings, setSettings] = useState<AuthoringSettings>(initial.settings);
  const [jobs, setJobs] = useState<AuthoringJob[]>(initial.jobs);
  const [courses, setCourses] = useState<AuthoringCourse[]>(initial.courses);
  const [apiKey, setApiKey] = useState("");
  const [clearKey, setClearKey] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const provider = useMemo(
    () => settings.providers.find((item) => item.id === settings.provider),
    [settings]
  );
  const activeJobs = jobs.filter((job) => job.active);
  const limits = initial.limits;

  const refresh = useCallback(async () => {
    try {
      const payload = await apiGetClient<AuthoringPayload>("/api/v1/authoring");
      setJobs(payload.jobs);
      setCourses(payload.courses);
    } catch (exc) {
      if (exc instanceof ApiClientError && exc.status !== 401) {
        setError(exc.message);
      }
    }
  }, []);

  useEffect(() => {
    if (activeJobs.length === 0) return;
    const timer = window.setInterval(() => {
      void refresh();
    }, 4000);
    return () => window.clearInterval(timer);
  }, [activeJobs.length, refresh]);

  async function saveSettings(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await apiPut<AuthoringSettings>(
        "/api/v1/authoring/settings",
        {
          provider: settings.provider,
          model: settings.model,
          base_url: settings.base_url,
          api_key: apiKey.trim() || undefined,
          clear_key: clearKey,
        },
        csrf
      );
      setSettings(updated);
      setApiKey("");
      setClearKey(false);
      setMessage(t(lang, "Configuración guardada."));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  }

  async function createJob(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const languages = data.getAll("languages");
    if (languages.length === 0) {
      setError(t(lang, "Selecciona al menos un idioma."));
      return;
    }
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      await apiUpload<AuthoringJob>("/api/v1/authoring/jobs", data, csrf);
      form.reset();
      setMessage(
        t(lang, "Trabajo creado. La unidad se generará en segundo plano.")
      );
      await refresh();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  }

  async function cancelJob(job: AuthoringJob) {
    setBusy(true);
    setError(null);
    try {
      await apiPost(`/api/v1/authoring/jobs/${job.id}/cancel`, {}, csrf);
      await refresh();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  }

  async function setPublished(course: AuthoringCourse, published: boolean) {
    setBusy(true);
    setError(null);
    try {
      await apiPost(
        `/api/v1/authoring/courses/${course.slug}/${
          published ? "publish" : "unpublish"
        }`,
        {},
        csrf
      );
      await refresh();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  }

  async function removeCourse(course: AuthoringCourse) {
    if (!window.confirm(t(lang, "¿Eliminar esta unidad generada?"))) return;
    setBusy(true);
    setError(null);
    try {
      await apiDelete(`/api/v1/authoring/courses/${course.slug}`, csrf);
      await refresh();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setBusy(false);
    }
  }

  function changeProvider(id: string) {
    const next = settings.providers.find((item) => item.id === id);
    setSettings((current) => ({
      ...current,
      provider: id,
      model: next?.models[0] ?? current.model,
      base_url: next?.default_base_url ?? "",
    }));
  }

  return (
    <>
      {message ? (
        <div className="flash flash-success" role="status">
          <Icon name="check-circle" />
          <span>{message}</span>
          <button type="button" onClick={() => setMessage(null)} aria-label={t(lang, "Cerrar")}>
            ×
          </button>
        </div>
      ) : null}
      {error ? (
        <div className="flash flash-danger" role="alert">
          <Icon name="alert" />
          <span>{error}</span>
          <button type="button" onClick={() => setError(null)} aria-label={t(lang, "Cerrar")}>
            ×
          </button>
        </div>
      ) : null}

      <div className="studio-grid">
        <section className="card card-pad studio-panel">
          <div className="card-head">
            <h3 className="card-title">
              <Icon name="cpu" /> {t(lang, "Motor de generación")}
            </h3>
          </div>
          <div
            className={`studio-engine ${
              settings.engine.available ? "is-ok" : "is-warn"
            }`}
          >
            <span className="studio-engine-dot" />
            <div>
              <strong>
                {t(lang, "OpenCode")}
                {settings.engine.version ? ` · ${settings.engine.version}` : ""}
              </strong>
              <p className="mb-0 small">{settings.engine.message}</p>
            </div>
          </div>
          <div className="studio-key-row">
            <span className="small muted">{t(lang, "Proveedor configurado")}:</span>
            <strong>{provider?.label ?? settings.provider}</strong>
            {settings.key_configured ? (
              <span className="badge badge-success">{settings.key_hint}</span>
            ) : (
              <span className="badge badge-warning">
                {t(lang, "Falta la API key")}
              </span>
            )}
          </div>

          <form className="studio-form" onSubmit={saveSettings}>
            <div className="form-grid">
              <label className="field">
                <span>{t(lang, "Proveedor")}</span>
                <select
                  value={settings.provider}
                  onChange={(event) => changeProvider(event.target.value)}
                >
                  {settings.providers.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>{t(lang, "Modelo")}</span>
                <input
                  value={settings.model}
                  onChange={(event) =>
                    setSettings((current) => ({
                      ...current,
                      model: event.target.value,
                    }))
                  }
                  list="studio-models"
                  required
                />
              </label>
            </div>
            <datalist id="studio-models">
              {settings.providers.flatMap((item) =>
                item.models.map((model) => (
                  <option value={model} key={`${item.id}-${model}`} />
                ))
              )}
            </datalist>
            <label className="field">
              <span>{t(lang, "Base URL")}</span>
              <input
                value={settings.base_url}
                onChange={(event) =>
                  setSettings((current) => ({
                    ...current,
                    base_url: event.target.value,
                  }))
                }
                placeholder={provider?.default_base_url ?? "https://…/v1"}
                autoComplete="off"
              />
            </label>
            <label className="field">
              <span>{t(lang, "API key")}</span>
              <input
                type="password"
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                autoComplete="new-password"
                placeholder={
                  settings.key_configured
                    ? `${settings.key_hint} · ${t(lang, "deja en blanco para conservarla")}`
                    : "sk-…"
                }
              />
            </label>
            <label className="checkbox-row small">
              <input
                type="checkbox"
                checked={clearKey}
                onChange={(event) => setClearKey(event.target.checked)}
              />
              {t(lang, "Borrar la clave guardada")}
            </label>
            <p className="small muted">
              {t(
                lang,
                "La clave se guarda en el servidor y nunca se devuelve al navegador."
              )}
            </p>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              <Icon name="shield" /> {t(lang, "Guardar configuración")}
            </button>
          </form>
        </section>

        <section className="card card-pad studio-panel">
          <div className="card-head">
            <h3 className="card-title">
              <Icon name="sparkles" /> {t(lang, "Nueva unidad a partir de documentos")}
            </h3>
          </div>
          <form
            className="studio-form"
            onSubmit={createJob}
            encType="multipart/form-data"
          >
            <div className="form-grid">
              <label className="field">
                <span>{t(lang, "Título de trabajo")}</span>
                <input
                  name="title"
                  required
                  maxLength={200}
                  placeholder={t(lang, "Redes neuronales en 4 lecciones")}
                />
              </label>
              <label className="field">
                <span>{t(lang, "Slug (opcional)")}</span>
                <input
                  name="slug"
                  maxLength={72}
                  pattern="[a-z0-9-]*"
                  placeholder="redes-neuronales"
                />
              </label>
            </div>
            <div className="field">
              <span>{t(lang, "Idiomas")}</span>
              <div className="checkbox-row">
                <label>
                  <input type="checkbox" name="languages" value="es" defaultChecked />{" "}
                  {t(lang, "Español")}
                </label>
                <label>
                  <input type="checkbox" name="languages" value="en" defaultChecked />{" "}
                  {t(lang, "English")}
                </label>
              </div>
            </div>
            <label className="field">
              <span>{t(lang, "Notas para el agente (opcional)")}</span>
              <textarea
                name="notes"
                rows={2}
                maxLength={2000}
                placeholder={t(
                  lang,
                  "Enfoca la unidad en el capítulo 3; nivel intermedio."
                )}
              />
            </label>
            <label className="field studio-upload">
              <span>{t(lang, "Documentos")}</span>
              <input
                type="file"
                name="files"
                multiple
                required
                accept=".pdf,.docx,.epub,.odt,.md,.markdown,.txt,.html,.htm"
              />
              <small className="muted">
                {t(
                  lang,
                  "Formatos: PDF, DOCX, EPUB, ODT, Markdown, HTML o TXT. Varios archivos se combinan en una sola unidad."
                )}
              </small>
            </label>
            <p className="small muted">
              {t(
                lang,
                "Máximo {n} MB por archivo y {m} archivos. El texto se recorta si supera el límite de contexto.",
                { n: limits.max_upload_mb, m: limits.max_files }
              )}
            </p>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              <Icon name="sparkles" /> {t(lang, "Generar unidad")}
            </button>
          </form>
        </section>
      </div>

      <div className="callout callout-info mt-4">
        <div className="callout-icon">i</div>
        <div className="callout-body">
          <strong className="callout-title">
            {t(lang, "Qué ocurre al generar")}
          </strong>
          <div className="callout-text">
            {t(
              lang,
              "El resultado se valida y se sanea antes de entrar en el catálogo. Nada del documento se ejecuta. La unidad queda en borrador hasta que la publiques."
            )}
          </div>
        </div>
      </div>

      <section className="card mt-4">
        <div className="card-head" style={{ padding: "18px 20px 0" }}>
          <h3 className="card-title">
            <Icon name="clock" /> {t(lang, "Trabajos recientes")}
          </h3>
          <button className="btn btn-ghost btn-sm" type="button" onClick={() => void refresh()}>
            <Icon name="refresh" /> {t(lang, "Actualizar")}
          </button>
        </div>
        {jobs.length ? (
          <div className="studio-jobs">
            {jobs.map((job) => (
              <article className="studio-job" key={job.id}>
                <div className="studio-job-head">
                  <div>
                    <strong>{job.title}</strong>
                    <p className="small muted mb-0">
                      {job.provider} · {job.model} · {fmt(job.created_at, lang)}
                    </p>
                  </div>
                  <span
                    className={`badge ${STATUS_TONE[job.status] ?? "badge-info"}`}
                  >
                    {t(lang, job.status_label)}
                  </span>
                </div>
                {job.error ? (
                  <p className="studio-error small">{job.error}</p>
                ) : null}
                <div className="row">
                  {job.course_slug &&
                  courses.some(
                    (course) =>
                      course.slug === job.course_slug &&
                      course.status === "published"
                  ) ? (
                    <a
                      className="btn btn-secondary btn-sm"
                      href={`/cursos/${job.course_slug}`}
                    >
                      <Icon name="book" /> {t(lang, "Abrir en el catálogo")}
                    </a>
                  ) : null}
                  {job.active ? (
                    <button
                      className="btn btn-ghost btn-sm"
                      type="button"
                      onClick={() => void cancelJob(job)}
                      disabled={busy}
                    >
                      <Icon name="x-circle" /> {t(lang, "Cancelar")}
                    </button>
                  ) : null}
                  {job.log ? (
                    <details className="studio-log">
                      <summary className="small">{t(lang, "Ver registro")}</summary>
                      <pre>{job.log}</pre>
                    </details>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-search" style={{ margin: 18 }}>
            <p className="mb-0">{t(lang, "Todavía no hay trabajos.")}</p>
          </div>
        )}
      </section>

      <section className="card mt-4">
        <div className="card-head" style={{ padding: "18px 20px 0" }}>
          <h3 className="card-title">
            <Icon name="book" /> {t(lang, "Unidades generadas")}
          </h3>
          <span className="small muted">
            {courses.length} {t(lang, "en total")}
          </span>
        </div>
        {courses.length ? (
          <div className="studio-courses">
            {courses.map((course) => (
              <article className="studio-course" key={course.slug}>
                <div>
                  <strong>
                    {course.summary.titles[lang] ??
                      course.summary.titles.es ??
                      course.title}
                  </strong>
                  <p className="small muted mb-0">
                    {course.slug} · {course.summary.lesson_count}{" "}
                    {t(lang, "lecciones")} · {course.summary.languages.join(" / ")}
                  </p>
                  <span
                    className={`badge ${
                      course.status === "published"
                        ? "badge-success"
                        : "badge-neutral"
                    }`}
                  >
                    {t(
                      lang,
                      course.status === "published" ? "Publicada" : "Borrador"
                    )}
                  </span>
                </div>
                <div className="row">
                  {course.status === "published" ? (
                    <>
                      <a
                        className="btn btn-secondary btn-sm"
                        href={`/cursos/${course.slug}`}
                      >
                        <Icon name="eye" /> {t(lang, "Abrir en el catálogo")}
                      </a>
                      <button
                        className="btn btn-ghost btn-sm"
                        type="button"
                        onClick={() => void setPublished(course, false)}
                        disabled={busy}
                      >
                        {t(lang, "Despublicar")}
                      </button>
                    </>
                  ) : (
                    <button
                      className="btn btn-primary btn-sm"
                      type="button"
                      onClick={() => void setPublished(course, true)}
                      disabled={busy}
                    >
                      <Icon name="check-circle" /> {t(lang, "Publicar")}
                    </button>
                  )}
                  <button
                    className="btn btn-ghost btn-sm"
                    type="button"
                    onClick={() => void removeCourse(course)}
                    disabled={busy}
                  >
                    {t(lang, "Eliminar")}
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-search" style={{ margin: 18 }}>
            <p className="mb-0">{t(lang, "Todavía no hay unidades generadas.")}</p>
          </div>
        )}
      </section>
    </>
  );
}
