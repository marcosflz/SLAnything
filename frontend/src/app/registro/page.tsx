import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { PublicShell } from "@/components/PublicShell";
import { Icon } from "@/components/ui";
import { RegisterForm, type AccountType } from "@/components/auth/RegisterForm";
import { invitationLabel } from "@/lib/roles";
import { ApiError, apiGet, getPublic, getSession } from "@/lib/api";
import { pick, t } from "@/lib/messages";
import type { InvitationInfo } from "@/lib/types";

export const metadata: Metadata = { title: "Crear cuenta" };

type RegisterPageProps = {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

function safeNext(value: string | string[] | undefined): string {
  const next = Array.isArray(value) ? value[0] : value;
  if (!next || !next.startsWith("/") || next.startsWith("//")) {
    return "/";
  }
  return next;
}

const TYPE_PARAM: Record<string, AccountType> = {
  individual: "individual",
  academia: "academy",
  codigo: "join",
};

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function RegisterPage({ searchParams }: RegisterPageProps) {
  const session = await getSession();
  if (session.user) {
    redirect("/");
  }

  const [publicData, params] = await Promise.all([getPublic(), searchParams]);
  const { site, lang } = publicData;
  const next = safeNext(params.next);
  const initialType = TYPE_PARAM[first(params.tipo) ?? ""] ?? "individual";
  const invite = first(params.invite);
  let inviteInfo: InvitationInfo | null = null;
  if (invite) {
    try {
      inviteInfo = await apiGet(`/api/v1/invitations/${encodeURIComponent(invite)}`);
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 404)) throw error;
    }
  }
  const query = new URLSearchParams();
  if (next !== "/") query.set("next", next);
  if (first(params.tipo)) query.set("tipo", first(params.tipo) as string);
  if (invite) query.set("invite", invite);
  const fullPath = query.toString() ? `/registro?${query.toString()}` : "/registro";

  return (
    <PublicShell site={site} lang={lang} fullPath={fullPath}>
      <div className="auth-wrap">
        <section className="auth-art">
          <div>
            <span className="eyebrow">{site.name}</span>
            <h2>{pick(lang, "Tu material, convertido en un curso.", "Your material, turned into a course.")}</h2>
            <p>
              {pick(
                lang,
                "Con una cuenta individual estudias y creas tus propias unidades. Con una academia, además, gestionas profesorado, alumnado, grupos y analítica.",
                "With an individual account you study and create your own units. With an academy you also manage teachers, students, groups and analytics."
              )}
            </p>
          </div>
          <div className="auth-quote">
            {pick(
              lang,
              "“Si algo no está en tu documento, no aparece en la lección: cada bloque cita su página.”",
              "“If something isn't in your document, it isn't in the lesson: every block cites its page.”"
            )}
          </div>
        </section>

        <section className="auth-card">
          <h2>{t(lang, "Crear cuenta")}</h2>
          {invite && !inviteInfo ? (
            <div className="flash flash-danger" role="alert">
              {site.signup_open
                ? pick(lang, "La invitación ha caducado o ya se usó. Puedes crear una cuenta normal.", "The invitation expired or was already used. You can create a regular account.")
                : pick(lang, "La invitación ha caducado, ya se usó o fue revocada. Pide un enlace nuevo.", "The invitation expired, was already used or was revoked. Ask for a new link.")}
            </div>
          ) : null}
          {inviteInfo || site.signup_open ? (
            <>
              <p>
                {t(
                  lang,
                  "Gratis, sin tarjeta. Solo necesitas un correo y una contraseña."
                )}
              </p>
              <RegisterForm
                lang={lang}
                next={next}
                initialType={initialType}
                invite={inviteInfo ? invite : undefined}
                inviteLabel={inviteInfo ? invitationLabel(inviteInfo, lang) : undefined}
                inviteEmail={inviteInfo?.email ?? undefined}
                askAcademyName={Boolean(inviteInfo?.needs_academy_name)}
              />
            </>
          ) : (
            <div className="flash flash-warning" role="status">
              <Icon name="key" />{" "}
              <span>
                {pick(
                  lang,
                  "El registro es solo por invitación. Si te han invitado, abre el enlace que recibiste. La administración de la plataforma invita a cuentas individuales y profesorado; el profesorado invita a su alumnado.",
                  "Sign-up is by invitation only. If you were invited, open the link you received. Platform administrators invite individual accounts and teachers; teachers invite their students."
                )}
              </span>
            </div>
          )}
          <p className="auth-alt">
            {t(lang, "¿Ya tienes cuenta?")}{" "}
            <Link href="/entrar">{t(lang, "Entrar")}</Link>
          </p>
        </section>
      </div>
    </PublicShell>
  );
}
