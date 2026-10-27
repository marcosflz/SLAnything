import Link from "next/link";

import { CourseCard, ComingSoonCard } from "@/components/course/CourseCard";
import { Icon } from "@/components/ui";
import { pick, t } from "@/lib/messages";
import type { Course, CourseSummary, Lang } from "@/lib/types";

const HERO_TOKENS: Record<Lang, string[]> = {
  es: ["El", "caballero", "miró", "hacia", "la", "llanura", "y", "vio"],
  en: ["The", "knight", "looked", "at", "the", "plain", "and", "saw"],
};

const HERO_BARS: Record<
  Lang,
  Array<{ label: string; width: number; percent: number }>
> = {
  es: [
    { label: "un", width: 74, percent: 34 },
    { label: "una", width: 52, percent: 24 },
    { label: "que", width: 38, percent: 17 },
    { label: "en", width: 21, percent: 9 },
  ],
  en: [
    { label: "a", width: 74, percent: 34 },
    { label: "the", width: 52, percent: 24 },
    { label: "that", width: 38, percent: 17 },
    { label: "in", width: 21, percent: 9 },
  ],
};

export function Landing({
  catalog,
  featured,
  lang,
}: {
  catalog: CourseSummary[];
  featured: Course;
  lang: Lang;
}) {
  const totalLessons = catalog.reduce((sum, course) => sum + course.lesson_count, 0);
  const totalMinutes = catalog.reduce((sum, course) => sum + course.total_minutes, 0);
  const catalogLabel =
    catalog.length === 1
      ? t(lang, "Biblioteca de cursos · 1 curso disponible")
      : t(lang, "Biblioteca de cursos · {n} cursos disponibles", {
          n: catalog.length,
        });

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow-dark">
            <Icon name="grid" /> {catalogLabel}
          </span>
          <h1>
            {t(lang, "Aprende IA desde los libros que")}{" "}
            <em>{t(lang, "la explican")}</em>.
          </h1>
          <p className="hero-lead">
            {t(
              lang,
              "Un aula online con cursos guiados, laboratorios que se ejecutan en el navegador y evaluación integrada. Empieza por el libro que quieras y continúa donde lo dejaste."
            )}
          </p>
          <div className="hero-actions">
            <Link className="btn btn-primary btn-lg" href="/cursos">
              <Icon name="grid" /> {t(lang, "Explorar cursos")}
            </Link>
            <Link className="btn btn-secondary btn-lg" href="/entrar">
              <Icon name="lock" /> {t(lang, "Ya tengo cuenta")}
            </Link>
          </div>
          <div className="hero-meta">
            <span>
              <Icon name="grid" />{" "}
              {catalog.length === 1
                ? t(lang, "1 curso")
                : t(lang, "{n} cursos", { n: catalog.length })}
            </span>
            <span>
              <Icon name="layers" />{" "}
              {t(lang, "{n} capítulos", { n: featured.chapter_count })}
            </span>
            <span>
              <Icon name="book" />{" "}
              {t(lang, "{n} lecciones", { n: totalLessons })}
            </span>
            <span>
              <Icon name="clock" />{" "}
              {t(lang, "{n} minutos", { n: totalMinutes })}
            </span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="hero-card">
            <div className="hero-card-top">
              <span className="dot" />{" "}
              {t(lang, "Aula LLM · predicción en vivo")}
            </div>
            <p className="hero-prompt">
              <strong>{pick(lang, "El caballero", "The knight")}</strong>{" "}
              {pick(
                lang,
                "miró hacia la llanura y vio…",
                "looked at the plain and saw…"
              )}
            </p>
            <div className="hero-tokens">
              {HERO_TOKENS[lang].map((token, index) => (
                <span className="hero-token" key={`${token}-${index}`}>
                  {token}
                </span>
              ))}
              <span className="hero-token is-next">…</span>
            </div>
            <div className="hero-bars">
              {HERO_BARS[lang].map((bar) => (
                <div className="hero-bar" key={bar.label}>
                  <span>{bar.label}</span>
                  <div className="hero-bar-track">
                    <span style={{ width: `${bar.width}%` }} />
                  </div>
                  <span>{bar.percent} %</span>
                </div>
              ))}
            </div>
          </div>
          <div className="hero-float">
            <Icon name="check-circle" />{" "}
            <span>
              <strong>{t(lang, "Progreso guardado")}</strong>
              <br />
              {t(lang, "Continúa donde lo dejaste")}
            </span>
          </div>
        </div>
      </section>

      <section className="landing-section" id="cursos">
        <span className="eyebrow-dark">{t(lang, "Cursos")}</span>
        <h2 className="section-title">{t(lang, "Elige tu próximo libro")}</h2>
        <p className="section-sub">
          {t(
            lang,
            "Cada curso es un recorrido completo con lecciones, laboratorios y quizzes. La biblioteca crecerá con nuevos libros."
          )}
        </p>
        <div className="catalog-grid">
          {catalog.map((course) => (
            <CourseCard key={course.slug} course={course} lang={lang} />
          ))}
          <ComingSoonCard lang={lang} />
        </div>
      </section>

      <section className="landing-section" id="como-funciona">
        <span className="eyebrow-dark">{t(lang, "Cómo funciona")}</span>
        <h2 className="section-title">
          {t(lang, "Menos vídeos. Más entender haciendo.")}
        </h2>
        <p className="section-sub">
          {t(
            lang,
            "Cada lección combina una idea, una imagen o una demo, y una comprobación. Si algo no queda claro, vuelves al laboratorio y cambias un parámetro."
          )}
        </p>
        <div className="feature-grid">
          <article className="feature">
            <div className="feature-icon">
              <Icon name="book" />
            </div>
            <h3>{t(lang, "Lecciones con hilo")}</h3>
            <p>
              {t(
                lang,
                "Capítulos breves que construyen intuición: del texto tokenizado a la atención, el pretraining y las instrucciones."
              )}
            </p>
          </article>
          <article className="feature">
            <div className="feature-icon">
              <Icon name="sparkles" />
            </div>
            <h3>{t(lang, "Laboratorios reales")}</h3>
            <p>
              {t(
                lang,
                "Entrena un modelo de n-gramas con El Quijote, ajusta la temperatura, explora la atención y calcula el coste de entrenar a escala."
              )}
            </p>
          </article>
          <article className="feature">
            <div className="feature-icon">
              <Icon name="target" />
            </div>
            <h3>{t(lang, "Progreso y quiz")}</h3>
            <p>
              {t(
                lang,
                "Marca lecciones, guarda apuntes y comprueba tu comprensión con preguntas corregidas en el servidor."
              )}
            </p>
          </article>
        </div>
      </section>

      <section className="landing-section" id="programa">
        <span className="eyebrow-dark">{t(lang, "Dentro del curso")}</span>
        <h2 className="section-title">
          {t(lang, "Entiende cómo funciona ChatGPT. Luego constrúyelo.")}
        </h2>
        <p className="section-sub">
          {t(
            lang,
            "El curso de referencia recorre el libro en {n} capítulos. Del texto tokenizado a la atención, el pretraining y las instrucciones.",
            { n: featured.chapter_count }
          )}
        </p>
        <div className="program-grid">
          {featured.chapters.map((chapter) => (
            <article className="program-item" key={chapter.slug}>
              <span className="program-num">
                {String(chapter.number).padStart(2, "0")}
              </span>
              <div>
                <h3>{chapter.title}</h3>
                <p>{chapter.subtitle}</p>
              </div>
              <span className="minutes">
                {chapter.lesson_count} lecciones · {chapter.total_minutes} min
              </span>
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section">
        <div className="steps">
          <article className="step">
            <h3>{t(lang, "Elige un curso")}</h3>
            <p>
              {t(
                lang,
                "Explora la biblioteca y abre el libro que quieras estudiar. Cada curso tiene su propio temario y progreso."
              )}
            </p>
          </article>
          <article className="step">
            <h3>{t(lang, "Estudia y experimenta")}</h3>
            <p>
              {t(
                lang,
                "Lee, mueve los controles de los laboratorios y marca cada lección al terminarla."
              )}
            </p>
          </article>
          <article className="step">
            <h3>{t(lang, "Demuéstralo")}</h3>
            <p>
              {t(
                lang,
                "Haz el quiz final. Con un 80 % superas el capítulo y consolidas lo aprendido."
              )}
            </p>
          </article>
        </div>
      </section>

      <section className="landing-section">
        <div className="cta-band">
          <div>
            <h2>{t(lang, "Tu próximo tema empieza por el libro adecuado.")}</h2>
            <p>
              {t(
                lang,
                "Sin GPU, sin instalar Python y sin perderte en terminología. Solo tú, el texto y un navegador."
              )}
            </p>
          </div>
          <Link className="btn btn-primary btn-lg" href="/registro">
            <Icon name="arrow-right" /> {t(lang, "Entrar al aula")}
          </Link>
        </div>
      </section>
    </>
  );
}
