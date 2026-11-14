import Link from "next/link";

import { PageHeader } from "@/components/charts/Kpi";
import { Forbidden, ShellPage } from "@/components/shell/ShellPage";
import { pick, type Lang } from "@/lib/messages";
import type { ShellPayload } from "@/lib/types";
import { cn } from "@/lib/utils";

const TABS = [
  ["/plataforma", "Resumen", "Overview"],
  ["/plataforma/usuarios", "Usuarios", "Users"],
  ["/plataforma/espacios", "Espacios", "Spaces"],
  ["/plataforma/cursos", "Cursos", "Courses"],
  ["/plataforma/ia", "Proveedor de IA", "AI provider"],
] as const;

/** Marco común de /plataforma/*: solo para la superadministración (ADR-021). */
export function PlatformLayout({
  shell,
  path,
  title,
  description,
  children,
}: {
  shell: ShellPayload;
  path: string;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  const lang: Lang = shell.lang;
  const allowed = Boolean(shell.user.permissions?.platform);
  return (
    <ShellPage shell={shell} path={path} title={title} kicker={pick(lang, "Plataforma", "Platform")}>
      {allowed ? (
        <>
          <PageHeader eyebrow={pick(lang, "Superadministración", "Superadmin")} title={title} description={description} />
          <nav aria-label={pick(lang, "Secciones de la plataforma", "Platform sections")} className="mb-6 overflow-x-auto border-b border-border scrollbar-thin">
            <ul className="m-0 flex min-w-max list-none gap-1 p-0">
              {TABS.map(([href, es, en]) => (
                <li key={href}>
                  <Link
                    href={href}
                    aria-current={path === href ? "page" : undefined}
                    className={cn(
                      "-mb-px block border-b-2 border-transparent px-3 py-2 text-sm text-muted-foreground no-underline hover:text-foreground hover:no-underline",
                      path === href && "border-primary font-medium text-foreground"
                    )}
                  >
                    {pick(lang, es, en)}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          {children}
        </>
      ) : (
        <Forbidden
          lang={lang}
          message={pick(
            lang,
            "Esta sección es solo para la superadministración de la plataforma.",
            "This section is only for platform superadmins."
          )}
        />
      )}
    </ShellPage>
  );
}
