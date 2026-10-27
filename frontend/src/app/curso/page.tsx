import { AppShell } from "@/components/AppShell";
import { CoursePageView } from "@/components/course/CoursePageView";
import { apiGet, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { CoursePayload } from "@/lib/types";

type SearchParams = Record<string, string | string[] | undefined>;

function withQuery(pathname: string, params: SearchParams): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      for (const item of value) search.append(key, item);
    } else if (value !== undefined) {
      search.set(key, value);
    }
  }
  const serialized = search.toString();
  return serialized ? `${pathname}?${serialized}` : pathname;
}

export default async function CoursePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const shell = await getShell("/curso");
  const data = await apiGet<CoursePayload>("/api/v1/course");
  const params = await searchParams;
  const lang = shell.lang;

  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={shell.courses}
      progress={shell.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname="/curso"
      fullPath={withQuery("/curso", params)}
      title={t(lang, "Programa del curso")}
      kicker={t(lang, "Programa completo")}
    >
      <CoursePageView
        course={data.course}
        courses={data.courses}
        progress={data.progress}
        stats={data.stats}
        nextLesson={data.next_lesson}
        lang={lang}
      />
    </AppShell>
  );
}
