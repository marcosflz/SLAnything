import { Check, ChevronRight } from "lucide-react";
import Link from "next/link";

import type { Course, CourseSummary, Lang, ProgressMap, Site, Stats, User } from "@/lib/types";
import { pick, t } from "@/lib/messages";
import { cn } from "@/lib/utils";
import { Lightbox } from "./Lightbox";
import { ReadingProgress } from "./ReadingProgress";
import { CommandPalette, CommandTrigger } from "./shell/CommandPalette";
import { NAV_ICONS, navSections } from "./shell/nav";
import { ShellFrame, SidebarButtons } from "./shell/ShellFrame";
import { ThemeButton, UserMenu } from "./shell/UserMenu";
import { WorkspaceSwitcher } from "./shell/WorkspaceSwitcher";

function isActive(current: string, href: string) {
  if (href === "/") return current === "/";
  return current === href || current.startsWith(`${href}/`);
}

/**
 * Shell de la aplicación: sidebar con espacio de trabajo, navegación por rol y
 * temario del curso activo; topbar con búsqueda ⌘K, idioma, tema y usuario.
 * Las páginas heredadas siguen usando `.content` para su ancho y márgenes.
 */
export function AppShell({
  user,
  course,
  progress,
  site,
  lang,
  pathname,
  fullPath,
  title,
  kicker,
  wide = false,
  children,
}: {
  user: User;
  course: Course;
  courses?: CourseSummary[];
  progress: ProgressMap;
  stats?: Stats;
  site: Site;
  lang: Lang;
  pathname: string;
  fullPath: string;
  query?: string;
  title: string;
  kicker: string;
  wide?: boolean;
  children: React.ReactNode;
}) {
  const sections = navSections(user, lang);
  const lessons = course.chapters.flatMap((chapter) =>
    chapter.lessons.map((lesson) => ({ slug: lesson.slug, title: lesson.title, chapter: chapter.number }))
  );
  const done = lessons.filter((lesson) => progress[lesson.slug]?.completed).length;
  const pct = lessons.length ? Math.round((done * 100) / lessons.length) : 0;

  const sidebar = (
    <>
      <div className="border-b border-border p-3 pr-12 lg:pr-3">
        <WorkspaceSwitcher user={user} lang={lang} />
      </div>
      <nav className="flex-1 overflow-y-auto px-3 py-3 scrollbar-thin" aria-label={t(lang, "Navegación principal")}>
        {sections.map((section) => (
          <div key={section.label} className="mb-4">
            <p className="m-0 mb-1 px-2 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
              {section.label}
            </p>
            <ul className="m-0 grid list-none gap-0.5 p-0">
              {section.items.map((item) => {
                const Icon = NAV_ICONS[item.icon];
                const active = isActive(pathname, item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm text-soft-foreground no-underline transition hover:bg-muted hover:text-foreground hover:no-underline",
                        active && "bg-primary-soft font-medium text-primary hover:bg-primary-soft hover:text-primary"
                      )}
                    >
                      <Icon className="size-4 shrink-0" aria-hidden="true" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}

        <div className="mb-2">
          <p className="m-0 mb-1 px-2 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
            {pick(lang, "Curso actual", "Current course")}
          </p>
          <Link
            href={`/cursos/${course.slug}`}
            className="mx-0 mb-2 block rounded-lg border border-border p-2.5 no-underline transition hover:border-border-strong hover:no-underline"
          >
            <span className="block truncate text-sm font-medium text-foreground">{course.title}</span>
            <span className="mt-2 flex items-center gap-2">
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-subtle">
                <span className="block h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
              </span>
              <span className="tabular text-xs text-muted-foreground">{pct}%</span>
            </span>
          </Link>
          {course.chapters.map((chapter) => {
            const chapterDone = chapter.lessons.filter((lesson) => progress[lesson.slug]?.completed).length;
            const open = chapter.lessons.some((lesson) => pathname === `/leccion/${lesson.slug}`);
            return (
              <details key={chapter.slug} open={open} className="group">
                <summary className="flex cursor-pointer list-none items-center gap-2 rounded-md px-2 py-1.5 text-[13px] text-soft-foreground hover:bg-muted [&::-webkit-details-marker]:hidden">
                  <ChevronRight className="size-3.5 shrink-0 text-muted-foreground transition group-open:rotate-90" aria-hidden="true" />
                  <span className="min-w-0 flex-1 truncate">
                    {chapter.number}. {chapter.title}
                  </span>
                  <span className="tabular text-[11px] text-muted-foreground">
                    {chapterDone}/{chapter.lesson_count}
                  </span>
                </summary>
                <ul className="m-0 mb-1 ml-4 grid list-none gap-px border-l border-border p-0 pl-2">
                  {chapter.lessons.map((lesson) => {
                    const current = pathname === `/leccion/${lesson.slug}`;
                    const completed = progress[lesson.slug]?.completed;
                    return (
                      <li key={lesson.slug}>
                        <Link
                          href={`/leccion/${lesson.slug}`}
                          prefetch={false}
                          aria-current={current ? "page" : undefined}
                          className={cn(
                            "flex items-center gap-2 rounded-md px-2 py-1 text-[13px] text-muted-foreground no-underline hover:bg-muted hover:text-foreground hover:no-underline",
                            current && "bg-muted font-medium text-foreground"
                          )}
                        >
                          <span
                            className={cn(
                              "grid size-4 shrink-0 place-items-center rounded-full border text-[9px]",
                              completed ? "border-success bg-success text-white" : "border-border-strong"
                            )}
                            aria-hidden="true"
                          >
                            {completed ? <Check className="size-2.5" strokeWidth={3} /> : null}
                          </span>
                          <span className="min-w-0 flex-1 truncate">{lesson.title}</span>
                          {completed ? <span className="sr-only">{pick(lang, "(completada)", "(completed)")}</span> : null}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </details>
            );
          })}
        </div>
      </nav>
      <div className="border-t border-border px-4 py-3 text-xs text-muted-foreground">
        {site.name} · {t(lang, "Uso educativo")} · {site.year}
      </div>
    </>
  );

  const paletteNav = sections.flatMap((section) => section.items);

  return (
    <>
      <a className="skip-link" href="#contenido">
        {t(lang, "Saltar al contenido")}
      </a>
      <ShellFrame sidebar={sidebar} labels={{ close: t(lang, "Cerrar menú") }}>
        <header className="sticky top-0 z-20 flex h-14 items-center gap-2 border-b border-border bg-background/85 px-3 backdrop-blur sm:px-4">
          <SidebarButtons
            openLabel={t(lang, "Abrir menú")}
            collapseLabel={t(lang, "Colapsar barra lateral")}
          />
          <div className="min-w-0 flex-1 leading-tight">
            <span className="block truncate text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
              {kicker}
            </span>
            <h1 className="truncate text-[15px] font-semibold">{title}</h1>
          </div>
          <div className="hidden w-64 md:block">
            <CommandTrigger lang={lang} />
          </div>
          <div className="flex items-center rounded-md border border-border p-0.5 text-xs" aria-label={t(lang, "Idioma")}>
            {/* Navegación completa: el cambio de cookie invalida la caché RSC. */}
            {(["es", "en"] as const).map((code) => (
              <a
                key={code}
                href={`/idioma/${code}?next=${encodeURIComponent(fullPath)}`}
                lang={code}
                hrefLang={code}
                aria-current={lang === code ? "true" : undefined}
                className={cn(
                  "rounded px-1.5 py-0.5 font-medium text-muted-foreground no-underline hover:text-foreground hover:no-underline",
                  lang === code && "bg-muted text-foreground"
                )}
              >
                {code.toUpperCase()}
              </a>
            ))}
          </div>
          <ThemeButton lang={lang} />
          <UserMenu user={user} lang={lang} />
        </header>
        <div className="reading-progress" aria-hidden="true">
          <span data-reading-progress />
        </div>
        <main id="contenido" className={cn("content", wide && "max-w-[1400px]")}>
          {children}
        </main>
      </ShellFrame>
      <CommandPalette lang={lang} nav={paletteNav} lessons={lessons} />
      <ReadingProgress />
      <Lightbox label={t(lang, "Vista ampliada de la figura")} closeLabel={t(lang, "Cerrar")} />
    </>
  );
}
