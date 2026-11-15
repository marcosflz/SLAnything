import type { Metadata } from "next";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { EmptyState } from "@/components/charts/Kpi";
import { allowForbidden } from "@/components/shell/ShellPage";
import { Card } from "@/components/ui/card";
import { Pill } from "@/components/ui/pill";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Auditoría", "Audit log") };
}

interface Entry {
  id: number;
  ts: string;
  action: string;
  target: string;
  ip: string;
  actor_name: string | null;
  actor_email: string | null;
  meta: Record<string, unknown>;
}

const LABELS: Record<string, [string, string]> = {
  "member.role": ["Cambio de rol", "Role change"],
  "member.remove": ["Miembro expulsado", "Member removed"],
  "member.join_code": ["Alta con código", "Joined with code"],
  "invite.create": ["Invitación creada", "Invitation created"],
  "invite.revoke": ["Invitación revocada", "Invitation revoked"],
  "invite.accept": ["Invitación aceptada", "Invitation accepted"],
  "group.create": ["Grupo creado", "Group created"],
  "group.delete": ["Grupo borrado", "Group deleted"],
  "group.enroll": ["Curso asignado", "Course assigned"],
  "course.publish": ["Unidad publicada", "Unit published"],
  "course.unpublish": ["Unidad retirada", "Unit unpublished"],
  "course.delete": ["Unidad borrada", "Unit deleted"],
  "workspace.ai.update": ["Clave de IA de la academia", "Academy AI key"],
  "workspace.ai.delete": ["Clave de IA quitada", "Academy AI key removed"],
  "course.edit": ["Unidad editada", "Unit edited"],
  "workspace.create": ["Academia creada", "Academy created"],
  "workspace.join_code": ["Código de clase cambiado", "Class code rotated"],
};

export default async function AuditPage() {
  const shell = await getShell("/admin/auditoria");
  const { lang } = shell;
  const data = await allowForbidden(apiGet<{ entries: Entry[] }>("/api/v1/admin/audit"));
  const fmt = new Intl.DateTimeFormat(lang === "en" ? "en-GB" : "es-ES", { dateStyle: "medium", timeStyle: "short" });
  return (
    <AdminLayout
      shell={shell}
      path="/admin/auditoria"
      title={pick(lang, "Registro de auditoría", "Audit log")}
      description={pick(lang, "Las últimas 200 acciones sensibles del espacio.", "The latest 200 sensitive actions in this workspace.")}
      allowed={Boolean(data)}
    >
      {data?.entries.length ? (
        <Card>
          <Table>
            <THead>
              <TR>
                <TH>{pick(lang, "Fecha", "Date")}</TH>
                <TH>{pick(lang, "Quién", "Who")}</TH>
                <TH>{pick(lang, "Acción", "Action")}</TH>
                <TH>{pick(lang, "Objeto", "Target")}</TH>
                <TH>IP</TH>
              </TR>
            </THead>
            <TBody>
              {data.entries.map((entry) => (
                <TR key={entry.id}>
                  <TD className="whitespace-nowrap text-muted-foreground">{fmt.format(new Date(entry.ts))}</TD>
                  <TD>{entry.actor_name ?? "—"}</TD>
                  <TD>
                    <Pill variant="secondary">{LABELS[entry.action] ? pick(lang, ...LABELS[entry.action]) : entry.action}</Pill>
                  </TD>
                  <TD className="max-w-xs truncate">
                    {entry.target}
                    {entry.meta?.to ? ` → ${String(entry.meta.to)}` : ""}
                  </TD>
                  <TD className="font-mono text-xs text-muted-foreground">{entry.ip}</TD>
                </TR>
              ))}
            </TBody>
          </Table>
        </Card>
      ) : data ? (
        <EmptyState title={pick(lang, "Sin actividad registrada todavía", "No activity recorded yet")} />
      ) : null}
    </AdminLayout>
  );
}
