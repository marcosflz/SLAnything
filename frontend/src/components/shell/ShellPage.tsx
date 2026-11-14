import { Home, ShieldAlert } from "lucide-react";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";
import { pick, type Lang } from "@/lib/messages";
import type { ShellPayload } from "@/lib/types";

/** Envoltorio común de las páginas nuevas: shell + ancho amplio opcional. */
export function ShellPage({
  shell,
  path,
  title,
  kicker,
  wide = true,
  children,
}: {
  shell: ShellPayload;
  path: string;
  title: string;
  kicker: string;
  wide?: boolean;
  children: React.ReactNode;
}) {
  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={shell.courses}
      progress={shell.progress}
      stats={shell.stats}
      site={shell.site}
      lang={shell.lang}
      pathname={path.split("?")[0]}
      fullPath={path}
      title={title}
      kicker={kicker}
      wide={wide}
    >
      {children}
    </AppShell>
  );
}

export function Forbidden({ lang, message }: { lang: Lang; message?: string }) {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-3 py-16 text-center">
      <span className="grid size-12 place-items-center rounded-full bg-warning-soft text-warning">
        <ShieldAlert className="size-6" aria-hidden="true" />
      </span>
      <h2 className="text-xl font-semibold">{pick(lang, "Acceso restringido", "Restricted access")}</h2>
      <p className="m-0 text-sm text-muted-foreground">
        {message ??
          pick(
            lang,
            "Tu rol en este espacio no permite ver esta sección. Cambia de espacio o pide acceso a la administración.",
            "Your role in this workspace cannot open this section. Switch workspace or ask an admin for access."
          )}
      </p>
      <Button asChild variant="outline">
        <Link href="/">
          <Home /> {pick(lang, "Volver al inicio", "Back home")}
        </Link>
      </Button>
    </div>
  );
}

/** Devuelve null si la API responde 403 (para pintar <Forbidden />). */
export async function allowForbidden<T>(promise: Promise<T>): Promise<T | null> {
  try {
    return await promise;
  } catch (error) {
    if (error instanceof ApiError && error.status === 403) return null;
    throw error;
  }
}
