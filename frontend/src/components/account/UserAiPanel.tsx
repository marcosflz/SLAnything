"use client";

import { Bot, KeyRound, Loader2, Trash2 } from "lucide-react";
import { useMemo, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input, NativeSelect } from "@/components/ui/form";
import { Pill } from "@/components/ui/pill";
import { apiDelete, apiPost, apiPut } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { UserAiSettings } from "@/lib/types";

/**
 * Proveedor de IA propio (ADR-024): una API key o la suscripción personal de
 * Claude. Solo lo ve quien puede crear unidades; el alumnado no lo tiene.
 */
export function UserAiPanel({ initial, csrf, lang }: { initial: UserAiSettings; csrf: string; lang: Lang }) {
  const [data, setData] = useState(initial);
  const first = initial.providers[0]?.id ?? "";
  const [provider, setProvider] = useState(initial.provider ?? first);
  const [model, setModel] = useState(initial.model || initial.providers.find((p) => p.id === (initial.provider ?? first))?.models[0] || "");
  const [secret, setSecret] = useState("");
  const [accept, setAccept] = useState(Boolean(initial.accepted_personal_at));
  const [busy, setBusy] = useState<"" | "save" | "test" | "delete">("");
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const info = useMemo(() => data.providers.find((item) => item.id === provider), [data.providers, provider]);
  const sameProvider = data.provider === provider;

  if (!data.enabled) return null;

  async function run(kind: "save" | "test" | "delete", action: () => Promise<void>) {
    setBusy(kind);
    setMessage(null);
    try {
      await action();
    } catch (err) {
      setMessage({ ok: false, text: err instanceof Error ? err.message : String(err) });
    } finally {
      setBusy("");
    }
  }

  function save(event: FormEvent) {
    event.preventDefault();
    run("save", async () => {
      const updated = await apiPut<UserAiSettings>(
        "/api/v1/account/ai",
        { provider, model, secret: secret || null, accept_personal: accept },
        csrf
      );
      setData(updated);
      setSecret("");
      setMessage({ ok: true, text: pick(lang, "Guardado. Tus próximas unidades usarán este proveedor.", "Saved. Your next units will use this provider.") });
    });
  }

  function test() {
    run("test", async () => {
      const result = await apiPost<{ ok: boolean; message: string }>("/api/v1/account/ai/test", {}, csrf);
      setMessage({ ok: result.ok, text: result.message });
    });
  }

  function remove() {
    run("delete", async () => {
      setData(await apiDelete<UserAiSettings>("/api/v1/account/ai", csrf));
      setSecret("");
      setMessage({ ok: true, text: pick(lang, "Eliminado. Volverás a usar el proveedor de la plataforma.", "Removed. You will use the platform provider again.") });
    });
  }

  const personal = Boolean(info?.personal);
  return (
    <Card id="proveedor-ia" className="lg:col-span-2">
      <CardHeader>
        <div>
          <CardTitle className="flex items-center gap-2">
            <Bot className="size-4" /> {pick(lang, "Proveedor de IA", "AI provider")}
          </CardTitle>
          <CardDescription>
            {pick(
              lang,
              "Opcional. Usa tu propia API key o tu suscripción de Claude para generar tus unidades. Si no configuras nada, se usa el proveedor de la plataforma. Solo tú puedes usar estas credenciales; nunca se aplican a lo que generan otras personas.",
              "Optional. Use your own API key or your Claude subscription to generate your units. If you set nothing, the platform provider is used. Only you can use these credentials; they never apply to what other people generate."
            )}
          </CardDescription>
        </div>
        {data.active ? (
          <Pill variant="success">
            <KeyRound /> {pick(lang, "En uso", "In use")}
          </Pill>
        ) : (
          <Pill variant="secondary">{pick(lang, "Plataforma", "Platform")}</Pill>
        )}
      </CardHeader>
      <CardContent>
        <form onSubmit={save} className="grid gap-3">
          {data.warning ? <p className="m-0 rounded-md bg-warning-soft px-3 py-2 text-sm text-warning">{data.warning}</p> : null}
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label={pick(lang, "Proveedor", "Provider")} htmlFor="user-ai-provider">
              <NativeSelect
                id="user-ai-provider"
                className="w-full"
                value={provider}
                onChange={(event) => {
                  const next = data.providers.find((item) => item.id === event.target.value);
                  setProvider(event.target.value);
                  setModel(next?.models[0] ?? "");
                  setSecret("");
                }}
              >
                {data.providers.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field
              label={pick(lang, "Modelo", "Model")}
              htmlFor="user-ai-model"
              hint={info?.model_optional ? pick(lang, "Vacío = el modelo por defecto de tu plan.", "Empty = your plan's default model.") : undefined}
            >
              <Input id="user-ai-model" list="user-ai-models" value={model} onChange={(event) => setModel(event.target.value)} required={!info?.model_optional} />
              <datalist id="user-ai-models">
                {info?.models.map((item) => <option key={item} value={item} />)}
              </datalist>
            </Field>
          </div>
          <p className="m-0 text-xs text-muted-foreground">{info?.notes}</p>
          {personal ? (
            <div className="grid gap-2 rounded-lg border border-border bg-muted/40 p-3 text-sm">
              <p className="m-0 font-medium">{pick(lang, "Cómo obtener el token", "How to get the token")}</p>
              <ol className="m-0 grid list-decimal gap-1 pl-5 text-muted-foreground">
                <li>{pick(lang, "Instala Claude Code en tu equipo e inicia sesión con tu suscripción.", "Install Claude Code on your computer and sign in with your subscription.")}</li>
                <li>
                  {pick(lang, "Ejecuta", "Run")} <code>claude setup-token</code> {pick(lang, "y copia el token que muestra.", "and copy the token it prints.")}
                </li>
                <li>{pick(lang, "Pégalo abajo. Se guarda cifrado y solo se usa en las unidades que generas tú.", "Paste it below. It is stored encrypted and only used for units you generate.")}</li>
              </ol>
              {data.claude_cli && !data.claude_cli.available ? (
                <p className="m-0 text-xs text-destructive">{data.claude_cli.message}</p>
              ) : data.claude_cli?.version ? (
                <p className="m-0 text-xs text-muted-foreground">Claude Code {data.claude_cli.version}</p>
              ) : null}
            </div>
          ) : null}
          {info?.requires_key ? (
            <Field label={personal ? pick(lang, "Token de la suscripción", "Subscription token") : "API key"} htmlFor="user-ai-secret">
              <Input
                id="user-ai-secret"
                type="password"
                autoComplete="off"
                value={secret}
                onChange={(event) => setSecret(event.target.value)}
                placeholder={sameProvider && data.key_configured ? data.key_hint : ""}
              />
            </Field>
          ) : null}
          {personal ? (
            <label className="flex items-start gap-2 text-sm">
              <input type="checkbox" className="mt-1" checked={accept} onChange={(event) => setAccept(event.target.checked)} />
              <span>
                {pick(
                  lang,
                  "Es mi suscripción personal. Solo la usaré yo para generar mis propias unidades y acepto cumplir las condiciones de Anthropic.",
                  "This is my personal subscription. Only I will use it to generate my own units and I agree to follow Anthropic's terms."
                )}
              </span>
            </label>
          ) : null}
          {message ? (
            <p className={message.ok ? "m-0 text-sm text-success" : "m-0 text-sm text-destructive"} role="status">
              {message.text}
            </p>
          ) : null}
          <div className="flex flex-wrap items-center justify-end gap-2">
            {data.configured ? (
              <>
                <Button type="button" variant="ghost" onClick={remove} disabled={Boolean(busy)}>
                  {busy === "delete" ? <Loader2 className="animate-spin" /> : <Trash2 />}
                  {pick(lang, "Quitar", "Remove")}
                </Button>
                <Button type="button" variant="outline" onClick={test} disabled={Boolean(busy) || !data.active}>
                  {busy === "test" ? <Loader2 className="animate-spin" /> : null}
                  {pick(lang, "Probar", "Test")}
                </Button>
              </>
            ) : null}
            <Button type="submit" disabled={Boolean(busy) || (personal && !accept)}>
              {busy === "save" ? <Loader2 className="animate-spin" /> : null}
              {pick(lang, "Guardar", "Save")}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
