import Link from "next/link";

import { Badge, Icon, ProgressBar } from "@/components/ui";
import { t } from "@/lib/messages";
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
        <Badge tone="success">{t(lang, "Disponible")}</Badge>
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
            {t(lang, "Basado en")} <em>{course.book.title}</em> ·{" "}
            {course.book.author}
            {course.book.year ? ` (${course.book.year})` : ""}
          </p>
        ) : null}
        <div className="course-card-meta">
          <span>
            <Icon name="clock" /> {course.total_minutes} min
          </span>
          <span>
            <Icon name="sparkles" />{" "}
            {t(lang, "{n} laboratorios", { n: course.lab_count })}
          </span>
          <span>
            <Icon name="cpu" /> {course.level}
          </span>
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

export function ComingSoonCard({ lang }: { lang: Lang }) {
  return (
    <article className="course-card is-coming">
      <div className="course-card-cover">
        <span className="course-card-icon">
          <Icon name="sparkles" />
        </span>
        <Badge tone="neutral">{t(lang, "En preparación")}</Badge>
      </div>
      <div className="course-card-body">
        <span className="eyebrow-dark">{t(lang, "Nuevos cursos")}</span>
        <h3>{t(lang, "El próximo libro")}</h3>
        <p>
          {t(
            lang,
            "Estamos preparando nuevos recorridos. La plataforma ya está lista para incorporarlos sin cambiar la experiencia."
          )}
        </p>
        <div className="course-card-meta">
          <span>
            <Icon name="layers" /> {t(lang, "Mismo formato modular")}
          </span>
        </div>
      </div>
    </article>
  );
}
