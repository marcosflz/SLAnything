import type { Metadata } from "next";

import { PageHeader } from "@/components/charts/Kpi";
import { Forbidden, ShellPage, allowForbidden } from "@/components/shell/ShellPage";
import { StudioHome } from "@/components/studio/StudioHome";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";
import type { AuthoringPayload } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Estudio", "Studio") };
}

export default async function StudioPage() {
  const shell = await getShell("/estudio");
  const { lang } = shell;
  const data = await allowForbidden(apiGet<AuthoringPayload>("/api/v1/authoring"));
  const title = pick(lang, "Estudio de autoría", "Authoring studio");

  return (
    <ShellPage shell={shell} path="/estudio" title={title} kicker={shell.user.workspace?.name ?? ""}>
      {data ? (
        <>
          <PageHeader
            eyebrow={pick(lang, "Estudio", "Studio")}
            title={pick(lang, "Del documento a una unidad de aprendizaje", "From document to learning unit")}
            description={pick(
              lang,
              "Convierte apuntes, PDFs y libros en lecciones guiadas con citas a la fuente, autoevaluación y glosario. Tú revisas y decides qué se publica.",
              "Turn notes, PDFs and books into guided lessons with source citations, self-assessment and glossary. You review and decide what gets published."
            )}
          />
          <StudioHome initial={data} csrf={shell.user.csrf_token} lang={lang} />
        </>
      ) : (
        <Forbidden
          lang={lang}
          message={pick(
            lang,
            "El alumnado no crea unidades: estudia los cursos de su academia. Si quieres generar las tuyas, abre tu cuenta individual desde «Mi cuenta».",
            "Students don't create units: they study their academy's courses. To generate your own, open your individual account from “My account”."
          )}
        />
      )}
    </ShellPage>
  );
}
