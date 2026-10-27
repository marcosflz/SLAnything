import Link from "next/link";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { Icon } from "@/components/ui";
import { ApiError, apiGet, getShell } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { t } from "@/lib/messages";
import type { AttemptReviewPayload } from "@/lib/types";

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

export default async function QuizAttemptPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<SearchParams>;
}) {
  const { id } = await params;
  const query = await searchParams;
  const pathname = `/quiz/intento/${id}`;
  const shell = await getShell(pathname);

  let payload: AttemptReviewPayload;
  try {
    payload = await apiGet<AttemptReviewPayload>(
      `/api/v1/quiz/attempts/${id}`
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const lang = shell.lang;
  const { quiz, attempt, review } = payload;
  const percent = attempt.percent;
  const passed = attempt.passed;
  const date = formatDate(attempt.created_at, lang);
  const summary = passed
    ? t(
        lang,
        "{score} de {total} respuestas correctas · {date}. Puedes seguir con el siguiente capítulo del programa.",
        { score: attempt.score, total: attempt.total, date }
      )
    : t(
        lang,
        "{score} de {total} respuestas correctas · {date}. Repasa las explicaciones y vuelve a intentarlo: no hay límite de intentos.",
        { score: attempt.score, total: attempt.total, date }
      );

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
      title={t(lang, "Resultado del quiz")}
      kicker={t(lang, "Revisión del intento")}
    >
      <div className="quiz-layout">
        <section className={`result-banner ${passed ? "is-pass" : "is-fail"}`}>
          <div className="result-score">
            {percent}
            <small>%</small>
          </div>
          <div style={{ flex: 1, minWidth: 220 }}>
            <h2>
              {passed
                ? t(lang, "¡Capítulo superado!")
                : t(lang, "Todavía no, pero vas por buen camino")}
            </h2>
            <p>{summary}</p>
          </div>
          <div className="row">
            <Link className="btn btn-primary" href={`/quiz/${quiz.id}`}>
              <Icon name="refresh" /> {t(lang, "Repetir quiz")}
            </Link>
            <Link
              className="btn btn-secondary"
              href={`/cursos/${payload.course.slug}`}
              style={{
                background: "rgba(255,255,255,.12)",
                borderColor: "rgba(255,255,255,.25)",
                color: "#fff",
              }}
            >
              <Icon name="book" /> {t(lang, "Volver al curso")}
            </Link>
          </div>
        </section>

        <div
          className="card card-pad mb-3"
          style={{
            display: "flex",
            gap: 14,
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <div style={{ flex: 1 }}>
            <strong style={{ fontSize: 14 }}>
              {t(lang, "Revisión pregunta a pregunta")}
            </strong>
            <p className="small muted mb-0">
              {t(
                lang,
                "Cada explicación te dice por qué la respuesta correcta lo es. Úsala para volver a la lección correspondiente."
              )}
            </p>
          </div>
          <Link className="btn btn-secondary btn-sm" href="/progreso">
            <Icon name="chart" /> {t(lang, "Mi progreso")}
          </Link>
        </div>

        <div className="result-list">
          {review.map((item) => (
            <article
              className={`result-item ${
                item.is_correct ? "is-correct" : "is-wrong"
              }`}
              key={item.number}
            >
              <div className="result-item-head">
                <Icon
                  name={item.is_correct ? "check-circle" : "x-circle"}
                />
                <span>
                  <strong>{item.number}.</strong> {item.question}
                </span>
              </div>
              <div className="result-answer">
                {item.selected === null ? (
                  <span style={{ color: "var(--warning)" }}>
                    {t(lang, "Sin responder.")}
                  </span>
                ) : (
                  <>
                    {t(lang, "Tu respuesta:")}{" "}
                    <strong>{item.selected_text}</strong>
                  </>
                )}
                {item.is_correct ? null : (
                  <>
                    <br />
                    {t(lang, "Respuesta correcta:")}{" "}
                    <strong>{item.correct_text}</strong>
                  </>
                )}
              </div>
              <div className="result-explanation">{item.explanation}</div>
            </article>
          ))}
        </div>

        <div className="quiz-actions">
          <Link className="btn btn-primary" href={`/quiz/${quiz.id}`}>
            <Icon name="refresh" /> {t(lang, "Intentar de nuevo")}
          </Link>
          <Link
            className="btn btn-secondary"
            href={`/cursos/${payload.course.slug}`}
          >
            <Icon name="book" /> {t(lang, "Volver al programa")}
          </Link>
          <Link className="btn btn-ghost" href="/progreso">
            <Icon name="chart" /> {t(lang, "Ver evolución")}
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
