"use client";

import { Menu as MenuIcon, PanelLeft, X } from "lucide-react";
import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";

import { cn } from "@/lib/utils";

const ShellContext = createContext<{ open: boolean; setOpen: (value: boolean) => void }>({
  open: false,
  setOpen: () => {},
});

/** Estado del menú lateral: cajón en móvil y colapsable en escritorio. */
export function ShellFrame({
  sidebar,
  children,
  labels,
}: {
  sidebar: React.ReactNode;
  children: React.ReactNode;
  labels: { close: string };
}) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    document.body.classList.toggle("no-scroll", open);
    if (!open) return;
    const onKey = (event: KeyboardEvent) => event.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <ShellContext.Provider value={{ open, setOpen }}>
      <div className="flex min-h-dvh">
        <aside
          id="sidebar"
          className={cn(
            "fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-border bg-card transition-transform duration-200 lg:sticky lg:top-0 lg:h-dvh lg:translate-x-0",
            "in-[.sidebar-collapsed]:lg:hidden",
            open ? "translate-x-0 shadow-pop" : "-translate-x-full"
          )}
        >
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="absolute top-3 right-3 grid size-8 cursor-pointer place-items-center rounded-md border-0 bg-transparent text-muted-foreground hover:bg-muted lg:hidden"
            aria-label={labels.close}
          >
            <X className="size-4" />
          </button>
          {sidebar}
        </aside>
        {open ? (
          <div
            className="fixed inset-0 z-30 bg-black/40 lg:hidden"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
        ) : null}
        <div className="flex min-w-0 flex-1 flex-col">{children}</div>
      </div>
    </ShellContext.Provider>
  );
}

export function SidebarButtons({ openLabel, collapseLabel }: { openLabel: string; collapseLabel: string }) {
  const { setOpen } = useContext(ShellContext);

  function toggleCollapse() {
    const root = document.documentElement;
    const collapsed = root.classList.toggle("sidebar-collapsed");
    try {
      localStorage.setItem("aula-sidebar-collapsed", collapsed ? "1" : "0");
    } catch {
      // Sin localStorage el estado dura hasta recargar.
    }
  }

  const base =
    "grid size-9 shrink-0 cursor-pointer place-items-center rounded-md border-0 bg-transparent text-muted-foreground transition hover:bg-muted hover:text-foreground";
  return (
    <>
      <button type="button" className={cn(base, "lg:hidden")} onClick={() => setOpen(true)} aria-label={openLabel}>
        <MenuIcon className="size-5" />
      </button>
      <button
        type="button"
        className={cn(base, "hidden lg:grid")}
        onClick={toggleCollapse}
        aria-label={collapseLabel}
        title={collapseLabel}
      >
        <PanelLeft className="size-[18px]" />
      </button>
    </>
  );
}
