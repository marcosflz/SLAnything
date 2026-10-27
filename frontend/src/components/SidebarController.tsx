"use client";

import { useEffect } from "react";

export function SidebarController() {
  useEffect(() => {
    const root = document.documentElement;
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.querySelector(".sidebar-backdrop");
    const collapseButton = document.querySelector<HTMLButtonElement>(
      "[data-sidebar-collapse]"
    );

    const open = () => {
      sidebar?.classList.add("is-open");
      backdrop?.classList.add("is-open");
      document.body.classList.add("no-scroll");
    };
    const close = () => {
      sidebar?.classList.remove("is-open");
      backdrop?.classList.remove("is-open");
      document.body.classList.remove("no-scroll");
    };

    const openers = Array.from(
      document.querySelectorAll("[data-sidebar-open]")
    );
    const closers = Array.from(
      document.querySelectorAll("[data-sidebar-close]")
    );
    openers.forEach((button) => button.addEventListener("click", open));
    closers.forEach((button) => button.addEventListener("click", close));

    function syncCollapseButton() {
      if (!collapseButton) return;
      const collapsed = root.classList.contains("sidebar-collapsed");
      const label = collapsed
        ? collapseButton.dataset.expandLabel
        : collapseButton.dataset.collapseLabel;
      collapseButton.setAttribute("aria-expanded", String(!collapsed));
      if (label) {
        collapseButton.setAttribute("aria-label", label);
        collapseButton.setAttribute("title", label);
      }
    }

    function toggleCollapse() {
      const collapsed = root.classList.toggle("sidebar-collapsed");
      try {
        localStorage.setItem("aula-sidebar-collapsed", collapsed ? "1" : "0");
      } catch {
        // localStorage puede no estar disponible.
      }
      syncCollapseButton();
    }

    collapseButton?.addEventListener("click", toggleCollapse);
    syncCollapseButton();

    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") close();
    }
    document.addEventListener("keydown", onKey);

    return () => {
      openers.forEach((button) => button.removeEventListener("click", open));
      closers.forEach((button) => button.removeEventListener("click", close));
      collapseButton?.removeEventListener("click", toggleCollapse);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  return null;
}
