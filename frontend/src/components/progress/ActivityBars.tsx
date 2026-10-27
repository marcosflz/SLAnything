import { t } from "@/lib/messages";
import type { ActivityDay, Lang } from "@/lib/types";

export function ActivityBars({
  activity,
  lang,
}: {
  activity: ActivityDay[];
  lang: Lang;
}) {
  const max = activity.reduce(
    (current, day) => Math.max(current, day.count),
    1
  );

  return (
    <div className="activity-bars" style={{ height: 86 }}>
      {activity.map((day, index) => {
        const classes = ["activity-bar"];
        if (day.count) classes.push("has-activity");
        if (day.is_today) classes.push("is-today");

        return (
          <div
            className="activity-day"
            key={day.day}
            title={`${day.label}: ${t(lang, "{n} acciones", {
              n: day.count,
            })}`}
          >
            <div
              className={classes.join(" ")}
              style={{ height: `${6 + (day.count / max) * 62}px` }}
            />
            <span className="activity-label">
              {(index + 1) % 4 === 0 ? day.label : ""}
            </span>
          </div>
        );
      })}
    </div>
  );
}
