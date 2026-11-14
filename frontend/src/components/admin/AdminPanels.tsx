"use client";

import { Check, Copy, KeyRound, Link2, Plus, RefreshCw, Trash2, UserMinus, Users } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { EmptyState } from "@/components/charts/Kpi";
import { roleLabel } from "@/components/shell/WorkspaceSwitcher";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input, NativeSelect } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { apiDelete, apiPost, apiPut, apiSendPatch } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import { formatDate, relativeDays } from "@/lib/utils";

export interface Member {
  id: number;
  name: string;
  email: string;
  role: string;
  last_login_at: string | null;
  joined_at: string;
  groups: string[];
}

export interface MembersData {
  workspace: { id: number; name: string; join_code: string | null; seat_limit: number | null; plan: string };
  members: Member[];
  me: number;
  my_role: string;
}

function useAction() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function run(fn: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await fn();
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }
  return { run, error, busy };
}

function CopyButton({ value, lang }: { value: string; lang: Lang }) {
  const [done, setDone] = useState(false);
  return (
    <Button
      size="sm"
      variant="outline"
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setDone(true);
        setTimeout(() => setDone(false), 1500);
      }}
    >
      {done ? <Check /> : <Copy />} {done ? pick(lang, "Copiado", "Copied") : pick(lang, "Copiar", "Copy")}
    </Button>
  );
}

export function MembersPanel({ data, csrf, lang }: { data: MembersData; csrf: string; lang: Lang }) {
  const { run, error, busy } = useAction();
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("");
  const isOwner = data.my_role === "owner";
  const rows = data.members.filter(
    (m) =>
      (!role || m.role === role) &&
      (!query || `${m.name} ${m.email}`.toLowerCase().includes(query.toLowerCase()))
  );
  const counts = data.members.reduce<Record<string, number>>((acc, m) => ({ ...acc, [m.role]: (acc[m.role] ?? 0) + 1 }), {});

  return (
    <div className="grid gap-6">
      <Card className="flex flex-wrap items-center gap-4 p-4">
        <span className="grid size-10 place-items-center rounded-lg bg-primary-soft text-primary">
          <KeyRound className="size-5" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="m-0 text-sm font-medium">{pick(lang, "Código de clase", "Class code")}</p>
          <p className="m-0 text-xs text-muted-foreground">
            {pick(lang, "Quien lo introduzca entra como estudiante.", "Anyone who enters it joins as a student.")}{" "}
            {data.workspace.seat_limit
              ? pick(lang, "Plazas: {u}/{l}", "Seats: {u}/{l}").replace("{u}", String(data.members.length)).replace("{l}", String(data.workspace.seat_limit))
              : null}
          </p>
        </div>
        <code className="rounded-md bg-muted px-3 py-1.5 font-mono text-lg tracking-[0.2em]">{data.workspace.join_code}</code>
        {data.workspace.join_code ? <CopyButton value={data.workspace.join_code} lang={lang} /> : null}
        <Button size="sm" variant="ghost" disabled={busy} onClick={() => run(() => apiPost("/api/v1/admin/join-code", {}, csrf))}>
          <RefreshCw /> {pick(lang, "Cambiar", "Rotate")}
        </Button>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>
              {data.members.length} {pick(lang, "miembros", "members")}
            </CardTitle>
            <CardDescription>
              {Object.entries(counts)
                .map(([key, n]) => `${n} ${roleLabel(key, lang).toLowerCase()}`)
                .join(" · ")}
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Input className="w-56" placeholder={pick(lang, "Buscar por nombre o correo", "Search name or email")} value={query} onChange={(e) => setQuery(e.target.value)} aria-label={pick(lang, "Buscar", "Search")} />
            <NativeSelect value={role} onChange={(e) => setRole(e.target.value)} aria-label={pick(lang, "Rol", "Role")}>
              <option value="">{pick(lang, "Todos los roles", "All roles")}</option>
              {["owner", "admin", "teacher", "student"].map((r) => (
                <option key={r} value={r}>
                  {roleLabel(r, lang)}
                </option>
              ))}
            </NativeSelect>
          </div>
        </CardHeader>
        {error ? <p className="mx-5 mb-3 rounded-md bg-destructive-soft px-3 py-2 text-sm text-destructive">{error}</p> : null}
        <Table>
          <THead>
            <TR>
              <TH>{pick(lang, "Nombre", "Name")}</TH>
              <TH>{pick(lang, "Rol", "Role")}</TH>
              <TH>{pick(lang, "Grupos", "Groups")}</TH>
              <TH>{pick(lang, "Último acceso", "Last login")}</TH>
              <TH>{pick(lang, "Alta", "Joined")}</TH>
              <TH className="sr-only">{pick(lang, "Acciones", "Actions")}</TH>
            </TR>
          </THead>
          <TBody>
            {rows.map((member) => {
              const locked = member.role === "owner" && !isOwner;
              return (
                <TR key={member.id}>
                  <TD>
                    <span className="block font-medium">{member.name}</span>
                    <span className="block text-xs text-muted-foreground">{member.email}</span>
                  </TD>
                  <TD>
                    <NativeSelect
                      value={member.role}
                      disabled={busy || locked || member.id === data.me}
                      aria-label={`${pick(lang, "Rol de", "Role of")} ${member.name}`}
                      onChange={(e) => run(() => apiSendPatch(`/api/v1/admin/members/${member.id}`, { role: e.target.value }, csrf))}
                    >
                      {(isOwner ? ["owner", "admin", "teacher", "student"] : ["admin", "teacher", "student"]).map((r) => (
                        <option key={r} value={r}>
                          {roleLabel(r, lang)}
                        </option>
                      ))}
                      {!isOwner && member.role === "owner" ? <option value="owner">{roleLabel("owner", lang)}</option> : null}
                    </NativeSelect>
                  </TD>
                  <TD>
                    <div className="flex flex-wrap gap-1">
                      {member.groups.map((g) => (
                        <Pill key={g} variant="secondary">
                          {g}
                        </Pill>
                      ))}
                    </div>
                  </TD>
                  <TD className="text-muted-foreground">{relativeDays(member.last_login_at, lang)}</TD>
                  <TD className="text-muted-foreground">{formatDate(member.joined_at, lang)}</TD>
                  <TD className="text-right">
                    {member.role !== "owner" && member.id !== data.me ? (
                      <Button
                        size="icon-sm"
                        variant="ghost"
                        aria-label={`${pick(lang, "Expulsar a", "Remove")} ${member.name}`}
                        onClick={() => {
                          if (window.confirm(pick(lang, "¿Quitar a {n} de la academia?", "Remove {n} from the academy?").replace("{n}", member.name)))
                            void run(() => apiDelete(`/api/v1/admin/members/${member.id}`, csrf));
                        }}
                      >
                        <UserMinus />
                      </Button>
                    ) : null}
                  </TD>
                </TR>
              );
            })}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}

export interface GroupsData {
  groups: { id: number; name: string; description: string; member_ids: number[]; enrollments: { course_slug: string; due_at: string | null }[] }[];
  members: { id: number; name: string; role: string }[];
}

export function GroupsPanel({
  data,
  courses,
  csrf,
  lang,
}: {
  data: GroupsData;
  courses: { slug: string; title: string }[];
  csrf: string;
  lang: Lang;
}) {
  const { run, error, busy } = useAction();
  const [name, setName] = useState("");
  const [editing, setEditing] = useState<number | null>(null);
  const [selection, setSelection] = useState<number[]>([]);
  const [course, setCourse] = useState(courses[0]?.slug ?? "");
  const [due, setDue] = useState("");
  const names = new Map(data.members.map((m) => [m.id, m.name]));
  const titles = new Map(courses.map((c) => [c.slug, c.title]));

  return (
    <div className="grid gap-6">
      <Card className="p-4">
        <form
          className="flex flex-wrap items-end gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            void run(async () => {
              await apiPost("/api/v1/admin/groups", { name }, csrf);
              setName("");
            });
          }}
        >
          <Field label={pick(lang, "Nuevo grupo o clase", "New group or class")} htmlFor="group-name" className="min-w-64 flex-1">
            <Input id="group-name" value={name} minLength={2} required onChange={(e) => setName(e.target.value)} placeholder={pick(lang, "Ej.: 2º Bachillerato B", "E.g. Year 12 B")} />
          </Field>
          <Button type="submit" disabled={busy}>
            <Plus /> {pick(lang, "Crear", "Create")}
          </Button>
        </form>
        {error ? <p className="m-0 mt-3 text-sm text-destructive">{error}</p> : null}
      </Card>
      {data.groups.length ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {data.groups.map((group) => (
            <Card key={group.id}>
              <CardHeader>
                <div>
                  <CardTitle>{group.name}</CardTitle>
                  <CardDescription>
                    {group.member_ids.length} {pick(lang, "miembros", "members")}
                  </CardDescription>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditing(editing === group.id ? null : group.id);
                      setSelection(group.member_ids);
                    }}
                  >
                    <Users /> {pick(lang, "Miembros", "Members")}
                  </Button>
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    aria-label={pick(lang, "Borrar grupo", "Delete group")}
                    onClick={() => window.confirm(pick(lang, "¿Borrar el grupo?", "Delete the group?")) && run(() => apiDelete(`/api/v1/admin/groups/${group.id}`, csrf))}
                  >
                    <Trash2 />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="grid gap-3">
                {editing === group.id ? (
                  <div className="grid gap-2 rounded-lg border border-border p-3">
                    <div className="grid max-h-56 gap-1 overflow-y-auto scrollbar-thin">
                      {data.members.map((m) => (
                        <label key={m.id} className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={selection.includes(m.id)}
                            onChange={(e) => setSelection(e.target.checked ? [...selection, m.id] : selection.filter((id) => id !== m.id))}
                          />
                          {m.name} <span className="text-xs text-muted-foreground">· {roleLabel(m.role, lang)}</span>
                        </label>
                      ))}
                    </div>
                    <Button
                      size="sm"
                      className="justify-self-end"
                      disabled={busy}
                      onClick={() =>
                        run(async () => {
                          await apiPut(`/api/v1/admin/groups/${group.id}/members`, { user_ids: selection }, csrf);
                          setEditing(null);
                        })
                      }
                    >
                      {pick(lang, "Guardar miembros", "Save members")}
                    </Button>
                  </div>
                ) : (
                  <p className="m-0 text-sm text-muted-foreground">
                    {group.member_ids.map((id) => names.get(id)).filter(Boolean).join(", ") || pick(lang, "Sin miembros", "No members")}
                  </p>
                )}
                <div>
                  <p className="m-0 mb-1.5 text-xs font-medium text-muted-foreground">{pick(lang, "Cursos asignados", "Assigned courses")}</p>
                  <div className="mb-2 flex flex-wrap gap-1">
                    {group.enrollments.length ? (
                      group.enrollments.map((e, i) => (
                        <Pill key={i}>
                          {titles.get(e.course_slug) ?? e.course_slug}
                          {e.due_at ? ` · ${formatDate(e.due_at, lang)}` : ""}
                        </Pill>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <NativeSelect value={course} onChange={(e) => setCourse(e.target.value)} aria-label={pick(lang, "Curso", "Course")}>
                      {courses.map((c) => (
                        <option key={c.slug} value={c.slug}>
                          {c.title}
                        </option>
                      ))}
                    </NativeSelect>
                    <Input type="date" className="w-40" value={due} onChange={(e) => setDue(e.target.value)} aria-label={pick(lang, "Fecha límite", "Due date")} />
                    <Button
                      size="sm"
                      variant="secondary"
                      disabled={busy || !course}
                      onClick={() => run(() => apiPost(`/api/v1/admin/groups/${group.id}/enrollments`, { course_slug: course, due_at: due || null }, csrf))}
                    >
                      {pick(lang, "Asignar", "Assign")}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState icon={Users} title={pick(lang, "Aún no hay grupos", "No groups yet")} description={pick(lang, "Los grupos permiten asignar cursos con fecha y filtrar la analítica por clase.", "Groups let you assign courses with due dates and filter analytics by class.")} />
      )}
    </div>
  );
}

export interface Invitation {
  id: number;
  email: string | null;
  role: string;
  state: "pending" | "accepted" | "expired" | "revoked";
  created_at: string;
  expires_at: string;
}

export function InvitesPanel({
  invitations,
  groups,
  canInviteAdmins,
  csrf,
  lang,
}: {
  invitations: Invitation[];
  groups: { id: number; name: string }[];
  canInviteAdmins: boolean;
  csrf: string;
  lang: Lang;
}) {
  const { run, error, busy } = useAction();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("student");
  const [group, setGroup] = useState("");
  const [link, setLink] = useState("");
  const state = {
    pending: ["Pendiente", "Pending", "warning"],
    accepted: ["Aceptada", "Accepted", "success"],
    expired: ["Caducada", "Expired", "secondary"],
    revoked: ["Revocada", "Revoked", "secondary"],
  } as const;

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>{pick(lang, "Invitar a la academia", "Invite to the academy")}</CardTitle>
            <CardDescription>
              {pick(
                lang,
                "Genera un enlace de un solo uso (14 días). Si indicas un correo, solo esa cuenta podrá aceptarlo. Cópialo y envíalo por tu canal habitual.",
                "Creates a single-use link (14 days). If you enter an email, only that account can accept it. Copy it and send it through your usual channel."
              )}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-wrap items-end gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              void run(async () => {
                const result = await apiPost<{ path: string }>(
                  "/api/v1/admin/invitations",
                  { email: email || null, role, group_id: group ? Number(group) : null },
                  csrf
                );
                setLink(`${window.location.origin}${result.path}`);
                setEmail("");
              });
            }}
          >
            <Field label={pick(lang, "Correo (opcional)", "Email (optional)")} htmlFor="inv-email" className="min-w-60 flex-1">
              <Input id="inv-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </Field>
            <Field label={pick(lang, "Rol", "Role")} htmlFor="inv-role">
              <NativeSelect id="inv-role" value={role} onChange={(e) => setRole(e.target.value)}>
                {(canInviteAdmins ? ["student", "teacher", "admin"] : ["student", "teacher"]).map((r) => (
                  <option key={r} value={r}>
                    {roleLabel(r, lang)}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field label={pick(lang, "Grupo", "Group")} htmlFor="inv-group">
              <NativeSelect id="inv-group" value={group} onChange={(e) => setGroup(e.target.value)}>
                <option value="">—</option>
                {groups.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Button type="submit" disabled={busy}>
              <Link2 /> {pick(lang, "Crear enlace", "Create link")}
            </Button>
          </form>
          {error ? <p className="m-0 mt-3 text-sm text-destructive">{error}</p> : null}
          {link ? (
            <div className="mt-4 flex flex-wrap items-center gap-2 rounded-lg bg-success-soft p-3">
              <code className="min-w-0 flex-1 truncate text-sm">{link}</code>
              <CopyButton value={link} lang={lang} />
            </div>
          ) : null}
        </CardContent>
      </Card>
      <Card>
        <Table>
          <THead>
            <TR>
              <TH>{pick(lang, "Destinatario", "Recipient")}</TH>
              <TH>{pick(lang, "Rol", "Role")}</TH>
              <TH>{pick(lang, "Estado", "State")}</TH>
              <TH>{pick(lang, "Caduca", "Expires")}</TH>
              <TH className="sr-only">{pick(lang, "Acciones", "Actions")}</TH>
            </TR>
          </THead>
          <TBody>
            {invitations.map((inv) => (
              <TR key={inv.id}>
                <TD>{inv.email ?? <span className="text-muted-foreground">{pick(lang, "Enlace abierto", "Open link")}</span>}</TD>
                <TD>{roleLabel(inv.role, lang)}</TD>
                <TD>
                  <Pill variant={state[inv.state][2]}>{lang === "en" ? state[inv.state][1] : state[inv.state][0]}</Pill>
                </TD>
                <TD className="text-muted-foreground">{formatDate(inv.expires_at, lang)}</TD>
                <TD className="text-right">
                  {inv.state === "pending" ? (
                    <Button size="sm" variant="ghost" onClick={() => run(() => apiDelete(`/api/v1/admin/invitations/${inv.id}`, csrf))}>
                      {pick(lang, "Revocar", "Revoke")}
                    </Button>
                  ) : null}
                </TD>
              </TR>
            ))}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
