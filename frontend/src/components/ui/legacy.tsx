import type { CSSProperties } from "react";

export function Icon({
  name,
  className = "icon",
}: {
  name: string;
  className?: string;
}) {
  return (
    <svg className={className} aria-hidden="true" focusable="false">
      <use href={`#i-${name}`} />
    </svg>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

export function ProgressBar({
  value,
  label,
  tone = "brand",
}: {
  value: number;
  label?: string;
  tone?: string;
}) {
  return (
    <div
      className="progress"
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <span
        className={`progress-bar progress-${tone}`}
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

export function Ring({
  value,
  size = 92,
  label,
}: {
  value: number;
  size?: number;
  label?: string;
}) {
  const radius = size / 2 - 7;
  const circumference = 2 * Math.PI * radius;
  const style = {
    "--ring-circumference": circumference,
    "--ring-value": circumference - (circumference * value) / 100,
  } as CSSProperties;

  return (
    <div className="ring" style={style}>
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} aria-hidden="true">
        <circle className="ring-track" cx={size / 2} cy={size / 2} r={radius} />
        <circle className="ring-fill" cx={size / 2} cy={size / 2} r={radius} />
      </svg>
      <span className="ring-label">
        {value}
        <small>%</small>
      </span>
      {label ? <span className="ring-caption">{label}</span> : null}
    </div>
  );
}

export function Stat({
  label,
  value,
  hint,
  icon = "chart",
  tone = "blue",
}: {
  label: string;
  value: React.ReactNode;
  hint?: string;
  icon?: string;
  tone?: string;
}) {
  return (
    <div className={`stat-card stat-${tone}`}>
      <div className="stat-icon">
        <Icon name={icon} />
      </div>
      <div className="stat-body">
        <span className="stat-label">{label}</span>
        <strong className="stat-value">{value}</strong>
        {hint ? <span className="stat-hint">{hint}</span> : null}
      </div>
    </div>
  );
}

export function LessonStatus({
  progress,
  completedLabel,
  progressLabel,
  pendingLabel,
}: {
  progress: { completed: boolean } | null;
  completedLabel: string;
  progressLabel: string;
  pendingLabel: string;
}) {
  if (progress?.completed) {
    return (
      <span className="lesson-state is-done">
        <Icon name="check" /> {completedLabel}
      </span>
    );
  }
  if (progress) {
    return <span className="lesson-state is-progress">{progressLabel}</span>;
  }
  return <span className="lesson-state">{pendingLabel}</span>;
}
