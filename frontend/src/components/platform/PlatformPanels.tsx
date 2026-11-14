"use client";

import { Ban, Eye, EyeOff, Search, ShieldCheck, ShieldOff, Trash2, Undo2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { EmptyState } from "@/components/charts/Kpi";
import { roleLabel } from "@/components/shell/WorkspaceSwitcher";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { apiDelete, apiPost, apiSendPatch } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AuthoringCourse, PlatformUser, PlatformWorkspace } from "@/lib/types";
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
