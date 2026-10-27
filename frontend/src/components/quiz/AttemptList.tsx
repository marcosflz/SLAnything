import Link from "next/link";

import { Badge } from "@/components/ui";
import { formatDate } from "@/lib/format";
import { t } from "@/lib/messages";
import type { Attempt, Lang } from "@/lib/types";

export function AttemptList({
  attempts,
  lang,
  showBadges = false,
}: {
  attempts: Attempt[];
  lang: Lang;
  showBadges?: boolean;
}) {
  return (
    <div className="attempt-list">
      {attempts.map((attempt) => (
        <Link
          className="attempt-row"
          href={`/quiz/intento/${attempt.id}`}
          key={attempt.id}
        >
          <span
            className={`attempt-score ${
              attempt.passed ? "is-pass" : "is-fail"
            }`}
          >
            {attempt.percent}%
          </span>
          <span>
            <strong>
              {attempt.score}/{attempt.total}
            </strong>
            <span className="attempt-meta">
              {formatDate(attempt.created_at, lang)}
            </span>
          </span>
          <span className="spacer" />
          {showBadges ? (
            <Badge tone={attempt.passed ? "success" : "warning"}>
              {attempt.passed
                ? t(lang, "Aprobado")
                : t(lang, "A repasar")}
            </Badge>
          ) : null}
          <span className="small" style={{ color: "var(--brand)" }}>
            {t(lang, "Revisar →")}
          </span>
        </Link>
      ))}
    </div>
  );
}
