import Link from "next/link";

import { getLang } from "@/lib/api";
import { t } from "@/lib/messages";

export default async function NotFound() {
  const lang = await getLang();
  return (
    <div className="public-shell">
      <main id="contenido" className="content" style={{ padding: "80px 24px" }}>
        <section className="card card-pad" style={{ maxWidth: 640, margin: "0 auto" }}>
          <span className="eyebrow-dark">404</span>
          <h1>{t(lang, "Página no encontrada")}</h1>
          <p className="muted">
            {t(
              lang,
              "La dirección no existe o el contenido se ha movido."
            )}
          </p>
          <Link className="btn btn-primary" href="/">
            {t(lang, "Volver al inicio")}
          </Link>
        </section>
      </main>
    </div>
  );
}
