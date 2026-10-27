import { formatDate, initials, percent } from "@/lib/format";
import { t } from "@/lib/messages";
import type { Lang, TeacherStudent } from "@/lib/types";
import { Badge, Icon } from "../ui";

export function TeacherTable({
  students,
  totalLessons,
  lang,
}: {
  students: TeacherStudent[];
  totalLessons: number;
  lang: Lang;
}) {
  return (
    <section className="card mt-4">
      <div className="card-head" style={{ padding: "18px 20px 0" }}>
        <h3 className="card-title">
          <Icon name="users" /> {t(lang, "Estudiantes")}
        </h3>
        <span className="small muted">
          {students.length} {t(lang, "en total")}
        </span>
      </div>

      {students.length ? (
        <div
          className="table-wrap"
          style={{
            margin: 0,
            border: 0,
            borderRadius: "0 0 var(--radius) var(--radius)",
          }}
        >
          <table className="teacher-table">
            <thead>
              <tr>
                <th>{t(lang, "Estudiante")}</th>
                <th>{t(lang, "Progreso")}</th>
                <th>{t(lang, "Mejor quiz")}</th>
                <th>{t(lang, "Intentos")}</th>
                <th>{t(lang, "Última actividad")}</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td>
                    <div className="student-cell">
                      <span className="avatar avatar-sm">
                        {initials(student.name)}
                      </span>
                      <span>
                        <strong>{student.name}</strong>
                        <small>{student.email}</small>
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className="mini-bar">
                      <span
                        style={{
                          width: `${percent(
                            student.completed,
                            totalLessons
                          )}%`,
                        }}
                      />
                    </span>
                    <span className="small">
                      {student.completed}/{totalLessons}
                    </span>
                  </td>
                  <td>
                    {student.best_score !== null ? (
                      <Badge
                        tone={
                          student.best_score >= 80 ? "success" : "warning"
                        }
                      >
                        {Math.round(student.best_score)} %
                      </Badge>
                    ) : (
                      <span className="muted small">—</span>
                    )}
                  </td>
                  <td className="small">{student.attempts}</td>
                  <td className="small muted">
                    {formatDate(student.last_seen, lang)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-search" style={{ margin: 18 }}>
          <p className="mb-0">
            {t(lang, "Todavía no hay estudiantes registrados.")}
          </p>
        </div>
      )}
    </section>
  );
}
