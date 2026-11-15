import type { Metadata } from "next";

import { AiProvidersPanel } from "@/components/account/AiProvidersPanel";
import { AdminLayout } from "@/components/admin/AdminLayout";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AiProvidersData } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "IA de la academia", "Academy AI") };
}

/** Claves de API que la academia comparte con su profesorado (ADR-025). */
export default async function AcademyAiPage() {
  const shell = await getShell("/admin/ia");
  const { lang } = shell;
  const data = await allowForbidden(apiGet<AiProvidersData>("/api/v1/admin/ai"));
  return (
    <AdminLayout
      shell={shell}
      path="/admin/ia"
      title={pick(lang, "IA de la academia", "Academy AI")}
      description={pick(
        lang,
        "Claves de API que el profesorado puede usar en el Estudio. Cada docente puede añadir además las suyas en «Mi cuenta».",
        "API keys teachers can use in the Studio. Each teacher can also add their own in “My account”."
      )}
      allowed={Boolean(data)}
    >
      {data ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <AiProvidersPanel initial={data} csrf={shell.user.csrf_token} lang={lang} scope="workspace" />
        </div>
      ) : null}
    </AdminLayout>
  );
}
