import { ChevronLeft } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { PageHeader } from "@/components/charts/Kpi";
import { Forbidden, ShellPage } from "@/components/shell/ShellPage";
import { JobWizard } from "@/components/studio/JobWizard";
import { Button } from "@/components/ui/button";
import { ApiError, apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AuthoringJob } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Proyecto del Estudio", "Studio project") };
}

export default async function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const path = `/estudio/trabajos/${id}`;
  const shell = await getShell(path);
  const { lang } = shell;
  let job: AuthoringJob | null = null;
  try {
    job = await apiGet<AuthoringJob>(`/api/v1/authoring/jobs/${encodeURIComponent(id)}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    if (!(error instanceof ApiError && error.status === 403)) throw error;
  }

  return (
    <ShellPage shell={shell} path={path} title={job?.title ?? pick(lang, "Proyecto", "Project")} kicker={pick(lang, "Estudio", "Studio")}>
      {job ? (
        <>
          <Button asChild variant="ghost" size="sm" className="mb-2 -ml-2">
            <Link href="/estudio">
              <ChevronLeft /> {pick(lang, "Estudio", "Studio")}
            </Link>
          </Button>
          <PageHeader title={job.title} description={job.source_names.join(" · ")} />
          <JobWizard initial={job} csrf={shell.user.csrf_token} lang={lang} />
        </>
      ) : (
        <Forbidden lang={lang} />
      )}
    </ShellPage>
  );
}
