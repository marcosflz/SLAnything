import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { ShellPage } from "@/components/shell/ShellPage";
import { Welcome } from "@/components/shell/Welcome";
import { getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Bienvenida", "Welcome") };
}

/** Punto de entrada para usuarios sin espacio de trabajo. */
export default async function WelcomePage() {
  const shell = await getShell("/bienvenida");
  if (shell.user.workspace) redirect("/");
  const { lang } = shell;
  return (
    <ShellPage shell={shell} path="/bienvenida" title={pick(lang, "Bienvenida", "Welcome")} kicker={shell.user.name} wide={false}>
      <Welcome
        csrf={shell.user.csrf_token}
        lang={lang}
        canCreateSpaces={shell.site.signup_open || Boolean(shell.user.permissions?.platform)}
      />
    </ShellPage>
  );
}
