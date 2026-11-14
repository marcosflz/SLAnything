import type { Metadata } from "next";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { GroupsPanel, type GroupsData } from "@/components/admin/AdminPanels";
import { allowForbidden } from "@/components/shell/ShellPage";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick } from "@/lib/messages";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Grupos", "Groups") };
}

export default async function GroupsPage() {
  const shell = await getShell("/admin/grupos");
  const { lang } = shell;
  const data = await allowForbidden(apiGet<GroupsData>("/api/v1/admin/groups"));
  const courses = shell.courses.filter((c) => c.status === "published").map((c) => ({ slug: c.slug, title: c.title }));
  return (
    <AdminLayout
      shell={shell}
      path="/admin/grupos"
      title={pick(lang, "Grupos y clases", "Groups and classes")}
      description={pick(lang, "Agrupa estudiantes, asigna cursos con fecha límite y filtra la analítica por clase.", "Group students, assign courses with due dates and filter analytics by class.")}
      allowed={Boolean(data)}
    >
      {data ? <GroupsPanel data={data} courses={courses} csrf={shell.user.csrf_token} lang={lang} /> : null}
    </AdminLayout>
  );
}
