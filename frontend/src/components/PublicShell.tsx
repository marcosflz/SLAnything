import Link from "next/link";

import type { Lang, Site } from "@/lib/types";
import { t } from "@/lib/messages";
import { Icon } from "./ui";
import { ThemeToggle } from "./ThemeToggle";
import { Lightbox } from "./Lightbox";

export function PublicShell({
  site,
  lang,
  fullPath,
  children,
}: {
  site: Site;
  lang: Lang;
  fullPath: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <a className="skip-link" href="#contenido">
        {t(lang, "Saltar al contenido")}
      </a>
      <div className="public-shell">
        <header className="public-nav">
          <Link className="brand brand-public" href="/">
            <span className="brand-mark">λ</span>
            <span className="brand-text">
              <strong>{site.name}</strong>
              <small>{t(lang, "De cero a GPT")}</small>
            </span>
          </Link>
          <nav className="public-links" aria-label={t(lang, "Navegación principal")}>
            <Link href="/cursos">{t(lang, "Cursos")}</Link>
            <Link href="/#como-funciona">{t(lang, "Cómo funciona")}</Link>
            <Link href="/#creditos">{t(lang, "Créditos")}</Link>
          </nav>
          <div className="public-actions">
            <div className="lang-switch" aria-label={t(lang, "Idioma")}>
              <a
                href={`/idioma/es?next=${encodeURIComponent(fullPath)}`}
                className={`lang-link ${lang === "es" ? "is-active" : ""}`}
                lang="es"
                hrefLang="es"
              >
                ES
              </a>
              <a
                href={`/idioma/en?next=${encodeURIComponent(fullPath)}`}
                className={`lang-link ${lang === "en" ? "is-active" : ""}`}
                lang="en"
                hrefLang="en"
              >
                EN
              </a>
            </div>
            <ThemeToggle lang={lang} />
            <Link className="btn btn-ghost" href="/entrar">
              {t(lang, "Entrar")}
            </Link>
            <Link className="btn btn-primary" href="/registro">
              {t(lang, "Empezar gratis")}
            </Link>
          </div>
        </header>

        <main id="contenido">{children}</main>

        <footer className="public-footer" id="creditos">
          <div>
            <Link className="brand brand-public" href="/">
              <span className="brand-mark">λ</span>
              <span className="brand-text">
                <strong>{site.name}</strong>
                <small>{t(lang, "De cero a GPT")}</small>
              </span>
            </Link>
            <p>
              {t(
                lang,
                "Cursos interactivos para entender y construir inteligencia artificial desde los libros que la explican."
              )}
            </p>
          </div>
          <div className="footer-links">
            <Link href="/entrar">{t(lang, "Entrar")}</Link>
            <Link href="/registro">{t(lang, "Crear cuenta")}</Link>
            <Link href="/salud">{t(lang, "Estado")}</Link>
          </div>
          <p className="footer-credit">
            {t(
              lang,
              "Material didáctico con fines educativos. Cada curso acredita el libro en el que se basa."
            )}{" "}
            {site.year}
          </p>
        </footer>
      </div>
      <Lightbox
        label={t(lang, "Vista ampliada de la figura")}
        closeLabel={t(lang, "Cerrar")}
      />
    </>
  );
}
