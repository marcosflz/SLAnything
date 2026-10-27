"use client";

import { useState } from "react";

import { t } from "@/lib/messages";
import type { Lang } from "@/lib/types";

export function CodeBlock({
  language,
  code,
  caption,
  lang,
}: {
  language: string;
  code: string;
  caption?: string | null;
  lang: Lang;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="code-block">
      <div className="code-head">
        <span className="code-lang">{language}</span>
        {caption ? <span className="code-caption">{caption}</span> : null}
        <button className="code-copy" type="button" onClick={copy}>
          {copied ? t(lang, "Copiado") : t(lang, "Copiar")}
        </button>
      </div>
      <pre>
        <code className={`language-${language}`}>{code}</code>
      </pre>
    </div>
  );
}
