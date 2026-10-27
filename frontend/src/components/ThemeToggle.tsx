"use client";

import { useEffect, useState } from "react";

import { Icon } from "./ui";
import type { Lang } from "@/lib/types";
import { t } from "@/lib/messages";

export function ThemeToggle({ lang }: { lang: Lang }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const current = document.documentElement.dataset.theme;
    setTheme(current === "dark" ? "dark" : "light");
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("aula-theme", next);
    } catch {
      // localStorage puede no estar disponible.
    }
    setTheme(next);
  }

  return (
    <button
      className="icon-btn theme-toggle"
      type="button"
      data-theme-toggle
      onClick={toggle}
      aria-label={
        theme === "dark"
          ? t(lang, "Cambiar a tema claro")
          : t(lang, "Cambiar a tema oscuro")
      }
    >
      <span className="theme-light">
        <Icon name="moon" />
      </span>
      <span className="theme-dark">
        <Icon name="sun" />
      </span>
    </button>
  );
}
