import Link from "next/link";

import type { Lang, Site } from "@/lib/types";
import { pick, t } from "@/lib/messages";
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
            <span className="brand-mark">S</span>
            <span className="brand-text">
              <strong>{site.name}</strong>
              <small>{pick(lang, "Aula virtual", "Virtual classroom")}</small>
            </span>
          </Link>
          <nav className="public-links" aria-label={t(lang, "Navegación principal")}>
            <Link href="/#como-funciona">{t(lang, "Cómo funciona")}</Link>
            <Link href="/#para-quien">{pick(lang, "Para quién", "Who it's for")}</Link>
            <Link href="/cursos">{pick(lang, "Biblioteca", "Library")}</Link>
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
              <span className="brand-mark">S</span>
              <span className="brand-text">
                <strong>{site.name}</strong>
                <small>{pick(lang, "Aula virtual", "Virtual classroom")}</small>
              </span>
            </Link>
            <p>
              {pick(
                lang,
                "Convierte apuntes, libros y manuales en cursos con lecciones, cuestionarios y seguimiento del progreso.",
                "Turn notes, books and manuals into courses with lessons, quizzes and progress tracking."
              )}
            </p>
          </div>
          <div className="footer-links">
            <Link href="/entrar">{t(lang, "Entrar")}</Link>
            <Link href="/registro">{t(lang, "Crear cuenta")}</Link>
            <Link href="/salud">{t(lang, "Estado")}</Link>
          </div>
          <p className="footer-credit">
            {pick(
              lang,
              "Material didáctico con fines educativos. Cada curso acredita la fuente en la que se basa.",
              "Educational material. Every course credits the source it is based on."
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
