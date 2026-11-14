import type { Metadata } from "next";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { InvitesPanel, type GroupsData, type Invitation } from "@/components/admin/AdminPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Invitaciones", "Invitations") };
}

export default async function InvitationsPage() {
  const shell = await getShell("/admin/invitaciones");
  const { lang } = shell;
  const [data, groups] = await Promise.all([
    allowForbidden(apiGet<{ invitations: Invitation[] }>("/api/v1/admin/invitations")),
    allowForbidden(apiGet<GroupsData>("/api/v1/admin/groups")),
  ]);
  return (
    <AdminLayout
      shell={shell}
      path="/admin/invitaciones"
      title={pick(lang, "Invitaciones", "Invitations")}
      description={pick(lang, "Enlaces de un solo uso para incorporar profesorado y estudiantes.", "Single-use links to bring in teachers and students.")}
      allowed={Boolean(data)}
    >
      {data ? (
        <InvitesPanel
          invitations={data.invitations}
          groups={(groups?.groups ?? []).map((g) => ({ id: g.id, name: g.name }))}
          canInviteAdmins={shell.user.ws_role === "owner"}
          csrf={shell.user.csrf_token}
          lang={lang}
        />
      ) : null}
    </AdminLayout>
  );
}
