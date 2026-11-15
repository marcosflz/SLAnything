"use client";

import { Bot } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { NativeSelect } from "@/components/ui/form";
import { apiGetClient } from "@/lib/client";
import { pick, type Lang } from "@/lib/messages";
import type { AiChoice, AiModelGroups } from "@/lib/types";

const KEY = "slanything.studio.model";
const SEP = "\u0000";

const encode = (c: AiChoice) => [c.source, c.provider, c.model].join(SEP);
function decode(value: string): AiChoice | null {
  const [source, provider, model] = value.split(SEP);
  return source && provider && model ? { source: source as AiChoice["source"], provider, model } : null;
}

function stored(): AiChoice | null {
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as AiChoice) : null;
  } catch {
    return null;
  }
}

/**
 * Selector de modelo del Estudio (ADR-025): todos los modelos activos de la persona, agrupados por
 * proveedor (suyos, compartidos por su academia y el de la plataforma). Recuerda la última elección.
 */
export function ModelPicker({
  lang,
  value,
  onChange,
  id = "studio-model",
}: {
  lang: Lang;
  value: AiChoice | null;
  onChange: (choice: AiChoice | null) => void;
  id?: string;
}) {
  const [data, setData] = useState<AiModelGroups | null>(null);

  useEffect(() => {
    let alive = true;
    apiGetClient<AiModelGroups>("/api/v1/ai/models")
      .then((groups) => {
        if (!alive) return;
        setData(groups);
        const valid = (c: AiChoice | null) =>
          Boolean(c && groups.groups.some((g) => g.source === c.source && g.provider === c.provider && g.models.some((m) => m.id === c.model)));
        if (!valid(value)) {
          const remembered = stored();
          onChange(valid(remembered) ? remembered : groups.default);
        }
      })
      .catch(() => alive && setData({ groups: [], default: null }));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!data) {
    return (
      <p className="m-0 text-xs text-muted-foreground" data-model-picker="loading">
        {pick(lang, "Cargando modelos…", "Loading models…")}
      </p>
    );
  }
  if (data.groups.length === 0) {
    return (
      <p className="m-0 text-xs text-muted-foreground" data-model-picker="empty">
        {pick(lang, "No hay ningún modelo disponible.", "No model available.")}{" "}
        <Link href="/cuenta#proveedor-ia">{pick(lang, "Configurar", "Set up")}</Link>
      </p>
    );
  }
  return (
    <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground" data-model-picker="ready">
      <label htmlFor={id} className="flex items-center gap-1.5">
        <Bot className="size-3.5" aria-hidden="true" /> {pick(lang, "Generar con", "Generate with")}
      </label>
      <NativeSelect
        id={id}
        className="h-8 max-w-full min-w-48 text-[13px] text-foreground"
        value={value ? encode(value) : ""}
        onChange={(event) => {
          const choice = decode(event.target.value);
          onChange(choice);
          try {
            if (choice) window.localStorage.setItem(KEY, JSON.stringify(choice));
          } catch {
            // Sin almacenamiento: la elección dura lo que la página.
          }
        }}
      >
        {data.groups.map((group) => (
          <optgroup key={`${group.source}-${group.provider}`} label={group.label}>
            {group.models.map((model) => (
              <option key={model.id} value={encode({ source: group.source, provider: group.provider, model: model.id })}>
                {model.label}
              </option>
            ))}
          </optgroup>
        ))}
      </NativeSelect>
      <Link href="/cuenta#proveedor-ia">{pick(lang, "Gestionar modelos", "Manage models")}</Link>
    </div>
  );
}
