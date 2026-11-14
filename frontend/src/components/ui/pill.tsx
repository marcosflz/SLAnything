import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const pillVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap [&_svg]:size-3",
  {
    variants: {
      variant: {
        default: "bg-primary-soft text-primary",
        secondary: "bg-muted text-soft-foreground",
        success: "bg-success-soft text-success",
        warning: "bg-warning-soft text-warning",
        destructive: "bg-destructive-soft text-destructive",
        violet: "bg-violet-soft text-violet",
        outline: "border border-border text-soft-foreground",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export type PillVariant = NonNullable<VariantProps<typeof pillVariants>["variant"]>;

/** Etiqueta compacta. Se llama Pill para no chocar con el Badge heredado. */
export function Pill({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof pillVariants>) {
  return <span className={cn(pillVariants({ variant }), className)} {...props} />;
}
