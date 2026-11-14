import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Sparkline } from "./Charts";

const tones = {
  primary: "bg-primary-soft text-primary",
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  destructive: "bg-destructive-soft text-destructive",
  violet: "bg-violet-soft text-violet",
  teal: "bg-teal-soft text-teal",
} as const;

export function KpiCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "primary",
  delta,
  deltaLabel,
  spark,
  sparkColor,
  className,
}: {
  label: string;
  value: React.ReactNode;
  hint?: React.ReactNode;
  icon?: LucideIcon;
  tone?: keyof typeof tones;
  delta?: number | null;
  deltaLabel?: string;
  spark?: number[];
  sparkColor?: string;
  className?: string;
}) {
  const trend =
    delta === undefined || delta === null ? null : delta > 0 ? "up" : delta < 0 ? "down" : "flat";
  const TrendIcon = trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus;
  return (
    <Card className={cn("flex flex-col gap-3 p-4", className)}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-[13px] font-medium text-muted-foreground">{label}</span>
        {Icon ? (
          <span className={cn("grid size-8 place-items-center rounded-lg", tones[tone])}>
            <Icon className="size-4" aria-hidden="true" />
          </span>
        ) : null}
      </div>
      <div className="flex items-end justify-between gap-3">
        <div className="min-w-0">
          <div className="tabular text-2xl leading-none font-semibold tracking-tight">{value}</div>
          {trend || hint ? (
            <div className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
              {trend ? (
                <span
                  className={cn(
                    "inline-flex items-center gap-0.5 font-medium",
                    trend === "up" && "text-success",
                    trend === "down" && "text-destructive"
                  )}
                >
                  <TrendIcon className="size-3.5" aria-hidden="true" />
                  {delta! > 0 ? "+" : ""}
                  {delta}
                  {deltaLabel ? ` ${deltaLabel}` : ""}
                </span>
              ) : null}
              {hint ? <span>{hint}</span> : null}
            </div>
          ) : null}
        </div>
        {spark && spark.length > 1 ? (
          <div className="w-24 shrink-0">
            <Sparkline data={spark} color={sparkColor} />
          </div>
        ) : null}
      </div>
    </Card>
  );
}

/** Mapa de calor de porcentajes (0–100) con texto visible en cada celda. */
export function Heatmap({
  columns,
  rows,
  caption,
  rowHeader,
}: {
  columns: string[];
  rows: { label: string; values: (number | null)[] }[];
  caption: string;
  rowHeader: string;
}) {
  function cell(value: number | null) {
    if (value === null) return { background: "var(--surface-2)", color: "var(--muted)" };
    const alpha = 0.08 + (value / 100) * 0.82;
    return {
      background: `color-mix(in srgb, var(--brand) ${Math.round(alpha * 100)}%, var(--surface))`,
      color: value > 55 ? "var(--on-brand)" : "var(--text)",
    };
  }
  return (
    <div className="overflow-x-auto scrollbar-thin">
      <table className="w-full border-separate border-spacing-1 text-xs">
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr>
            <th scope="col" className="px-2 text-left font-medium text-muted-foreground">
              {rowHeader}
            </th>
            {columns.map((column) => (
              <th key={column} scope="col" className="min-w-11 font-medium text-muted-foreground">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <th scope="row" className="max-w-40 truncate px-2 text-left font-medium">
                {row.label}
              </th>
              {row.values.map((value, index) => (
                <td
                  key={index}
                  className="tabular h-8 rounded-md text-center font-medium"
                  style={cell(value)}
                >
                  {value === null ? "—" : `${value}%`}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Embudo horizontal: empezaron vs. completaron por paso. */
export function Funnel({
  steps,
  total,
  startedLabel,
  completedLabel,
}: {
  steps: { key: string; label: string; started: number; completed: number }[];
  total: number;
  startedLabel: string;
  completedLabel: string;
}) {
  const max = Math.max(1, total);
  return (
    <div className="grid gap-1.5">
      <div className="mb-1 flex gap-4 text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1.5">
          <span className="size-2.5 rounded-sm bg-primary/25" /> {startedLabel}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="size-2.5 rounded-sm bg-primary" /> {completedLabel}
        </span>
      </div>
      {steps.map((step) => (
        <div key={step.key} className="grid grid-cols-[minmax(0,14rem)_1fr_3.5rem] items-center gap-3 text-xs">
          <span className="truncate text-soft-foreground" title={step.label}>
            {step.label}
          </span>
          <div className="relative h-4 overflow-hidden rounded bg-muted">
            <div className="absolute inset-y-0 left-0 rounded bg-primary/25" style={{ width: `${(step.started / max) * 100}%` }} />
            <div className="absolute inset-y-0 left-0 rounded bg-primary" style={{ width: `${(step.completed / max) * 100}%` }} />
          </div>
          <span className="tabular text-right text-muted-foreground">
            {step.completed}/{step.started}
          </span>
        </div>
      ))}
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-border-strong px-6 py-10 text-center">
      {Icon ? (
        <span className="mb-1 grid size-10 place-items-center rounded-full bg-muted text-muted-foreground">
          <Icon className="size-5" aria-hidden="true" />
        </span>
      ) : null}
      <p className="m-0 font-medium">{title}</p>
      {description ? <p className="m-0 max-w-md text-sm text-muted-foreground">{description}</p> : null}
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}

export function PageHeader({
  title,
  description,
  actions,
  eyebrow,
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  eyebrow?: string;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        {eyebrow ? (
          <p className="m-0 mb-1 text-xs font-medium tracking-wide text-primary uppercase">{eyebrow}</p>
        ) : null}
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        {description ? <p className="m-0 mt-1 max-w-2xl text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
