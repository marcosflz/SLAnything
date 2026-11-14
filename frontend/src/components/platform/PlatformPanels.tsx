"use client";

import { Ban, Check, Copy, Eye, EyeOff, Link2, Search, ShieldCheck, ShieldOff, Trash2, Undo2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { EmptyState } from "@/components/charts/Kpi";
import { roleLabel } from "@/lib/roles";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input, NativeSelect } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { apiDelete, apiPost, apiSendPatch } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AuthoringCourse, PlatformInvitation, PlatformUser, PlatformWorkspace } from "@/lib/types";
import { formatDate, relativeDays } from "@/lib/utils";

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

function ErrorLine({ error }: { error: string }) {
  return error ? <p className="m-0 mb-3 rounded-md bg-destructive-soft px-3 py-2 text-sm text-destructive">{error}</p> : null;
}

// ---------------------------------------------------------------------------
// Usuarios
// ---------------------------------------------------------------------------

export function PlatformUsersPanel({
  users,
  total,
  me,
  query,
  csrf,
  lang,
}: {
  users: PlatformUser[];
  total: number;
  me: number;
  query: string;
  csrf: string;
  lang: Lang;
}) {
  const { run, error, busy } = useAction();
  return (
    <Card>
      <CardContent className="pt-5">
        <form method="get" className="mb-4 flex gap-2">
          <Input name="q" defaultValue={query} placeholder={pick(lang, "Buscar por nombre o correo", "Search by name or email")} aria-label={pick(lang, "Buscar", "Search")} />
          <Button type="submit" variant="outline">
            <Search /> {pick(lang, "Buscar", "Search")}
          </Button>
        </form>
        <ErrorLine error={error} />
        <p className="m-0 mb-2 text-xs text-muted-foreground">
          {pick(lang, "{n} usuarios", "{n} users").replace("{n}", String(total))}
        </p>
        <Table>
          <THead>
            <TR>
              <TH>{pick(lang, "Usuario", "User")}</TH>
              <TH>{pick(lang, "Espacios", "Spaces")}</TH>
              <TH>{pick(lang, "Último acceso", "Last login")}</TH>
              <TH className="text-right">{pick(lang, "Acciones", "Actions")}</TH>
            </TR>
          </THead>
          <TBody>
            {users.map((user) => (
              <TR key={user.id}>
                <TD>
                  <span className="block font-medium">
                    {user.name}{" "}
                    {user.is_platform_admin ? <Pill variant="violet">Superadmin</Pill> : null}{" "}
                    {user.disabled_at ? <Pill variant="destructive">{pick(lang, "Desactivado", "Disabled")}</Pill> : null}
                  </span>
                  <span className="text-xs text-muted-foreground">{user.email}</span>
                </TD>
                <TD>
                  <span className="flex flex-wrap gap-1">
                    {user.workspaces.length ? (
                      user.workspaces.map((ws) => (
                        <Pill key={ws.id} variant="outline">
                          {ws.kind === "personal" ? pick(lang, "Individual", "Individual") : `${ws.name} · ${roleLabel(ws.role, lang)}`}
                        </Pill>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </span>
                </TD>
                <TD className="text-sm text-muted-foreground">{user.last_login_at ? relativeDays(user.last_login_at, lang) : "—"}</TD>
                <TD className="text-right">
                  {user.id !== me ? (
                    <span className="inline-flex gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={busy}
                        onClick={() => run(() => apiSendPatch(`/api/v1/platform/users/${user.id}`, { is_platform_admin: !user.is_platform_admin }, csrf))}
                        title={user.is_platform_admin ? pick(lang, "Quitar superadmin", "Remove superadmin") : pick(lang, "Hacer superadmin", "Make superadmin")}
                      >
                        {user.is_platform_admin ? <ShieldOff /> : <ShieldCheck />}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={busy}
                        onClick={() => run(() => apiSendPatch(`/api/v1/platform/users/${user.id}`, { disabled: !user.disabled_at }, csrf))}
                        title={user.disabled_at ? pick(lang, "Reactivar", "Re-enable") : pick(lang, "Desactivar", "Disable")}
                      >
                        {user.disabled_at ? <Undo2 /> : <Ban />}
                      </Button>
                    </span>
                  ) : (
                    <span className="text-xs text-muted-foreground">{pick(lang, "Tú", "You")}</span>
                  )}
                </TD>
              </TR>
            ))}
          </TBody>
        </Table>
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Espacios
// ---------------------------------------------------------------------------

function WorkspaceRow({ ws, csrf, lang, run, busy }: { ws: PlatformWorkspace; csrf: string; lang: Lang; run: (fn: () => Promise<unknown>) => void; busy: boolean }) {
  const [quota, setQuota] = useState(ws.settings.gen_monthly?.toString() ?? "");
  const [seats, setSeats] = useState(ws.seat_limit?.toString() ?? "");
  function save() {
    run(() =>
      apiSendPatch(
        `/api/v1/platform/workspaces/${ws.id}`,
        {
          ...(quota === "" ? { clear_gen_monthly: true } : { gen_monthly: Number(quota) }),
          ...(seats === "" ? { clear_seat_limit: true } : { seat_limit: Number(seats) }),
        },
        csrf
      )
    );
  }
  return (
    <TR>
      <TD>
        <span className="block font-medium">{ws.name}</span>
        <span className="text-xs text-muted-foreground">
          {ws.kind === "personal" ? pick(lang, "Cuenta individual", "Individual account") : pick(lang, "Academia", "Academy")} ·{" "}
          {ws.owner_email ?? "—"}
        </span>
      </TD>
      <TD className="tabular text-sm">{ws.members}</TD>
      <TD className="tabular text-sm">{ws.courses}</TD>
      <TD className="tabular text-sm">{ws.jobs_month}</TD>
      <TD>
        <Input
          className="w-24"
          type="number"
          min={0}
          value={quota}
          onChange={(event) => setQuota(event.target.value)}
          placeholder={pick(lang, "global", "global")}
          aria-label={pick(lang, "Cuota mensual de generaciones", "Monthly generation quota")}
        />
      </TD>
      <TD>
        {ws.kind === "organization" ? (
          <Input
            className="w-24"
            type="number"
            min={0}
            value={seats}
            onChange={(event) => setSeats(event.target.value)}
            placeholder="∞"
            aria-label={pick(lang, "Plazas", "Seats")}
          />
        ) : (
          <span className="text-xs text-muted-foreground">—</span>
        )}
      </TD>
      <TD className="text-right">
        <span className="inline-flex gap-1">
          <Button size="sm" variant="secondary" disabled={busy} onClick={save}>
            {pick(lang, "Guardar", "Save")}
          </Button>
          {ws.kind === "organization" && ws.courses === 0 ? (
            <Button
              size="sm"
              variant="ghost"
              disabled={busy}
              title={pick(lang, "Borrar academia", "Delete academy")}
              onClick={() => {
                if (window.confirm(pick(lang, "¿Borrar esta academia y sus membresías?", "Delete this academy and its memberships?"))) {
                  run(() => apiDelete(`/api/v1/platform/workspaces/${ws.id}`, csrf));
                }
              }}
            >
              <Trash2 />
            </Button>
          ) : null}
        </span>
      </TD>
    </TR>
  );
}

export function PlatformWorkspacesPanel({ workspaces, csrf, lang }: { workspaces: PlatformWorkspace[]; csrf: string; lang: Lang }) {
  const { run, error, busy } = useAction();
  return (
    <Card>
      <CardContent className="pt-5">
        <ErrorLine error={error} />
        <p className="m-0 mb-3 text-sm text-muted-foreground">
          {pick(
            lang,
            "Deja la cuota vacía para usar el valor global. Las plazas solo limitan academias.",
            "Leave the quota empty to use the global value. Seats only limit academies."
          )}
        </p>
        <Table>
          <THead>
            <TR>
              <TH>{pick(lang, "Espacio", "Space")}</TH>
              <TH>{pick(lang, "Miembros", "Members")}</TH>
              <TH>{pick(lang, "Cursos", "Courses")}</TH>
              <TH>{pick(lang, "Gener. mes", "Gen. month")}</TH>
              <TH>{pick(lang, "Cuota", "Quota")}</TH>
              <TH>{pick(lang, "Plazas", "Seats")}</TH>
              <TH />
            </TR>
          </THead>
          <TBody>
            {workspaces.map((ws) => (
              <WorkspaceRow key={ws.id} ws={ws} csrf={csrf} lang={lang} run={run} busy={busy} />
            ))}
          </TBody>
        </Table>
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Cursos generados
// ---------------------------------------------------------------------------

export function PlatformCoursesPanel({
  courses,
  csrf,
  lang,
}: {
  courses: (AuthoringCourse & { workspace_name?: string | null })[];
  csrf: string;
  lang: Lang;
}) {
  const { run, error, busy } = useAction();
  if (!courses.length) {
    return (
      <EmptyState
        title={pick(lang, "Aún no hay cursos generados", "No generated courses yet")}
        description={pick(lang, "Los cursos que se creen desde el Estudio aparecerán aquí.", "Courses created from the Studio will appear here.")}
      />
    );
  }
  return (
    <Card>
      <CardContent className="pt-5">
        <ErrorLine error={error} />
        <Table>
          <THead>
            <TR>
              <TH>{pick(lang, "Curso", "Course")}</TH>
              <TH>{pick(lang, "Espacio", "Space")}</TH>
              <TH>{pick(lang, "Estado", "Status")}</TH>
              <TH>{pick(lang, "Actualizado", "Updated")}</TH>
              <TH className="text-right">{pick(lang, "Acciones", "Actions")}</TH>
            </TR>
          </THead>
          <TBody>
            {courses.map((course) => {
              const isPublic = course.visibility === "public";
              return (
                <TR key={course.slug}>
                  <TD>
                    <span className="block font-medium">{course.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {course.summary.lesson_count} {pick(lang, "lecciones", "lessons")} · {course.slug}
                    </span>
                  </TD>
                  <TD className="text-sm">{course.workspace_name ?? "—"}</TD>
                  <TD>
                    <span className="flex flex-wrap gap-1">
                      <Pill variant={course.status === "published" ? "success" : "secondary"}>
                        {course.status === "published" ? pick(lang, "Publicado", "Published") : pick(lang, "Borrador", "Draft")}
                      </Pill>
                      {isPublic ? <Pill variant="violet">{pick(lang, "Abierto", "Open")}</Pill> : null}
                    </span>
                  </TD>
                  <TD className="text-sm text-muted-foreground">{formatDate(course.updated_at, lang)}</TD>
                  <TD className="text-right">
                    <span className="inline-flex gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={busy}
                        title={isPublic ? pick(lang, "Limitar a su espacio", "Limit to its space") : pick(lang, "Abrir a toda la plataforma", "Open to the whole platform")}
                        onClick={() =>
                          run(() =>
                            apiPost(`/api/v1/platform/courses/${course.slug}/visibility`, { visibility: isPublic ? "workspace" : "public" }, csrf)
                          )
                        }
                      >
                        {isPublic ? <EyeOff /> : <Eye />}
                      </Button>
                      {course.status === "published" ? (
                        <Button
                          size="sm"
                          variant="ghost"
                          disabled={busy}
                          title={pick(lang, "Despublicar", "Unpublish")}
                          onClick={() => run(() => apiPost(`/api/v1/platform/courses/${course.slug}/unpublish`, {}, csrf))}
                        >
                          <Undo2 />
                        </Button>
                      ) : null}
                    </span>
                  </TD>
                </TR>
              );
            })}
          </TBody>
        </Table>
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Invitaciones de plataforma (ADR-022)
// ---------------------------------------------------------------------------

type InviteChoice = "individual" | "teacher_new" | "teacher_existing";

function CopyLink({ value, lang }: { value: string; lang: Lang }) {
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

function inviteKindLabel(invite: PlatformInvitation, lang: Lang): string {
  if (invite.kind === "individual") return pick(lang, "Cuenta individual", "Individual account");
  if (invite.workspace_id) {
    return pick(lang, "Profesor en {a}", "Teacher in {a}").replace("{a}", invite.workspace_name ?? "—");
  }
  return invite.academy_name
    ? pick(lang, "Profesor · academia nueva «{a}»", "Teacher · new academy “{a}”").replace("{a}", invite.academy_name)
    : pick(lang, "Profesor · academia nueva", "Teacher · new academy");
}

export function PlatformInvitationsPanel({
  invitations,
  academies,
  csrf,
  lang,
}: {
  invitations: PlatformInvitation[];
  academies: { id: number; name: string }[];
  csrf: string;
  lang: Lang;
}) {
  const { run, error, busy } = useAction();
  const [choice, setChoice] = useState<InviteChoice>("individual");
  const [email, setEmail] = useState("");
  const [academyName, setAcademyName] = useState("");
  const [academyId, setAcademyId] = useState(academies[0] ? String(academies[0].id) : "");
  const [link, setLink] = useState("");
  const state = {
    pending: ["Pendiente", "Pending", "warning"],
    accepted: ["Aceptada", "Accepted", "success"],
    expired: ["Caducada", "Expired", "secondary"],
    revoked: ["Revocada", "Revoked", "secondary"],
  } as const;

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const body =
      choice === "individual"
        ? { kind: "individual", email: email || null }
        : choice === "teacher_new"
          ? { kind: "teacher", email: email || null, academy_name: academyName || null }
          : { kind: "teacher", email: email || null, workspace_id: Number(academyId) };
    void run(async () => {
      const result = await apiPost<{ path: string }>("/api/v1/platform/invitations", body, csrf);
      setLink(`${window.location.origin}${result.path}`);
      setEmail("");
      setAcademyName("");
    });
  }

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>{pick(lang, "Invitar a la plataforma", "Invite to the platform")}</CardTitle>
            <CardDescription>
              {pick(
                lang,
                "El registro es solo por invitación. Genera un enlace de un solo uso (14 días) para una cuenta individual o para un profesor; el profesorado invita después a su alumnado. Si indicas un correo, solo esa dirección podrá usarlo.",
                "Sign-up is by invitation only. Create a single-use link (14 days) for an individual account or a teacher; teachers then invite their students. If you enter an email, only that address can use it."
              )}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form className="flex flex-wrap items-end gap-3" onSubmit={submit}>
            <Field label={pick(lang, "Tipo", "Type")} htmlFor="pinv-kind">
              <NativeSelect id="pinv-kind" value={choice} onChange={(e) => setChoice(e.target.value as InviteChoice)}>
                <option value="individual">{pick(lang, "Cuenta individual (autónomo)", "Individual account (self-learner)")}</option>
                <option value="teacher_new">{pick(lang, "Profesor · academia nueva", "Teacher · new academy")}</option>
                <option value="teacher_existing" disabled={!academies.length}>
                  {pick(lang, "Profesor · academia existente", "Teacher · existing academy")}
                </option>
              </NativeSelect>
            </Field>
            <Field label={pick(lang, "Correo (opcional)", "Email (optional)")} htmlFor="pinv-email" className="min-w-56 flex-1">
              <Input id="pinv-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </Field>
            {choice === "teacher_new" ? (
              <Field label={pick(lang, "Academia (opcional)", "Academy (optional)")} htmlFor="pinv-academy" className="min-w-56">
                <Input
                  id="pinv-academy"
                  maxLength={80}
                  value={academyName}
                  onChange={(e) => setAcademyName(e.target.value)}
                  placeholder={pick(lang, "Si lo dejas vacío, lo elige el profesor", "Leave empty to let the teacher choose")}
                />
              </Field>
            ) : null}
            {choice === "teacher_existing" ? (
              <Field label={pick(lang, "Academia", "Academy")} htmlFor="pinv-ws">
                <NativeSelect id="pinv-ws" value={academyId} onChange={(e) => setAcademyId(e.target.value)}>
                  {academies.map((academy) => (
                    <option key={academy.id} value={academy.id}>
                      {academy.name}
                    </option>
                  ))}
                </NativeSelect>
              </Field>
            ) : null}
            <Button type="submit" disabled={busy}>
              <Link2 /> {pick(lang, "Crear enlace", "Create link")}
            </Button>
          </form>
          <ErrorLine error={error} />
          {link ? (
            <div className="mt-4 flex flex-wrap items-center gap-2 rounded-lg bg-success-soft p-3">
              <code className="min-w-0 flex-1 truncate text-sm">{link}</code>
              <CopyLink value={link} lang={lang} />
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-5">
          {invitations.length ? (
            <Table>
              <THead>
                <TR>
                  <TH>{pick(lang, "Tipo", "Type")}</TH>
                  <TH>{pick(lang, "Destinatario", "Recipient")}</TH>
                  <TH>{pick(lang, "Estado", "Status")}</TH>
                  <TH>{pick(lang, "Caduca", "Expires")}</TH>
                  <TH />
                </TR>
              </THead>
              <TBody>
                {invitations.map((invite) => {
                  const [es, en, tone] = state[invite.state];
                  return (
                    <TR key={invite.id}>
                      <TD className="text-sm">{inviteKindLabel(invite, lang)}</TD>
                      <TD className="text-sm">
                        {invite.email ?? pick(lang, "Cualquiera con el enlace", "Anyone with the link")}
                        {invite.accepted_email ? (
                          <span className="block text-xs text-muted-foreground">→ {invite.accepted_email}</span>
                        ) : null}
                      </TD>
                      <TD>
                        <Pill variant={tone}>{pick(lang, es, en)}</Pill>
                      </TD>
                      <TD className="text-sm text-muted-foreground">{formatDate(invite.expires_at, lang)}</TD>
                      <TD className="text-right">
                        {invite.state === "pending" ? (
                          <Button
                            size="sm"
                            variant="ghost"
                            disabled={busy}
                            title={pick(lang, "Revocar", "Revoke")}
                            onClick={() => run(() => apiDelete(`/api/v1/platform/invitations/${invite.id}`, csrf))}
                          >
                            <Ban />
                          </Button>
                        ) : null}
                      </TD>
                    </TR>
                  );
                })}
              </TBody>
            </Table>
          ) : (
            <EmptyState
              title={pick(lang, "Aún no hay invitaciones", "No invitations yet")}
              description={pick(lang, "Las invitaciones que crees aparecerán aquí con su estado.", "Invitations you create will appear here with their status.")}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
