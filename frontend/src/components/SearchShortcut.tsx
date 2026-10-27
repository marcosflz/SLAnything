"use client";

import { useEffect } from "react";

export function SearchShortcut() {
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const tag = target?.tagName?.toLowerCase();
      const typing =
        tag === "input" ||
        tag === "textarea" ||
        tag === "select" ||
        target?.isContentEditable;
      if (event.key === "/" && !typing) {
        const input = document.getElementById("busqueda") as HTMLInputElement | null;
        if (input) {
          event.preventDefault();
          input.focus();
        }
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  return null;
}
