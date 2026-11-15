import type { Metadata } from "next";

import { AiProvidersPanel } from "@/components/account/AiProvidersPanel";
import { AccountPanel, type AccountData } from "@/components/admin/AccountPanel";
import { PageHeader } from "@/components/charts/Kpi";
import { allowForbidden, ShellPage } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AiProvidersData } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Mi cuenta", "My account") };
}

export default async function AccountPage() {
  const shell = await getShell("/cuenta");
  const { lang } = shell;
  const data = await apiGet<AccountData>("/api/v1/account");
  // Solo quien crea unidades tiene proveedor propio; el alumnado recibe 403.
  const ai = shell.user.permissions?.author
    ? await allowForbidden(apiGet<AiProvidersData>("/api/v1/account/ai"))
    : null;
  return (
    <ShellPage shell={shell} path="/cuenta" title={pick(lang, "Mi cuenta", "My account")} kicker={shell.user.name}>
      <PageHeader title={pick(lang, "Mi cuenta", "My account")} description={pick(lang, "Perfil, seguridad y espacios.", "Profile, security and workspaces.")} />
      <AccountPanel
        data={data}
        csrf={shell.user.csrf_token}
        lang={lang}
        canOpenPersonal={shell.site.signup_open || Boolean(shell.user.permissions?.platform)}
      />
      {ai ? (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <AiProvidersPanel initial={ai} csrf={shell.user.csrf_token} lang={lang} scope="user" />
        </div>
      ) : null}
    </ShellPage>
  );
}
