import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { ActivityBars } from "@/components/progress/ActivityBars";
import { AttemptList } from "@/components/quiz/AttemptList";
import {
  Icon,
  LessonStatus,
  ProgressBar,
  Ring,
  Stat,
} from "@/components/ui";
import { apiGet, getShell } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { t } from "@/lib/messages";
import type { ProgressPayload } from "@/lib/types";

type SearchParams = Record<string, string | string[] | undefined>;

function buildFullPath(pathname: string, searchParams: SearchParams): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(searchParams)) {
    if (Array.isArray(value)) {
      for (const item of value) query.append(key, item);
    } else if (value !== undefined) {
      query.set(key, value);
    }
  }
  const suffix = query.toString();
  return suffix ? `${pathname}?${suffix}` : pathname;
}

export default async function ProgressPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const query = await searchParams;
  const pathname = "/progreso";
  const shell = await getShell(pathname);
  const payload = await apiGet<ProgressPayload>("/api/v1/progress");

  const lang = shell.lang;
  const { course, stats, rows, attempts, activity, avg_score: avgScore, streak } =
    payload;
  const quizLesson = course.lessons.find((lesson) => lesson.quiz_id !== null);
  const quizHref = `/quiz/${quizLesson?.quiz_id ?? "quiz-capitulo-1"}`;

  return (
    <AppShell
      user={shell.user}
      course={course}
      courses={payload.courses}
      progress={payload.progress}
      stats={stats}
      site={shell.site}
      lang={lang}
      pathname={pathname}
      fullPath={buildFullPath(pathname, query)}
      title={t(lang, "Mi progreso")}
      kicker={t(lang, "Tu recorrido")}
    >
      <div className="page-head">
        <span className="eyebrow-dark">
          {t(lang, "{n} capítulos", { n: course.chapter_count })} ·{" "}
          {course.title}
        </span>
        <h2>{t(lang, "Así va tu aprendizaje")}</h2>
        <p>
          {t(
            lang,
            "Todo tu progreso se guarda en el aula: lecciones completadas, apuntes, intentos de quiz y actividad diaria."
          )}
        </p>
        <Link className="btn btn-ghost btn-sm" href="/cursos">
          <Icon name="grid" /> {t(lang, "Cambiar de curso")}
        </Link>
      </div>

      <div className="stat-grid stat-grid-4">
        <Stat
          label={t(lang, "Lecciones")}
          value={`${stats.completed} / ${stats.total}`}
          hint={t(lang, "completadas")}
          icon="check-circle"
          tone="green"
        />
        <Stat
          label={t(lang, "Progreso")}
          value={`${stats.pct} %`}
          hint={t(lang, "del curso")}
          icon="chart"
          tone="blue"
        />
        <Stat
          label={t(lang, "Nota media")}
          value={avgScore === null ? "—" : `${avgScore} %`}
          hint={t(lang, "en los quizzes")}
          icon="trophy"
          tone="violet"
        />
        <Stat
          label={t(lang, "Racha")}
          value={
            streak === 1
              ? t(lang, "{n} día", { n: streak })
              : t(lang, "{n} días", { n: streak })
          }
          hint={t(lang, "consecutivos")}
          icon="flame"
          tone="amber"
        />
      </div>

      <div className="progress-grid mt-4">
        <section className="card card-pad">
          <div className="card-head">
            <h3 className="card-title">
              <Icon name="list" /> {t(lang, "Lecciones del curso")}
            </h3>
            <span className="small muted">
              {stats.completed === 1
                ? t(lang, "{n} completada", { n: stats.completed })
                : t(lang, "{n} completadas", { n: stats.completed })}
            </span>
          </div>
          <div className="table-wrap" style={{ margin: 0, border: 0 }}>
            <table className="progress-table">
              <thead>
                <tr>
                  <th>{t(lang, "Lección")}</th>
                  <th>{t(lang, "Estado")}</th>
                  <th>{t(lang, "Última visita")}</th>
                  <th></th>
                </tr>
              </thead>
              {course.chapters.map((chapter) => (
                <tbody key={chapter.slug}>
                  <tr className="chapter-row">
                    <td colSpan={4}>
                      <strong>
                        {t(lang, "Capítulo {n}", { n: chapter.number })}
                      </strong>{" "}
                      · {chapter.title}
                    </td>
                  </tr>
                  {rows
                    .filter((row) =>
                      chapter.lessons.some(
                        (lesson) => lesson.slug === row.lesson.slug
                      )
                    )
                    .map((row) => (
                      <tr key={row.lesson.slug}>
                        <td>
                          <strong>{row.lesson.number}.</strong>{" "}
                          {row.lesson.title}
                        </td>
                        <td>
                          <LessonStatus
                            progress={row.progress}
                            completedLabel={t(lang, "Completada")}
                            progressLabel={t(lang, "En curso")}
                            pendingLabel={t(lang, "Pendiente")}
                          />
                        </td>
                        <td className="muted">
                          {row.progress?.last_seen_at
                            ? formatDate(row.progress.last_seen_at, lang)
                            : "—"}
                        </td>
                        <td>
                          <Link
                            className="small"
                            href={`/leccion/${row.lesson.slug}`}
                          >
                            {t(lang, "Abrir →")}
                          </Link>
                        </td>
                      </tr>
                    ))}
                </tbody>
              ))}
            </table>
          </div>
        </section>

        <aside className="stack">
          <section className="card card-pad center">
            <span className="eyebrow-dark">{t(lang, "Progreso total")}</span>
            <div className="mt-3">
              <Ring
                value={stats.pct}
                size={126}
                label={t(lang, "del curso")}
              />
            </div>
            <ProgressBar
              value={stats.pct}
              label={t(lang, "Progreso del curso")}
              tone="success"
            />
            <p className="small muted mt-3 mb-0">
              {t(lang, "{completed} de {total} lecciones completadas", {
                completed: stats.completed,
                total: stats.total,
              })}
            </p>
          </section>

          <section className="card card-pad">
            <div className="card-head">
              <h3 className="card-title">
                <Icon name="chart" /> {t(lang, "Actividad · 28 días")}
              </h3>
            </div>
            <ActivityBars activity={activity} lang={lang} />
          </section>
        </aside>
      </div>

      <section className="card card-pad mt-4">
        <div className="card-head">
          <h3 className="card-title">
            <Icon name="trophy" /> {t(lang, "Intentos de quiz")}
          </h3>
          <Link className="small" href={quizHref}>
            {t(lang, "Hacer el quiz →")}
          </Link>
        </div>
        {attempts.length > 0 ? (
          <AttemptList attempts={attempts} lang={lang} showBadges />
        ) : (
          <div className="empty-search">
            <p className="mb-0">
              {t(
                lang,
                "Aún no hay intentos. Cuando termines un capítulo, su quiz te dará una medida de lo aprendido."
              )}
            </p>
          </div>
        )}
      </section>
    </AppShell>
  );
}
