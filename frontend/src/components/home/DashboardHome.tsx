import Link from "next/link";

import { Icon, Ring, Stat } from "@/components/ui";
import { formatDate } from "@/lib/format";
import { t } from "@/lib/messages";
import type { DashboardPayload, Lang, ProgressMap, User } from "@/lib/types";

export function DashboardHome({
  data,
  progress,
  lang,
  user,
}: {
  data: DashboardPayload;
  progress: ProgressMap;
  lang: Lang;
  user: User;
}) {
  const {
    course,
    courses,
    stats,
    next_lesson,
    avg_score,
    streak,
    activity,
    attempts,
  } = data;
  const maxActivity = Math.max(1, ...activity.map((day) => day.count));
  const firstName = user.name.trim().split(/\s+/)[0] || user.name;

  return (
    <>
      <div className="dashboard-head">
        <div>
          <span className="eyebrow-dark">
            {t(lang, "{n} capítulos", { n: course.chapter_count })} ·{" "}
            {course.title}
          </span>
          <h2>
            {t(lang, "Hola")}, {firstName}.
          </h2>
          <p>
            {stats.pct === 100
              ? t(
                  lang,
                  "Has terminado el capítulo. Puedes repasar o repetir el quiz."
                )
              : t(
                  lang,
                  "Tu siguiente paso está a un clic. Sin prisa, pero sin pausa."
                )}
          </p>
        </div>
        <div className="row">
          <Link className="btn btn-ghost" href="/cursos">
            <Icon name="grid" /> {t(lang, "Explorar cursos")}
          </Link>
          <Link className="btn btn-secondary" href={`/cursos/${course.slug}`}>
            <Icon name="list" /> {t(lang, "Ver el programa")}
          </Link>
        </div>
      </div>

      <section className="card card-pad">
        <div className="card-head">
          <h3 className="card-title">
            <Icon name="grid" /> {t(lang, "Tus cursos")}
          </h3>
          <Link className="small" href="/cursos">
            {t(lang, "Ver catálogo →")}
          </Link>
        </div>
        <div className="course-strip">
          {courses.map((item) => (
            <Link
              className={`course-strip-item ${
                item.slug === course.slug ? "is-active" : ""
              }`}
              href={`/cursos/${item.slug}`}
              key={item.slug}
            >
              <span className="course-strip-icon">
                <Icon name="book" />
              </span>
              <span className="course-strip-body">
                <strong>{item.title}</strong>
                <small>
                  {t(lang, "{completed} de {total} lecciones", {
                    completed: item.stats.completed,
                    total: item.stats.total,
                  })}
                </small>
              </span>
              <span className="course-strip-pct">{item.stats.pct} %</span>
            </Link>
          ))}
        </div>
      </section>

      <div className="dash-grid">
        <div className="dash-main">
          <section className="continue-card">
            <span className="eyebrow">
              {next_lesson
                ? t(lang, "Siguiente paso")
                : t(lang, "Curso completado")}
            </span>
            {next_lesson ? (
              <>
                <h3>{next_lesson.title}</h3>
                <p>{next_lesson.summary}</p>
                {next_lesson.chapter_title ? (
                  <p className="small muted">
                    {t(lang, "Capítulo {n}", {
                      n: next_lesson.chapter_number ?? "",
                    })}{" "}
                    · {next_lesson.chapter_title}
                  </p>
                ) : null}
                <Link
                  className="btn btn-primary"
                  href={`/leccion/${next_lesson.slug}`}
                  prefetch={false}
                >
                  <Icon name="play" /> {t(lang, "Continuar lección")}
                </Link>
                <div className="continue-meta">
                  <span>
                    <Icon name="clock" /> {next_lesson.minutes} min
                  </span>
                  <span>
                    <Icon name="target" />{" "}
                    {t(lang, "{n} objetivos", {
                      n: next_lesson.objectives.length,
                    })}
                  </span>
                  {next_lesson.labs.length ? (
                    <span>
                      <Icon name="sparkles" />{" "}
                      {next_lesson.labs.length === 1
                        ? t(lang, "{n} laboratorio", {
                            n: next_lesson.labs.length,
                          })
                        : t(lang, "{n} laboratorios", {
                            n: next_lesson.labs.length,
                          })}
                    </span>
                  ) : null}
                </div>
              </>
            ) : (
              <>
                <h3>{t(lang, "Has llegado al final del curso.")}</h3>
                <p>
                  {t(
                    lang,
                    "Repasa las ideas clave o vuelve a intentar los quizzes para consolidar."
                  )}
                </p>
                <Link
                  className="btn btn-primary"
                  href={`/cursos/${course.slug}`}
                >
                  <Icon name="book" /> {t(lang, "Ver el programa")}
                </Link>
              </>
            )}
          </section>

          <div className="stat-grid">
            <Stat
              label={t(lang, "Lecciones completadas")}
              value={`${stats.completed} / ${stats.total}`}
              hint={t(lang, "de este curso")}
              icon="check-circle"
              tone="green"
            />
            <Stat
              label={t(lang, "Racha actual")}
              value={
                streak === 1
                  ? t(lang, "{n} día", { n: streak })
                  : t(lang, "{n} días", { n: streak })
              }
              hint={t(lang, "actividad consecutiva")}
              icon="flame"
              tone="amber"
            />
            <Stat
              label={t(lang, "Nota media")}
              value={avg_score !== null ? `${avg_score} %` : "—"}
              hint={t(lang, "en los intentos de quiz")}
              icon="trophy"
              tone="violet"
            />
            <Stat
              label={t(lang, "Laboratorios")}
              value={String(course.lab_count)}
              hint={t(lang, "interactivos en el curso")}
              icon="sparkles"
              tone="blue"
            />
          </div>

          <section className="card activity-card">
            <div className="card-head">
              <h3 className="card-title">
                <Icon name="chart" /> {t(lang, "Tu actividad reciente")}
              </h3>
              <span className="small muted">
                {t(lang, "Últimos 14 días")}
              </span>
            </div>
            <div
              className="activity-bars"
              aria-label={t(lang, "Actividad de los últimos 14 días")}
            >
              {activity.map((day, index) => (
                <div
                  className="activity-day"
                  key={day.day}
                  title={`${day.label}: ${t(lang, "{n} acciones", {
                    n: day.count,
                  })}`}
                >
                  <div
                    className={`activity-bar ${
                      day.count ? "has-activity" : ""
                    } ${day.is_today ? "is-today" : ""}`}
                    style={{
                      height: `${8 + (day.count / maxActivity) * 52}px`,
                    }}
                  />
                  <span className="activity-label">
                    {index % 2 === 0 ? day.label : ""}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="card card-pad">
            <div className="card-head">
              <h3 className="card-title">
                <Icon name="route" /> {t(lang, "La ruta del curso")}
              </h3>
              <Link className="small" href={`/cursos/${course.slug}`}>
                {t(lang, "Ver detalle")}
              </Link>
            </div>
            <div className="next-list">
              {course.chapters.map((chapter) => {
                const done = chapter.lessons.filter(
                  (lesson) => progress[lesson.slug]?.completed
                ).length;
                const isActive = chapter.lessons.some(
                  (lesson) => next_lesson?.slug === lesson.slug
                );
                return (
                  <Link
                    className={`next-item ${
                      done === chapter.lesson_count ? "is-done" : ""
                    } ${isActive ? "is-active" : ""}`}
                    href={`/cursos/${course.slug}#capitulo-${chapter.number}`}
                    prefetch={false}
                    key={chapter.slug}
                  >
                    <span className="num">
                      {done === chapter.lesson_count ? (
                        <Icon name="check" />
                      ) : (
                        chapter.number
                      )}
                    </span>
                    <span>{chapter.title}</span>
                    <span className="spacer" />
                    <span className="small muted">
                      {done}/{chapter.lesson_count} · {chapter.total_minutes} min
                    </span>
                  </Link>
                );
              })}
            </div>
          </section>
        </div>

        <aside className="dash-side">
          <section className="card card-pad center">
            <span className="eyebrow-dark">
              {t(lang, "Progreso del curso")}
            </span>
            <div className="mt-3">
              <Ring
                value={stats.pct}
                size={118}
                label={t(lang, "completado")}
              />
            </div>
            <p className="small muted mt-3 mb-0">
              {t(
                lang,
                "{completed} de {total} lecciones completadas",
                {
                  completed: stats.completed,
                  total: stats.total,
                }
              )}
            </p>
            <Link
              className="btn btn-secondary btn-block mt-3"
              href="/progreso"
            >
              <Icon name="chart" /> {t(lang, "Ver mi progreso")}
            </Link>
          </section>

          <section className="card card-pad">
            <div className="card-head">
              <h3 className="card-title">
                <Icon name="trophy" /> {t(lang, "Últimos intentos")}
              </h3>
            </div>
            {attempts.length ? (
              <div className="attempt-list">
                {attempts.map((attempt) => (
                  <Link
                    className="attempt-row"
                    href={`/quiz/intento/${attempt.id}`}
                    key={attempt.id}
                  >
                    <span
                      className={`attempt-score ${
                        attempt.passed ? "is-pass" : "is-fail"
                      }`}
                    >
                      {attempt.percent}%
                    </span>
                    <span>
                      <strong>
                        {attempt.score}/{attempt.total}
                      </strong>
                      <span className="attempt-meta">
                        {formatDate(attempt.created_at, lang)}
                      </span>
                    </span>
                    <Icon name="chevron-down" />
                  </Link>
                ))}
              </div>
            ) : (
              <p className="small muted mb-0">
                {t(
                  lang,
                  "Todavía no has hecho el quiz. Cuando lo hagas, tus resultados aparecerán aquí."
                )}
              </p>
            )}
          </section>

          <section className="card card-pad">
            <h3 className="card-title">
              <Icon name="bookmark" /> {t(lang, "Accesos rápidos")}
            </h3>
            <div className="stack mt-2">
              <Link className="next-item" href="/cursos">
                <Icon name="grid" /> {t(lang, "Catálogo de cursos")}
              </Link>
              <Link className="next-item" href="/glosario">
                <Icon name="glossary" /> {t(lang, "Glosario del curso")}
              </Link>
              <Link className="next-item" href="/recursos">
                <Icon name="folder" /> {t(lang, "Recursos y descargas")}
              </Link>
              <Link className="next-item" href={`/cursos/${course.slug}`}>
                <Icon name="target" /> {t(lang, "Repaso y quizzes")}
              </Link>
            </div>
          </section>
        </aside>
      </div>
    </>
  );
}
