"use client";

import { Command } from "cmdk";
import { BookOpen, CornerDownLeft, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Dialog, DialogContent, DialogTitle } from "@/components/ui/overlay";
import { pick, type Lang } from "@/lib/messages";
import { NAV_ICONS, type NavItem } from "./nav";

export interface PaletteLesson {
  slug: string;
  title: string;
  chapter: number;
}

/** Barra de comandos ⌘K / Ctrl+K / «/»: navegación, lecciones y búsqueda. */
export function CommandPalette({
  lang,
  nav,
  lessons,
}: {
  lang: Lang;
  nav: NavItem[];
  lessons: PaletteLesson[];
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const tag = target?.tagName?.toLowerCase();
      const typing = tag === "input" || tag === "textarea" || tag === "select" || target?.isContentEditable;
      if ((event.key === "k" && (event.metaKey || event.ctrlKey)) || (event.key === "/" && !typing)) {
        event.preventDefault();
        setOpen((value) => !value);
      }
    }
    function onOpen() {
      setOpen(true);
    }
    document.addEventListener("keydown", onKey);
    window.addEventListener("open-command-palette", onOpen);
    return () => {
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("open-command-palette", onOpen);
    };
  }, []);

  function go(href: string) {
    setOpen(false);
    setQuery("");
    router.push(href);
  }

  const item =
    "flex cursor-pointer items-center gap-2.5 rounded-md px-2.5 py-2 text-sm data-[selected=true]:bg-muted [&_svg]:size-4 [&_svg]:text-muted-foreground";
  const group =
    "px-1 py-1 [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="top-[18%] max-w-xl translate-y-0 gap-0 overflow-hidden p-0" closeLabel={pick(lang, "Cerrar", "Close")}>
        <DialogTitle className="sr-only">{pick(lang, "Buscar y navegar", "Search and navigate")}</DialogTitle>
        <Command label={pick(lang, "Comandos", "Commands")} loop>
          <div className="flex items-center gap-2 border-b border-border px-3">
            <Search className="size-4 text-muted-foreground" aria-hidden="true" />
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder={pick(lang, "Busca una lección, una página o un término…", "Search a lesson, page or term…")}
              className="h-12 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
          </div>
          <Command.List className="max-h-[min(60vh,420px)] overflow-y-auto p-1 scrollbar-thin">
            <Command.Empty className="px-3 py-6 text-center text-sm text-muted-foreground">
              {pick(lang, "Sin coincidencias.", "No matches.")}
            </Command.Empty>
            {query.trim().length >= 2 ? (
              <Command.Group heading={pick(lang, "Buscar", "Search")} className={group}>
                <Command.Item
                  value={`buscar ${query}`}
                  onSelect={() => go(`/buscar?q=${encodeURIComponent(query.trim())}`)}
                  className={item}
                >
                  <Search />
                  {pick(lang, "Buscar «{q}» en la biblioteca", "Search “{q}” in the library").replace("{q}", query.trim())}
                  <CornerDownLeft className="ml-auto" />
                </Command.Item>
              </Command.Group>
            ) : null}
            <Command.Group heading={pick(lang, "Ir a", "Go to")} className={group}>
              {nav.map((entry) => {
                const Icon = NAV_ICONS[entry.icon];
                return (
                  <Command.Item key={entry.href} value={entry.label} onSelect={() => go(entry.href)} className={item}>
                    <Icon />
                    {entry.label}
                  </Command.Item>
                );
              })}
            </Command.Group>
            {lessons.length ? (
              <Command.Group heading={pick(lang, "Lecciones", "Lessons")} className={group}>
                {lessons.map((lesson) => (
                  <Command.Item
                    key={lesson.slug}
                    value={`${lesson.title} ${lesson.slug}`}
                    onSelect={() => go(`/leccion/${lesson.slug}`)}
                    className={item}
                  >
                    <BookOpen />
                    <span className="min-w-0 flex-1 truncate">{lesson.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {pick(lang, "Cap.", "Ch.")} {lesson.chapter}
                    </span>
                  </Command.Item>
                ))}
              </Command.Group>
            ) : null}
          </Command.List>
        </Command>
      </DialogContent>
    </Dialog>
  );
}

export function CommandTrigger({ lang }: { lang: Lang }) {
  return (
    <button
      type="button"
      onClick={() => window.dispatchEvent(new Event("open-command-palette"))}
      className="flex h-9 w-full max-w-xs cursor-pointer items-center gap-2 rounded-md border border-border bg-card px-3 text-sm text-muted-foreground shadow-card transition hover:border-border-strong"
      aria-label={pick(lang, "Buscar (Ctrl+K)", "Search (Ctrl+K)")}
    >
      <Search className="size-4" aria-hidden="true" />
      <span className="flex-1 truncate text-left">{pick(lang, "Buscar…", "Search…")}</span>
      <kbd className="hidden rounded border border-border bg-muted px-1.5 font-sans text-[11px] sm:inline">Ctrl K</kbd>
    </button>
  );
}
