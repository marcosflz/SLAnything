"use client";

import { Building2, Check, ChevronsUpDown, KeyRound, Plus, User as UserIcon } from "lucide-react";
import { useState } from "react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  Menu,
  MenuContent,
  MenuItem,
  MenuLabel,
  MenuSeparator,
  MenuTrigger,
} from "@/components/ui/overlay";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/form";
import { apiPost } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { User, WorkspaceRef } from "@/lib/types";

export function roleLabel(role: string | null | undefined, lang: Lang): string {
  const labels: Record<string, [string, string]> = {
    owner: ["Propietario", "Owner"],
    admin: ["Administración", "Admin"],
    teacher: ["Profesorado", "Teacher"],
    student: ["Estudiante", "Student"],
  };
  const pair = labels[role ?? "student"] ?? labels.student;
  return lang === "en" ? pair[1] : pair[0];
}

function WsIcon({ ws }: { ws: WorkspaceRef }) {
  const Icon = ws.kind === "personal" ? UserIcon : Building2;
  return (
    <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-primary text-primary-foreground">
      <Icon className="size-4" aria-hidden="true" />
    </span>
  );
}

export function WorkspaceSwitcher({ user, lang }: { user: User; lang: Lang }) {
  const [dialog, setDialog] = useState<"create" | "join" | null>(null);
  const [value, setValue] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const active = user.workspace;
  const list = user.workspaces ?? [];

  async function switchTo(id: number) {
    if (id === active?.id) return;
    await apiPost("/api/v1/workspaces/switch", { workspace_id: id }, user.csrf_token);
    window.location.href = "/";
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (dialog === "create") {
        await apiPost("/api/v1/workspaces", { name: value }, user.csrf_token);
      } else {
        await apiPost("/api/v1/workspaces/join", { code: value }, user.csrf_token);
      }
      window.location.href = "/";
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  if (!active) return null;
  return (
    <>
      <Menu>
        <MenuTrigger asChild>
          <button
            type="button"
            className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg border border-transparent bg-transparent p-1.5 text-left transition hover:bg-muted data-[state=open]:bg-muted"
            aria-label={pick(lang, "Cambiar de espacio", "Switch workspace")}
          >
            <WsIcon ws={active} />
            <span className="min-w-0 flex-1 leading-tight">
              <span className="block truncate text-sm font-semibold">{active.name}</span>
              <span className="block truncate text-xs text-muted-foreground">
                {active.kind === "personal"
                  ? pick(lang, "Espacio personal", "Personal space")
                  : roleLabel(active.role, lang)}
              </span>
            </span>
            <ChevronsUpDown className="size-4 text-muted-foreground" aria-hidden="true" />
          </button>
        </MenuTrigger>
        <MenuContent align="start" className="w-64">
          <MenuLabel>{pick(lang, "Tus espacios", "Your workspaces")}</MenuLabel>
          {list.map((ws) => (
            <MenuItem key={ws.id} onSelect={() => switchTo(ws.id)}>
              {ws.kind === "personal" ? <UserIcon /> : <Building2 />}
              <span className="min-w-0 flex-1 truncate">{ws.name}</span>
              {ws.id === active.id ? <Check className="!text-primary" /> : null}
            </MenuItem>
          ))}
          <MenuSeparator />
          <MenuItem onSelect={() => { setValue(""); setError(""); setDialog("create"); }}>
            <Plus /> {pick(lang, "Crear academia", "Create academy")}
          </MenuItem>
          <MenuItem onSelect={() => { setValue(""); setError(""); setDialog("join"); }}>
            <KeyRound /> {pick(lang, "Unirme con un código", "Join with a code")}
          </MenuItem>
        </MenuContent>
      </Menu>

      <Dialog open={dialog !== null} onOpenChange={(open) => !open && setDialog(null)}>
        <DialogContent closeLabel={pick(lang, "Cerrar", "Close")}>
          <DialogTitle>
            {dialog === "create"
              ? pick(lang, "Crear una academia", "Create an academy")
              : pick(lang, "Unirme a una academia", "Join an academy")}
          </DialogTitle>
          <DialogDescription>
            {dialog === "create"
              ? pick(
                  lang,
                  "Tendrás un espacio compartido con profesorado, estudiantes, grupos y analítica. Serás su propietario.",
                  "You get a shared space with teachers, students, groups and analytics. You will be its owner."
                )
              : pick(
                  lang,
                  "Pide a tu profesor el código de clase de 8 caracteres.",
                  "Ask your teacher for the 8-character class code."
                )}
          </DialogDescription>
          <form onSubmit={submit} className="grid gap-3">
            <Input
              autoFocus
              required
              minLength={dialog === "create" ? 2 : 4}
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder={
                dialog === "create"
                  ? pick(lang, "Nombre de la academia", "Academy name")
                  : "ABCD2345"
              }
              aria-label={dialog === "create" ? pick(lang, "Nombre", "Name") : pick(lang, "Código", "Code")}
            />
            {error ? <p className="m-0 text-sm text-destructive">{error}</p> : null}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" onClick={() => setDialog(null)}>
                {pick(lang, "Cancelar", "Cancel")}
              </Button>
              <Button type="submit" disabled={busy}>
                {dialog === "create" ? pick(lang, "Crear", "Create") : pick(lang, "Unirme", "Join")}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
