import type { Metadata } from "next";

import { PlatformLayout } from "@/components/platform/PlatformLayout";
import { PlatformInvitationsPanel } from "@/components/platform/PlatformPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { PlatformInvitation } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Invitaciones", "Invitations") };
}

export default async function PlatformInvitationsPage() {
  const shell = await getShell("/plataforma/invitaciones");
  const { lang } = shell;
  const data = shell.user.permissions?.platform
    ? await allowForbidden(
        apiGet<{ invitations: PlatformInvitation[]; academies: { id: number; name: string }[] }>(
          "/api/v1/platform/invitations"
        )
      )
    : null;
  return (
    <PlatformLayout
      shell={shell}
      path="/plataforma/invitaciones"
      title={pick(lang, "Invitaciones", "Invitations")}
      description={pick(
        lang,
        "Cuentas individuales y profesorado entran por invitación de la plataforma.",
        "Individual accounts and teachers join by platform invitation."
      )}
    >
      {data ? (
        <PlatformInvitationsPanel
          invitations={data.invitations}
          academies={data.academies}
          csrf={shell.user.csrf_token}
          lang={lang}
        />
      ) : null}
    </PlatformLayout>
  );
}
