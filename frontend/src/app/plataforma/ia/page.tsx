import type { Metadata } from "next";

import { PlatformLayout } from "@/components/platform/PlatformLayout";
import { allowForbidden } from "@/components/shell/ShellPage";
import { ProviderSettings } from "@/components/studio/StudioHome";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AuthoringSettings } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Proveedor de IA", "AI provider") };
}

export default async function PlatformAiPage() {
  const shell = await getShell("/plataforma/ia");
  const { lang } = shell;
  const settings = shell.user.permissions?.platform
    ? await allowForbidden(apiGet<AuthoringSettings>("/api/v1/platform/ai"))
    : null;
  return (
    <PlatformLayout
      shell={shell}
      path="/plataforma/ia"
      title={pick(lang, "Proveedor de IA", "AI provider")}
      description={pick(
        lang,
        "Modelo y credenciales que usa el Estudio en toda la plataforma. La API key nunca se envía al navegador.",
        "Model and credentials the Studio uses across the platform. The API key is never sent to the browser."
      )}
    >
      {settings ? (
        <div className="max-w-2xl">
          <ProviderSettings initial={settings} csrf={shell.user.csrf_token} lang={lang} />
        </div>
      ) : null}
    </PlatformLayout>
  );
}
