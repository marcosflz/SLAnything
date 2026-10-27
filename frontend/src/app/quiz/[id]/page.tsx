import Link from "next/link";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { AttemptList } from "@/components/quiz/AttemptList";
import { QuizForm } from "@/components/quiz/QuizForm";
import { Icon } from "@/components/ui";
import { ApiError, apiGet, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { QuizPayload } from "@/lib/types";

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

export default async function QuizPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<SearchParams>;
}) {
  const { id } = await params;
  const query = await searchParams;
  const pathname = `/quiz/${id}`;
  const shell = await getShell(pathname);

  let payload: QuizPayload;
  try {
    payload = await apiGet<QuizPayload>(`/api/v1/quiz/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const lang = shell.lang;
  const { quiz, attempts, best_attempt: bestAttempt } = payload;
  const attemptCount = attempts.length;

  return (
    <AppShell
      user={shell.user}
      course={payload.course}
      courses={payload.courses}
      progress={payload.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname={pathname}
      fullPath={buildFullPath(pathname, query)}
      title={quiz.title}
      kicker={t(lang, "Autoevaluación")}
    >
      <div className="quiz-layout">
        <nav className="breadcrumb" aria-label={t(lang, "Migas de pan")}>
          <Link href="/cursos">
            <Icon name="grid" /> {t(lang, "Cursos")}
          </Link>
          <span>/</span>
          <Link href={`/cursos/${payload.course.slug}`}>
            {payload.course.title}
          </Link>
          <span>/</span>
          <span>{quiz.title}</span>
        </nav>
        <header className="quiz-header">
          <span className="eyebrow-dark">
            <Icon name="trophy" />{" "}
            {t(lang, "Capítulo {n}", { n: payload.chapter.number })} ·{" "}
            {payload.chapter.title}
          </span>
          <h2>{quiz.title}</h2>
          <p>{quiz.description}</p>
          <div className="quiz-meta">
            <span>
              <Icon name="list" />{" "}
              {t(lang, "{n} preguntas", { n: quiz.total })}
            </span>
            <span>
              <Icon name="target" />{" "}
              {t(lang, "{pct} % para aprobar", { pct: quiz.pass_score })}
            </span>
            <span>
              <Icon name="refresh" /> {t(lang, "Intentos ilimitados")}
            </span>
          </div>
        </header>

        {bestAttempt ? (
          <div
            className={`callout callout-${
              bestAttempt.passed ? "success" : "info"
            }`}
          >
            <div className="callout-icon">
              {bestAttempt.passed ? "✓" : "i"}
            </div>
            <div className="callout-body">
              <strong className="callout-title">
                {t(lang, "Tu mejor resultado hasta ahora: {pct} %", {
                  pct: bestAttempt.percent,
                })}
              </strong>
              <div className="callout-text">
                {t(lang, "{score} de {total} correctas.", {
                  score: bestAttempt.score,
                  total: bestAttempt.total,
                })}{" "}
                {bestAttempt.passed
                  ? t(
                      lang,
                      "Ya has superado el quiz; puedes repetirlo para consolidar."
                    )
                  : t(
                      lang,
                      "Sigue practicando: cada intento te muestra qué repasar."
                    )}
              </div>
            </div>
          </div>
        ) : null}

        <QuizForm quiz={quiz} csrf={shell.user.csrf_token} lang={lang} />

        {attemptCount > 0 ? (
          <section className="card card-pad mt-4">
            <div className="card-head">
              <h3 className="card-title">
                <Icon name="clock" /> {t(lang, "Intentos anteriores")}
              </h3>
              <span className="small muted">
                {attemptCount === 1
                  ? t(lang, "{n} intento", { n: attemptCount })
                  : t(lang, "{n} intentos", { n: attemptCount })}
              </span>
            </div>
            <AttemptList attempts={attempts} lang={lang} />
          </section>
        ) : null}
      </div>
    </AppShell>
  );
}
