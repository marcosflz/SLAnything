import Link from "next/link";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { BlockRenderer } from "@/components/BlockRenderer";
import { LessonAside } from "@/components/lesson/LessonAside";
import { Badge, Icon } from "@/components/ui";
import { ApiError, apiGet, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { LessonPayload } from "@/lib/types";

type SearchParams = Record<string, string | string[] | undefined>;

function withQuery(pathname: string, params: SearchParams): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      for (const item of value) search.append(key, item);
    } else if (value !== undefined) {
      search.set(key, value);
    }
  }
  const serialized = search.toString();
  return serialized ? `${pathname}?${serialized}` : pathname;
}

export default async function LessonPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<SearchParams>;
}) {
  const { slug } = await params;
  const shell = await getShell(`/leccion/${slug}`);
  const data = await apiGet<LessonPayload>(
    `/api/v1/lessons/${slug}`
  ).catch((error: unknown) => {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  });

  const search = await searchParams;
  const lang = shell.lang;
  const lesson = data.lesson;
  const chapter = data.chapter;
  const pathname = `/leccion/${slug}`;
  const query = typeof search.q === "string" ? search.q : "";
  const completedCount = chapter.lessons.filter(
    (item) => data.all_progress[item.slug]?.completed
  ).length;
  const courseCompleted = Object.values(data.all_progress).filter(
    (row) => row.completed
  ).length;

  return (
    <AppShell
      user={shell.user}
      course={data.course}
      courses={data.courses}
      progress={data.all_progress}
      stats={data.stats}
      site={shell.site}
      lang={lang}
      pathname={pathname}
      fullPath={withQuery(pathname, search)}
      query={query}
      title={lesson.title}
      kicker={t(lang, "Lección {n} de {total}", {
        n: lesson.number,
        total: chapter.lesson_count,
      })}
    >
      <nav className="breadcrumb" aria-label={t(lang, "Migas de pan")}>
        <Link href="/cursos">
          <Icon name="grid" /> {t(lang, "Cursos")}
        </Link>
        <span>/</span>
        <Link href={`/cursos/${data.course.slug}`}>{data.course.title}</Link>
        <span>/</span>
        <span>{lesson.title}</span>
      </nav>
      <div className="lesson-layout">
        <article className="lesson-main">
          <header className="lesson-header">
            <span className="eyebrow-dark">
              <Icon name="book" />{" "}
              {t(lang, "Capítulo {n}", { n: chapter.number })} ·{" "}
              {chapter.title}
            </span>
            <h2>{lesson.title}</h2>
            <p>{lesson.summary}</p>
            <div className="lesson-header-meta">
              <span>
                <Icon name="clock" />{" "}
                {t(lang, "{n} minutos", { n: lesson.minutes })}
              </span>
              <span>
                <Icon name="target" />{" "}
                {t(lang, "{n} objetivos", { n: lesson.objectives.length })}
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
              {data.progress?.completed ? (
                <span style={{ color: "var(--success)" }}>
                  <Icon name="check-circle" /> {t(lang, "Completada")}
                </span>
              ) : null}
            </div>
            {lesson.python_blocks.length ? (
              <a
                className="btn btn-secondary btn-sm"
                href={`/api/v1/downloads/lessons/${lesson.slug}/code`}
              >
                <Icon name="download" />{" "}
                {t(lang, "Descargar los ejemplos de esta lección (.py)")}
              </a>
            ) : null}
          </header>

          <section
            className="objectives"
            aria-label={t(lang, "Objetivos de la lección")}
          >
            <h3>{t(lang, "Al terminar sabrás…")}</h3>
            <ul>
              {lesson.objectives.map((objective, position) => (
                <li key={position}>{objective}</li>
              ))}
            </ul>
          </section>

          <div className="prose">
            {lesson.blocks.map((block, position) => (
              <BlockRenderer
                key={position}
                block={block}
                index={position + 1}
                lessonSlug={lesson.slug}
                labMeta={data.lab_meta}
                csrf={shell.user.csrf_token}
                lang={lang}
              />
            ))}
          </div>

          {data.quiz ? (
            <section className="card card-pad mt-4">
              <div className="card-head">
                <h3 className="card-title">
                  <Icon name="trophy" /> {t(lang, "Comprueba lo aprendido")}
                </h3>
                {data.best_attempt ? (
                  <Badge
                    tone={
                      data.best_attempt.percent >= data.quiz.pass_score
                        ? "success"
                        : "warning"
                    }
                  >
                    {data.best_attempt.percent} % · {t(lang, "mejor intento")}
                  </Badge>
                ) : null}
              </div>
              <p className="small muted">{data.quiz.description}</p>
              <div className="row">
                <Link
                  className="btn btn-primary"
                  href={`/quiz/${data.quiz.id}`}
                >
                  <Icon name="play" />{" "}
                  {data.best_attempt
                    ? t(lang, "Repetir quiz")
                    : t(lang, "Empezar quiz")}
                </Link>
                <span className="small muted">
                  {t(
                    lang,
                    "{n} preguntas · necesitas {pct} % para aprobar",
                    { n: data.quiz.total, pct: data.quiz.pass_score }
                  )}
                </span>
              </div>
            </section>
          ) : null}

          <nav
            className="lesson-nav"
            aria-label={t(lang, "Navegación entre lecciones")}
          >
            {data.prev_lesson ? (
              <Link
                className="lesson-nav-link"
                href={`/leccion/${data.prev_lesson.slug}`}
              >
                <small>{t(lang, "← Anterior")}</small>
                <strong>{data.prev_lesson.title}</strong>
              </Link>
            ) : (
              <span />
            )}
            {data.next_lesson ? (
              <Link
                className="lesson-nav-link next"
                href={`/leccion/${data.next_lesson.slug}`}
              >
                <small>{t(lang, "Siguiente →")}</small>
                <strong>{data.next_lesson.title}</strong>
              </Link>
            ) : (
              <Link
                className="lesson-nav-link next"
                href={`/cursos/${data.course.slug}`}
              >
                <small>{t(lang, "Fin del curso")}</small>
                <strong>{t(lang, "Volver al curso")}</strong>
              </Link>
            )}
          </nav>
        </article>

        <LessonAside
          slug={lesson.slug}
          lessonNumber={lesson.number}
          chapterTotal={chapter.lesson_count}
          courseTotal={data.course.lesson_count}
          courseCompleted={courseCompleted}
          progress={data.progress}
          completedCount={completedCount}
          note={data.note}
          bookmarked={data.bookmarked}
          quiz={data.quiz}
          bestAttempt={data.best_attempt}
          csrf={shell.user.csrf_token}
          lang={lang}
        />
      </div>
    </AppShell>
  );
}
