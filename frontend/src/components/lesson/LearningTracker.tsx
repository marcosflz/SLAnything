"use client";

import { useEffect } from "react";

type TrackedEvent = {
  verb: "lesson.heartbeat" | "lab.interacted" | "check.answered";
  course: string;
  lesson: string;
  object?: string;
  duration_ms?: number;
};

const HEARTBEAT_MS = 30_000;
const IDLE_MS = 120_000;

/**
 * Mide el tiempo real de estudio de una lección (ADR-018).
 *
 * Cada 30 s, si la pestaña está visible y hubo actividad reciente (scroll,
 * teclado, ratón), suma un latido. Los eventos se agrupan y se envían con
 * `sendBeacon` al ocultar la página, para no perderlos al navegar.
 */
export function LearningTracker({
  course,
  lesson,
  csrf,
}: {
  course: string;
  lesson: string;
  csrf: string;
}) {
  useEffect(() => {
    let queue: TrackedEvent[] = [];
    let lastActivity = Date.now();
    let lastBeat = Date.now();
    const labsTouched = new Set<string>();

    const flush = (useBeacon: boolean) => {
      if (!queue.length) return;
      const body = JSON.stringify({ events: queue, csrf_token: csrf });
      queue = [];
      if (useBeacon && navigator.sendBeacon) {
        navigator.sendBeacon("/api/v1/events", new Blob([body], { type: "application/json" }));
        return;
      }
      void fetch("/api/v1/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        keepalive: true,
      }).catch(() => undefined);
    };

    const beat = () => {
      const now = Date.now();
      const elapsed = now - lastBeat;
      lastBeat = now;
      if (document.visibilityState !== "visible") return;
      if (now - lastActivity > IDLE_MS) return;
      queue.push({ verb: "lesson.heartbeat", course, lesson, duration_ms: Math.min(elapsed, 60_000) });
      if (queue.length >= 4) flush(false);
    };

    const onActivity = () => {
      lastActivity = Date.now();
    };

    // Un evento por laboratorio y visita: basta para medir uso, sin ruido.
    const onLab = (event: Event) => {
      const target = event.target as HTMLElement | null;
      const lab = target?.closest<HTMLElement>("[data-lab]");
      const id = lab?.dataset.lab;
      if (!id || labsTouched.has(id)) return;
      labsTouched.add(id);
      queue.push({ verb: "lab.interacted", course, lesson, object: id });
    };

    const onVisibility = () => {
      if (document.visibilityState === "hidden") {
        beat();
        flush(true);
      } else {
        lastBeat = Date.now();
      }
    };

    const timer = window.setInterval(beat, HEARTBEAT_MS);
    const activity = ["scroll", "keydown", "pointerdown", "pointermove"] as const;
    activity.forEach((name) => window.addEventListener(name, onActivity, { passive: true }));
    document.addEventListener("input", onLab, true);
    document.addEventListener("click", onLab, true);
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("pagehide", onVisibility);

    return () => {
      window.clearInterval(timer);
      activity.forEach((name) => window.removeEventListener(name, onActivity));
      document.removeEventListener("input", onLab, true);
      document.removeEventListener("click", onLab, true);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("pagehide", onVisibility);
      beat();
      flush(true);
    };
  }, [course, lesson, csrf]);

  return null;
}
