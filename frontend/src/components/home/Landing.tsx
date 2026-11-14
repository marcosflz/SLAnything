import Link from "next/link";

import { CourseCard } from "@/components/course/CourseCard";
import { Icon } from "@/components/ui";
import { pick } from "@/lib/messages";
import type { CourseSummary, Lang } from "@/lib/types";

/** Ejemplo del flujo documento → temario → unidad, sin atarlo a ninguna materia. */
const SAMPLE_DOC: Record<Lang, { file: string; pages: string; outline: string[] }> = {
  es: {
    file: "apuntes-historia-contemporanea.pdf",
    pages: "48 páginas",
    outline: ["La Revolución industrial", "Liberalismo y nacionalismo", "El movimiento obrero"],
  },
  en: {
    file: "modern-history-notes.pdf",
    pages: "48 pages",
    outline: ["The Industrial Revolution", "Liberalism and nationalism", "The labour movement"],
  },
};

const AUDIENCES = [
  {
    key: "individual",
    icon: "user",
    title: ["Aprendo por mi cuenta", "I learn on my own"],
    text: [
      "Crea tu cuenta individual, sube tus apuntes o un libro y estudia con lecciones, cuestionarios y tu propio progreso.",
      "Create an individual account, upload your notes or a book and study with lessons, quizzes and your own progress.",
    ],
    cta: ["Crear cuenta individual", "Create an individual account"],
    invite: ["Por invitación de la plataforma", "By platform invitation"],
  },
  {
    key: "academia",
    icon: "graduation",
    title: ["Enseño a un grupo", "I teach a group"],
    text: [
      "Crea una academia, invita a tu profesorado y alumnado, asigna cursos por grupo y sigue la analítica de clase.",
      "Create an academy, invite teachers and students, assign courses by group and follow class analytics.",
    ],
    cta: ["Crear una academia", "Create an academy"],
    invite: ["El profesorado entra por invitación de la plataforma", "Teachers join by platform invitation"],
  },
  {
    key: "codigo",
    icon: "key",
    title: ["Soy alumno", "I'm a student"],
    text: [
      "Únete a tu clase con el código o el enlace de invitación que te dé tu profesor. Verás los cursos que te asignen.",
      "Join your class with the code or invitation link from your teacher. You will see the courses assigned to you.",
    ],
    cta: ["Tengo un código de clase", "I have a class code"],
    invite: ["Tu profesor te envía el enlace de invitación", "Your teacher sends you the invitation link"],
  },
] as const;

export function Landing({
  catalog,
  formats,
  lang,
  signupOpen,
}: {
  catalog: CourseSummary[];
  formats: string[];
  lang: Lang;
  /** Con el registro cerrado (ADR-022) no se ofrece crear cuenta. */
  signupOpen: boolean;
}) {
  const doc = SAMPLE_DOC[lang];
  const p = (pair: readonly [string, string]) => pick(lang, pair[0], pair[1]);

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow-dark">
            <Icon name="sparkles" /> {pick(lang, "Aula virtual para cualquier materia", "A virtual classroom for any subject")}
          </span>
          <h1>
            {pick(lang, "Convierte cualquier material en", "Turn any material into")}{" "}
            <em>{pick(lang, "un curso", "a course")}</em>.
          </h1>
          <p className="hero-lead">
            {pick(
              lang,
              "Sube apuntes, un libro o un manual y SLAnything lo transforma en lecciones guiadas, cuestionarios y glosario, siempre con su fuente citada. Aprende por tu cuenta o enseña a toda una clase.",
              "Upload notes, a book or a manual and SLAnything turns it into guided lessons, quizzes and a glossary, always citing its source. Learn on your own or teach a whole class."
            )}
          </p>
          <div className="hero-actions">
            {signupOpen ? (
              <>
                <Link className="btn btn-primary btn-lg" href="/registro">
                  <Icon name="arrow-right" /> {pick(lang, "Empezar gratis", "Start for free")}
                </Link>
                <Link className="btn btn-secondary btn-lg" href="/entrar">
                  <Icon name="lock" /> {pick(lang, "Ya tengo cuenta", "I have an account")}
                </Link>
              </>
            ) : (
              <Link className="btn btn-primary btn-lg" href="/entrar">
                <Icon name="lock" /> {pick(lang, "Entrar", "Log in")}
              </Link>
            )}
          </div>
          {signupOpen ? null : (
            <p className="hero-lead" style={{ fontSize: 14, marginTop: 14 }}>
              {pick(
                lang,
                "El acceso es por invitación: la administración de la plataforma invita a cuentas individuales y profesorado, y el profesorado invita a su alumnado.",
                "Access is by invitation: platform administrators invite individual accounts and teachers, and teachers invite their students."
              )}
            </p>
          )}
          <div className="hero-meta">
            <span>
              <Icon name="folder" /> {formats.join(" · ")}
            </span>
            <span>
              <Icon name="globe" /> {pick(lang, "Español e inglés", "Spanish and English")}
            </span>
          </div>
        </div>

        <div className="hero-visual" aria-hidden="true">
          <div className="hero-card">
            <div className="hero-card-top">
              <span className="dot" /> {pick(lang, "Del documento al curso", "From document to course")}
            </div>
            <p className="hero-prompt">
              <strong>{doc.file}</strong> · {doc.pages}
            </p>
            <div className="hero-tokens">
              {doc.outline.map((item, index) => (
                <span className="hero-token" key={item}>
                  {index + 1}. {item}
                </span>
              ))}
              <span className="hero-token is-next">+ {pick(lang, "cuestionario", "quiz")}</span>
            </div>
            <div className="hero-bars">
              {[
                { label: pick(lang, "Lecciones", "Lessons"), width: 100, value: "9" },
                { label: pick(lang, "Con cita", "Cited"), width: 92, value: "92 %" },
                { label: pick(lang, "Preguntas", "Questions"), width: 60, value: "24" },
              ].map((bar) => (
                <div className="hero-bar" key={bar.label}>
                  <span>{bar.label}</span>
                  <div className="hero-bar-track">
                    <span style={{ width: `${bar.width}%` }} />
                  </div>
                  <span>{bar.value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="hero-float">
            <Icon name="check-circle" />{" "}
            <span>
              <strong>{pick(lang, "Tú revisas el temario", "You review the outline")}</strong>
              <br />
              {pick(lang, "Nada se publica sin tu visto bueno", "Nothing is published without your approval")}
            </span>
          </div>
        </div>
      </section>

      <section className="landing-section" id="como-funciona">
        <span className="eyebrow-dark">{pick(lang, "Cómo funciona", "How it works")}</span>
        <h2 className="section-title">{pick(lang, "Del documento a la evaluación en tres pasos.", "From document to assessment in three steps.")}</h2>
        <p className="section-sub">
          {pick(
            lang,
            "El Estudio lee tu material, propone un temario que puedes editar y genera cada lección citando las páginas en las que se apoya.",
            "The Studio reads your material, proposes an outline you can edit and writes each lesson citing the pages it relies on."
          )}
        </p>
        <div className="steps">
          <article className="step">
            <h3>{pick(lang, "Sube tu material", "Upload your material")}</h3>
            <p>
              {pick(
                lang,
                "Apuntes, libros, manuales o artículos en PDF, Word, EPUB, Markdown o texto. Elige idioma y nivel.",
                "Notes, books, manuals or articles in PDF, Word, EPUB, Markdown or text. Choose language and level."
              )}
            </p>
          </article>
          <article className="step">
            <h3>{pick(lang, "Revisa el temario", "Review the outline")}</h3>
            <p>
              {pick(
                lang,
                "Reordena capítulos y lecciones, ajusta los objetivos y decide qué se genera antes de gastar un solo minuto.",
                "Reorder chapters and lessons, adjust the objectives and decide what gets generated before spending a single minute."
              )}
            </p>
          </article>
          <article className="step">
            <h3>{pick(lang, "Aprende y evalúate", "Learn and assess")}</h3>
            <p>
              {pick(
                lang,
                "Lecciones con comprobaciones, cuestionario por capítulo, glosario, apuntes y un panel con tu progreso.",
                "Lessons with checks, a quiz per chapter, glossary, notes and a dashboard with your progress."
              )}
            </p>
          </article>
        </div>
      </section>

      <section className="landing-section" id="para-quien">
        <span className="eyebrow-dark">{pick(lang, "Para quién", "Who it's for")}</span>
        <h2 className="section-title">{pick(lang, "Una cuenta individual o una academia.", "An individual account or an academy.")}</h2>
        <p className="section-sub">
          {signupOpen
            ? pick(
                lang,
                "Elige cómo vas a usar SLAnything. Siempre puedes unirte más tarde a una clase o abrir tu cuenta individual.",
                "Choose how you will use SLAnything. You can always join a class later or open your individual account."
              )
            : pick(
                lang,
                "Tres formas de usar SLAnything. En todas se entra con un enlace de invitación.",
                "Three ways to use SLAnything. All of them start with an invitation link."
              )}
        </p>
        <div className="feature-grid">
          {AUDIENCES.map((audience) => (
            <article className="feature" key={audience.key}>
              <div className="feature-icon">
                <Icon name={audience.icon} />
              </div>
              <h3>{p(audience.title)}</h3>
              <p>{p(audience.text)}</p>
              {signupOpen ? (
                <Link className="btn btn-secondary" style={{ marginTop: 14 }} href={`/registro?tipo=${audience.key}`}>
                  <Icon name="arrow-right" /> {p(audience.cta)}
                </Link>
              ) : (
                <p style={{ marginTop: 14, fontWeight: 600 }}>
                  <Icon name="key" /> {p(audience.invite)}
                </p>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="landing-section" id="funciones">
        <span className="eyebrow-dark">{pick(lang, "Qué incluye", "What's included")}</span>
        <h2 className="section-title">{pick(lang, "Menos copiar y pegar. Más entender.", "Less copy and paste. More understanding.")}</h2>
        <div className="feature-grid">
          <article className="feature">
            <div className="feature-icon">
              <Icon name="book" />
            </div>
            <h3>{pick(lang, "Lecciones con fuente", "Lessons with sources")}</h3>
            <p>
              {pick(
                lang,
                "Cada bloque cita la página del documento en la que se basa. Si algo no está en tu material, no se inventa.",
                "Every block cites the page of the document it is based on. If something isn't in your material, it isn't made up."
              )}
            </p>
          </article>
          <article className="feature">
            <div className="feature-icon">
              <Icon name="target" />
            </div>
            <h3>{pick(lang, "Evaluación integrada", "Built-in assessment")}</h3>
            <p>
              {pick(
                lang,
                "Preguntas de respuesta única, múltiple o verdadero/falso, corregidas en el servidor y con explicación.",
                "Single-answer, multiple-answer or true/false questions, graded on the server and explained."
              )}
            </p>
          </article>
          <article className="feature">
            <div className="feature-icon">
              <Icon name="chart" />
            </div>
            <h3>{pick(lang, "Progreso y analítica", "Progress and analytics")}</h3>
            <p>
              {pick(
                lang,
                "Tiempo de estudio, racha, dominio por capítulo y, para el profesorado, embudo, alumnado en riesgo y análisis de preguntas.",
                "Study time, streak, mastery by chapter and, for teachers, funnel, students at risk and item analysis."
              )}
            </p>
          </article>
        </div>
      </section>

      {catalog.length ? (
        <section className="landing-section" id="cursos">
          <span className="eyebrow-dark">{pick(lang, "Biblioteca abierta", "Open library")}</span>
          <h2 className="section-title">{pick(lang, "Cursos disponibles para todos", "Courses available to everyone")}</h2>
          <div className="catalog-grid">
            {catalog.map((course) => (
              <CourseCard key={course.slug} course={course} lang={lang} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="landing-section">
        <div className="cta-band">
          <div>
            <h2>{pick(lang, "Tu próximo curso ya está en tus apuntes.", "Your next course is already in your notes.")}</h2>
            <p>
              {pick(
                lang,
                "Sin instalar nada. Solo tu material, un navegador y unos minutos de revisión.",
                "Nothing to install. Just your material, a browser and a few minutes of review."
              )}
            </p>
          </div>
          <Link className="btn btn-primary btn-lg" href={signupOpen ? "/registro" : "/entrar"}>
            <Icon name="arrow-right" />{" "}
            {signupOpen ? pick(lang, "Crear mi cuenta", "Create my account") : pick(lang, "Entrar", "Log in")}
          </Link>
        </div>
      </section>
    </>
  );
}
