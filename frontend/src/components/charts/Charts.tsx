"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { cn } from "@/lib/utils";

type Datum = Record<string, string | number | null>;

const axis = {
  stroke: "var(--muted)",
  fontSize: 11,
  tickLine: false,
  axisLine: false,
} as const;

function ChartTooltip({
  active,
  payload,
  label,
  unit,
}: {
  active?: boolean;
  payload?: { value: number; name: string; color: string }[];
  label?: string;
  unit?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-border bg-popover px-2.5 py-1.5 text-xs shadow-pop">
      <div className="mb-0.5 font-medium text-foreground">{label}</div>
      {payload.map((item) => (
        <div key={item.name} className="flex items-center gap-1.5 text-muted-foreground">
          <span className="size-2 rounded-full" style={{ background: item.color }} />
          <span className="tabular text-foreground">
            {item.value}
            {unit ? ` ${unit}` : ""}
          </span>
        </div>
      ))}
    </div>
  );
}

/** Tabla oculta con los mismos datos, para lectores de pantalla. */
function SrTable({ data, x, y, caption }: { data: Datum[]; x: string; y: string; caption: string }) {
  return (
    <table className="sr-only">
      <caption>{caption}</caption>
      <tbody>
        {data.map((row, index) => (
          <tr key={index}>
            <th scope="row">{row[x]}</th>
            <td>{row[y]}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function AreaTrend({
  data,
  x,
  y,
  label,
  unit,
  height = 180,
  color = "var(--chart-1)",
  className,
}: {
  data: Datum[];
  x: string;
  y: string;
  label: string;
  unit?: string;
  height?: number;
  color?: string;
  className?: string;
}) {
  const id = `grad-${y}-${label.length}`;
  return (
    <figure className={cn("m-0", className)} aria-label={label}>
      <div style={{ height }} aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 6, right: 6, bottom: 0, left: -18 }}>
            <defs>
              <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.28} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="3 3" />
            <XAxis dataKey={x} {...axis} minTickGap={24} />
            <YAxis {...axis} allowDecimals={false} width={40} />
            <Tooltip content={<ChartTooltip unit={unit} />} cursor={{ stroke: "var(--border-strong)" }} />
            <Area
              type="monotone"
              dataKey={y}
              stroke={color}
              strokeWidth={2}
              fill={`url(#${id})`}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <SrTable data={data} x={x} y={y} caption={label} />
    </figure>
  );
}

export function BarTrend({
  data,
  x,
  y,
  label,
  unit,
  height = 180,
  color = "var(--chart-1)",
  className,
}: {
  data: Datum[];
  x: string;
  y: string;
  label: string;
  unit?: string;
  height?: number;
  color?: string;
  className?: string;
}) {
  return (
    <figure className={cn("m-0", className)} aria-label={label}>
      <div style={{ height }} aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 6, right: 6, bottom: 0, left: -18 }}>
            <CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="3 3" />
            <XAxis dataKey={x} {...axis} minTickGap={12} />
            <YAxis {...axis} allowDecimals={false} width={40} />
            <Tooltip content={<ChartTooltip unit={unit} />} cursor={{ fill: "var(--surface-2)" }} />
            <Bar dataKey={y} fill={color} radius={[4, 4, 0, 0]} isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <SrTable data={data} x={x} y={y} caption={label} />
    </figure>
  );
}

export function ScoreLine({
  data,
  x,
  y,
  label,
  passScore = 80,
  height = 180,
  className,
}: {
  data: Datum[];
  x: string;
  y: string;
  label: string;
  passScore?: number;
  height?: number;
  className?: string;
}) {
  return (
    <figure className={cn("m-0", className)} aria-label={label}>
      <div style={{ height }} aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 6, right: 6, bottom: 0, left: -18 }}>
            <CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="3 3" />
            <XAxis dataKey={x} {...axis} minTickGap={16} />
            <YAxis {...axis} domain={[0, 100]} width={40} />
            <ReferenceLine
              y={passScore}
              stroke="var(--success)"
              strokeDasharray="4 4"
              label={{ value: `${passScore}%`, fill: "var(--success)", fontSize: 10, position: "right" }}
            />
            <Tooltip content={<ChartTooltip unit="%" />} />
            <Line
              type="monotone"
              dataKey={y}
              stroke="var(--chart-4)"
              strokeWidth={2}
              dot={{ r: 3, fill: "var(--chart-4)" }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <SrTable data={data} x={x} y={y} caption={label} />
    </figure>
  );
}

export function Sparkline({
  data,
  color = "var(--chart-1)",
  height = 36,
}: {
  data: number[];
  color?: string;
  height?: number;
}) {
  const points = data.map((value, index) => ({ i: index, v: value }));
  return (
    <div style={{ height }} aria-hidden="true">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
          <Area
            type="monotone"
            dataKey="v"
            stroke={color}
            strokeWidth={1.5}
            fill={color}
            fillOpacity={0.12}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
