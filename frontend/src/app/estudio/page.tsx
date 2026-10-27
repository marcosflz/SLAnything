import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { StudioPanel } from "@/components/authoring/StudioPanel";
import { Icon } from "@/components/ui";
import { ApiError, apiGet, getLang, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { AuthoringPayload } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: t(lang, "Estudio") };
}

export default async function StudioPage() {
  const shell = await getShell("/estudio");
  const { lang } = shell;

  let data: AuthoringPayload | null = null;
  try {
    data = await apiGet<AuthoringPayload>("/api/v1/authoring");
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 403)) throw error;
  }

  if (!data) {
    return (
      <AppShell
        user={shell.user}
        course={shell.course}
        courses={shell.courses}
        progress={shell.progress}
        stats={shell.stats}
        site={shell.site}
        lang={lang}
        pathname="/estudio"
        fullPath="/estudio"
        title={t(lang, "Acceso restringido")}
        kicker={t(lang, "Error {code}", { code: 403 })}
      >
        <div className="error-page">
          <div className="error-code">403</div>
          <h1>{t(lang, "Acceso restringido")}</h1>
          <p>{t(lang, "No tienes permiso para ver esta página.")}</p>
          <div className="row" style={{ justifyContent: "center" }}>
            <Link className="btn btn-primary" href="/">
              <Icon name="home" /> {t(lang, "Volver al inicio")}
            </Link>
            <Link className="btn btn-secondary" href="/curso">
              <Icon name="book" /> {t(lang, "Ir al curso")}
            </Link>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={shell.courses}
      progress={shell.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname="/estudio"
      fullPath="/estudio"
      title={t(lang, "Convierte documentos en unidades")}
      kicker={t(lang, "Estudio de autoría")}
    >
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="sparkles" /> {t(lang, "OpenCode · autoría asistida")}
        </span>
        <h2>{t(lang, "Del documento a una unidad publicable")}</h2>
        <p>
          {t(
            lang,
            "Sube un PDF, DOCX, EPUB, Markdown o TXT y OpenCode lo convierte en una unidad didáctica revisable antes de publicarla."
          )}
        </p>
      </div>
      <StudioPanel
        initial={data}
        csrf={shell.user.csrf_token}
        lang={lang}
      />
    </AppShell>
  );
}
