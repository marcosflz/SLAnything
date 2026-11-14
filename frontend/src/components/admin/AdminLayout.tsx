import Link from "next/link";

import { PageHeader } from "@/components/charts/Kpi";
import { Forbidden, ShellPage } from "@/components/shell/ShellPage";
import { pick, type Lang } from "@/lib/messages";
import type { ShellPayload } from "@/lib/types";
import { cn } from "@/lib/utils";

const TABS = [
  ["/admin", "Resumen", "Overview"],
  ["/admin/usuarios", "Miembros", "Members"],
  ["/admin/grupos", "Grupos", "Groups"],
  ["/admin/invitaciones", "Invitaciones", "Invitations"],
  ["/admin/auditoria", "Auditoría", "Audit log"],
] as const;

/** Marco común de /admin/*: shell, cabecera y pestañas. */
export function AdminLayout({
  shell,
  path,
  title,
  description,
  allowed,
  children,
}: {
  shell: ShellPayload;
  path: string;
  title: string;
  description?: string;
  allowed: boolean;
  children: React.ReactNode;
}) {
  const lang: Lang = shell.lang;
  const workspace = shell.user.workspace;
  // El profesorado sin gestión solo ve sus invitaciones de alumnado (ADR-022).
  const tabs = shell.user.permissions?.manage ? TABS : TABS.filter(([href]) => href === "/admin/invitaciones");
  return (
    <ShellPage shell={shell} path={path} title={title} kicker={pick(lang, "Administración", "Management")}>
      {allowed && workspace?.kind === "organization" ? (
        <>
          <PageHeader eyebrow={workspace.name} title={title} description={description} />
          <nav aria-label={pick(lang, "Secciones de administración", "Management sections")} className="mb-6 overflow-x-auto border-b border-border scrollbar-thin">
            <ul className="m-0 flex min-w-max list-none gap-1 p-0">
              {tabs.map(([href, es, en]) => (
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
            "La administración solo está disponible para owners y admins de una academia. Cambia de espacio o crea una academia desde el selector.",
            "Management is only available to academy owners and admins. Switch workspace or create an academy from the switcher."
          )}
        />
      )}
    </ShellPage>
  );
}
