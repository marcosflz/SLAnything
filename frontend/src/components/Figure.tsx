"use client";

import { openLightbox } from "./Lightbox";

export function Figure({
  src,
  alt,
  caption,
  credit,
  wide,
  zoomLabel,
}: {
  src: string;
  alt: string;
  caption: string;
  credit?: string | null;
  wide?: boolean;
  zoomLabel: string;
}) {
  return (
    <figure className={`figure${wide ? " figure-wide" : ""}`}>
      <button
        className="figure-zoom"
        type="button"
        onClick={() => openLightbox(src, alt)}
        aria-label={zoomLabel}
      >
        <img src={src} alt={alt} loading="lazy" decoding="async" />
      </button>
      <figcaption>
        <span>{caption}</span>
        {credit ? <small className="figure-credit">{credit}</small> : null}
      </figcaption>
    </figure>
  );
}
