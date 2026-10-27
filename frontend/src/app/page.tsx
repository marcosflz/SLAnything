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
import type { DashboardPayload } from "@/lib/types";

export default async function HomePage() {
  const session = await getSession();

  if (!session.user) {
    const pub = await getPublic();
    return (
      <PublicShell site={pub.site} lang={pub.lang} fullPath="/">
        <Landing catalog={pub.catalog} featured={pub.course} lang={pub.lang} />
      </PublicShell>
    );
  }

  const [shell, data] = await Promise.all([
    getShell("/"),
    apiGet<DashboardPayload>("/api/v1/dashboard"),
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
      kicker={t(shell.lang, "Tu aula")}
    >
      <DashboardHome
        data={data}
        progress={shell.progress}
        lang={shell.lang}
        user={shell.user}
      />
    </AppShell>
  );
}
