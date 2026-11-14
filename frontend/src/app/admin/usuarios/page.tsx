import type { Metadata } from "next";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { MembersPanel, type MembersData } from "@/components/admin/AdminPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Miembros", "Members") };
}

export default async function MembersPage() {
  const shell = await getShell("/admin/usuarios");
  const { lang } = shell;
  const data = await allowForbidden(apiGet<MembersData>("/api/v1/admin/members"));
  return (
    <AdminLayout
      shell={shell}
      path="/admin/usuarios"
      title={pick(lang, "Miembros", "Members")}
      description={pick(lang, "Roles, accesos y grupos de cada persona.", "Roles, access and groups for each person.")}
      allowed={Boolean(data)}
    >
      {data ? <MembersPanel data={data} csrf={shell.user.csrf_token} lang={lang} /> : null}
    </AdminLayout>
  );
}
