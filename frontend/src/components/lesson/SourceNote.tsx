import { BookOpen } from "lucide-react";

import { pick, type Lang } from "@/lib/messages";

/** Cita visible al pie de un bloque generado: «Fuente: p. 12, p. 13». */
export function SourceNote({ sources, lang }: { sources: string[]; lang: Lang }) {
  const pages = Array.from(
    new Set(
      sources.map((source) => {
        const match = /:p(\d+)/.exec(source);
        return match ? `p. ${match[1]}` : null;
      })
    )
  ).filter(Boolean);
  if (!pages.length) return null;
  return (
    <p className="-mt-2 mb-4 flex items-center gap-1.5 text-xs text-muted-foreground">
      <BookOpen className="size-3.5" aria-hidden="true" />
      {pick(lang, "Fuente", "Source")}: {pages.join(", ")}
    </p>
  );
}
