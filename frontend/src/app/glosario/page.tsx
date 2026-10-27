import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { GlossaryFilter } from "@/components/GlossaryFilter";
import { Icon } from "@/components/ui";
import { apiGet, getLang, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { GlossaryPayload } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: t(lang, "Glosario") };
}

export default async function GlossaryPage() {
  const shell = await getShell("/glosario");
  const data = await apiGet<GlossaryPayload>("/api/v1/glossary");
  const { lang } = shell;

  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={data.courses}
      progress={data.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname="/glosario"
      fullPath="/glosario"
      title={t(lang, "Glosario")}
      kicker={t(lang, "Vocabulario del curso")}
    >
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="glossary" /> {t(lang, "Curso completo")}
        </span>
        <h2>{t(lang, "Las palabras que necesitas")}</h2>
        <p>
          {t(
            lang,
            "Una definición breve para cada término. Si una te resulta opaca, abre la lección enlazada: ahí está el contexto y el ejemplo."
          )}
        </p>
      </div>

      <GlossaryFilter groups={data.groups} lang={lang} />
    </AppShell>
  );
}
