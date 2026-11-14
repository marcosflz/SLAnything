import type { Metadata } from "next";

import { PlatformLayout } from "@/components/platform/PlatformLayout";
import { PlatformCoursesPanel } from "@/components/platform/PlatformPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AuthoringCourse } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Cursos", "Courses") };
}

export default async function PlatformCoursesPage() {
  const shell = await getShell("/plataforma/cursos");
  const { lang } = shell;
  const data = shell.user.permissions?.platform
    ? await allowForbidden(
        apiGet<{ courses: (AuthoringCourse & { workspace_name?: string | null })[] }>("/api/v1/platform/courses")
      )
    : null;
  return (
    <PlatformLayout
      shell={shell}
      path="/plataforma/cursos"
      title={pick(lang, "Cursos generados", "Generated courses")}
      description={pick(
        lang,
        "Todos los cursos del Estudio. Abre un curso a toda la plataforma o retíralo si no cumple las normas.",
        "Every Studio course. Open a course to the whole platform or withdraw it if it breaks the rules."
      )}
    >
      {data ? <PlatformCoursesPanel courses={data.courses} csrf={shell.user.csrf_token} lang={lang} /> : null}
    </PlatformLayout>
  );
}
