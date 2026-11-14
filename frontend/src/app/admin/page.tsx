import { Activity, BookOpen, Sparkles, Users } from "lucide-react";
import type { Metadata } from "next";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { roleLabel } from "@/components/shell/WorkspaceSwitcher";
import { AreaTrend } from "@/components/charts/Charts";
import { KpiCard } from "@/components/charts/Kpi";
import { allowForbidden } from "@/components/shell/ShellPage";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { WorkspaceMetrics } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Administración", "Management") };
}

export default async function AdminHome() {
  const shell = await getShell("/admin");
  const { lang } = shell;
  const data = await allowForbidden(apiGet<WorkspaceMetrics>("/api/v1/admin/metrics"));
  return (
    <AdminLayout
      shell={shell}
      path="/admin"
      title={pick(lang, "Resumen de la academia", "Academy overview")}
      description={pick(lang, "Uso, miembros, contenidos y generación.", "Usage, members, content and generation.")}
      allowed={Boolean(data)}
    >
      {data ? (
        <div className="grid gap-6">
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              label={pick(lang, "Miembros", "Members")}
              value={data.seat_limit ? `${data.members}/${data.seat_limit}` : data.members}
              icon={Users}
              hint={Object.entries(data.roles)
                .map(([role, n]) => `${n} ${roleLabel(role, lang).toLowerCase()}`)
                .join(" · ")}
            />
            <KpiCard
              label={pick(lang, "Activos hoy / semana", "Active today / week")}
              value={`${data.dau} / ${data.wau}`}
              icon={Activity}
              tone="success"
              spark={data.daily_active.slice(-14).map((d) => d.active)}
            />
            <KpiCard
              label={pick(lang, "Unidades publicadas", "Published units")}
              value={data.courses.published ?? 0}
              icon={BookOpen}
              tone="violet"
              hint={`${data.courses.draft ?? 0} ${pick(lang, "borradores", "drafts")}`}
            />
            <KpiCard
              label={pick(lang, "Generaciones con éxito", "Successful generations")}
              value={data.jobs.success_rate === null ? "—" : `${data.jobs.success_rate}%`}
              icon={Sparkles}
              tone="warning"
              hint={data.jobs.avg_minutes ? `${data.jobs.avg_minutes} min ${pick(lang, "de media", "on average")}` : undefined}
            />
          </section>
          <Card>
            <CardHeader>
              <div>
                <CardTitle>{pick(lang, "Usuarios activos por día", "Daily active users")}</CardTitle>
                <CardDescription>{pick(lang, "Últimos 30 días", "Last 30 days")}</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <AreaTrend
                data={data.daily_active.map((d) => ({ day: formatDate(d.day, lang), active: d.active }))}
                x="day"
                y="active"
                label={pick(lang, "Usuarios activos por día", "Daily active users")}
              />
            </CardContent>
          </Card>
        </div>
      ) : null}
    </AdminLayout>
  );
}
