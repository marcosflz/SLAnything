"use client";

import { Dialog as D, DropdownMenu as DM, Tabs as T, Tooltip as TT } from "radix-ui";
import { X } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";

/* ----------------------------------------------------------------- Dialog */

export const Dialog = D.Root;
export const DialogTrigger = D.Trigger;
export const DialogClose = D.Close;

export function DialogContent({
  className,
  children,
  closeLabel = "Cerrar",
  side,
  ...props
}: React.ComponentProps<typeof D.Content> & {
  closeLabel?: string;
  side?: "left" | "right";
}) {
  const position = side
    ? cn(
        "fixed inset-y-0 z-50 flex h-full w-[85vw] max-w-sm flex-col bg-card shadow-pop",
        side === "left"
          ? "left-0 border-r data-[state=open]:slide-in-from-left"
          : "right-0 border-l data-[state=open]:slide-in-from-right"
      )
    : "fixed top-1/2 left-1/2 z-50 grid w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl border bg-card p-6 shadow-pop data-[state=open]:zoom-in-95";
  return (
    <D.Portal>
      <D.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-[1px] data-[state=open]:animate-in data-[state=open]:fade-in-0" />
      <D.Content
        className={cn(position, "outline-none data-[state=open]:animate-in", className)}
        {...props}
      >
        {children}
        <D.Close
          className="absolute top-3 right-3 rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          aria-label={closeLabel}
        >
          <X className="size-4" />
        </D.Close>
      </D.Content>
    </D.Portal>
  );
}

export function DialogTitle({ className, ...props }: React.ComponentProps<typeof D.Title>) {
  return <D.Title className={cn("text-lg font-semibold", className)} {...props} />;
}

export function DialogDescription({
  className,
  ...props
}: React.ComponentProps<typeof D.Description>) {
  return (
    <D.Description className={cn("m-0 text-sm text-muted-foreground", className)} {...props} />
  );
}

/* ----------------------------------------------------------- DropdownMenu */

export const Menu = DM.Root;
export const MenuTrigger = DM.Trigger;
export const MenuGroup = DM.Group;

export function MenuContent({
  className,
  sideOffset = 6,
  ...props
}: React.ComponentProps<typeof DM.Content>) {
  return (
    <DM.Portal>
      <DM.Content
        sideOffset={sideOffset}
        className={cn(
          "z-50 min-w-52 overflow-hidden rounded-lg border border-border bg-popover p-1 text-popover-foreground shadow-pop data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
          className
        )}
        {...props}
      />
    </DM.Portal>
  );
}

export function MenuItem({ className, ...props }: React.ComponentProps<typeof DM.Item>) {
  return (
    <DM.Item
      className={cn(
        "relative flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm text-foreground no-underline outline-none select-none hover:no-underline data-[disabled]:opacity-50 data-[highlighted]:bg-muted [&_svg]:size-4 [&_svg]:text-muted-foreground",
        className
      )}
      {...props}
    />
  );
}

export function MenuLabel({ className, ...props }: React.ComponentProps<typeof DM.Label>) {
  return (
    <DM.Label
      className={cn("px-2 py-1.5 text-xs font-medium text-muted-foreground", className)}
      {...props}
    />
  );
}

export function MenuSeparator({ className, ...props }: React.ComponentProps<typeof DM.Separator>) {
  return <DM.Separator className={cn("-mx-1 my-1 h-px bg-border", className)} {...props} />;
}

/* -------------------------------------------------------------------- Tabs */

export const Tabs = T.Root;
export const TabsContent = T.Content;

export function TabsList({ className, ...props }: React.ComponentProps<typeof T.List>) {
  return (
    <T.List
      className={cn(
        "inline-flex h-9 items-center gap-1 rounded-lg bg-muted p-1 text-muted-foreground",
        className
      )}
      {...props}
    />
  );
}

export function TabsTrigger({ className, ...props }: React.ComponentProps<typeof T.Trigger>) {
  return (
    <T.Trigger
      className={cn(
        "inline-flex h-7 cursor-pointer items-center gap-1.5 rounded-md border-0 bg-transparent px-3 text-[13px] font-medium whitespace-nowrap transition data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-card",
        className
      )}
      {...props}
    />
  );
}

/* ----------------------------------------------------------------- Tooltip */

export function Tip({
  content,
  children,
  side = "top",
}: {
  content: React.ReactNode;
  children: React.ReactNode;
  side?: "top" | "right" | "bottom" | "left";
}) {
  return (
    <TT.Provider delayDuration={200}>
      <TT.Root>
        <TT.Trigger asChild>{children}</TT.Trigger>
        <TT.Portal>
          <TT.Content
            side={side}
            sideOffset={6}
            className="z-50 rounded-md bg-foreground px-2 py-1 text-xs text-background shadow-pop data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0"
          >
            {content}
          </TT.Content>
        </TT.Portal>
      </TT.Root>
    </TT.Provider>
  );
}
