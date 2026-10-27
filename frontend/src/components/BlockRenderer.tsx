import type { Block, LabMap, Lang } from "@/lib/types";
import { t } from "@/lib/messages";
import { CodeBlock } from "./CodeBlock";
import { Figure } from "./Figure";
import { Lab } from "./Lab";
import { PythonRunner } from "./PythonRunner";
import { Icon } from "./ui";

function html(value: unknown): string {
  return typeof value === "string" ? value : "";
}

export function BlockRenderer({
  block,
  index,
  lessonSlug,
  labMeta,
  csrf,
  lang,
}: {
  block: Block;
  index: number;
  lessonSlug: string;
  labMeta: LabMap;
  csrf: string;
  lang: Lang;
}) {
  switch (block.type) {
    case "lead":
      return (
        <p
          className="lesson-lead"
          dangerouslySetInnerHTML={{ __html: html(block.html) }}
        />
      );
    case "p":
      return <p dangerouslySetInnerHTML={{ __html: html(block.html) }} />;
    case "h2":
      return <h2 id={html(block.anchor)}>{html(block.text)}</h2>;
    case "h3":
      return <h3 id={html(block.anchor)}>{html(block.text)}</h3>;
    case "callout": {
      const tone = html(block.tone);
      const symbol =
        tone === "warning" || tone === "danger"
          ? "!"
          : tone === "success"
            ? "✓"
            : tone === "tip"
              ? "★"
              : "i";
      return (
        <aside className={`callout callout-${tone}`}>
          <div className="callout-icon">{symbol}</div>
          <div className="callout-body">
            <strong className="callout-title">{html(block.title)}</strong>
            <div
              className="callout-text"
              dangerouslySetInnerHTML={{ __html: html(block.html) }}
            />
          </div>
        </aside>
      );
    }
    case "figure": {
      const alt = html(block.alt);
      return (
        <Figure
          src={`/static/${html(block.src)}`}
          alt={alt}
          caption={html(block.caption)}
          credit={block.credit ? html(block.credit) : null}
          wide={Boolean(block.wide)}
          zoomLabel={t(lang, "Ampliar imagen: {alt}", { alt })}
        />
      );
    }
    case "code":
      return (
        <CodeBlock
          language={html(block.language)}
          code={html(block.code)}
          caption={block.caption ? html(block.caption) : null}
          lang={lang}
        />
      );
    case "python":
      return (
        <PythonRunner
          code={html(block.code)}
          caption={block.caption ? html(block.caption) : null}
          lessonSlug={lessonSlug}
          index={index}
          csrf={csrf}
          lang={lang}
        />
      );
    case "table": {
      const headers = Array.isArray(block.headers) ? (block.headers as string[]) : [];
      const rows = Array.isArray(block.rows) ? (block.rows as string[][]) : [];
      return (
        <div className="table-wrap">
          <table>
            {block.caption ? <caption>{html(block.caption)}</caption> : null}
            <thead>
              <tr>
                {headers.map((header, position) => (
                  <th
                    key={position}
                    scope="col"
                    dangerouslySetInnerHTML={{ __html: header }}
                  />
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      dangerouslySetInnerHTML={{ __html: cell }}
                    />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {block.note ? (
            <p
              className="table-note"
              dangerouslySetInnerHTML={{ __html: html(block.note) }}
            />
          ) : null}
        </div>
      );
    }
    case "quote":
      return (
        <blockquote className="quote">
          <p dangerouslySetInnerHTML={{ __html: html(block.text) }} />
          {block.source ? <cite>{html(block.source)}</cite> : null}
        </blockquote>
      );
    case "list": {
      const items = Array.isArray(block.items) ? (block.items as string[]) : [];
      const List = block.ordered ? "ol" : "ul";
      return (
        <List className="lesson-list-text">
          {items.map((item, position) => (
            <li key={position} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </List>
      );
    }
    case "lab": {
      const id = html(block.lab);
      return <Lab id={id} meta={labMeta[id]} lang={lang} />;
    }
    case "keypoints": {
      const items = Array.isArray(block.items) ? (block.items as string[]) : [];
      return (
        <div className="keypoints">
          <h3>
            <Icon name="target" /> {t(lang, "Ideas clave")}
          </h3>
          <ul>
            {items.map((item, position) => (
              <li key={position} dangerouslySetInnerHTML={{ __html: item }} />
            ))}
          </ul>
        </div>
      );
    }
    case "check":
      return (
        <details className="self-check">
          <summary>
            <Icon name="circle-help" /> {html(block.question)}
          </summary>
          <div
            className="self-check-answer"
            dangerouslySetInnerHTML={{ __html: html(block.answer) }}
          />
        </details>
      );
    case "divider":
      return <hr className="divider" />;
    default:
      return null;
  }
}
