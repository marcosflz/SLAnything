import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { Icon } from "@/components/ui";
import { apiGet, getLang, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { SearchPayload } from "@/lib/types";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}): Promise<Metadata> {
  const { q = "" } = await searchParams;
  const query = q.trim();
  const lang = await getLang();
  return {
    title: query
      ? t(lang, "Buscar: {query}", { query })
      : t(lang, "Buscar"),
  };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const shell = await getShell("/buscar");
  const data = await apiGet<SearchPayload>(
    `/api/v1/search?q=${encodeURIComponent(q)}`
  );
  const { lang } = shell;
  const query = data.query;
  const fullPath = `/buscar${q ? `?q=${encodeURIComponent(q)}` : ""}`;

  return (
    <AppShell
      user={shell.user}
      course={data.course}
      courses={data.courses}
      progress={data.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname="/buscar"
      fullPath={fullPath}
      query={query}
      title={t(lang, "Buscar en el curso")}
      kicker={t(lang, "Buscador")}
    >
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="search" /> {t(lang, "Curso completo")}
        </span>
        <h2>
          {query
            ? t(lang, "Resultados para “{query}”", { query })
            : t(lang, "¿Qué quieres encontrar?")}
        </h2>
        <p>
          {t(
            lang,
            "Busca una idea, una sigla o un concepto. El buscador recorre títulos, resúmenes y el texto completo de las lecciones."
          )}
        </p>
      </div>

      <form
        className="search-box"
        method="get"
        action="/buscar"
        role="search"
        style={{ maxWidth: 680 }}
      >
        <Icon name="search" />
        <label className="sr-only" htmlFor="buscar-q">
          {t(lang, "Buscar")}
        </label>
        <input
          id="buscar-q"
          type="search"
          name="q"
          defaultValue={query}
          placeholder={t(
            lang,
            "Por ejemplo: atención, temperatura, pretraining…"
          )}
          autoFocus
        />
        <button className="btn btn-primary btn-sm" type="submit">
          {t(lang, "Buscar")}
        </button>
      </form>

      {query && data.results.length ? (
        <>
          <p className="small muted">
            {data.results.length === 1
              ? t(lang, "{n} resultado", { n: data.results.length })
              : t(lang, "{n} resultados", { n: data.results.length })}
            .
          </p>
          <div className="module-list">
            {data.results.map((result) => (
              <Link
                key={result.lesson.slug}
                className="lesson-row"
                href={`/leccion/${result.lesson.slug}`}
                prefetch={false}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div className="lesson-num">
                  {String(result.lesson.number).padStart(2, "0")}
                </div>
                <div className="lesson-info">
                  <h3>{result.lesson.title}</h3>
                  <p style={{ whiteSpace: "normal", color: "var(--muted)" }}>
                    {result.snippet}
                  </p>
                  <div className="lesson-info-meta">
                    <span>
                      <Icon name="clock" /> {result.lesson.minutes} min
                    </span>
                    <span>
                      <Icon name="grid" />{" "}
                      {result.lesson.course_title ?? data.course.title}
                    </span>
                    <span>
                      <Icon name="book" />{" "}
                      {t(lang, "Lección {n}", {
                        n: result.lesson.number,
                      })}
                    </span>
                  </div>
                </div>
                <span className="btn btn-secondary btn-sm">
                  <Icon name="arrow-right" /> {t(lang, "Abrir")}
                </span>
              </Link>
            ))}
          </div>
        </>
      ) : query ? (
        <div className="empty-search">
          <h3 style={{ marginBottom: 6 }}>{t(lang, "Sin resultados")}</h3>
          <p className="mb-0">
            {t(
              lang,
              "Prueba con una palabra más general, por ejemplo “token”, “atención” o “datos”."
            )}
          </p>
        </div>
      ) : (
        <div className="empty-search">
          <h3 style={{ marginBottom: 6 }}>{t(lang, "Empieza a escribir")}</h3>
          <p className="mb-0">
            {t(
              lang,
              "El buscador está disponible también con la tecla"
            )}{" "}
            <kbd>/</kbd> {t(lang, "desde cualquier página.")}
          </p>
        </div>
      )}
    </AppShell>
  );
}
