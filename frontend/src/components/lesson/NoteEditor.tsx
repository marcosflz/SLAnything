"use client";

import { useState, type FormEvent } from "react";

import { ApiClientError, apiPost } from "@/lib/client";
import { t } from "@/lib/messages";
import type { Lang } from "@/lib/types";

type SaveState = "idle" | "saving" | "saved" | "error";

export function NoteEditor({
  slug,
  csrf,
  note,
  lang,
}: {
  slug: string;
  csrf: string;
  note: string;
  lang: Lang;
}) {
  const [body, setBody] = useState(note);
  const [state, setState] = useState<SaveState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  function update(value: string) {
    setBody(value);
    if (state !== "saving") {
      setState("idle");
      setErrorMessage("");
    }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (state === "saving") return;

    setState("saving");
    setErrorMessage("");
    try {
      await apiPost<{ ok: boolean; message?: string }>(
        `/api/v1/lessons/${slug}/note`,
        { body },
        csrf
      );
      setState("saved");
    } catch (error) {
      setErrorMessage(
        error instanceof ApiClientError
          ? error.message
          : t(lang, "El servidor no respondió. Inténtalo de nuevo.")
      );
      setState("error");
    }
  }

  const savingLabel = `${t(lang, "Guardar")}…`;
  const status =
    state === "saving"
      ? savingLabel
      : state === "saved"
        ? t(lang, "Apuntes guardados.")
        : state === "error"
          ? errorMessage
          : "";

  return (
    <form onSubmit={save}>
      <label className="sr-only" htmlFor="nota">
        {t(lang, "Apuntes de la lección")}
      </label>
      <textarea
        className="note-area"
        id="nota"
        name="body"
        maxLength={20000}
        data-note
        data-note-label={t(lang, "{n} caracteres")}
        value={body}
        onChange={(event) => update(event.target.value)}
        placeholder={t(lang, "Escribe una idea, una duda o un ejemplo…")}
        aria-describedby="nota-contador"
      />
      <div className="note-meta">
        <span id="nota-contador" data-note-count>
          {t(lang, "{n} caracteres", { n: body.length })}
        </span>
        <button
          className="btn btn-secondary btn-sm"
          type="submit"
          disabled={state === "saving"}
          aria-busy={state === "saving"}
        >
          {state === "saving" ? savingLabel : t(lang, "Guardar")}
        </button>
      </div>
      {status ? (
        <p
          className={`small ${state === "error" ? "" : "muted"}`}
          role="status"
          aria-live="polite"
          style={{
            margin: "6px 0 0",
            color: state === "error" ? "var(--danger)" : undefined,
          }}
        >
          {status}
        </p>
      ) : null}
    </form>
  );
}
