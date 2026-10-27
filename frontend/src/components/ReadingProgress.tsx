"use client";

import { useEffect } from "react";

export function ReadingProgress() {
  useEffect(() => {
    const bar = document.querySelector("[data-reading-progress]") as HTMLElement | null;
    const prose = document.querySelector(".prose");
    if (!bar || !prose) return;

    const update = () => {
      const rect = prose.getBoundingClientRect();
      const total = rect.height - window.innerHeight * 0.55;
      const read = Math.min(Math.max(-rect.top + 120, 0), Math.max(total, 1));
      bar.style.width = `${Math.min(100, (read / Math.max(total, 1)) * 100)}%`;
    };

    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, []);

  return null;
}
