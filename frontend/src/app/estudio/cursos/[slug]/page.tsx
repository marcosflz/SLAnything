import { ChevronLeft } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Forbidden, ShellPage } from "@/components/shell/ShellPage";
import { CourseReview } from "@/components/studio/CourseReview";
import { Button } from "@/components/ui/button";
import { ApiError, apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AuthoringCourse } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Revisión de la unidad", "Unit review") };
}

export default async function CourseReviewPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const path = `/estudio/cursos/${slug}`;
  const shell = await getShell(path);
  const { lang } = shell;
  let course: AuthoringCourse | null = null;
  try {
    course = await apiGet<AuthoringCourse>(`/api/v1/authoring/courses/${encodeURIComponent(slug)}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    if (!(error instanceof ApiError && error.status === 403)) throw error;
  }

  return (
    <ShellPage shell={shell} path={path} title={course?.title ?? pick(lang, "Unidad", "Unit")} kicker={pick(lang, "Revisión", "Review")}>
      {course?.package ? (
        <>
          <Button asChild variant="ghost" size="sm" className="mb-3 -ml-2">
            <Link href="/estudio">
              <ChevronLeft /> {pick(lang, "Estudio", "Studio")}
            </Link>
          </Button>
          <CourseReview
            initial={course}
            csrf={shell.user.csrf_token}
            lang={lang}
            canPublishPublic={Boolean(shell.user.permissions?.platform)}
          />
        </>
      ) : (
        <Forbidden lang={lang} />
      )}
    </ShellPage>
  );
}
