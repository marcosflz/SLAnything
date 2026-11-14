import {
  AlertTriangle,
  BookOpenCheck,
  Clock3,
  Download,
  GraduationCap,
  Target,
  TrendingDown,
  Users,
} from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";

import { AreaTrend, BarTrend } from "@/components/charts/Charts";
import { EmptyState, Funnel, Heatmap, KpiCard, PageHeader } from "@/components/charts/Kpi";
import { Forbidden, ShellPage, allowForbidden } from "@/components/shell/ShellPage";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { NativeSelect } from "@/components/ui/form";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/overlay";
import { Pill } from "@/components/ui/pill";
import { Progress } from "@/components/ui/progress";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { apiGet, getLang, getShell } from "@/lib/api";
import { pick, type Lang } from "@/lib/messages";
import type { CourseAnalytics, ItemStat, StudentRow } from "@/lib/types";
import { formatDate, relativeDays } from "@/lib/utils";

export async function generateMetadata(): Promise<Metadata> {
  const lang = await getLang();
  return { title: pick(lang, "Analítica", "Analytics") };
}

function riskLabel(risk: StudentRow["risk"][number], lang: Lang) {
  return {
    never_started: pick(lang, "Sin empezar", "Not started"),
    inactive: pick(lang, "Inactivo", "Inactive"),
    low_score: pick(lang, "Nota baja", "Low score"),
  }[risk];
}

function flagPill(flag: ItemStat["flag"], lang: Lang) {
  if (!flag) return <Pill variant="success">{pick(lang, "OK", "OK")}</Pill>;
  const map = {
    hard: [pick(lang, "Muy difícil", "Too hard"), "destructive"],
    easy: [pick(lang, "Muy fácil", "Too easy"), "secondary"],
    low_discrimination: [pick(lang, "No discrimina", "Low discrimination"), "warning"],
  } as const;
  const [label, variant] = map[flag];
  return <Pill variant={variant}>{label}</Pill>;
}

export default async function AnalyticsPage({
  searchParams,
}: {
  searchParams: Promise<{ course?: string; group?: string; days?: string }>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams();
  if (params.course) query.set("course", params.course);
  if (params.group) query.set("group", params.group);
  query.set("days", params.days ?? "30");
  const path = `/analitica?${query.toString()}`;
  const shell = await getShell(path, params.course);
  const lang = shell.lang;
  const data = await allowForbidden(apiGet<CourseAnalytics>(`/api/v1/analytics/course?${query.toString()}`));
  const title = pick(lang, "Analítica del curso", "Course analytics");

  if (!data) {
    return (
      <ShellPage shell={shell} path={path} title={title} kicker={pick(lang, "Enseñar", "Teach")}>
        <Forbidden lang={lang} />
      </ShellPage>
    );
  }

  const { kpis } = data;
  const daily = data.daily_active.map((item) => ({ day: formatDate(item.day, lang), active: item.active }));
  const funnelSteps = data.funnel.map((step) => ({
    key: step.slug,
    label: `${step.chapter}. ${step.title}`,
    started: step.started,
    completed: step.completed,
  }));

  return (
    <ShellPage shell={shell} path={path} title={title} kicker={shell.user.workspace?.name ?? ""}>
      <PageHeader
        eyebrow={pick(lang, "Analítica", "Analytics")}
        title={data.course.title}
        description={pick(
          lang,
          "Progreso, participación, resultados y calidad de las preguntas de tus estudiantes.",
          "Progress, engagement, results and question quality for your students."
        )}
        actions={
          <>
            <form className="flex flex-wrap items-center gap-2" method="get">
              <NativeSelect name="course" defaultValue={data.course.slug} aria-label={pick(lang, "Curso", "Course")}>
                {data.courses.map((course) => (
                  <option key={course.slug} value={course.slug}>
                    {course.title}
                  </option>
                ))}
              </NativeSelect>
              <NativeSelect name="group" defaultValue={data.group ?? ""} aria-label={pick(lang, "Grupo", "Group")}>
                <option value="">{pick(lang, "Todos los grupos", "All groups")}</option>
                {data.groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </NativeSelect>
              <NativeSelect name="days" defaultValue={String(data.days)} aria-label={pick(lang, "Periodo", "Period")}>
                {[7, 30, 90].map((days) => (
                  <option key={days} value={days}>
                    {pick(lang, "{n} días", "{n} days").replace("{n}", String(days))}
                  </option>
                ))}
              </NativeSelect>
              <Button type="submit" variant="secondary">
                {pick(lang, "Aplicar", "Apply")}
              </Button>
            </form>
            <Button asChild variant="outline">
              <a href={`/api/v1/analytics/course.csv?${query.toString()}`} download>
                <Download /> CSV
              </a>
            </Button>
          </>
        }
      />

      {kpis.students === 0 ? (
        <EmptyState
          icon={Users}
          title={pick(lang, "Todavía no hay estudiantes", "No students yet")}
          description={pick(
            lang,
            "Invita a tus estudiantes o comparte el código de clase desde Administración.",
            "Invite your students or share the class code from Manage."
          )}
          action={
            <Button asChild>
              <Link href="/admin/invitaciones">{pick(lang, "Invitar estudiantes", "Invite students")}</Link>
            </Button>
          }
        />
      ) : (
        <div className="grid gap-6">
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              label={pick(lang, "Estudiantes activos (7 d)", "Active students (7 d)")}
              value={`${kpis.active_week}/${kpis.students}`}
              icon={Users}
              spark={data.daily_active.slice(-14).map((item) => item.active)}
            />
            <KpiCard
              label={pick(lang, "Progreso medio", "Average progress")}
              value={`${kpis.avg_completion}%`}
              icon={BookOpenCheck}
              tone="success"
              hint={data.drop_off ? `${pick(lang, "abandono en", "drop-off at")} «${data.drop_off.title}»` : undefined}
            />
            <KpiCard
              label={pick(lang, "Tasa de aprobados", "Pass rate")}
              value={kpis.pass_rate === null ? "—" : `${kpis.pass_rate}%`}
              icon={GraduationCap}
              tone="violet"
              hint={kpis.avg_score === null ? undefined : `${pick(lang, "nota media", "avg score")} ${kpis.avg_score}%`}
            />
            <KpiCard
              label={pick(lang, "En riesgo", "At risk")}
              value={kpis.at_risk}
              icon={AlertTriangle}
              tone={kpis.at_risk ? "destructive" : "success"}
              hint={`${kpis.study_hours} h ${pick(lang, "de estudio en total", "studied in total")}`}
            />
          </section>

          <Tabs defaultValue="overview">
            <TabsList className="mb-4">
              <TabsTrigger value="overview">{pick(lang, "Resumen", "Overview")}</TabsTrigger>
              <TabsTrigger value="students">{pick(lang, "Estudiantes", "Students")}</TabsTrigger>
              <TabsTrigger value="items">{pick(lang, "Preguntas", "Questions")}</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="grid gap-6">
              <div className="grid gap-6 xl:grid-cols-3">
                <Card className="xl:col-span-2">
                  <CardHeader>
                    <div>
                      <CardTitle>{pick(lang, "Participación diaria", "Daily engagement")}</CardTitle>
                      <CardDescription>{pick(lang, "Estudiantes con actividad cada día", "Students active each day")}</CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <AreaTrend data={daily} x="day" y="active" label={pick(lang, "Estudiantes activos por día", "Active students per day")} />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <div>
                      <CardTitle>{pick(lang, "Tiempo de estudio", "Study time")}</CardTitle>
                      <CardDescription>{pick(lang, "Estudiantes por tramo en el periodo", "Students per bracket in the period")}</CardDescription>
                    </div>
                    <Clock3 className="size-4 text-muted-foreground" aria-hidden="true" />
                  </CardHeader>
                  <CardContent>
                    <BarTrend data={data.time_distribution} x="label" y="students" color="var(--chart-2)" label={pick(lang, "Distribución del tiempo", "Time distribution")} />
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <div>
                    <CardTitle>{pick(lang, "Embudo de lecciones", "Lesson funnel")}</CardTitle>
                    <CardDescription>
                      {data.drop_off
                        ? pick(lang, "Mayor pérdida: «{t}» (−{n} estudiantes)", "Biggest loss: “{t}” (−{n} students)")
                            .replace("{t}", data.drop_off.title)
                            .replace("{n}", String(data.drop_off.loss))
                        : pick(lang, "Cuántos empiezan y completan cada lección", "How many start and complete each lesson")}
                    </CardDescription>
                  </div>
                  <TrendingDown className="size-4 text-muted-foreground" aria-hidden="true" />
                </CardHeader>
                <CardContent className="max-h-[420px] overflow-y-auto scrollbar-thin">
                  <Funnel
                    steps={funnelSteps}
                    total={kpis.students}
                    startedLabel={pick(lang, "Empezada", "Started")}
                    completedLabel={pick(lang, "Completada", "Completed")}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div>
                    <CardTitle>{pick(lang, "Mapa de calor por capítulo", "Chapter heatmap")}</CardTitle>
                    <CardDescription>{pick(lang, "% de lecciones completadas por estudiante y capítulo", "% lessons completed per student and chapter")}</CardDescription>
                  </div>
                  <Target className="size-4 text-muted-foreground" aria-hidden="true" />
                </CardHeader>
                <CardContent>
                  <Heatmap
                    caption={pick(lang, "Progreso por capítulo", "Progress per chapter")}
                    rowHeader={pick(lang, "Estudiante", "Student")}
                    columns={data.heatmap.chapters.map((n) => `${pick(lang, "C", "Ch")}${n}`)}
                    rows={data.heatmap.rows.map((row) => ({ label: row.name, values: row.chapters }))}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="students">
              <Card>
                <Table>
                  <THead>
                    <TR>
                      <TH>{pick(lang, "Estudiante", "Student")}</TH>
                      <TH>{pick(lang, "Progreso", "Progress")}</TH>
                      <TH>{pick(lang, "Nota media", "Avg score")}</TH>
                      <TH>{pick(lang, "Tiempo", "Time")}</TH>
                      <TH>{pick(lang, "Última actividad", "Last active")}</TH>
                      <TH>{pick(lang, "Alertas", "Alerts")}</TH>
                    </TR>
                  </THead>
                  <TBody>
                    {data.students.map((row) => (
                      <TR key={row.user_id}>
                        <TD className="font-medium">{row.name}</TD>
                        <TD className="min-w-36">
                          <div className="flex items-center gap-2">
                            <Progress value={row.completion} className="w-24" label={`${row.name}: ${row.completion}%`} />
                            <span className="tabular text-xs text-muted-foreground">{row.completion}%</span>
                          </div>
                        </TD>
                        <TD className="tabular">{row.avg_score === null ? "—" : `${row.avg_score}%`}</TD>
                        <TD className="tabular">{row.minutes} min</TD>
                        <TD className="text-muted-foreground">{relativeDays(row.last_seen, lang)}</TD>
                        <TD>
                          <div className="flex flex-wrap gap-1">
                            {row.risk.length ? (
                              row.risk.map((risk) => (
                                <Pill key={risk} variant={risk === "low_score" ? "destructive" : "warning"}>
                                  {riskLabel(risk, lang)}
                                </Pill>
                              ))
                            ) : (
                              <Pill variant="success">{pick(lang, "Al día", "On track")}</Pill>
                            )}
                          </div>
                        </TD>
                      </TR>
                    ))}
                  </TBody>
                </Table>
              </Card>
            </TabsContent>

            <TabsContent value="items" className="grid gap-6">
              <p className="m-0 text-sm text-muted-foreground">
                {pick(
                  lang,
                  "p = proporción de aciertos (último intento de cada estudiante). Discriminación = aciertos del 27 % mejor − 27 % peor; por debajo de 0,1 la pregunta no separa a quien domina el tema. Revisa en el Estudio las preguntas marcadas.",
                  "p = share of correct answers (each student's latest attempt). Discrimination = top 27% − bottom 27% correct rate; below 0.1 the question does not separate those who master the topic. Review flagged questions in the Studio."
                )}
              </p>
              {data.quizzes.map((quiz) => (
                <Card key={quiz.quiz_id}>
                  <CardHeader>
                    <div>
                      <CardTitle>
                        {pick(lang, "Capítulo", "Chapter")} {quiz.chapter} · {quiz.title}
                      </CardTitle>
                      <CardDescription>
                        {quiz.attempts} {pick(lang, "estudiantes con intento", "students attempted")}
                      </CardDescription>
                    </div>
                  </CardHeader>
                  {quiz.items.length ? (
                    <Table>
                      <THead>
                        <TR>
                          <TH>#</TH>
                          <TH>{pick(lang, "Pregunta", "Question")}</TH>
                          <TH>p</TH>
                          <TH>{pick(lang, "Discr.", "Discr.")}</TH>
                          <TH>{pick(lang, "Distractor más elegido", "Top distractor")}</TH>
                          <TH>{pick(lang, "Estado", "Status")}</TH>
                        </TR>
                      </THead>
                      <TBody>
                        {quiz.items.map((item) => (
                          <TR key={item.question_id}>
                            <TD className="tabular text-muted-foreground">{item.number}</TD>
                            <TD className="max-w-md">
                              <span className="line-clamp-2">{item.prompt}</span>
                            </TD>
                            <TD className="tabular">{item.p_value.toFixed(2)}</TD>
                            <TD className="tabular">{item.discrimination === null ? "—" : item.discrimination.toFixed(2)}</TD>
                            <TD className="max-w-xs text-muted-foreground">
                              {item.top_distractor ? (
                                <span className="line-clamp-2">
                                  {item.top_distractor} ({Math.round((item.top_distractor_rate ?? 0) * 100)}%)
                                </span>
                              ) : (
                                "—"
                              )}
                            </TD>
                            <TD>{flagPill(item.flag, lang)}</TD>
                          </TR>
                        ))}
                      </TBody>
                    </Table>
                  ) : (
                    <CardContent>
                      <p className="m-0 text-sm text-muted-foreground">{pick(lang, "Sin intentos todavía.", "No attempts yet.")}</p>
                    </CardContent>
                  )}
                </Card>
              ))}
            </TabsContent>
          </Tabs>
        </div>
      )}
    </ShellPage>
  );
}
