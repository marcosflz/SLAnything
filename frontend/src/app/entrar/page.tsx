import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { PublicShell } from "@/components/PublicShell";
import { LoginForm } from "@/components/auth/LoginForm";
import { getPublic, getSession } from "@/lib/api";
import { pick, t } from "@/lib/messages";
import type { DemoAccount } from "@/lib/types";

const DEMO_LABELS: Record<DemoAccount["profile"], [string, string]> = {
  student: ["Alumno", "Student"],
  teacher: ["Profesora (academia)", "Teacher (academy)"],
  academy_admin: ["Administración (academia)", "Academy admin"],
  self_learner: ["Cuenta individual", "Individual account"],
  platform: ["Superadmin", "Superadmin"],
};

export const metadata: Metadata = { title: "Entrar" };

type LoginPageProps = {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

function safeNext(value: string | string[] | undefined): string {
  const next = Array.isArray(value) ? value[0] : value;
  if (!next || !next.startsWith("/") || next.startsWith("//")) {
    return "/";
  }
  return next;
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const session = await getSession();
  if (session.user) {
    redirect("/");
  }

  const [publicData, params] = await Promise.all([getPublic(), searchParams]);
  const { site, lang } = publicData;
  const next = safeNext(params.next);
  const fullPath =
    next === "/" ? "/entrar" : `/entrar?next=${encodeURIComponent(next)}`;

  return (
    <PublicShell site={site} lang={lang} fullPath={fullPath}>
      <div className="auth-wrap">
        <section className="auth-art">
          <div>
            <span className="eyebrow">{site.name}</span>
            <h2>{t(lang, "Vuelve a donde lo dejaste.")}</h2>
            <p>
              {pick(
                lang,
                "Tus cursos, tu progreso, tus apuntes y tus unidades en borrador te esperan.",
                "Your courses, progress, notes and draft units are waiting for you."
              )}
            </p>
          </div>
          <div className="auth-quote">
            {pick(
              lang,
              "“Aprender es convertir información en algo que puedes explicar con tus palabras.”",
              "“Learning is turning information into something you can explain in your own words.”"
            )}
          </div>
        </section>

        <section className="auth-card">
          <h2>{t(lang, "Entrar")}</h2>
          <p>{t(lang, "Accede con tu correo y contraseña.")}</p>
          <LoginForm lang={lang} next={next} />
          <p className="auth-alt">
            {site.signup_open ? (
              <>
                {t(lang, "¿No tienes cuenta?")}{" "}
                <Link href="/registro">{t(lang, "Crear una cuenta gratis")}</Link>
              </>
            ) : (
              pick(
                lang,
                "¿No tienes cuenta? El acceso es por invitación: abre el enlace que te hayan enviado.",
                "No account? Access is by invitation: open the link you were sent."
              )
            )}
          </p>
          {publicData.demo_accounts.length ? (
            <div className="demo-box">
              <strong>{pick(lang, "Cuentas de demostración", "Demo accounts")}</strong>
              {publicData.demo_accounts.map((account) => (
                <div key={account.email} className="mt-1">
                  {DEMO_LABELS[account.profile][lang === "en" ? 1 : 0]}: <code>{account.email}</code> ·{" "}
                  <code>{account.password}</code>
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </PublicShell>
  );
}
