import { Building2 } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";

import { AcceptInvite } from "@/components/admin/AccountPanel";
import { roleLabel } from "@/components/shell/WorkspaceSwitcher";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ApiError, apiGet, getLang, getSession } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Invitación", "Invitation") };
}

/** Página pública: muestra la invitación y permite aceptarla tras entrar o registrarse. */
export default async function InvitationPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const lang = await getLang();
  const session = await getSession();
  let invite: { workspace: string; role: string; email: string | null } | null = null;
  try {
    invite = await apiGet(`/api/v1/invitations/${encodeURIComponent(token)}`);
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 404)) throw error;
  }
  const next = encodeURIComponent(`/invitacion/${token}`);
  return (
    <main className="grid min-h-dvh place-items-center bg-background p-4">
      <Card className="w-full max-w-md p-6 text-center">
        <span className="mx-auto mb-3 grid size-12 place-items-center rounded-full bg-primary-soft text-primary">
          <Building2 className="size-6" aria-hidden="true" />
        </span>
        {invite ? (
          <>
            <h1 className="text-xl font-semibold">{pick(lang, "Te han invitado a {w}", "You are invited to {w}").replace("{w}", invite.workspace)}</h1>
            <p className="m-0 mt-2 mb-5 text-sm text-muted-foreground">
              {pick(lang, "Rol", "Role")}: {roleLabel(invite.role, lang)}
              {invite.email ? ` · ${invite.email}` : ""}
            </p>
            {session.user ? (
              <AcceptInvite token={token} csrf={session.csrf_token} lang={lang} />
            ) : (
              <div className="grid gap-2">
                <Button asChild>
                  <Link href={`/registro?next=${next}`}>{pick(lang, "Crear cuenta y aceptar", "Sign up and accept")}</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href={`/entrar?next=${next}`}>{pick(lang, "Ya tengo cuenta", "I already have an account")}</Link>
                </Button>
              </div>
            )}
          </>
        ) : (
          <>
            <h1 className="text-xl font-semibold">{pick(lang, "Invitación no válida", "Invalid invitation")}</h1>
            <p className="m-0 mt-2 mb-5 text-sm text-muted-foreground">
              {pick(lang, "El enlace ha caducado, ya se usó o fue revocado. Pide uno nuevo a tu academia.", "The link expired, was already used or was revoked. Ask your academy for a new one.")}
            </p>
            <Button asChild variant="outline">
              <Link href="/">{pick(lang, "Ir al inicio", "Go home")}</Link>
            </Button>
          </>
        )}
      </Card>
    </main>
  );
}
