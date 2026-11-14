import Link from "next/link";

import { Badge, Icon, ProgressBar } from "@/components/ui";
import { formatDate } from "@/lib/utils";
import { pick, t } from "@/lib/messages";
import type { CourseSummary, Lang } from "@/lib/types";

export function CourseCard({
  course,
  lang,
  href,
  showProgress = false,
}: {
  course: CourseSummary;
  lang: Lang;
  href?: string;
  showProgress?: boolean;
}) {
  const target = href ?? `/cursos/${course.slug}`;
  const started = course.stats.completed > 0;

  return (
    <article className={`course-card accent-${course.accent}`}>
      <div className="course-card-cover">
        <span className="course-card-icon">
          <Icon name="book" />
        </span>
        {course.assigned ? (
          <Badge tone="warning">
            {course.due_at
              ? pick(lang, "Asignado · {d}", "Assigned · {d}").replace("{d}", formatDate(course.due_at, lang))
              : pick(lang, "Asignado", "Assigned")}
          </Badge>
        ) : course.is_sample ? (
          <Badge tone="neutral">{pick(lang, "Curso de ejemplo", "Sample course")}</Badge>
        ) : (
          <Badge tone="success">{t(lang, "Disponible")}</Badge>
        )}
      </div>
      <div className="course-card-body">
        <span className="eyebrow-dark">
          {t(lang, "{n} capítulos · {m} lecciones", {
            n: course.chapter_count,
            m: course.lesson_count,
          })}
        </span>
        <h3>{course.title}</h3>
        <p>{course.subtitle}</p>
        {course.book ? (
          <p className="course-book">
            {pick(lang, "Fuente", "Source")}: <em>{course.book.title}</em>
            {course.book.author ? ` · ${course.book.author}` : ""}
            {course.book.year ? ` (${course.book.year})` : ""}
          </p>
        ) : null}
        <div className="course-card-meta">
          <span>
            <Icon name="clock" /> {course.total_minutes} min
          </span>
          {course.lab_count ? (
            <span>
              <Icon name="sparkles" />{" "}
              {t(lang, "{n} laboratorios", { n: course.lab_count })}
            </span>
          ) : null}
          {course.level ? (
            <span>
              <Icon name="target" /> {course.level}
            </span>
          ) : null}
        </div>

        {showProgress ? (
          <div className="course-card-progress">
            <div className="row" style={{ justifyContent: "space-between" }}>
              <span className="small muted">
                {t(lang, "{completed} de {total} lecciones", {
                  completed: course.stats.completed,
                  total: course.stats.total,
                })}
              </span>
              <strong className="small">{course.stats.pct} %</strong>
            </div>
            <ProgressBar
              value={course.stats.pct}
              label={t(lang, "Progreso del curso")}
              tone="success"
            />
          </div>
        ) : null}

        <Link className="btn btn-primary btn-block" href={target}>
          <Icon name={started ? "play" : "arrow-right"} />{" "}
          {showProgress
            ? started
              ? t(lang, "Continuar curso")
              : t(lang, "Empezar curso")
            : t(lang, "Ver el curso")}
        </Link>
      </div>
    </article>
  );
}
