import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { PublicShell } from "@/components/PublicShell";
import { ComingSoonCard, CourseCard } from "@/components/course/CourseCard";
import { Icon } from "@/components/ui";
import { apiGet, getCatalog, getLang, getSession, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { CatalogPayload } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: t(lang, "Cursos") };
}

async function CatalogBody({ showProgress }: { showProgress: boolean }) {
  const catalog = await apiGet<CatalogPayload>("/api/v1/catalog");
  const { lang, courses } = catalog;
  const countLabel =
    courses.length === 1
      ? t(lang, "1 curso disponible")
      : t(lang, "{n} cursos disponibles", { n: courses.length });

  return (
    <>
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="grid" /> {countLabel}
        </span>
        <h2>{t(lang, "Elige qué quieres aprender")}</h2>
        <p>
          {t(
            lang,
            "Cada curso es un recorrido modular con su propio temario, laboratorios, quizzes y progreso. Puedes entrar en cualquier momento y cambiar de curso sin perder lo avanzado."
          )}
        </p>
      </div>

      <div className="catalog-grid catalog-grid-wide">
        {courses.map((course) => (
          <CourseCard
            key={course.slug}
            course={course}
            lang={lang}
            showProgress={showProgress}
          />
        ))}
        <ComingSoonCard lang={lang} />
      </div>

      <section className="card card-pad mt-4">
        <div className="card-head">
          <h3 className="card-title">
            <Icon name="info" /> {t(lang, "Cómo se organiza la biblioteca")}
          </h3>
        </div>
        <div className="feature-grid">
          <div>
            <h3 style={{ fontSize: 14 }}>{t(lang, "Un curso, un libro")}</h3>
            <p className="small muted mb-0">
              {t(
                lang,
                "Cada curso parte de un libro y mantiene su propio temario, figuras, laboratorios y quizzes."
              )}
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: 14 }}>
              {t(lang, "Progreso independiente")}
            </h3>
            <p className="small muted mb-0">
              {t(
                lang,
                "Tus lecciones, apuntes, marcadores e intentos se guardan por curso. Cambiar de libro no mezcla tu avance."
              )}
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: 14 }}>{t(lang, "Misma experiencia")}</h3>
            <p className="small muted mb-0">
              {t(
                lang,
                "Todos los cursos comparten navegación, buscador, glosario y panel de progreso."
              )}
            </p>
          </div>
        </div>
      </section>
    </>
  );
}

export default async function CatalogPage() {
  const session = await getSession();

  if (!session.user) {
    const [catalog, lang] = await Promise.all([getCatalog(), getLang()]);
    return (
      <PublicShell site={catalog.site} lang={lang} fullPath="/cursos">
        <div className="public-page">
          <CatalogBody showProgress={false} />
        </div>
      </PublicShell>
    );
  }

  const [shell, catalog] = await Promise.all([
    getShell("/cursos"),
    apiGet<CatalogPayload>("/api/v1/catalog"),
  ]);

  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={shell.courses}
      progress={shell.progress}
      stats={shell.stats}
      site={shell.site}
      lang={shell.lang}
      pathname="/cursos"
      fullPath="/cursos"
      title={t(shell.lang, "Cursos")}
      kicker={t(shell.lang, "Biblioteca de cursos")}
    >
      <CatalogBody showProgress />
    </AppShell>
  );
}
