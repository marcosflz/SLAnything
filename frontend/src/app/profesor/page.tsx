import type { Metadata } from "next";
import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { TeacherTable } from "@/components/teacher/TeacherTable";
import { Icon, Stat } from "@/components/ui";
import { ApiError, apiGet, getLang, getShell } from "@/lib/api";
import { t } from "@/lib/messages";
import type { TeacherPayload } from "@/lib/types";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: t(lang, "Profesorado") };
}

export default async function TeacherPage() {
  const shell = await getShell("/profesor");
  const { lang } = shell;

  let data: TeacherPayload | null = null;
  try {
    data = await apiGet<TeacherPayload>("/api/v1/teacher");
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
        pathname="/profesor"
        fullPath="/profesor"
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

  const teacherStats = data.stats;

  return (
    <AppShell
      user={shell.user}
      course={data.course}
      courses={data.courses}
      progress={data.progress}
      stats={shell.stats}
      site={shell.site}
      lang={lang}
      pathname="/profesor"
      fullPath="/profesor"
      title={t(lang, "Seguimiento del curso")}
      kicker={t(lang, "Panel del profesorado")}
    >
      <div className="page-head">
        <span className="eyebrow-dark">
          <Icon name="graduation" /> {t(lang, "Curso completo")}
        </span>
        <h2>{t(lang, "¿Cómo va la clase?")}</h2>
        <p>
          {t(
            lang,
            "Una vista agregada del avance del estudiantado. Los datos se actualizan con cada lección visitada y cada intento de quiz."
          )}
        </p>
      </div>

      <div className="stat-grid stat-grid-4">
        <Stat
          label={t(lang, "Estudiantes")}
          value={teacherStats.students}
          hint={t(lang, "cuentas registradas")}
          icon="users"
          tone="blue"
        />
        <Stat
          label={t(lang, "Activos (7 días)")}
          value={teacherStats.active_week}
          hint={t(lang, "con actividad reciente")}
          icon="flame"
          tone="amber"
        />
        <Stat
          label={t(lang, "Intentos de quiz")}
          value={teacherStats.attempts}
          hint={t(lang, "en total")}
          icon="trophy"
          tone="violet"
        />
        <Stat
          label={t(lang, "Nota media")}
          value={
            teacherStats.avg_score === null
              ? "—"
              : `${teacherStats.avg_score} %`
          }
          hint={t(lang, "de todos los intentos")}
          icon="chart"
          tone="green"
        />
      </div>

      <TeacherTable
        students={data.students}
        totalLessons={teacherStats.total_lessons}
        lang={lang}
      />

      <div className="callout callout-info mt-4">
        <div className="callout-icon">i</div>
        <div className="callout-body">
          <strong className="callout-title">
            {t(lang, "Nota sobre privacidad")}
          </strong>
          <div className="callout-text">
            {t(
              lang,
              "Este panel muestra datos de progreso con fines didácticos. En una instalación real, limita el acceso, informa al estudiantado y aplica una política de retención."
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
