"use client";

import { useMemo, useRef, useState } from "react";

import { t } from "@/lib/messages";
import type { Lang } from "@/lib/types";
import { Icon } from "./ui";

type OutputItem =
  | { type: "image"; mime?: string; data: string }
  | { type: "table"; html: string }
  | { type: "text"; text: string };

interface RunResult {
  ok: boolean;
  stdout?: string;
  error?: string;
  stderr?: string;
  outputs?: OutputItem[];
  duration_ms?: number;
}

export function PythonRunner({
  code,
  caption,
  lessonSlug,
  index,
  csrf,
  lang,
}: {
  code: string;
  caption?: string | null;
  lessonSlug: string;
  index: number;
  csrf: string;
  lang: Lang;
}) {
  const [source, setSource] = useState(code);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [status, setStatus] = useState(t(lang, "Salida"));
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lines = useMemo(() => source.split("\n").length, [source]);

  async function run() {
    if (running) return;
    setRunning(true);
    setResult(null);
    setStatus(t(lang, "Ejecutando…"));
    const started = performance.now();
    try {
      const response = await fetch("/api/ejecutar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrf,
        },
        body: JSON.stringify({ code: source, lesson: lessonSlug || null }),
      });
      const data = (await response.json().catch(() => null)) as
        | (RunResult & { detail?: string })
        | null;
      const elapsed = Math.max(1, Math.round(performance.now() - started));
      if (!response.ok) {
        throw new Error(
          (typeof data?.error === "string" && data.error) ||
            (typeof data?.detail === "string" && data.detail) ||
            t(lang, "No se pudo ejecutar el código.")
        );
      }
      const next = { ...(data ?? {}), duration_ms: elapsed } as RunResult;
      setResult(next);
      setStatus(
        next.error
          ? t(lang, "El código devolvió un error.")
          : t(lang, "El código se ejecutó correctamente.")
      );
    } catch (error) {
      setResult({
        ok: false,
        error:
          error instanceof Error
            ? error.message
            : t(lang, "El servidor no respondió. Inténtalo de nuevo."),
      });
      setStatus(t(lang, "El código devolvió un error."));
    } finally {
      setRunning(false);
    }
  }

  function onKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Tab") {
      event.preventDefault();
      const target = event.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const next = `${source.slice(0, start)}    ${source.slice(end)}`;
      setSource(next);
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      });
    }
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      void run();
    }
  }

  const stdout = result?.stdout ?? "";
  const outputs = result?.outputs ?? [];
  const hasOutput = Boolean(result);

  return (
    <div
      className="py-runner"
      data-python-runner
      data-filename={`ejemplo-${index}.py`}
      data-lesson={lessonSlug}
    >
      <div className="code-head py-head">
        <span className="code-lang">{t(lang, "Python · ejecutable")}</span>
        {caption ? <span className="code-caption">{caption}</span> : null}
        <div className="py-actions">
          <button
            className="btn btn-primary btn-sm"
            type="button"
            data-py-run
            onClick={() => void run()}
            disabled={running}
          >
            <Icon name="play" /> {t(lang, "Ejecutar")}
          </button>
          <button
            className="btn btn-ghost btn-sm"
            type="button"
            data-py-reset
            onClick={() => {
              setSource(code);
              setResult(null);
              setStatus(t(lang, "Salida"));
            }}
          >
            <Icon name="refresh" /> {t(lang, "Restablecer")}
          </button>
          <a
            className="btn btn-secondary btn-sm"
            data-py-download
            href={`/api/v1/downloads/lessons/${lessonSlug}/code/${index}`}
          >
            <Icon name="download" /> {t(lang, "Descargar")}
          </a>
        </div>
      </div>
      <div className="py-editor">
        <div className="py-gutter" data-py-gutter aria-hidden="true">
          {Array.from({ length: lines }, (_, i) => i + 1).join("\n")}
        </div>
        <textarea
          ref={textareaRef}
          className="py-source"
          spellCheck={false}
          autoCapitalize="off"
          autoComplete="off"
          aria-label={t(lang, "Código Python editable")}
          value={source}
          onChange={(event) => setSource(event.target.value)}
          onKeyDown={onKeyDown}
        />
      </div>
      <div className="py-meta">
        <span>
          <Icon name="server" />{" "}
          {t(
            lang,
            "Se ejecuta en el servidor, en un proceso aislado y con límite de tiempo y memoria."
          )}
        </span>
        <span>{t(lang, "También puedes descargarlo y ejecutarlo en tu equipo.")}</span>
      </div>
      <div
        className="py-output"
        data-py-output
        hidden={!hasOutput}
        aria-live="polite"
      >
        <div className="py-output-head">
          <span data-py-status>{status}</span>
          <span className="py-duration" data-py-duration>
            {result?.duration_ms ? `${result.duration_ms} ms` : ""}
          </span>
          <button
            className="code-copy"
            type="button"
            data-py-clear
            onClick={() => {
              setResult(null);
              setStatus(t(lang, "Salida"));
            }}
          >
            {t(lang, "Limpiar")}
          </button>
        </div>
        {stdout ? (
          <pre className="py-stdout" data-py-stdout>
            {stdout}
          </pre>
        ) : null}
        {result?.error ? (
          <div className="py-error" data-py-error>
            {result.error}
          </div>
        ) : null}
        <div className="py-results" data-py-results>
          {outputs.map((item, position) => {
            if (item.type === "image") {
              return (
                <img
                  key={position}
                  className="py-plot"
                  loading="lazy"
                  alt={t(lang, "Gráfico generado por el ejemplo")}
                  src={`data:${item.mime ?? "image/png"};base64,${item.data}`}
                />
              );
            }
            if (item.type === "table") {
              return (
                <div
                  key={position}
                  className="py-table-wrap"
                  dangerouslySetInnerHTML={{ __html: item.html }}
                />
              );
            }
            if (item.type === "text") {
              return (
                <pre key={position} className="py-result-text">
                  {item.text}
                </pre>
              );
            }
            return null;
          })}
        </div>
        {!stdout && !result?.error && outputs.length === 0 ? (
          <pre className="py-stdout">{t(lang, "Sin salida.")}</pre>
        ) : null}
      </div>
    </div>
  );
}
