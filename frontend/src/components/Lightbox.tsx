"use client";

import { useEffect, useRef } from "react";

export function openLightbox(src: string, alt: string) {
  window.dispatchEvent(
    new CustomEvent("aula:lightbox", { detail: { src, alt } })
  );
}

export function Lightbox({ label, closeLabel }: { label: string; closeLabel: string }) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    function onOpen(event: Event) {
      const detail = (event as CustomEvent<{ src: string; alt: string }>).detail;
      const image = imageRef.current;
      if (!dialog || !image) return;
      image.src = detail.src;
      image.alt = detail.alt || "Figura ampliada";
      if (typeof dialog.showModal === "function") dialog.showModal();
    }

    function onClick(event: MouseEvent) {
      if (event.target === dialog) dialog?.close();
    }

    window.addEventListener("aula:lightbox", onOpen);
    dialog?.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("aula:lightbox", onOpen);
      dialog?.removeEventListener("click", onClick);
    };
  }, []);

  return (
    <dialog className="lightbox" id="lightbox" aria-label={label} ref={dialogRef}>
      <button
        className="lightbox-close"
        type="button"
        data-lightbox-close
        aria-label={closeLabel}
        onClick={() => dialogRef.current?.close()}
      >
        ×
      </button>
      <img alt="" ref={imageRef} />
    </dialog>
  );
}
