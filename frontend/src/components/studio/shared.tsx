import { Pill, type PillVariant } from "@/components/ui/pill";
import { pick, type Lang } from "@/lib/messages";
import type { JobStatus, Localized } from "@/lib/types";

export function loc(value: Localized | string | undefined | null, lang: string, fallback = ""): string {
  if (!value) return fallback;
  if (typeof value === "string") return value;
  return value[lang] ?? Object.values(value)[0] ?? fallback;
}

const STATUS: Record<JobStatus, { es: string; en: string; variant: PillVariant }> = {
  queued: { es: "En cola", en: "Queued", variant: "secondary" },
  extracting: { es: "Analizando", en: "Analyzing", variant: "default" },
  awaiting_scope: { es: "Elige el contenido", en: "Choose content", variant: "warning" },
  outlining: { es: "Diseñando temario", en: "Outlining", variant: "default" },
  awaiting_outline: { es: "Revisa el temario", en: "Review outline", variant: "warning" },
  generating: { es: "Generando", en: "Generating", variant: "default" },
  validating: { es: "Validando", en: "Validating", variant: "default" },
  ready: { es: "Lista", en: "Ready", variant: "success" },
  failed: { es: "Error", en: "Failed", variant: "destructive" },
  cancelled: { es: "Cancelada", en: "Cancelled", variant: "secondary" },
};

export function StatusPill({ status, lang }: { status: JobStatus; lang: Lang }) {
  const info = STATUS[status] ?? STATUS.queued;
  const working = ["queued", "extracting", "outlining", "generating", "validating"].includes(status);
  return (
    <Pill variant={info.variant}>
      {working ? <span className="size-1.5 animate-pulse rounded-full bg-current" aria-hidden="true" /> : null}
      {lang === "en" ? info.en : info.es}
    </Pill>
  );
}

export const STEPS = ["upload", "analyze", "scope", "outline", "generate", "review"] as const;
export type Step = (typeof STEPS)[number];

export function stepFor(status: JobStatus): Step {
  switch (status) {
    case "queued":
    case "extracting":
      return "analyze";
    case "awaiting_scope":
      return "scope";
    case "outlining":
    case "awaiting_outline":
      return "outline";
    case "generating":
    case "validating":
      return "generate";
    case "ready":
      return "review";
    default:
      return "analyze";
  }
}

export function stepLabel(step: Step, lang: Lang): string {
  const labels: Record<Step, [string, string]> = {
    upload: ["Subir", "Upload"],
    analyze: ["Analizar", "Analyze"],
    scope: ["Elegir contenido", "Choose content"],
    outline: ["Temario", "Outline"],
    generate: ["Generar", "Generate"],
    review: ["Revisar y publicar", "Review & publish"],
  };
  return pick(lang, labels[step][0], labels[step][1]);
}
