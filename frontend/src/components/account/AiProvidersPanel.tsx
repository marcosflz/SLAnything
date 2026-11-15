"use client";

import { Bot, ExternalLink, KeyRound, Loader2, Plus, Search, Star, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Field, Input } from "@/components/ui/form";
import { Dialog, DialogContent, DialogDescription, DialogTitle, Menu, MenuContent, MenuItem, MenuTrigger } from "@/components/ui/overlay";
import { Pill, type PillVariant } from "@/components/ui/pill";
import { apiDelete, apiPost, apiPut } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AiModelEntry, AiProvidersData, AiProviderView } from "@/lib/types";

type Scope = "user" | "workspace";

const BASE: Record<Scope, string> = { user: "/api/v1/account/ai", workspace: "/api/v1/admin/ai" };

function errorText(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

/**
 * Proveedores de IA (ADR-025). En la cuenta: claves de API y suscripciones personales, varias a
 * la vez, con los modelos visibles y el predeterminado. En una academia: claves de API
 * compartidas con el profesorado (nunca suscripciones).
 */
export function AiProvidersPanel({
  initial,
  csrf,
  lang,
  scope,
}: {
  initial: AiProvidersData;
  csrf: string;
  lang: Lang;
  scope: Scope;
}) {
  const [data, setData] = useState(initial);
  const [drafts, setDrafts] = useState<string[]>([]);
  if (!data.enabled) return null;

  const sections: { kind: "api" | "subscription"; title: string; description: string }[] =
    scope === "user"
      ? [
          {
            kind: "subscription",
            title: pick(lang, "Suscripciones", "Subscriptions"),
            description: pick(
              lang,
              "Tus propios planes (Claude, ChatGPT, OpenCode Go). Son tuyos: solo se usan en lo que generas tú y nunca se comparten.",
              "Your own plans (Claude, ChatGPT, OpenCode Go). They are yours: only used for what you generate and never shared."
            ),
          },
          {
            kind: "api",
            title: pick(lang, "Claves de API", "API keys"),
            description: pick(
              lang,
              "Servicios de pago por uso con tu clave. Puedes tener varios activos y elegir qué modelos de cada uno aparecen en el Estudio.",
              "Pay-as-you-go services with your key. Keep several active and choose which models of each appear in the Studio."
            ),
          },
        ]
      : [
          {
            kind: "api",
            title: pick(lang, "Claves de API de la academia", "Academy API keys"),
            description: pick(
              lang,
              "Claves que el profesorado de esta academia puede usar en el Estudio. Las suscripciones personales no se comparten.",
              "Keys this academy's teachers can use in the Studio. Personal subscriptions are never shared."
            ),
          },
        ];

  return (
    <div className="grid gap-6 lg:col-span-2" id="proveedor-ia">
      {sections.map((section) => {
        const all = data.providers.filter((p) => (p.kind ?? "api") === section.kind);
        const shown = all.filter(
          (p) => p.config || drafts.includes(p.id) || (scope === "user" && section.kind === "subscription" && p.link !== "key")
        );
        const addable = all.filter((p) => !shown.includes(p));
        return (
          <Card key={section.kind}>
            <CardHeader>
              <div>
                <CardTitle className="flex items-center gap-2">
                  {section.kind === "subscription" ? <Bot className="size-4" /> : <KeyRound className="size-4" />} {section.title}
                </CardTitle>
                <CardDescription>{section.description}</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="grid gap-4">
              {shown.length === 0 ? (
                <p className="m-0 rounded-lg border border-dashed border-border px-4 py-5 text-center text-sm text-muted-foreground">
                  {pick(lang, "Aún no has añadido ninguno.", "Nothing added yet.")}
                </p>
              ) : null}
              {shown.map((provider) => (
                <ProviderCard
                  key={provider.id}
                  provider={provider}
                  data={data}
                  scope={scope}
                  csrf={csrf}
                  lang={lang}
                  onData={(next) => {
                    setData(next);
                    setDrafts((prev) => prev.filter((id) => id !== provider.id));
                  }}
                  onDiscard={() => setDrafts((prev) => prev.filter((id) => id !== provider.id))}
                />
              ))}
              {addable.length > 0 ? (
                <Menu>
                  <MenuTrigger asChild>
                    <Button type="button" variant="outline" className="justify-self-start">
                      <Plus />{" "}
                      {section.kind === "subscription"
                        ? pick(lang, "Añadir suscripción", "Add subscription")
                        : pick(lang, "Añadir servicio", "Add service")}
                    </Button>
                  </MenuTrigger>
                  <MenuContent align="start">
                    {addable.map((p) => (
                      <MenuItem key={p.id} onSelect={() => setDrafts((prev) => [...prev, p.id])}>
                        {p.label}
                      </MenuItem>
                    ))}
                  </MenuContent>
                </Menu>
              ) : null}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

function ProviderCard({
  provider,
  data,
  scope,
  csrf,
  lang,
  onData,
  onDiscard,
}: {
  provider: AiProviderView;
  data: AiProvidersData;
  scope: Scope;
  csrf: string;
  lang: Lang;
  onData: (data: AiProvidersData) => void;
  onDiscard: () => void;
}) {
  const base = BASE[scope];
  const config = provider.config;
  const [secret, setSecret] = useState("");
  const [accept, setAccept] = useState(Boolean(config?.accepted_personal_at));
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [choosing, setChoosing] = useState(false);
  const [linking, setLinking] = useState(false);
  const personal = provider.personal;
  const linked = provider.link === "claude" || provider.link === "chatgpt";
  const isDefault = (model: string) =>
    scope === "user"
      ? data.default?.source === "user" && data.default.provider === provider.id && data.default.model === model
      : config?.model === model;

  async function run(kind: string, action: () => Promise<void>) {
    setBusy(kind);
    setMessage(null);
    try {
      await action();
    } catch (err) {
      setMessage({ ok: false, text: errorText(err) });
    } finally {
      setBusy("");
    }
  }

  function save(event?: FormEvent) {
    event?.preventDefault();
    run("save", async () => {
      onData(
        await apiPut<AiProvidersData>(
          `${base}/providers`,
          { provider: provider.id, secret: secret.trim() || null, accept_personal: accept },
          csrf
        )
      );
      setSecret("");
      setMessage({ ok: true, text: pick(lang, "Guardado.", "Saved.") });
    });
  }

  function toggle(enabled: boolean) {
    run("toggle", async () => onData(await apiPut<AiProvidersData>(`${base}/providers`, { provider: provider.id, enabled }, csrf)));
  }

  async function saveModels(models: AiModelEntry[]): Promise<boolean> {
    try {
      onData(
        await apiPut<AiProvidersData>(
          `${base}/providers`,
          { provider: provider.id, models: models.map(({ id, label }) => ({ id, label })) },
          csrf
        )
      );
      return true;
    } catch (err) {
      setMessage({ ok: false, text: errorText(err) });
      return false;
    }
  }

  function makeDefault(model: string) {
    run("default", async () => {
      onData(
        scope === "user"
          ? await apiPut<AiProvidersData>(`${base}/default`, { source: "user", provider: provider.id, model }, csrf)
          : await apiPut<AiProvidersData>(`${base}/providers`, { provider: provider.id, model }, csrf)
      );
    });
  }

  function test() {
    run("test", async () => {
      const result = await apiPost<{ ok: boolean; message: string }>(`${base}/providers/${provider.id}/test`, {}, csrf);
      setMessage({ ok: result.ok, text: result.message });
    });
  }

  function remove() {
    run("delete", async () => {
      onData(await apiDelete<AiProvidersData>(`${base}/providers/${provider.id}`, csrf));
      setMessage(null);
    });
  }

  let status: { text: string; variant: PillVariant } = { text: pick(lang, "Sin configurar", "Not set up"), variant: "secondary" };
  if (config && !config.key_readable) status = { text: pick(lang, "Vuelve a configurarlo", "Set it up again"), variant: "warning" };
  else if (config?.ready && config.enabled) status = { text: pick(lang, "Activo", "Active"), variant: "success" };
  else if (config && !config.enabled) status = { text: pick(lang, "Desactivado", "Disabled"), variant: "secondary" };
  else if (linked) status = { text: pick(lang, "Sin vincular", "Not linked"), variant: "secondary" };

  return (
    <section className="grid gap-3 rounded-lg border border-border p-4">
      <header className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="m-0 text-[15px] font-semibold">{provider.label}</h3>
          <p className="m-0 mt-0.5 text-xs text-muted-foreground">{provider.notes}</p>
        </div>
        <div className="flex items-center gap-3">
          <Pill variant={status.variant}>{status.text}</Pill>
          {config && config.key_configured ? (
            <label className="flex items-center gap-1.5 text-xs">
              <input type="checkbox" checked={config.enabled} disabled={Boolean(busy)} onChange={(e) => toggle(e.target.checked)} />
              {pick(lang, "Activo", "Active")}
            </label>
          ) : null}
        </div>
      </header>

      {provider.link === "key" ? (
        <form onSubmit={save} className="grid gap-2 sm:grid-cols-[1fr_auto] sm:items-end">
          {provider.requires_key ? (
            <Field label="API key" htmlFor={`secret-${scope}-${provider.id}`}>
              <Input
                id={`secret-${scope}-${provider.id}`}
                type="password"
                autoComplete="off"
                value={secret}
                onChange={(event) => setSecret(event.target.value)}
                placeholder={config?.key_configured ? config.key_hint : ""}
              />
            </Field>
          ) : (
            <p className="m-0 text-sm text-muted-foreground">{pick(lang, "No necesita clave.", "No key needed.")}</p>
          )}
          <Button type="submit" disabled={Boolean(busy) || (provider.requires_key && !secret.trim() && !config?.key_configured) || (Boolean(config) && !secret.trim())}>
            {busy === "save" ? <Loader2 className="animate-spin" /> : null}
            {config ? pick(lang, "Guardar clave", "Save key") : pick(lang, "Añadir", "Add")}
          </Button>
        </form>
      ) : (
        <div className="grid gap-2">
          {config?.account ? (
            <p className="m-0 text-sm text-muted-foreground">{pick(lang, "Cuenta vinculada:", "Linked account:")} {config.account}</p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant={config?.key_configured ? "outline" : "default"} onClick={() => setLinking(true)}>
              {config?.key_configured ? pick(lang, "Volver a vincular", "Link again") : pick(lang, "Vincular mi cuenta", "Link my account")}
            </Button>
          </div>
          {provider.link === "claude" && data.claude_cli && !data.claude_cli.available ? (
            <p className="m-0 text-xs text-destructive">{data.claude_cli.message}</p>
          ) : null}
        </div>
      )}

      {config?.ready ? (
        <div className="grid gap-2">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[13px] font-medium">
              {pick(lang, "Modelos activos", "Active models")} <span className="font-normal text-muted-foreground">({config.models.length})</span>
            </span>
            <Button type="button" size="sm" variant="outline" onClick={() => setChoosing(true)}>
              {pick(lang, "Elegir modelos", "Choose models")}
            </Button>
          </div>
          {config.models.length === 0 ? (
            <p className="m-0 text-xs text-warning">{pick(lang, "Elige al menos un modelo.", "Choose at least one model.")}</p>
          ) : (
            <ul className="m-0 flex list-none flex-wrap gap-1.5 p-0">
              {config.models.map((model) => (
                <li key={model.id}>
                  <button
                    type="button"
                    title={isDefault(model.id) ? pick(lang, "Predeterminado", "Default") : pick(lang, "Usar como predeterminado", "Use as default")}
                    onClick={() => (isDefault(model.id) ? undefined : makeDefault(model.id))}
                    className={
                      "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs " +
                      (isDefault(model.id) ? "border-primary/50 bg-primary-soft text-primary" : "border-border hover:bg-muted")
                    }
                  >
                    {isDefault(model.id) ? <Star className="size-3 fill-current" /> : null}
                    {model.label}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : null}

      {message ? (
        <p className={message.ok ? "m-0 text-sm text-success" : "m-0 text-sm text-destructive"} role="status">
          {message.text}
        </p>
      ) : null}

      <div className="flex flex-wrap justify-end gap-2">
        {config?.ready ? (
          <Button type="button" size="sm" variant="outline" onClick={test} disabled={Boolean(busy)}>
            {busy === "test" ? <Loader2 className="animate-spin" /> : null}
            {pick(lang, "Probar", "Test")}
          </Button>
        ) : null}
        {config ? (
          <Button type="button" size="sm" variant="ghost" onClick={remove} disabled={Boolean(busy)}>
            {busy === "delete" ? <Loader2 className="animate-spin" /> : <Trash2 />} {pick(lang, "Quitar", "Remove")}
          </Button>
        ) : provider.link === "key" ? (
          <Button type="button" size="sm" variant="ghost" onClick={onDiscard}>
            {pick(lang, "Descartar", "Discard")}
          </Button>
        ) : null}
      </div>

      {config ? (
        <ModelChooser
          open={choosing}
          onOpenChange={setChoosing}
          url={`${base}/providers/${provider.id}/models`}
          csrf={csrf}
          lang={lang}
          label={provider.label}
          canList={provider.can_list !== false}
          selected={config.models}
          onSave={saveModels}
        />
      ) : null}
      {linked ? (
        <LinkDialog
          open={linking}
          onOpenChange={setLinking}
          provider={provider}
          csrf={csrf}
          lang={lang}
          personal={personal}
          accept={accept}
          onAccept={setAccept}
          onLinked={(next) => {
            onData(next);
            setLinking(false);
            setMessage({ ok: true, text: pick(lang, "Cuenta vinculada.", "Account linked.") });
          }}
          onPasteToken={async (token) => {
            onData(
              await apiPut<AiProvidersData>(`${base}/providers`, { provider: provider.id, secret: token, accept_personal: true }, csrf)
            );
            setLinking(false);
            setMessage({ ok: true, text: pick(lang, "Token guardado.", "Token saved.") });
          }}
        />
      ) : null}
    </section>
  );
}

function LinkDialog({
  open,
  onOpenChange,
  provider,
  csrf,
  lang,
  accept,
  onAccept,
  onLinked,
  onPasteToken,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  provider: AiProviderView;
  csrf: string;
  lang: Lang;
  personal: boolean;
  accept: boolean;
  onAccept: (value: boolean) => void;
  onLinked: (data: AiProvidersData) => void;
  onPasteToken: (token: string) => Promise<void>;
}) {
  const chatgpt = provider.link === "chatgpt";
  const kind = chatgpt ? "chatgpt" : "claude";
  const [linkId, setLinkId] = useState<string | null>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [token, setToken] = useState("");
  const [mode, setMode] = useState<"web" | "token">("web");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setBusy(true);
    setError(null);
    setUrl(null);
    try {
      const started = await apiPost<{ link_id: string; url: string }>(`/api/v1/account/ai/${kind}/link/start`, {}, csrf);
      setLinkId(started.link_id);
      setUrl(started.url);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (open) {
      setCode("");
      setToken("");
      setMode("web");
      void start();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  function close(next: boolean) {
    if (!next && linkId) void apiPost("/api/v1/account/ai/link/cancel", { link_id: linkId }, csrf).catch(() => {});
    onOpenChange(next);
  }

  async function finish(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "token") {
        await onPasteToken(token.trim());
      } else {
        onLinked(
          await apiPost<AiProvidersData>(
            `/api/v1/account/ai/${kind}/link/finish`,
            { link_id: linkId, code: code.trim(), accept_personal: accept },
            csrf
          )
        );
      }
    } catch (err) {
      setError(errorText(err));
      if (mode === "web") {
        setLinkId(null);
        setUrl(null);
      }
    } finally {
      setBusy(false);
    }
  }

  const redirectOk = !chatgpt || code.trim().startsWith("http://127.0.0.1:1455/");
  return (
    <Dialog open={open} onOpenChange={close}>
      <DialogContent closeLabel={pick(lang, "Cerrar", "Close")}>
        <form onSubmit={finish} className="grid gap-4">
          <div className="grid gap-1">
            <DialogTitle>{chatgpt ? pick(lang, "Vincular tu cuenta de ChatGPT", "Link your ChatGPT account") : pick(lang, "Vincular tu cuenta de Claude", "Link your Claude account")}</DialogTitle>
            <DialogDescription>
              {chatgpt
                ? pick(
                    lang,
                    "Usa «Sign in with ChatGPT», la vía oficial de OpenAI (en preview). El uso cuenta para tu plan; puedes limitarlo o desconectar SLAnything en ChatGPT → Ajustes → Uso.",
                    "Uses “Sign in with ChatGPT”, OpenAI's official route (preview). Usage counts toward your plan; you can limit it or disconnect SLAnything in ChatGPT → Settings → Usage."
                  )
                : pick(
                    lang,
                    "Usa el `claude setup-token` oficial, que corre en el servidor. El token se guarda cifrado y solo se usa en lo que generas tú.",
                    "Uses the official `claude setup-token`, run on the server. The token is stored encrypted and only used for what you generate."
                  )}
            </DialogDescription>
          </div>
          {mode === "web" ? (
            <ol className="m-0 grid list-decimal gap-3 pl-5 text-sm">
              <li>
                {chatgpt ? pick(lang, "Abre ChatGPT y autoriza el acceso.", "Open ChatGPT and authorize access.") : pick(lang, "Abre Anthropic, inicia sesión con tu suscripción y autoriza.", "Open Anthropic, sign in with your subscription and authorize.")}
                <div className="mt-2">
                  {url ? (
                    <Button asChild size="sm" variant="outline">
                      <a href={url} target="_blank" rel="noopener noreferrer">
                        {chatgpt ? "ChatGPT" : "Anthropic"} <ExternalLink />
                      </a>
                    </Button>
                  ) : (
                    <Button type="button" size="sm" variant="outline" disabled={busy} onClick={() => void start()}>
                      {busy ? <Loader2 className="animate-spin" /> : null} {pick(lang, "Empezar de nuevo", "Start again")}
                    </Button>
                  )}
                </div>
              </li>
              <li>
                <label htmlFor={`link-code-${kind}`}>
                  {chatgpt
                    ? pick(lang, "Al terminar, el navegador irá a una página que no carga (empieza por http://127.0.0.1:1455/). Es normal: copia su dirección completa y pégala aquí:", "When done, the browser goes to a page that won't load (starting with http://127.0.0.1:1455/). That's expected: copy its full address and paste it here:")
                    : pick(lang, "Copia el código que muestra Anthropic y pégalo aquí:", "Copy the code Anthropic shows and paste it here:")}
                </label>
                <Input
                  id={`link-code-${kind}`}
                  className="mt-2"
                  autoComplete="off"
                  spellCheck={false}
                  value={code}
                  disabled={!url}
                  onChange={(event) => setCode(event.target.value)}
                />
              </li>
            </ol>
          ) : (
            <Field label={pick(lang, "Token de `claude setup-token`", "Token from `claude setup-token`")} htmlFor="link-token">
              <Input id="link-token" type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} placeholder="sk-ant-oat01-…" />
            </Field>
          )}
          <label className="flex items-start gap-2 text-sm">
            <input type="checkbox" className="mt-1" checked={accept} onChange={(event) => onAccept(event.target.checked)} />
            <span>
              {pick(
                lang,
                "Es mi suscripción personal. Solo la usaré yo para mis propias unidades y acepto las condiciones del proveedor.",
                "This is my personal subscription. Only I will use it for my own units and I accept the provider's terms."
              )}
            </span>
          </label>
          {error ? <p className="m-0 text-sm text-destructive" role="alert">{error}</p> : null}
          <div className="flex flex-wrap items-center justify-between gap-2">
            {!chatgpt ? (
              <Button type="button" variant="link" size="sm" className="px-0" onClick={() => setMode(mode === "web" ? "token" : "web")}>
                {mode === "web" ? pick(lang, "Prefiero pegar un token", "I'd rather paste a token") : pick(lang, "Vincular desde el navegador", "Link from the browser")}
              </Button>
            ) : (
              <span />
            )}
            <Button
              type="submit"
              disabled={busy || !accept || (mode === "web" ? !url || !code.trim() || !redirectOk : !token.trim())}
            >
              {busy ? <Loader2 className="animate-spin" /> : null} {pick(lang, "Vincular", "Link")}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function ModelChooser({
  open,
  onOpenChange,
  url,
  csrf,
  lang,
  label,
  canList,
  selected,
  onSave,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  url: string;
  csrf: string;
  lang: Lang;
  label: string;
  canList: boolean;
  selected: AiModelEntry[];
  onSave: (models: AiModelEntry[]) => Promise<boolean>;
}) {
  const [catalog, setCatalog] = useState<AiModelEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [chosen, setChosen] = useState<Map<string, AiModelEntry>>(new Map());
  const [custom, setCustom] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    setChosen(new Map(selected.map((m) => [m.id, m])));
    setQuery("");
    setError(null);
    if (!canList) {
      setCatalog([]);
      return;
    }
    setCatalog(null);
    let alive = true;
    apiPost<{ models: AiModelEntry[] }>(url, {}, csrf)
      .then((data) => alive && setCatalog(data.models))
      .catch((err) => {
        if (!alive) return;
        setError(errorText(err));
        setCatalog([]);
      });
    return () => {
      alive = false;
    };
  }, [open, url, csrf, canList, selected]);

  const all = useMemo(() => {
    const list = [...(catalog ?? [])];
    for (const model of chosen.values()) if (!list.some((m) => m.id === model.id)) list.unshift(model);
    return list;
  }, [catalog, chosen]);
  const needle = query.trim().toLowerCase();
  const visible = needle ? all.filter((m) => m.id.toLowerCase().includes(needle) || m.label.toLowerCase().includes(needle)) : all;

  function toggle(model: AiModelEntry, on: boolean) {
    setChosen((prev) => {
      const next = new Map(prev);
      if (on) next.set(model.id, model);
      else next.delete(model.id);
      return next;
    });
  }

  async function save() {
    setSaving(true);
    const ok = await onSave(all.filter((m) => chosen.has(m.id)).map((m) => ({ id: m.id, label: chosen.get(m.id)!.label })));
    setSaving(false);
    if (ok) onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[85svh] flex-col" closeLabel={pick(lang, "Cerrar", "Close")}>
        <div className="grid gap-1">
          <DialogTitle>{pick(lang, "Modelos de", "Models of")} {label}</DialogTitle>
          <DialogDescription>{pick(lang, "Solo los modelos activos aparecen en el selector del Estudio.", "Only active models appear in the Studio picker.")}</DialogDescription>
        </div>
        <div className="relative">
          <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input className="pl-9" value={query} onChange={(e) => setQuery(e.target.value)} placeholder={pick(lang, "Buscar modelo", "Search model")} aria-label={pick(lang, "Buscar modelo", "Search model")} />
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            {chosen.size} {pick(lang, "activos", "active")}
          </span>
          <span className="flex gap-3">
            <button type="button" className="hover:text-foreground hover:underline" onClick={() => setChosen(new Map([...chosen, ...visible.map((m) => [m.id, m] as const)]))}>
              {pick(lang, "Activar todos", "Select all")}
            </button>
            <button
              type="button"
              className="hover:text-foreground hover:underline"
              onClick={() => {
                const next = new Map(chosen);
                for (const m of visible) next.delete(m.id);
                setChosen(next);
              }}
            >
              {pick(lang, "Ninguno", "None")}
            </button>
          </span>
        </div>
        <div className="min-h-32 flex-1 overflow-y-auto rounded-lg border border-border">
          {catalog === null ? (
            <p className="m-0 flex items-center gap-2 p-4 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" /> {pick(lang, "Consultando modelos…", "Loading models…")}
            </p>
          ) : visible.length === 0 ? (
            <p className="m-0 p-4 text-sm text-muted-foreground">
              {error ?? pick(lang, "Sin modelos que mostrar: añádelos por su nombre.", "No models to show: add them by name.")}
            </p>
          ) : (
            <ul className="m-0 list-none divide-y divide-border p-0">
              {visible.map((model) => (
                <li key={model.id} className="flex items-center gap-3 px-3 py-2">
                  <input id={`m-${model.id}`} type="checkbox" checked={chosen.has(model.id)} onChange={(e) => toggle(model, e.target.checked)} />
                  <label htmlFor={`m-${model.id}`} className="min-w-0 flex-1 cursor-pointer">
                    <span className="block truncate text-sm">{model.label}</span>
                    {model.label !== model.id ? <span className="block truncate text-xs text-muted-foreground">{model.id}</span> : null}
                    {model.hint ? <span className="block text-xs text-warning">{model.hint}</span> : null}
                  </label>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex gap-2">
          <Input
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                if (custom.trim()) toggle({ id: custom.trim(), label: custom.trim() }, true);
                setCustom("");
              }
            }}
            placeholder={pick(lang, "Añadir un modelo por su nombre", "Add a model by name")}
            aria-label={pick(lang, "Añadir modelo", "Add model")}
          />
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              if (custom.trim()) toggle({ id: custom.trim(), label: custom.trim() }, true);
              setCustom("");
            }}
          >
            {pick(lang, "Añadir", "Add")}
          </Button>
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
            {pick(lang, "Cancelar", "Cancel")}
          </Button>
          <Button type="button" disabled={saving || chosen.size === 0} onClick={() => void save()}>
            {saving ? <Loader2 className="animate-spin" /> : null} {pick(lang, "Guardar", "Save")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
