import { cn } from "@/lib/utils";

export function Progress({
  value,
  label,
  className,
  tone = "primary",
}: {
  value: number;
  label?: string;
  className?: string;
  tone?: "primary" | "success" | "warning" | "destructive";
}) {
  const pct = Math.max(0, Math.min(100, Math.round(value)));
  const color = {
    primary: "bg-primary",
    success: "bg-success",
    warning: "bg-warning",
    destructive: "bg-destructive",
  }[tone];
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={pct}
      aria-label={label}
      className={cn("h-2 w-full overflow-hidden rounded-full bg-subtle", className)}
    >
      <div
        className={cn("h-full rounded-full transition-[width]", color)}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("animate-pulse rounded-md bg-subtle", className)} {...props} />;
}
