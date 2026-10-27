import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { PublicShell } from "@/components/PublicShell";
import { LoginForm } from "@/components/auth/LoginForm";
import { getPublic, getSession } from "@/lib/api";
import { t } from "@/lib/messages";

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
            <span className="eyebrow">{t(lang, "Aula LLM · Curso completo")}</span>
            <h2>{t(lang, "Vuelve a donde lo dejaste.")}</h2>
            <p>
              {t(
                lang,
                "Tu progreso, tus apuntes y tus intentos de quiz te esperan. Entra y continúa construyendo intuición sobre los LLM."
              )}
            </p>
          </div>
          <div className="auth-quote">
            {t(
              lang,
              "“Un LLM no devuelve una única palabra: devuelve una probabilidad para cada token posible y elige una.”"
            )}
          </div>
        </section>

        <section className="auth-card">
          <h2>{t(lang, "Entrar")}</h2>
          <p>{t(lang, "Accede con tu correo y contraseña.")}</p>
          <LoginForm lang={lang} next={next} />
          <p className="auth-alt">
            {t(lang, "¿No tienes cuenta?")}{" "}
            <Link href="/registro">{t(lang, "Crear una cuenta gratis")}</Link>
          </p>
          <div className="demo-box">
            <strong>{t(lang, "Cuenta de demostración")}</strong>
            <br />
            {t(lang, "Correo")}: <code>demo@aulallm.local</code>
            <br />
            {t(lang, "Contraseña")}: <code>demo1234</code>
          </div>
        </section>
      </div>
    </PublicShell>
  );
}
