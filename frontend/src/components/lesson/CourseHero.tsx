import Link from "next/link";

import { Icon, Ring } from "@/components/ui";
import { t } from "@/lib/messages";
import type { Course, Lang, LessonSummary, Stats } from "@/lib/types";

export function CourseHero({
  course,
  stats,
  nextLesson,
  chapter,
  lang,
}: {
  course: Course;
  stats: Stats;
  nextLesson: LessonSummary | null;
  chapter: string;
  lang: Lang;
}) {
  return (
    <section className="course-hero">
      <div>
        <span className="eyebrow">{chapter}</span>
        <h2>{course.title}</h2>
        <p>{course.description}</p>
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
        {nextLesson ? (
          <Link className="btn btn-primary mt-3" href={`/leccion/${nextLesson.slug}`}>
            <Icon name="play" />{" "}
            {stats.completed ? t(lang, "Continuar") : t(lang, "Empezar")}:{" "}
            {nextLesson.title}
          </Link>
        ) : null}
      </div>
      <div className="course-progress-box">
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
            <Link className="small" href="/progreso" style={{ color: "#bfdbfe" }}>
              {t(lang, "Ver mi progreso →")}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
