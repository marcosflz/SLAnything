import Link from "next/link";

import type {
  Course,
  CourseSummary,
  Lang,
  ProgressMap,
  Site,
  Stats,
  User,
} from "@/lib/types";
import { t } from "@/lib/messages";
import { Icon } from "./ui";
import { ThemeToggle } from "./ThemeToggle";
import { LogoutButton } from "./LogoutButton";
import { SearchShortcut } from "./SearchShortcut";
import { ReadingProgress } from "./ReadingProgress";
import { SidebarController } from "./SidebarController";
import { Lightbox } from "./Lightbox";

function active(current: string, prefix: string) {
  if (prefix === "/") return current === "/";
  return current === prefix || current.startsWith(`${prefix}/`);
}

export function AppShell({
  user,
  course,
  courses,
  progress,
  site,
  lang,
  pathname,
  fullPath,
  query = "",
  title,
  kicker,
  children,
}: {
  user: User;
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
  stats: Stats;
  site: Site;
  lang: Lang;
  pathname: string;
  fullPath: string;
  query?: string;
  title: string;
  kicker: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <a className="skip-link" href="#contenido">
        {t(lang, "Saltar al contenido")}
      </a>
      <div className="app-shell">
        <aside className="sidebar" id="sidebar" aria-label={t(lang, "Navegación del curso")}>
          <div className="sidebar-head">
            <Link className="brand" href="/">
              <span className="brand-mark">λ</span>
              <span className="brand-text">
                <strong>{site.name}</strong>
                <small>{t(lang, "De cero a GPT")}</small>
              </span>
            </Link>
            <button
              className="icon-btn sidebar-close"
              type="button"
              data-sidebar-close
              aria-label={t(lang, "Cerrar menú")}
            >
              <Icon name="x" />
            </button>
          </div>

          <div className="sidebar-course">
            <span className="eyebrow">
              {t(lang, "{n} capítulos", { n: course.chapter_count })}
            </span>
            <Link href={`/cursos/${course.slug}`} className="sidebar-course-title">
              {course.title}
            </Link>
            <div className="sidebar-meta">
              <span>
                <Icon name="book" />{" "}
                {t(lang, "{n} lecciones", { n: course.lesson_count })}
              </span>
              <span>
                <Icon name="clock" /> {course.total_minutes} min
              </span>
            </div>
          </div>

          <nav className="sidebar-nav">
            <Link href="/" className={`side-link ${active(pathname, "/") ? "is-active" : ""}`}>
              <Icon name="home" /> {t(lang, "Inicio")}
            </Link>
            <Link
              href="/cursos"
              className={`side-link ${active(pathname, "/cursos") ? "is-active" : ""}`}
            >
              <Icon name="grid" /> {t(lang, "Cursos")}
              {courses.length > 1 ? (
                <span className="side-link-count">{courses.length}</span>
              ) : null}
            </Link>
            <Link
              href="/progreso"
              className={`side-link ${active(pathname, "/progreso") ? "is-active" : ""}`}
            >
              <Icon name="chart" /> {t(lang, "Mi progreso")}
            </Link>
            <Link
              href="/glosario"
              className={`side-link ${active(pathname, "/glosario") ? "is-active" : ""}`}
            >
              <Icon name="glossary" /> {t(lang, "Glosario")}
            </Link>
            <Link
              href="/recursos"
              className={`side-link ${active(pathname, "/recursos") ? "is-active" : ""}`}
            >
              <Icon name="folder" /> {t(lang, "Recursos")}
            </Link>
            {user.role === "teacher" ? (
              <>
                <Link
                  href="/estudio"
                  className={`side-link ${active(pathname, "/estudio") ? "is-active" : ""}`}
                >
                  <Icon name="sparkles" /> {t(lang, "Estudio")}
                </Link>
                <Link
                  href="/profesor"
                  className={`side-link ${active(pathname, "/profesor") ? "is-active" : ""}`}
                >
                  <Icon name="graduation" /> {t(lang, "Profesorado")}
                </Link>
              </>
            ) : null}
          </nav>

          <div className="sidebar-lessons">
            <div className="sidebar-lessons-head">
              <span className="sidebar-label">{t(lang, "Lecciones")}</span>
            </div>
            {course.chapters.map((chapter) => {
              const doneCount = chapter.lessons.filter(
                (lesson) => progress[lesson.slug]?.completed
              ).length;
              const activeChapter = chapter.lessons.some(
                (lesson) => pathname === `/leccion/${lesson.slug}`
              );
              return (
                <details
                  className="side-chapter"
                  key={chapter.slug}
                  open={activeChapter}
                >
                  <summary className="side-chapter-head">
                    <span className="side-num">{chapter.number}</span>
                    <span className="side-title">{chapter.title}</span>
                    <span className="side-chapter-count">
                      {doneCount}/{chapter.lesson_count}
                    </span>
                  </summary>
                  <div className="side-chapter-lessons">
                    <Link
                      className="side-chapter-link"
                      href={`/curso#capitulo-${chapter.number}`}
                    >
                      {t(lang, "Ver capítulo")}
                    </Link>
                    {chapter.lessons.map((lesson) => {
                      const done = progress[lesson.slug]?.completed;
                      return (
                        <Link
                          key={lesson.slug}
                          href={`/leccion/${lesson.slug}`}
                          prefetch={false}
                          className={`side-lesson ${
                            pathname === `/leccion/${lesson.slug}`
                              ? "is-active"
                              : ""
                          } ${done ? "is-done" : ""}`}
                        >
                          <span className="side-num">
                            {done ? <Icon name="check" /> : lesson.number}
                          </span>
                          <span className="side-title">{lesson.title}</span>
                        </Link>
                      );
                    })}
                  </div>
                </details>
              );
            })}
          </div>

          <div className="sidebar-foot">
            <div className="sidebar-user">
              <span className="avatar">{user.initials}</span>
              <span className="sidebar-user-text">
                <strong>{user.name}</strong>
                <small>
                  {user.role === "teacher" ? t(lang, "Profesorado") : t(lang, "Estudiante")}
                </small>
              </span>
              <LogoutButton csrf={user.csrf_token} label={t(lang, "Cerrar sesión")} />
            </div>
          </div>
        </aside>
        <div className="sidebar-backdrop" data-sidebar-close />

        <div className="app-main">
          <header className="topbar">
            <button
              className="icon-btn sidebar-toggle"
              type="button"
              data-sidebar-collapse
              data-collapse-label={t(lang, "Colapsar barra lateral")}
              data-expand-label={t(lang, "Expandir barra lateral")}
              aria-label={t(lang, "Colapsar barra lateral")}
              aria-expanded="true"
              title={t(lang, "Colapsar barra lateral")}
            >
              <Icon name="panel-left" />
            </button>
            <button
              className="icon-btn mobile-only"
              type="button"
              data-sidebar-open
              aria-label={t(lang, "Abrir menú")}
            >
              <Icon name="menu" />
            </button>
            <div className="topbar-heading">
              <span className="topbar-kicker">{kicker}</span>
              <h1 className="topbar-title">{title}</h1>
            </div>
            <form className="topbar-search" action="/buscar" method="get" role="search">
              <label className="sr-only" htmlFor="busqueda">
                {t(lang, "Buscar en el curso")}
              </label>
              <Icon name="search" />
              <input
                id="busqueda"
                type="search"
                name="q"
                defaultValue={query}
                placeholder={t(lang, "Buscar en la biblioteca…")}
                autoComplete="off"
              />
              <kbd>/</kbd>
            </form>
            <div className="lang-switch" aria-label={t(lang, "Idioma")}>
              {/* Navegación completa, no Link: el cambio de cookie debe invalidar
                  la caché de RSC del router de Next. */}
              <a
                href={`/idioma/es?next=${encodeURIComponent(fullPath)}`}
                className={`lang-link ${lang === "es" ? "is-active" : ""}`}
                lang="es"
                hrefLang="es"
              >
                ES
              </a>
              <a
                href={`/idioma/en?next=${encodeURIComponent(fullPath)}`}
                className={`lang-link ${lang === "en" ? "is-active" : ""}`}
                lang="en"
                hrefLang="en"
              >
                EN
              </a>
            </div>
            <ThemeToggle lang={lang} />
            <details className="user-menu">
              <summary>
                <span className="avatar avatar-sm">{user.initials}</span>
                <Icon name="chevron-down" />
              </summary>
              <div className="user-menu-panel">
                <span className="user-menu-name">{user.name}</span>
                <span className="user-menu-email">{user.email}</span>
                <Link href="/progreso">
                  <Icon name="chart" /> {t(lang, "Mi progreso")}
                </Link>
                <Link href="/glosario">
                  <Icon name="glossary" /> {t(lang, "Glosario")}
                </Link>
                {user.role === "teacher" ? (
                  <Link href="/estudio">
                    <Icon name="sparkles" /> {t(lang, "Estudio")}
                  </Link>
                ) : null}
                <LogoutButton
                  csrf={user.csrf_token}
                  label={t(lang, "Cerrar sesión")}
                  className=""
                >
                  <Icon name="logout" /> {t(lang, "Cerrar sesión")}
                </LogoutButton>
              </div>
            </details>
          </header>

          <div className="reading-progress" aria-hidden="true">
            <span data-reading-progress />
          </div>

          <main id="contenido" className="content">
            {children}
          </main>

          <footer className="app-footer">
            <span>
              {site.name} ·{" "}
              {t(
                lang,
                "Biblioteca de cursos interactivos para aprender IA construyendo."
              )}
            </span>
            <span>
              {t(lang, "Uso educativo")} · {site.year}
            </span>
          </footer>
        </div>
      </div>
      <SidebarController />
      <SearchShortcut />
      <ReadingProgress />
      <Lightbox
        label={t(lang, "Vista ampliada de la figura")}
        closeLabel={t(lang, "Cerrar")}
      />
    </>
  );
}
