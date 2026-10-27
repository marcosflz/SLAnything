import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { Icon } from "@/components/ui";
import { apiGet, getLang, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { Lang, ResourceItem, ResourcesPayload } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: t(lang, "Recursos") };
}

function ResourceAction({ item, lang }: { item: ResourceItem; lang: Lang }) {
  const rootRelative = item.href.startsWith("/");
  const content = (
    <>
      <Icon name={rootRelative ? "download" : "external"} /> {t(lang, "Abrir")}
    </>
  );

  if (item.href.startsWith("http")) {
    return (
      <a
        className="btn btn-secondary"
        href={item.href}
        target="_blank"
        rel="noopener"
      >
        {content}
      </a>
    );
  }

  if (item.href.startsWith("/api/") || item.href.startsWith("/static/")) {
    return (
      <a className="btn btn-secondary" href={item.href}>
        {content}
      </a>
    );
  }

  return (
    <Link className="btn btn-secondary" href={item.href}>
      {content}
    </Link>
  );
}

export default async function ResourcesPage() {
  const shell = await getShell("/recursos");
  const data = await apiGet<ResourcesPayload>("/api/v1/resources");
  const { lang } = shell;

  return (
    <AppShell
      user={shell.user}
      course={data.course}
      courses={data.courses}
      progress={data.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname="/recursos"
      fullPath="/recursos"
      title={t(lang, "Recursos")}
      kicker={t(lang, "Material de apoyo")}
    >
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="folder" /> {t(lang, "Curso completo")}
        </span>
        <h2>{t(lang, "Para seguir explorando")}</h2>
        <p>
          {t(
            lang,
            "Descargas, datos y material complementario. Todo lo que necesitas para reproducir las demos o profundizar."
          )}
        </p>
      </div>

      <div className="resource-grid">
        {data.resources.map((item) => (
          <article className="resource-card" key={`${item.title}-${item.href}`}>
            <span className="resource-icon">
              <Icon name={item.icon || "folder"} />
            </span>
            <div style={{ minWidth: 0 }}>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <div className="row">
                <ResourceAction item={item} lang={lang} />
                {item.meta ? (
                  <span className="small muted">{item.meta}</span>
                ) : null}
              </div>
            </div>
          </article>
        ))}
      </div>

      <section className="card card-pad mt-4" id="creditos">
        <div className="card-head">
          <h3 className="card-title">
            <Icon name="shield" /> {t(lang, "Créditos y licencias")}
          </h3>
        </div>
        <div className="prose" style={{ maxWidth: "none", fontSize: "13.5px" }}>
          <p>
            {t(lang, "Este material es de")}{" "}
            <strong>{t(lang, "uso educativo personal")}</strong>
            {data.course.book ? (
              <>
                {" "}
                {t(lang, "y está basado en")}{" "}
                <em>{data.course.book.title}</em> ·{" "}
                {data.course.book.author}
                {data.course.book.year ? ` (${data.course.book.year})` : ""}
              </>
            ) : null}
            .{" "}
            {t(
              lang,
              "Las figuras y marcas pertenecen a sus autores y editoriales; se incluyen únicamente como apoyo al estudio. No las redistribuyas fuera de este contexto."
            )}
          </p>
          <p>
            {t(lang, "Los diagramas")} <code>fig_es_*.png</code>{" "}
            {t(lang, "son elaboración propia. El fragmento de")}{" "}
            <em>Don Quijote</em>{" "}
            {t(
              lang,
              "procede de Project Gutenberg y es de dominio público; se usa como corpus didáctico para el laboratorio de n-gramas."
            )}
          </p>
          <p className="mb-0">
            {t(
              lang,
              "Las estimaciones de tokens, memoria y coste son aproximadas y de orden de magnitud. No sustituyen una medición sobre hardware real."
            )}
          </p>
        </div>
      </section>
    </AppShell>
  );
}
