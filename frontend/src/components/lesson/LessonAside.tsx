import Link from "next/link";

import { Icon, ProgressBar } from "@/components/ui";
import { percent } from "@/lib/format";
import { t } from "@/lib/messages";
import type { Attempt, Lang, ProgressRow, QuizMeta } from "@/lib/types";
import { LessonActions, type LessonActionLabels } from "./LessonActions";
import { NoteEditor } from "./NoteEditor";

export function LessonAside({
  slug,
  lessonNumber,
  chapterTotal,
  courseTotal,
  courseCompleted,
  progress,
  completedCount,
  note,
  bookmarked,
  quiz,
  bestAttempt,
  csrf,
  lang,
}: {
  slug: string;
  lessonNumber: number;
  chapterTotal: number;
  courseTotal: number;
  courseCompleted: number;
  progress: ProgressRow | null;
  completedCount: number;
  note: string;
  bookmarked: boolean;
  quiz: QuizMeta | null;
  bestAttempt: Attempt | null;
  csrf: string;
  lang: Lang;
}) {
  const total = chapterTotal;
  const actionLabels: LessonActionLabels = {
    markComplete: t(lang, "Marcar como completada"),
    markPending: t(lang, "Marcar como pendiente"),
    addBookmark: t(lang, "Guardar en marcadores"),
    removeBookmark: t(lang, "Quitar marcador"),
    saving: `${t(lang, "Guardar")}…`,
    completedSaved: t(lang, "Lección marcada como completada."),
    pendingSaved: t(lang, "Lección marcada como pendiente."),
    bookmarkSaved: t(lang, "Marcador actualizado."),
    bookmarkRemoved: t(lang, "Marcador actualizado."),
    error: t(lang, "El servidor no respondió. Inténtalo de nuevo."),
  };

  return (
    <aside className="lesson-aside">
      <section className="card aside-card">
        <h3>
          <Icon name="chart" /> {t(lang, "Tu progreso")}
        </h3>
        <div className="aside-progress">
          <div style={{ flex: 1 }}>
            <strong>
              {progress?.completed
                ? t(lang, "Lección completada")
                : t(lang, "Aún en curso")}
            </strong>
            <small>
              {t(lang, "Lección {n} de {total}", {
                n: lessonNumber,
                total,
              })}
            </small>
          </div>
        </div>
        <ProgressBar
          value={percent(completedCount, total)}
          label={t(lang, "Progreso del capítulo")}
          tone="success"
        />
        <p className="small muted" style={{ margin: "7px 0 0" }}>
          {t(lang, "{completed} de {total} lecciones completadas", {
            completed: completedCount,
            total,
          })}
        </p>
        <p className="small muted" style={{ margin: "3px 0 0" }}>
          {t(lang, "{completed} de {total} lecciones del curso", {
            completed: courseCompleted,
            total: courseTotal,
          })}
        </p>
        <div className="mt-3">
          <LessonActions
            action="complete"
            slug={slug}
            csrf={csrf}
            completed={Boolean(progress?.completed)}
            bookmarked={bookmarked}
            labels={actionLabels}
          />
        </div>
      </section>

      <section className="card aside-card">
        <h3>
          <Icon name="notebook" /> {t(lang, "Tus apuntes")}
        </h3>
        <NoteEditor slug={slug} csrf={csrf} note={note} lang={lang} />
      </section>

      <section className="card aside-card">
        <h3>
          <Icon name="bookmark" /> {t(lang, "Marcador")}
        </h3>
        <p>{t(lang, "Guarda esta lección para volver más tarde.")}</p>
        <LessonActions
          action="bookmark"
          slug={slug}
          csrf={csrf}
          completed={Boolean(progress?.completed)}
          bookmarked={bookmarked}
          labels={actionLabels}
        />
      </section>

      {quiz ? (
        <section className="card aside-card">
          <h3>
            <Icon name="trophy" /> {t(lang, "Quiz del capítulo")}
          </h3>
          {bestAttempt ? (
            <>
              <p>
                {t(lang, "Mejor resultado: {pct} % ({score}/{total}).", {
                  pct: bestAttempt.percent,
                  score: bestAttempt.score,
                  total: bestAttempt.total,
                })}
              </p>
              <Link className="btn btn-primary btn-block" href={`/quiz/${quiz.id}`}>
                <Icon name="refresh" /> {t(lang, "Repetir quiz")}
              </Link>
            </>
          ) : (
            <>
              <p>
                {t(
                  lang,
                  "Diez preguntas para comprobar las ideas del capítulo."
                )}
              </p>
              <Link className="btn btn-primary btn-block" href={`/quiz/${quiz.id}`}>
                <Icon name="play" /> {t(lang, "Hacer el quiz")}
              </Link>
            </>
          )}
        </section>
      ) : null}

      <section className="card aside-card">
        <h3>
          <Icon name="lightbulb" /> {t(lang, "Consejo de estudio")}
        </h3>
        <p className="mb-0">
          {t(
            lang,
            "Si una idea no queda clara, vuelve al laboratorio y cambia un parámetro. Aprender LLMs es construir intuición, no memorizar siglas."
          )}
        </p>
      </section>
    </aside>
  );
}
