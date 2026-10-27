import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import type {
  CatalogPayload,
  CourseDetailPayload,
  CoursePayload,
  DashboardPayload,
  Lang,
  LessonPayload,
  ProgressPayload,
  PublicPayload,
  SessionPayload,
  ShellPayload,
} from "./types";

const API_URL = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function getLang(): Promise<Lang> {
  const store = await cookies();
  return store.get("aula_lang")?.value === "en" ? "en" : "es";
}

function withLang(path: string, lang: Lang): string {
  return `${path}${path.includes("?") ? "&" : "?"}lang=${lang}`;
}

export async function apiGet<T>(path: string, lang?: Lang): Promise<T> {
  const store = await cookies();
  const resolvedLang = lang ?? (await getLang());
  const response = await fetch(`${API_URL}${withLang(path, resolvedLang)}`, {
    headers: { cookie: store.toString() },
    cache: "no-store",
  });

  if (!response.ok) {
    let detail = `API ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // La respuesta no era JSON.
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export async function getSession(): Promise<SessionPayload> {
  return apiGet<SessionPayload>("/api/v1/session");
}

export async function getPublic(): Promise<PublicPayload> {
  return apiGet<PublicPayload>("/api/v1/public");
}

export async function getCatalog(): Promise<CatalogPayload> {
  return apiGet<CatalogPayload>("/api/v1/catalog");
}

export async function getCourse(
  slug: string,
  lang?: Lang
): Promise<CourseDetailPayload> {
  return apiGet<CourseDetailPayload>(`/api/v1/courses/${slug}`, lang);
}

export async function requireSession(nextPath: string): Promise<SessionPayload> {
  const session = await getSession();
  if (!session.user) {
    redirect(`/entrar?next=${encodeURIComponent(nextPath)}`);
  }
  return session;
}

export async function getShell(
  nextPath: string,
  courseSlug?: string
): Promise<ShellPayload> {
  const path = courseSlug
    ? `/api/v1/shell?course=${encodeURIComponent(courseSlug)}`
    : "/api/v1/shell";
  try {
    return await apiGet<ShellPayload>(path);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect(`/entrar?next=${encodeURIComponent(nextPath)}`);
    }
    throw error;
  }
}

export type {
  CourseDetailPayload,
  CoursePayload,
  DashboardPayload,
  LessonPayload,
  ProgressPayload,
};
