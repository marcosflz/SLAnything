"use client";

import { useState } from "react";

import { apiPost } from "@/lib/client";
import { Icon } from "./ui";

export function LogoutButton({
  csrf,
  label,
  className = "icon-btn",
  title,
  children,
}: {
  csrf: string;
  label: string;
  className?: string;
  title?: string;
  children?: React.ReactNode;
}) {
  const [busy, setBusy] = useState(false);

  async function logout() {
    if (busy) return;
    setBusy(true);
    try {
      await apiPost("/api/v1/auth/logout", {}, csrf);
    } catch {
      // La cookie se borra igualmente al recargar si la sesión ya no existe.
    }
    window.location.href = "/";
  }

  return (
    <button
      className={className}
      type="button"
      onClick={logout}
      disabled={busy}
      title={title ?? label}
      aria-label={label}
    >
      {children ?? <Icon name="logout" />}
    </button>
  );
}
