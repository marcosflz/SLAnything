import { Library } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { PublicShell } from "@/components/PublicShell";
import { EmptyState } from "@/components/charts/Kpi";
import { CourseCard } from "@/components/course/CourseCard";
import { Icon } from "@/components/ui";
import { apiGet, getCatalog, getLang, getSession, getShell } from "@/lib/api";
import { pick, t } from "@/lib/messages";
import type { CatalogPayload, CourseSummary, Lang, User } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: t(lang, "Cursos") };
}

function CourseGrid({
  title,
  courses,
  lang,
  showProgress,
}: {
  title?: string;
  courses: CourseSummary[];
  lang: Lang;
  showProgress: boolean;
}) {
  if (!courses.length) return null;
  return (
    <section className="mb-6">
      {title ? <h3 className="mb-3 text-sm font-semibold tracking-wide text-muted-foreground uppercase">{title}</h3> : null}
      <div className="catalog-grid catalog-grid-wide">
        {courses.map((course) => (
          <CourseCard key={course.slug} course={course} lang={lang} showProgress={showProgress} />
        ))}
      </div>
    </section>
  );
}

async function CatalogBody({ user }: { user: User | null }) {
  const catalog = await apiGet<CatalogPayload>("/api/v1/catalog");
  const { lang, courses } = catalog;
  const showProgress = Boolean(user);
  const countLabel =
    courses.length === 1
      ? t(lang, "1 curso disponible")
      : t(lang, "{n} cursos disponibles", { n: courses.length });
  const assigned = courses.filter((course) => course.assigned);
  const samples = courses.filter((course) => !course.assigned && course.is_sample);
  const rest = courses.filter((course) => !course.assigned && !course.is_sample);
  const grouped = assigned.length > 0 || samples.length > 0;

  return (
    <>
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="grid" /> {countLabel}
        </span>
        <h2>{t(lang, "Elige qué quieres aprender")}</h2>
        <p>
          {user
            ? pick(
                lang,
                "Los cursos de tu espacio, los que comparte la plataforma en abierto y, si están activados, los cursos de ejemplo. Cada uno guarda su propio progreso.",
                "Courses in your space, those the platform shares openly and, if enabled, the sample courses. Each one keeps its own progress."
              )
            : pick(
                lang,
                "Cursos abiertos de la plataforma. Crea una cuenta para generar los tuyos a partir de cualquier documento.",
                "Open courses on the platform. Create an account to generate your own from any document."
              )}
        </p>
      </div>

      {courses.length === 0 ? (
        <EmptyState
          icon={Library}
          title={pick(lang, "La biblioteca está vacía", "The library is empty")}
          description={
            user?.permissions?.author
              ? pick(
                  lang,
                  "Sube un documento al Estudio: en unos minutos tendrás tu primera unidad con lecciones, cuestionario y glosario.",
                  "Upload a document to the Studio: in a few minutes you will have your first unit with lessons, quiz and glossary."
                )
              : user
                ? pick(
                    lang,
                    "Tu academia aún no ha publicado cursos. Aparecerán aquí en cuanto lo haga.",
                    "Your academy has not published courses yet. They will appear here as soon as it does."
                  )
                : pick(
                    lang,
                    "Todavía no hay cursos abiertos. Crea una cuenta y genera el tuyo.",
                    "There are no open courses yet. Create an account and generate yours."
                  )
          }
          action={
            user?.permissions?.author ? (
              <Link className="btn btn-primary" href="/estudio">
                <Icon name="sparkles" /> {pick(lang, "Abrir el Estudio", "Open the Studio")}
              </Link>
            ) : !user ? (
              <Link className="btn btn-primary" href="/registro">
                <Icon name="arrow-right" /> {pick(lang, "Crear cuenta", "Create account")}
              </Link>
            ) : null
          }
        />
      ) : (
        <>
          <CourseGrid
            title={assigned.length ? pick(lang, "Asignados por tu academia", "Assigned by your academy") : undefined}
            courses={assigned}
            lang={lang}
            showProgress={showProgress}
          />
          <CourseGrid
            title={grouped && rest.length ? pick(lang, "Más cursos", "More courses") : undefined}
            courses={rest}
            lang={lang}
            showProgress={showProgress}
          />
          <CourseGrid
            title={samples.length ? pick(lang, "Cursos de ejemplo", "Sample courses") : undefined}
            courses={samples}
            lang={lang}
            showProgress={showProgress}
          />
        </>
      )}
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
          <CatalogBody user={null} />
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
      <CatalogBody user={shell.user} />
    </AppShell>
  );
}
