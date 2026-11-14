import { FolderOpen } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { EmptyState } from "@/components/charts/Kpi";
import { Icon } from "@/components/ui";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick, t } from "@/lib/messages";
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
          <Icon name="folder" /> {data.course?.title ?? t(lang, "Recursos")}
        </span>
        <h2>{pick(lang, "Material del curso", "Course material")}</h2>
        <p>
          {pick(
            lang,
            "Documentos de origen, descargas y ejemplos del curso activo. Cambia de curso en la biblioteca para ver los suyos.",
            "Source documents, downloads and examples for the active course. Switch course in the library to see its own."
          )}
        </p>
      </div>

      {data.resources.length ? (
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
      ) : (
        <EmptyState
          icon={FolderOpen}
          title={pick(lang, "Este curso no tiene recursos adicionales", "This course has no extra resources")}
          description={pick(
            lang,
            "Las lecciones, el cuestionario y el glosario ya contienen todo el material del curso.",
            "The lessons, quiz and glossary already contain all the course material."
          )}
        />
      )}

      {data.course ? (
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
              {data.source ? (
                <>
                  {" "}
                  {t(lang, "y está basado en")} <em>{data.source.title}</em>
                  {data.source.author ? ` · ${data.source.author}` : ""}
                  {data.source.year ? ` (${data.source.year})` : ""}
                </>
              ) : null}
              .{" "}
              {pick(
                lang,
                "Los derechos del material original pertenecen a sus autores; el curso solo lo reelabora como apoyo al estudio. No lo redistribuyas fuera de este contexto.",
                "Rights to the original material belong to its authors; the course only reworks it as a study aid. Do not redistribute it outside this context."
              )}
            </p>
            {data.course.is_sample ? (
              <p className="mb-0">
                {t(lang, "Los diagramas")} <code>fig_es_*.png</code>{" "}
                {t(lang, "son elaboración propia. El fragmento de")}{" "}
                <em>Don Quijote</em>{" "}
                {t(
                  lang,
                  "procede de Project Gutenberg y es de dominio público; se usa como corpus didáctico para el laboratorio de n-gramas."
                )}
              </p>
            ) : null}
          </div>
        </section>
      ) : null}
    </AppShell>
  );
}
