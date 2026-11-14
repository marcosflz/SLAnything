import type { Metadata } from "next";

import { PlatformLayout } from "@/components/platform/PlatformLayout";
import { PlatformWorkspacesPanel } from "@/components/platform/PlatformPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { PlatformWorkspace } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Espacios", "Spaces") };
}

export default async function PlatformWorkspacesPage() {
  const shell = await getShell("/plataforma/espacios");
  const { lang } = shell;
  const data = shell.user.permissions?.platform
    ? await allowForbidden(apiGet<{ workspaces: PlatformWorkspace[] }>("/api/v1/platform/workspaces"))
    : null;
  return (
    <PlatformLayout
      shell={shell}
      path="/plataforma/espacios"
      title={pick(lang, "Espacios", "Spaces")}
      description={pick(lang, "Academias y cuentas individuales: cuotas de generación y plazas.", "Academies and individual accounts: generation quotas and seats.")}
    >
      {data ? <PlatformWorkspacesPanel workspaces={data.workspaces} csrf={shell.user.csrf_token} lang={lang} /> : null}
    </PlatformLayout>
  );
}
