"use client";

import { Building2, KeyRound, User as UserIcon } from "lucide-react";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/form";
import { apiPost } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";

/**
 * Usuario sin ningún espacio (por ejemplo, un alumno al que han dado de baja de
 * su academia): puede unirse a otra clase, abrir su cuenta individual o crear
 * una academia.
 */
export function Welcome({
  csrf,
  lang,
  canCreateSpaces = true,
}: {
  csrf: string;
  lang: Lang;
  canCreateSpaces?: boolean;
}) {
  const [code, setCode] = useState("");
  const [academy, setAcademy] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run(path: string, body: Record<string, string>) {
    setBusy(true);
    setError("");
    try {
      await apiPost(path, body, csrf);
      window.location.href = "/";
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  function submitCode(event: FormEvent) {
    event.preventDefault();
    run("/api/v1/workspaces/join", { code });
  }

  function submitAcademy(event: FormEvent) {
    event.preventDefault();
    run("/api/v1/workspaces", { name: academy });
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-6">
      <div>
        <h2 className="m-0 text-2xl font-semibold tracking-tight">{pick(lang, "Elige cómo seguir", "Choose how to continue")}</h2>
        <p className="m-0 mt-1 text-sm text-muted-foreground">
          {pick(
            lang,
            "Ahora mismo no perteneces a ningún espacio. Únete a una clase, abre tu cuenta individual o crea tu propia academia.",
            "You don't belong to any space right now. Join a class, open your individual account or create your own academy."
          )}
        </p>
      </div>
      {error ? <p className="m-0 rounded-md bg-destructive-soft px-3 py-2 text-sm text-destructive">{error}</p> : null}
      {canCreateSpaces ? null : (
        <p className="m-0 text-sm text-muted-foreground">
          {pick(
            lang,
            "Si necesitas una cuenta individual o una academia, pídesela a la administración de la plataforma: te enviará una invitación.",
            "If you need an individual account or an academy, ask the platform administrators: they will send you an invitation."
          )}
        </p>
      )}
      <div className={canCreateSpaces ? "grid gap-4 md:grid-cols-3" : "grid max-w-sm gap-4"}>
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2">
                <KeyRound className="size-4" /> {pick(lang, "Tengo un código", "I have a code")}
              </CardTitle>
              <CardDescription>{pick(lang, "Entra como estudiante en una academia.", "Join an academy as a student.")}</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitCode} className="grid gap-2">
              <Input
                required
                minLength={4}
                maxLength={16}
                value={code}
                onChange={(event) => setCode(event.target.value.toUpperCase())}
                placeholder="ABCD2345"
                aria-label={pick(lang, "Código de clase", "Class code")}
              />
              <Button type="submit" disabled={busy}>
                {pick(lang, "Unirme", "Join")}
              </Button>
            </form>
          </CardContent>
        </Card>
        {canCreateSpaces ? (
          <>
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2">
                <UserIcon className="size-4" /> {pick(lang, "Cuenta individual", "Individual account")}
              </CardTitle>
              <CardDescription>
                {pick(lang, "Aprende por tu cuenta y crea tus propias unidades.", "Learn on your own and create your own units.")}
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <Button className="w-full" variant="outline" disabled={busy} onClick={() => run("/api/v1/workspaces/personal", {})}>
              {pick(lang, "Abrir mi cuenta individual", "Open my individual account")}
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="size-4" /> {pick(lang, "Academia", "Academy")}
              </CardTitle>
              <CardDescription>
                {pick(lang, "Gestiona profesorado, alumnado y grupos.", "Manage teachers, students and groups.")}
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={submitAcademy} className="grid gap-2">
              <Input
                required
                minLength={2}
                maxLength={80}
                value={academy}
                onChange={(event) => setAcademy(event.target.value)}
                placeholder={pick(lang, "Nombre de la academia", "Academy name")}
                aria-label={pick(lang, "Nombre de la academia", "Academy name")}
              />
              <Button type="submit" variant="outline" disabled={busy}>
                {pick(lang, "Crear academia", "Create academy")}
              </Button>
            </form>
          </CardContent>
        </Card>
          </>
        ) : null}
      </div>
    </div>
  );
}
