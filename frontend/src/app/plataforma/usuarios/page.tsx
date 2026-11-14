import type { Metadata } from "next";

import { PlatformLayout } from "@/components/platform/PlatformLayout";
import { PlatformUsersPanel } from "@/components/platform/PlatformPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { PlatformUser } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Usuarios", "Users") };
}

export default async function PlatformUsersPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q = "" } = await searchParams;
  const path = q ? `/plataforma/usuarios?q=${encodeURIComponent(q)}` : "/plataforma/usuarios";
  const shell = await getShell(path);
  const { lang } = shell;
  const data = shell.user.permissions?.platform
    ? await allowForbidden(
        apiGet<{ users: PlatformUser[]; total: number; me: number }>(`/api/v1/platform/users?limit=200&q=${encodeURIComponent(q)}`)
      )
    : null;
  return (
    <PlatformLayout
      shell={shell}
      path="/plataforma/usuarios"
      title={pick(lang, "Usuarios", "Users")}
      description={pick(lang, "Todas las cuentas de la plataforma, sus espacios y su acceso.", "Every account on the platform, its spaces and its access.")}
    >
      {data ? (
        <PlatformUsersPanel users={data.users} total={data.total} me={data.me} query={q} csrf={shell.user.csrf_token} lang={lang} />
      ) : null}
    </PlatformLayout>
  );
}
