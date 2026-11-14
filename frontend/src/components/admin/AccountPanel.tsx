"use client";

import { KeyRound, LogOut, MonitorSmartphone, UserRound } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { roleLabel } from "@/components/shell/WorkspaceSwitcher";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { apiPost, apiSendPatch } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { WorkspaceRef } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export interface AccountData {
  name: string;
  email: string;
  created_at: string;
  last_login_at: string | null;
  workspaces: WorkspaceRef[];
  sessions: { created_at: string; expires_at: string; current: boolean }[];
}

export function AccountPanel({ data, csrf, lang }: { data: AccountData; csrf: string; lang: Lang }) {
  const router = useRouter();
  const [name, setName] = useState(data.name);
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  async function run(fn: () => Promise<unknown>, ok: string) {
    setMsg(null);
    try {
      await fn();
      setMsg({ ok: true, text: ok });
      router.refresh();
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : String(err) });
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {msg ? (
        <p className={`m-0 rounded-md px-3 py-2 text-sm lg:col-span-2 ${msg.ok ? "bg-success-soft text-success" : "bg-destructive-soft text-destructive"}`}>{msg.text}</p>
      ) : null}
      <Card>
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <UserRound className="size-4" /> {pick(lang, "Perfil", "Profile")}
            </CardTitle>
            <CardDescription>
              {data.email} · {pick(lang, "desde", "since")} {formatDate(data.created_at, lang)}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form
            className="flex items-end gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              void run(() => apiSendPatch("/api/v1/account", { name }, csrf), pick(lang, "Perfil actualizado.", "Profile updated."));
            }}
          >
            <Field label={pick(lang, "Nombre", "Name")} htmlFor="acc-name" className="flex-1">
              <Input id="acc-name" value={name} minLength={2} maxLength={80} onChange={(e) => setName(e.target.value)} />
            </Field>
            <Button type="submit" variant="secondary">
              {pick(lang, "Guardar", "Save")}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <KeyRound className="size-4" /> {pick(lang, "Contraseña", "Password")}
            </CardTitle>
            <CardDescription>{pick(lang, "Al cambiarla se cierran tus otras sesiones.", "Changing it signs out your other sessions.")}</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              void run(async () => {
                await apiPost("/api/v1/account/password", { current, new: next }, csrf);
                setCurrent("");
                setNext("");
              }, pick(lang, "Contraseña cambiada.", "Password changed."));
            }}
          >
            <Field label={pick(lang, "Actual", "Current")} htmlFor="pw-current">
              <Input id="pw-current" type="password" autoComplete="current-password" value={current} onChange={(e) => setCurrent(e.target.value)} required />
            </Field>
            <Field label={pick(lang, "Nueva (mín. 8 caracteres)", "New (min. 8 characters)")} htmlFor="pw-new">
              <Input id="pw-new" type="password" autoComplete="new-password" minLength={8} value={next} onChange={(e) => setNext(e.target.value)} required />
            </Field>
            <Button type="submit" variant="secondary" className="justify-self-end">
              {pick(lang, "Cambiar contraseña", "Change password")}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>{pick(lang, "Tus espacios", "Your workspaces")}</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <ul className="m-0 grid list-none gap-2 p-0">
            {data.workspaces.map((ws) => (
              <li key={ws.id} className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
                <span>{ws.name}</span>
                <Pill variant="secondary">{ws.kind === "personal" ? pick(lang, "Cuenta individual", "Individual account") : roleLabel(ws.role, lang)}</Pill>
              </li>
            ))}
            {data.workspaces.length === 0 ? (
              <li className="text-sm text-muted-foreground">{pick(lang, "No perteneces a ningún espacio.", "You don't belong to any space.")}</li>
            ) : null}
          </ul>
          {!data.workspaces.some((ws) => ws.kind === "personal") ? (
            <div className="mt-4 rounded-lg border border-dashed border-border p-3 text-sm">
              <p className="m-0 font-medium">{pick(lang, "¿Quieres crear unidades para ti?", "Want to create units for yourself?")}</p>
              <p className="m-0 mt-1 text-muted-foreground">
                {pick(
                  lang,
                  "Abre tu cuenta individual: tendrás tu propio Estudio y tu biblioteca. En tus academias seguirás con el mismo rol.",
                  "Open your individual account: you get your own Studio and library. Your role in your academies stays the same."
                )}
              </p>
              <Button
                size="sm"
                className="mt-3"
                onClick={() =>
                  run(async () => {
                    await apiPost("/api/v1/workspaces/personal", {}, csrf);
                    window.location.href = "/";
                  }, pick(lang, "Cuenta individual creada.", "Individual account created."))
                }
              >
                <UserRound /> {pick(lang, "Abrir mi cuenta individual", "Open my individual account")}
              </Button>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle className="flex items-center gap-2">
              <MonitorSmartphone className="size-4" /> {pick(lang, "Sesiones abiertas", "Open sessions")}
            </CardTitle>
          </div>
          {data.sessions.length > 1 ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => run(() => apiPost("/api/v1/account/sessions/revoke-others", {}, csrf), pick(lang, "Otras sesiones cerradas.", "Other sessions closed."))}
            >
              <LogOut /> {pick(lang, "Cerrar las demás", "Close the others")}
            </Button>
          ) : null}
        </CardHeader>
        <CardContent>
          <ul className="m-0 grid list-none gap-2 p-0 text-sm">
            {data.sessions.map((s, i) => (
              <li key={i} className="flex items-center justify-between">
                <span>
                  {pick(lang, "Iniciada", "Started")} {formatDate(s.created_at, lang)}
                </span>
                {s.current ? <Pill variant="success">{pick(lang, "Esta sesión", "This session")}</Pill> : <span className="text-xs text-muted-foreground">{pick(lang, "caduca", "expires")} {formatDate(s.expires_at, lang)}</span>}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

export function AcceptInvite({ token, csrf, lang }: { token: string; csrf: string; lang: Lang }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <div className="grid gap-2">
      {error ? <p className="m-0 text-sm text-destructive">{error}</p> : null}
      <Button
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setError("");
          try {
            const result = await apiPost<{ workspace_id: number }>(`/api/v1/invitations/${token}/accept`, {}, csrf);
            await apiPost("/api/v1/workspaces/switch", { workspace_id: result.workspace_id }, csrf);
            window.location.href = "/";
          } catch (err) {
            setError(err instanceof Error ? err.message : String(err));
            setBusy(false);
          }
        }}
      >
        {pick(lang, "Aceptar invitación", "Accept invitation")}
      </Button>
    </div>
  );
}
