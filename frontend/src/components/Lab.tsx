"use client";

import { useEffect, useRef, useState } from "react";

import { t } from "@/lib/messages";
import type { LabMeta, Lang } from "@/lib/types";
import { Icon } from "./ui";

type LabModule = {
  default?: { mount?: (root: HTMLElement) => void };
};

export function Lab({
  id,
  meta,
  lang,
}: {
  id: string;
  meta: LabMeta | undefined;
  lang: Lang;
}) {
  const rootRef = useRef<HTMLElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    let cancelled = false;

    async function mount() {
      try {
        const url = `/static/js/labs/${id}.js`;
        const module = (await import(
          /* webpackIgnore: true */ url
        )) as LabModule;
        if (cancelled) return;
        if (!module.default || typeof module.default.mount !== "function") {
          throw new Error(`Lab ${id} no exporta mount()`);
        }
        const body = root?.querySelector("[data-lab-body]");
        if (body) body.innerHTML = "";
        module.default.mount(root as HTMLElement);
        if (!cancelled) {
          root?.classList.add("is-ready");
          setStatus("ready");
        }
      } catch (error) {
        console.error(`No se pudo cargar el laboratorio ${id}`, error);
        if (!cancelled) setStatus("error");
      }
    }

    if (!("IntersectionObserver" in window)) {
      void mount();
      return () => {
        cancelled = true;
      };
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            observer.unobserve(entry.target);
            void mount();
          }
        }
      },
      { rootMargin: "320px 0px" }
    );
    observer.observe(root);
    return () => {
      cancelled = true;
      observer.disconnect();
    };
  }, [id]);

  return (
    <section
      className={`lab lab-${meta?.accent ?? "blue"}`}
      data-lab={id}
      ref={rootRef}
    >
      <header className="lab-head">
        <div className="lab-title">
          <span className="lab-icon">
            <Icon name={meta?.icon ?? "sparkles"} />
          </span>
          <div>
            <span className="lab-kicker">{t(lang, "Laboratorio interactivo")}</span>
            <h3>{meta?.title ?? id}</h3>
          </div>
        </div>
        <p>{meta?.description ?? ""}</p>
      </header>
      <div className="lab-body" data-lab-body />
      {status === "loading" ? (
        <div className="lab-loading">
          <span className="spinner" /> {t(lang, "Cargando laboratorio…")}
        </div>
      ) : null}
      {status === "error" ? (
        <div className="lab-error">
          <strong>{t(lang, "No se pudo cargar este laboratorio.")}</strong>
          <p>{t(lang, "Recarga la página o revisa la consola del navegador.")}</p>
        </div>
      ) : null}
    </section>
  );
}
