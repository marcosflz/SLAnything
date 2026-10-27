import EN from "./messages.json";

export type Lang = "es" | "en";

type Vars = Record<string, string | number>;

export function t(lang: Lang, key: string, vars: Vars = {}): string {
  const template = lang === "en" ? (EN as Record<string, string>)[key] ?? key : key;
  return template.replace(/\{(\w+)\}/g, (_, name: string) =>
    vars[name] === undefined ? `{${name}}` : String(vars[name])
  );
}

export function pick(lang: Lang, es: string, en: string): string {
  return lang === "en" ? en : es;
}
