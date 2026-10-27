"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Icon } from "@/components/ui";
import { ApiClientError, apiPost } from "@/lib/client";
import type { MutationResult } from "@/lib/types";

export interface LessonActionLabels {
  markComplete: string;
  markPending: string;
  addBookmark: string;
  removeBookmark: string;
  saving: string;
  completedSaved: string;
  pendingSaved: string;
  bookmarkSaved: string;
  bookmarkRemoved: string;
  error: string;
}

export function LessonActions({
  action = "complete",
  slug,
  csrf,
  completed,
  bookmarked,
  labels,
}: {
  action?: "complete" | "bookmark";
  slug: string;
  csrf: string;
  completed: boolean;
  bookmarked: boolean;
  labels: LessonActionLabels;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [status, setStatus] = useState("");
  const [isCompleted, setIsCompleted] = useState(completed);
  const [isBookmarked, setIsBookmarked] = useState(bookmarked);

  const isComplete = action === "complete";
  const active = isComplete ? isCompleted : isBookmarked;
  const label = isComplete
    ? active
      ? labels.markPending
      : labels.markComplete
    : active
      ? labels.removeBookmark
      : labels.addBookmark;
  const buttonClass = isComplete
    ? `btn ${active ? "btn-secondary" : "btn-success"} btn-block`
    : `btn ${active ? "btn-primary" : "btn-secondary"} btn-block`;

  async function submit() {
    if (busy) return;
    setBusy(true);
    setFailed(false);
    setStatus(labels.saving);

    try {
      if (isComplete) {
        const next = !isCompleted;
        const result = await apiPost<MutationResult>(
          `/api/v1/lessons/${slug}/complete`,
          { completed: next },
          csrf
        );
        setIsCompleted(result.completed ?? next);
        setStatus(
          result.message ??
            (next ? labels.completedSaved : labels.pendingSaved)
        );
      } else {
        const result = await apiPost<MutationResult>(
          `/api/v1/lessons/${slug}/bookmark`,
          {},
          csrf
        );
        const next = result.bookmarked ?? !isBookmarked;
        setIsBookmarked(next);
        setStatus(
          result.message ?? (next ? labels.bookmarkSaved : labels.bookmarkRemoved)
        );
      }
      router.refresh();
    } catch (error) {
      setFailed(true);
      setStatus(
        error instanceof ApiClientError ? error.message : labels.error
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button
        className={buttonClass}
        type="button"
        onClick={() => void submit()}
        disabled={busy}
        aria-busy={busy}
      >
        <Icon name={isComplete ? "check" : "bookmark"} /> {label}
      </button>
      {status ? (
        <p
          className={`small ${failed ? "" : "muted"}`}
          role="status"
          aria-live="polite"
          style={{
            margin: "6px 0 0",
            color: failed ? "var(--danger)" : undefined,
          }}
        >
          {status}
        </p>
      ) : null}
    </>
  );
}
