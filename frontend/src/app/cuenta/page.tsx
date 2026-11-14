import type { Metadata } from "next";

import { AccountPanel, type AccountData } from "@/components/admin/AccountPanel";
import { PageHeader } from "@/components/charts/Kpi";
import { ShellPage } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Mi cuenta", "My account") };
}

export default async function AccountPage() {
  const shell = await getShell("/cuenta");
  const { lang } = shell;
  const data = await apiGet<AccountData>("/api/v1/account");
  return (
    <ShellPage shell={shell} path="/cuenta" title={pick(lang, "Mi cuenta", "My account")} kicker={shell.user.name}>
      <PageHeader title={pick(lang, "Mi cuenta", "My account")} description={pick(lang, "Perfil, seguridad y espacios.", "Profile, security and workspaces.")} />
      <AccountPanel data={data} csrf={shell.user.csrf_token} lang={lang} />
    </ShellPage>
  );
}
