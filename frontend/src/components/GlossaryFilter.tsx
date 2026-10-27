"use client";

import Link from "next/link";
import { Fragment, useRef } from "react";

import { t } from "@/lib/messages";
import type { GlossaryPayload, Lang } from "@/lib/types";
import { Icon } from "./ui";

export function GlossaryFilter({
  groups,
  lang,
}: {
  groups: GlossaryPayload["groups"];
  lang: Lang;
}) {
  const gridRef = useRef<HTMLDivElement>(null);
  const emptyRef = useRef<HTMLDivElement>(null);

  function filter(rawQuery: string) {
    const grid = gridRef.current;
    if (!grid) return;

    const query = rawQuery.trim().toLocaleLowerCase("es");
    let visible = 0;

    grid.querySelectorAll<HTMLElement>("[data-term-card]").forEach((card) => {
      const match = !query || (card.dataset.term ?? "").includes(query);
      card.hidden = !match;
      if (match) visible += 1;
    });

    grid
      .querySelectorAll<HTMLElement>("[data-glossary-letter]")
      .forEach((letter) => {
        let sibling = letter.nextElementSibling;
        let hasVisible = false;
        while (sibling && !sibling.matches("[data-glossary-letter]")) {
          if (sibling.matches("[data-term-card]:not([hidden])")) hasVisible = true;
          sibling = sibling.nextElementSibling;
        }
        letter.hidden = !hasVisible;
      });

    if (emptyRef.current) emptyRef.current.hidden = visible !== 0;
  }

  return (
    <>
      <div className="search-box">
        <Icon name="search" />
        <label className="sr-only" htmlFor="glosario-busqueda">
          {t(lang, "Buscar término")}
        </label>
        <input
          id="glosario-busqueda"
          type="search"
          placeholder={t(lang, "Buscar un término o una definición…")}
          data-glossary-search
          autoComplete="off"
          onChange={(event) => filter(event.currentTarget.value)}
        />
      </div>

      <div className="glossary-grid" data-glossary-grid ref={gridRef}>
        {groups.map((group) => (
          <Fragment key={group.letter}>
            <div className="glossary-letter" data-glossary-letter>
              {group.letter}
            </div>
            {group.terms.map((term) => (
              <article
                key={`${group.letter}-${term.term}`}
                className="term-card"
                data-term-card
                data-term={`${term.term} ${term.definition}`.toLowerCase()}
              >
                <h3>{term.term}</h3>
                <p>{term.definition}</p>
                {term.lesson ? (
                  <Link href={`/leccion/${term.lesson}`}>
                    {t(lang, "Ver en la lección →")}
                  </Link>
                ) : null}
              </article>
            ))}
          </Fragment>
        ))}
      </div>

      <div className="empty-search" data-glossary-empty ref={emptyRef} hidden>
        <p className="mb-0">
          {t(lang, "No hay términos que coincidan con tu búsqueda.")}
        </p>
      </div>
    </>
  );
}
