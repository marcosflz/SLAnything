"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="public-shell">
      <main id="contenido" className="content" style={{ padding: "80px 24px" }}>
        <section className="card card-pad" style={{ maxWidth: 640, margin: "0 auto" }}>
          <span className="eyebrow-dark">500</span>
          <h1>Algo se ha roto</h1>
          <p className="muted">
            Ha ocurrido un error interno. Vuelve a intentarlo en unos segundos.
          </p>
          <button className="btn btn-primary" type="button" onClick={reset}>
            Reintentar
          </button>
        </section>
      </main>
    </div>
  );
}
