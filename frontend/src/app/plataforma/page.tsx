import { BookOpen, Building2, Sparkles, Users } from "lucide-react";
import type { Metadata } from "next";

import { KpiCard } from "@/components/charts/Kpi";
import { PlatformLayout } from "@/components/platform/PlatformLayout";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { PlatformOverview } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Plataforma", "Platform") };
}

export default async function PlatformPage() {
  const shell = await getShell("/plataforma");
  const { lang } = shell;
  const data = shell.user.permissions?.platform
    ? await allowForbidden(apiGet<PlatformOverview>("/api/v1/platform/overview"))
    : null;
  return (
    <PlatformLayout
      shell={shell}
      path="/plataforma"
      title={pick(lang, "Resumen de la plataforma", "Platform overview")}
      description={pick(lang, "Uso global: cuentas, academias, cursos y generaciones.", "Global usage: accounts, academies, courses and generations.")}
    >
      {data ? (
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label={pick(lang, "Usuarios", "Users")}
            value={data.users.total}
            icon={Users}
            hint={pick(lang, "Activos esta semana: {a} · desactivados: {d}", "Active this week: {a} · disabled: {d}")
              .replace("{a}", String(data.users.wau))
              .replace("{d}", String(data.users.disabled))}
          />
          <KpiCard
            label={pick(lang, "Espacios", "Spaces")}
            value={data.workspaces.organization + data.workspaces.personal}
            icon={Building2}
            tone="violet"
            hint={pick(lang, "Academias: {o} · cuentas individuales: {p}", "Academies: {o} · individual accounts: {p}")
              .replace("{o}", String(data.workspaces.organization))
              .replace("{p}", String(data.workspaces.personal))}
          />
          <KpiCard
            label={pick(lang, "Cursos publicados", "Published courses")}
            value={data.courses.published}
            icon={BookOpen}
            tone="success"
            hint={pick(lang, "Abiertos: {p} · en borrador: {d}", "Open: {p} · drafts: {d}")
              .replace("{p}", String(data.courses.public))
              .replace("{d}", String(data.courses.draft))}
          />
          <KpiCard
            label={pick(lang, "Generaciones este mes", "Generations this month")}
            value={data.jobs.month}
            icon={Sparkles}
            tone="warning"
            hint={pick(lang, "Fallidas: {f}", "Failed: {f}").replace("{f}", String(data.jobs.failed_month))}
          />
        </section>
      ) : null}
    </PlatformLayout>
  );
}
