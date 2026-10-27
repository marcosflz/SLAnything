import Link from "next/link";

import { Icon, LessonStatus, Ring } from "@/components/ui";
import { t } from "@/lib/messages";
import type {
  Course,
  CourseSummary,
  Lang,
  LessonSummary,
  ProgressMap,
  Stats,
} from "@/lib/types";

export function CoursePageView({
  course,
  courses,
  progress,
  stats,
  nextLesson,
  lang,
  publicView = false,
}: {
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
  stats: Stats;
  nextLesson: LessonSummary | null;
  lang: Lang;
  publicView?: boolean;
}) {
  return (
    <>
      <nav className="breadcrumb" aria-label={t(lang, "Migas de pan")}>
        <Link href="/cursos">
          <Icon name="grid" /> {t(lang, "Cursos")}
        </Link>
        <span>/</span>
        <span>{course.title}</span>
      </nav>

      <section className="course-hero">
        <div>
          <span className="eyebrow">
            {t(lang, "{n} capítulos · {m} lecciones", {
              n: course.chapter_count,
              m: course.lesson_count,
            })}
          </span>
          <h2>{course.title}</h2>
          <p>{course.description}</p>
          {course.book ? (
            <p className="course-book course-book-hero">
              {t(lang, "Basado en")} <em>{course.book.title}</em> ·{" "}
              {course.book.author}
              {course.book.year ? ` (${course.book.year})` : ""}
            </p>
          ) : null}
          <div className="course-hero-meta">
            <span>
              <Icon name="layers" />{" "}
              {t(lang, "{n} capítulos", { n: course.chapter_count })}
            </span>
            <span>
              <Icon name="book" />{" "}
              {t(lang, "{n} lecciones", { n: course.lesson_count })}
            </span>
            <span>
              <Icon name="clock" />{" "}
              {t(lang, "{n} minutos", { n: course.total_minutes })}
            </span>
            <span>
              <Icon name="sparkles" />{" "}
              {t(lang, "{n} laboratorios", { n: course.lab_count })}
            </span>
            <span>
              <Icon name="cpu" /> {course.level}
            </span>
          </div>
          {publicView ? (
            <Link
              className="btn btn-primary mt-3"
              href={`/entrar?next=${encodeURIComponent(`/cursos/${course.slug}`)}`}
            >
              <Icon name="lock" /> {t(lang, "Inicia sesión para empezar")}
            </Link>
          ) : nextLesson ? (
            <Link className="btn btn-primary mt-3" href={`/leccion/${nextLesson.slug}`}>
              <Icon name="play" />{" "}
              {stats.completed ? t(lang, "Continuar") : t(lang, "Empezar")}:{" "}
              {nextLesson.title}
            </Link>
          ) : null}
        </div>
        <div className="course-progress-box">
          {publicView ? (
            <div className="course-public-note">
              <strong>{t(lang, "Acceso abierto")}</strong>
              <small>
                {t(
                  lang,
                  "Crea una cuenta para guardar tu progreso, apuntes y resultados."
                )}
              </small>
              <Link className="btn btn-primary btn-block mt-3" href="/registro">
                <Icon name="arrow-right" /> {t(lang, "Crear cuenta")}
              </Link>
            </div>
          ) : (
            <>
              <Ring value={stats.pct} size={104} label={t(lang, "completado")} />
              <div>
                <strong>
                  {t(lang, "{completed} / {total}", {
                    completed: stats.completed,
                    total: stats.total,
                  })}
                </strong>
                <small>{t(lang, "lecciones completadas")}</small>
                <div className="mt-2">
                  <Link
                    className="small"
                    href={`/progreso?course=${course.slug}`}
                    style={{ color: "#bfdbfe" }}
                  >
                    {t(lang, "Ver mi progreso →")}
                  </Link>
                </div>
              </div>
            </>
          )}
        </div>
      </section>

      <div
        className="row"
        id="programa"
        style={{ justifyContent: "space-between", marginBottom: 14 }}
      >
        <h3 style={{ fontSize: 18 }}>{t(lang, "Capítulos y lecciones")}</h3>
        <span className="small muted">
          {t(lang, "Marca cada lección al terminarla para avanzar")}
        </span>
      </div>

      {course.chapters.map((chapter) => {
        const chapterDone = chapter.lessons.filter(
          (lesson) => progress[lesson.slug]?.completed
        ).length;
        return (
          <section
            className="chapter-section"
            id={`capitulo-${chapter.number}`}
            key={chapter.slug}
          >
            <header className="chapter-head">
              <div>
                <span className="eyebrow">
                  {t(lang, "Capítulo {n}", { n: chapter.number })}
                </span>
                <h3>{chapter.title}</h3>
                <p>{chapter.subtitle}</p>
              </div>
              <div className="chapter-meta">
                <span>
                  <Icon name="book" />{" "}
                  {t(lang, "{n} lecciones", { n: chapter.lesson_count })}
                </span>
                <span>
                  <Icon name="clock" /> {chapter.total_minutes} min
                </span>
                <span>
                  <Icon name="check-circle" /> {chapterDone}/
                  {chapter.lesson_count}
                </span>
              </div>
            </header>

            <div className="module-list">
              {chapter.lessons.map((lesson) => {
                const row = progress[lesson.slug];
                const isNext = nextLesson?.slug === lesson.slug;
                const classes = [
                  "lesson-row",
                  row?.completed ? "is-done" : "",
                  isNext ? "is-active" : "",
                ]
                  .filter(Boolean)
                  .join(" ");
                const lessonHref = publicView
                  ? `/entrar?next=${encodeURIComponent(`/leccion/${lesson.slug}`)}`
                  : `/leccion/${lesson.slug}`;

                return (
                  <article key={lesson.slug} className={classes}>
                    <div className="lesson-num">
                      {row?.completed ? (
                        <Icon name="check" />
                      ) : (
                        String(lesson.number).padStart(2, "0")
                      )}
                    </div>
                    <div className="lesson-info">
                      <h3>
                        <Link href={lessonHref} style={{ color: "inherit" }}>
                          {lesson.title}
                        </Link>
                      </h3>
                      <p>{lesson.summary}</p>
                      <div className="lesson-info-meta">
                        <span>
                          <Icon name="clock" /> {lesson.minutes} min
                        </span>
                        <span>
                          <Icon name="target" />{" "}
                          {t(lang, "{n} objetivos", {
                            n: lesson.objectives.length,
                          })}
                        </span>
                        {lesson.labs.length ? (
                          <span>
                            <Icon name="sparkles" />{" "}
                            {t(
                              lang,
                              lesson.labs.length === 1
                                ? "{n} laboratorio"
                                : "{n} laboratorios",
                              { n: lesson.labs.length }
                            )}
                          </span>
                        ) : null}
                        {lesson.quiz_id ? (
                          <span>
                            <Icon name="trophy" /> {t(lang, "Quiz")}
                          </span>
                        ) : null}
                      </div>
                    </div>
                    <div className="row">
                      {publicView ? (
                        <>
                          <span className="lesson-state">
                            {t(lang, "Inicia sesión")}
                          </span>
                          <Link
                            className="btn btn-secondary btn-sm"
                            href={lessonHref}
                          >
                            <Icon name="lock" /> {t(lang, "Abrir")}
                          </Link>
                        </>
                      ) : (
                        <>
                          <LessonStatus
                            progress={row ?? null}
                            completedLabel={t(lang, "Completada")}
                            progressLabel={t(lang, "En curso")}
                            pendingLabel={t(lang, "Pendiente")}
                          />
                          <Link
                            className="btn btn-secondary btn-sm"
                            href={lessonHref}
                          >
                            <Icon name="arrow-right" />{" "}
                            {row?.completed
                              ? t(lang, "Repasar")
                              : t(lang, "Entrar a la lección")}
                          </Link>
                        </>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        );
      })}

      <section className="card card-pad mt-4">
        <div className="card-head">
          <h3 className="card-title">
            <Icon name="info" /> {t(lang, "Cómo aprovechar el curso")}
          </h3>
        </div>
        <div className="feature-grid">
          <div>
            <h3 style={{ fontSize: 14 }}>{t(lang, "1 · Lee y predice")}</h3>
            <p className="small muted mb-0">
              {t(
                lang,
                "Antes de seguir, intenta anticipar la respuesta. El cerebro aprende más cuando se equivoca y corrige."
              )}
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: 14 }}>
              {t(lang, "2 · Toca los laboratorios")}
            </h3>
            <p className="small muted mb-0">
              {t(
                lang,
                "Mueve la temperatura, cambia el contexto, prueba otra precisión. Cada control enseña algo."
              )}
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: 14 }}>{t(lang, "3 · Cierra con el quiz")}</h3>
            <p className="small muted mb-0">
              {t(
                lang,
                "El quiz no es un examen: es una forma de detectar qué idea necesita otra pasada."
              )}
            </p>
          </div>
        </div>
      </section>

      {courses.length > 1 ? (
        <section className="card card-pad mt-4">
          <div className="card-head">
            <h3 className="card-title">
              <Icon name="grid" /> {t(lang, "Otros cursos")}
            </h3>
            <Link className="small" href="/cursos">
              {t(lang, "Ver catálogo →")}
            </Link>
          </div>
          <div className="course-strip">
            {courses
              .filter((item) => item.slug !== course.slug)
              .map((item) => (
                <Link
                  className="course-strip-item"
                  href={`/cursos/${item.slug}`}
                  key={item.slug}
                >
                  <span className="course-strip-icon">
                    <Icon name="book" />
                  </span>
                  <span className="course-strip-body">
                    <strong>{item.title}</strong>
                    <small>{item.subtitle}</small>
                  </span>
                </Link>
              ))}
          </div>
        </section>
      ) : null}
    </>
  );
}
