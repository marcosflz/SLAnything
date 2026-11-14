"use client";

import { LineChart, LogOut, Moon, Sun, UserRound } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Menu, MenuContent, MenuItem, MenuLabel, MenuSeparator, MenuTrigger } from "@/components/ui/overlay";
import { apiPost } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { User } from "@/lib/types";
import { profileLabel } from "@/lib/roles";

export function ThemeButton({ lang }: { lang: Lang }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  useEffect(() => {
    setTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
  }, []);
  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("aula-theme", next);
    } catch {
      // Sin localStorage el tema dura hasta recargar.
    }
    setTheme(next);
  }
  const label = theme === "dark" ? pick(lang, "Cambiar a tema claro", "Switch to light theme") : pick(lang, "Cambiar a tema oscuro", "Switch to dark theme");
  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={label}
      title={label}
      data-theme-toggle
      className="grid size-9 cursor-pointer place-items-center rounded-md border-0 bg-transparent text-muted-foreground transition hover:bg-muted hover:text-foreground"
    >
      {theme === "dark" ? <Sun className="size-[18px]" /> : <Moon className="size-[18px]" />}
    </button>
  );
}

export function UserMenu({ user, lang }: { user: User; lang: Lang }) {
  async function logout() {
    try {
      await apiPost("/api/v1/auth/logout", {}, user.csrf_token);
    } catch {
      // Si la sesión ya no existe, recargar basta.
    }
    window.location.href = "/";
  }
  return (
    <Menu>
      <MenuTrigger asChild>
        <button
          type="button"
          className="grid size-9 cursor-pointer place-items-center rounded-full border-0 bg-primary text-[13px] font-semibold text-primary-foreground ring-offset-2 ring-offset-background transition hover:ring-2 hover:ring-primary/40"
          aria-label={pick(lang, "Menú de usuario", "User menu")}
        >
          {user.initials}
        </button>
      </MenuTrigger>
      <MenuContent align="end" className="w-60">
        <MenuLabel className="text-foreground">
          <span className="block truncate text-sm font-semibold">{user.name}</span>
          <span className="block truncate text-xs font-normal text-muted-foreground">{user.email}</span>
          <span className="mt-1 block text-xs font-normal text-muted-foreground">
            {user.workspace ? `${user.workspace.name} · ` : ""}
            {profileLabel(user, lang)}
            {user.permissions?.platform && user.profile ? ` · ${pick(lang, "Superadmin", "Superadmin")}` : ""}
          </span>
        </MenuLabel>
        <MenuSeparator />
        <MenuItem asChild>
          <Link href="/cuenta">
            <UserRound /> {pick(lang, "Mi cuenta", "My account")}
          </Link>
        </MenuItem>
        <MenuItem asChild>
          <Link href="/progreso">
            <LineChart /> {pick(lang, "Mi progreso", "My progress")}
          </Link>
        </MenuItem>
        <MenuSeparator />
        <MenuItem onSelect={logout}>
          <LogOut /> {pick(lang, "Cerrar sesión", "Log out")}
        </MenuItem>
      </MenuContent>
    </Menu>
  );
}
