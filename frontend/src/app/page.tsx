import { AppShell } from "@/components/AppShell";
import { PublicShell } from "@/components/PublicShell";
import { DashboardHome } from "@/components/home/DashboardHome";
import { Landing } from "@/components/home/Landing";
import {
  apiGet,
  getPublic,
  getSession,
  getShell,
} from "@/lib/api";
import { t } from "@/lib/messages";
import type { AuthoringPayload, DashboardPayload, StudentKpis } from "@/lib/types";

export default async function HomePage() {
  const session = await getSession();

  if (!session.user) {
    const pub = await getPublic();
    return (
      <PublicShell site={pub.site} lang={pub.lang} fullPath="/">
        <Landing catalog={pub.catalog} formats={pub.formats} lang={pub.lang} signupOpen={pub.site.signup_open} />
      </PublicShell>
    );
  }

  const [shell, data, kpis, studio] = await Promise.all([
    getShell("/"),
    apiGet<DashboardPayload>("/api/v1/dashboard"),
    apiGet<StudentKpis>("/api/v1/analytics/me"),
    session.user.permissions?.author
      ? apiGet<AuthoringPayload>("/api/v1/authoring").catch(() => null)
      : Promise.resolve(null),
  ]);

  return (
    <AppShell
      user={shell.user}
      course={shell.course}
      courses={shell.courses}
      progress={shell.progress}
      stats={shell.stats}
      site={shell.site}
      lang={shell.lang}
      pathname="/"
      fullPath="/"
      title={t(shell.lang, "Inicio")}
      kicker={shell.user.workspace?.name ?? t(shell.lang, "Tu aula")}
    >
      <DashboardHome data={data} kpis={kpis} studio={studio} lang={shell.lang} user={shell.user} />
    </AppShell>
  );
}
