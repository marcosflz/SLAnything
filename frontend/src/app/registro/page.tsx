import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { PublicShell } from "@/components/PublicShell";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { getPublic, getSession } from "@/lib/api";
import { t } from "@/lib/messages";

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

export default async function RegisterPage({ searchParams }: RegisterPageProps) {
  const session = await getSession();
  if (session.user) {
    redirect("/");
  }

  const [publicData, params] = await Promise.all([getPublic(), searchParams]);
  const { site, lang } = publicData;
  const next = safeNext(params.next);
  const fullPath =
    next === "/" ? "/registro" : `/registro?next=${encodeURIComponent(next)}`;

  return (
    <PublicShell site={site} lang={lang} fullPath={fullPath}>
      <div className="auth-wrap">
        <section className="auth-art">
          <div>
            <span className="eyebrow">{t(lang, "Aula LLM · Curso completo")}</span>
            <h2>{t(lang, "Empieza por entender. Termina construyendo.")}</h2>
            <p>
              {t(
                lang,
                "Ocho lecciones, siete laboratorios y un quiz. Sin instalar nada y sin GPU. Tu progreso se guarda automáticamente."
              )}
            </p>
          </div>
          <div className="auth-quote">
            {t(
              lang,
              "“Predecir la siguiente palabra parece simple. De esa tarea emergen la gramática, el estilo y buena parte del razonamiento.”"
            )}
          </div>
        </section>

        <section className="auth-card">
          <h2>{t(lang, "Crear cuenta")}</h2>
          <p>
            {t(
              lang,
              "Gratis, sin tarjeta. Solo necesitas un correo y una contraseña."
            )}
          </p>
          <RegisterForm lang={lang} next={next} />
          <p className="auth-alt">
            {t(lang, "¿Ya tienes cuenta?")}{" "}
            <Link href="/entrar">{t(lang, "Entrar")}</Link>
          </p>
        </section>
      </div>
    </PublicShell>
  );
}
