import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { PublicShell } from "@/components/PublicShell";
import { CoursePageView } from "@/components/course/CoursePageView";
import { ApiError, getCourse, getLang, getSession, getShell } from "@/lib/api";
import { t } from "@/lib/messages";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const lang = await getLang();
  try {
    const data = await getCourse(slug, lang);
    return { title: data.course.title, description: data.course.description };
  } catch {
    return { title: t(lang, "Curso no encontrado") };
  }
}

export default async function CourseDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const session = await getSession();

  if (!session.user) {
    const lang = await getLang();
    let data;
    try {
      data = await getCourse(slug, lang);
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) notFound();
      throw error;
    }
    return (
      <PublicShell site={data.site} lang={data.lang} fullPath={`/cursos/${slug}`}>
        <div className="public-page">
          <CoursePageView
            course={data.course}
            courses={data.courses}
            progress={data.progress}
            stats={data.stats}
            nextLesson={data.next_lesson}
            lang={data.lang}
            publicView
          />
        </div>
      </PublicShell>
    );
  }

  let shell;
  let data;
  try {
    [shell, data] = await Promise.all([
      getShell(`/cursos/${slug}`, slug),
      getCourse(slug),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={shell.courses}
      progress={shell.progress}
      stats={shell.stats}
      site={shell.site}
      lang={shell.lang}
      pathname={`/cursos/${slug}`}
      fullPath={`/cursos/${slug}`}
      title={t(shell.lang, "Programa del curso")}
      kicker={t(shell.lang, "Programa completo")}
    >
      <CoursePageView
        course={data.course}
        courses={data.courses}
        progress={data.progress}
        stats={data.stats}
        nextLesson={data.next_lesson}
        lang={shell.lang}
      />
    </AppShell>
  );
}
