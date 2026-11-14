import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Combina clases condicionales y resuelve conflictos de Tailwind. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const hours = Math.floor(minutes / 60);
  const rest = Math.round(minutes % 60);
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

export function formatDate(value: string | null | undefined, lang: "es" | "en"): string {
  if (!value) return "—";
  const date = new Date(value.length <= 10 ? `${value}T00:00:00Z` : value);
  return date.toLocaleDateString(lang === "en" ? "en-GB" : "es-ES", {
    day: "numeric",
    month: "short",
    timeZone: "UTC",
  });
}

export function relativeDays(value: string | null | undefined, lang: "es" | "en"): string {
  if (!value) return lang === "en" ? "never" : "nunca";
  const days = Math.floor((Date.now() - new Date(value).getTime()) / 86_400_000);
  if (days <= 0) return lang === "en" ? "today" : "hoy";
  if (days === 1) return lang === "en" ? "yesterday" : "ayer";
  return lang === "en" ? `${days} days ago` : `hace ${days} días`;
}
