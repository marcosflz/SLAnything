import {
  ArrowRight,
  BookOpenCheck,
  Clock3,
  Code2,
  Flame,
  FlaskConical,
  GraduationCap,
  LayoutGrid,
  ListChecks,
  RotateCcw,
  Sparkles,
  Target,
} from "lucide-react";
import Link from "next/link";

import { AreaTrend, ScoreLine } from "@/components/charts/Charts";
import { EmptyState, KpiCard } from "@/components/charts/Kpi";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Pill } from "@/components/ui/pill";
import { Progress } from "@/components/ui/progress";
import { pick } from "@/lib/messages";
import type { DashboardPayload, Lang, ProgressMap, StudentKpis, User } from "@/lib/types";
import { formatDate, formatMinutes } from "@/lib/utils";

export function DashboardHome({
  data,
  kpis,
  lang,
  user,
}: {
  data: DashboardPayload;
  kpis: StudentKpis;
  progress?: ProgressMap;
  lang: Lang;
  user: User;
}) {
  const { course, courses, next_lesson } = data;
  const firstName = user.name.trim().split(/\s+/)[0] || user.name;
  const titles = new Map(
    course.chapters.flatMap((chapter) => chapter.lessons.map((lesson) => [lesson.slug, lesson.title] as const))
  );
  const continueSlug = kpis.continue_lesson ?? next_lesson?.slug ?? null;
  const continueTitle = continueSlug ? titles.get(continueSlug) : null;
  const daily = kpis.study.daily.map((day) => ({
    day: formatDate(day.day, lang),
    minutes: Math.round(day.minutes),
  }));
  const weekDelta = kpis.study.week_minutes - kpis.study.prev_week_minutes;
  const scores = kpis.score_trend.map((item, index) => ({
    attempt: `#${index + 1}`,
    percent: item.percent,
  }));
  const canCreate = user.permissions?.author;

  return (
    <div className="grid gap-6">
      {/* Saludo y siguiente paso */}
      <section className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-gradient-to-br from-primary-soft to-card p-5 sm:p-6">
        <div className="min-w-0">
          <p className="m-0 text-xs font-medium tracking-wide text-primary uppercase">{course.title}</p>
          <h2 className="mt-1 text-2xl font-semibold tracking-tight">
            {pick(lang, "Hola", "Hi")}, {firstName}.
          </h2>
          <p className="m-0 mt-1 text-sm text-muted-foreground">
            {kpis.completion.pct === 100
              ? pick(lang, "Has completado el curso. Repasa lo que falle o empieza otro.", "You finished the course. Review weak spots or start another.")
              : kpis.completion.eta
                ? pick(lang, "A tu ritmo actual terminarás el {d}.", "At your current pace you will finish on {d}.").replace("{d}", formatDate(kpis.completion.eta, lang))
                : pick(lang, "Tu siguiente paso está a un clic.", "Your next step is one click away.")}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {continueSlug ? (
            <Button asChild size="lg">
              <Link href={`/leccion/${continueSlug}`} prefetch={false}>
                {pick(lang, "Continuar", "Continue")}: <span className="max-w-56 truncate">{continueTitle}</span>
                <ArrowRight />
              </Link>
            </Button>
          ) : null}
          {canCreate ? (
            <Button asChild variant="outline" size="lg">
              <Link href="/estudio">
                <Sparkles /> {pick(lang, "Crear desde un documento", "Create from a document")}
              </Link>
            </Button>
          ) : null}
        </div>
      </section>

      {/* KPIs */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label={pick(lang, "Indicadores", "Indicators")}>
        <KpiCard
          label={pick(lang, "Estudio esta semana", "Study this week")}
          value={formatMinutes(kpis.study.week_minutes)}
          icon={Clock3}
          delta={weekDelta}
          deltaLabel="min"
          hint={pick(lang, "objetivo {g}", "goal {g}").replace("{g}", formatMinutes(kpis.study.goal_minutes))}
          spark={kpis.study.daily.slice(-14).map((day) => day.minutes)}
        />
        <KpiCard
          label={pick(lang, "Progreso del curso", "Course progress")}
          value={`${kpis.completion.pct}%`}
          icon={BookOpenCheck}
          tone="success"
          hint={pick(lang, "{d} de {t} lecciones", "{d} of {t} lessons")
            .replace("{d}", String(kpis.completion.done))
            .replace("{t}", String(kpis.completion.total))}
        />
        <KpiCard
          label={pick(lang, "Nota media", "Average score")}
          value={kpis.avg_score === null ? "—" : `${kpis.avg_score}%`}
          icon={GraduationCap}
          tone="violet"
          hint={pick(lang, "{n} intentos", "{n} attempts").replace("{n}", String(kpis.score_trend.length))}
          spark={kpis.score_trend.map((item) => item.percent)}
          sparkColor="var(--chart-4)"
        />
        <KpiCard
          label={pick(lang, "Racha de estudio", "Study streak")}
          value={`${kpis.streak} ${kpis.streak === 1 ? pick(lang, "día", "day") : pick(lang, "días", "days")}`}
          icon={Flame}
          tone="warning"
          hint={pick(lang, "solo cuenta aprender", "only learning counts")}
        />
      </section>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>{pick(lang, "Tiempo de estudio", "Study time")}</CardTitle>
              <CardDescription>{pick(lang, "Minutos por día, últimos 28 días", "Minutes per day, last 28 days")}</CardDescription>
            </div>
            <div className="w-40 text-right">
              <div className="mb-1 text-xs text-muted-foreground">
                {pick(lang, "Objetivo semanal", "Weekly goal")} · {kpis.study.goal_pct}%
              </div>
              <Progress value={kpis.study.goal_pct} tone={kpis.study.goal_pct >= 100 ? "success" : "primary"} label={pick(lang, "Objetivo semanal", "Weekly goal")} />
            </div>
          </CardHeader>
          <CardContent>
            <AreaTrend data={daily} x="day" y="minutes" unit="min" label={pick(lang, "Minutos de estudio por día", "Study minutes per day")} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>{pick(lang, "Para repasar", "To review")}</CardTitle>
              <CardDescription>
                {pick(lang, "Preguntas que fallaste en tu último intento", "Questions you missed on your last attempt")}
              </CardDescription>
            </div>
            {kpis.review_count ? <Pill variant="warning">{kpis.review_count}</Pill> : null}
          </CardHeader>
          <CardContent>
            {kpis.review.length ? (
              <ul className="m-0 grid list-none gap-2 p-0">
                {kpis.review.slice(0, 4).map((item) => (
                  <li key={`${item.quiz_id}-${item.question_id}`} className="rounded-lg border border-border p-3">
                    <details>
                      <summary className="cursor-pointer text-sm font-medium">{item.prompt}</summary>
                      <p className="m-0 mt-2 text-sm text-success">✓ {item.answer}</p>
                      <p className="m-0 mt-1 text-xs text-muted-foreground">{item.explanation}</p>
                    </details>
                  </li>
                ))}
                {kpis.review[0] ? (
                  <li>
                    <Button asChild variant="outline" size="sm" className="w-full">
                      <Link href={`/quiz/${kpis.review[0].quiz_id}`}>
                        <RotateCcw /> {pick(lang, "Repetir el cuestionario", "Retake the quiz")}
                      </Link>
                    </Button>
                  </li>
                ) : null}
              </ul>
            ) : (
              <EmptyState
                icon={ListChecks}
                title={pick(lang, "Nada pendiente", "Nothing pending")}
                description={pick(lang, "Cuando falles una pregunta aparecerá aquí para repasarla.", "Questions you miss will show up here for review.")}
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>{pick(lang, "Dominio por capítulo", "Mastery by chapter")}</CardTitle>
              <CardDescription>
                {pick(lang, "40 % lecciones completadas + 60 % mejor nota del quiz", "40% lessons completed + 60% best quiz score")}
              </CardDescription>
            </div>
            <Target className="size-4 text-muted-foreground" aria-hidden="true" />
          </CardHeader>
          <CardContent className="grid gap-3">
            {kpis.chapters.map((chapter) => (
              <Link
                key={chapter.number}
                href={`/cursos/${course.slug}#capitulo-${chapter.number}`}
                className="grid grid-cols-[1.75rem_1fr_3rem] items-center gap-3 rounded-md text-foreground no-underline hover:no-underline"
              >
                <span className="grid size-7 place-items-center rounded-md bg-muted text-xs font-semibold">{chapter.number}</span>
                <span className="min-w-0">
                  <span className="mb-1 block truncate text-sm">{chapter.title}</span>
                  <Progress
                    value={chapter.mastery}
                    tone={chapter.mastery >= 80 ? "success" : chapter.mastery >= 40 ? "primary" : "warning"}
                    label={`${chapter.title}: ${chapter.mastery}%`}
                  />
                </span>
                <span className="tabular text-right text-sm font-medium">{chapter.mastery}%</span>
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>{pick(lang, "Evolución de notas", "Score trend")}</CardTitle>
              <CardDescription>{pick(lang, "Cada intento de cuestionario; aprobado a partir del 80 %", "Each quiz attempt; pass mark 80%")}</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            {scores.length ? (
              <ScoreLine data={scores} x="attempt" y="percent" label={pick(lang, "Nota por intento", "Score per attempt")} />
            ) : (
              <EmptyState
                icon={GraduationCap}
                title={pick(lang, "Aún no hay intentos", "No attempts yet")}
                description={pick(lang, "Haz el cuestionario de un capítulo para ver tu evolución.", "Take a chapter quiz to see your progress.")}
              />
            )}
            <div className="mt-4 grid grid-cols-3 gap-2 border-t border-border pt-4 text-center">
              {[
                { icon: Code2, value: kpis.practice.code_runs, label: pick(lang, "ejecuciones", "code runs") },
                { icon: FlaskConical, value: kpis.practice.lab_interactions, label: pick(lang, "labs", "labs") },
                { icon: ListChecks, value: kpis.practice.checks, label: pick(lang, "comprobaciones", "checks") },
              ].map((item) => (
                <div key={item.label}>
                  <item.icon className="mx-auto mb-1 size-4 text-muted-foreground" aria-hidden="true" />
                  <div className="tabular text-lg font-semibold">{item.value}</div>
                  <div className="text-xs text-muted-foreground">{item.label}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>{pick(lang, "Tus cursos", "Your courses")}</CardTitle>
            <CardDescription>{pick(lang, "Cursos disponibles en este espacio", "Courses available in this workspace")}</CardDescription>
          </div>
          <Button asChild variant="ghost" size="sm">
            <Link href="/cursos">
              <LayoutGrid /> {pick(lang, "Biblioteca", "Library")}
            </Link>
          </Button>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((item) => (
            <Link
              key={item.slug}
              href={`/cursos/${item.slug}`}
              className="group rounded-lg border border-border p-4 text-foreground no-underline transition hover:border-primary/50 hover:no-underline hover:shadow-card"
            >
              <div className="mb-3 flex items-start justify-between gap-2">
                <span className="line-clamp-2 text-sm font-medium group-hover:text-primary">{item.title}</span>
                {item.slug === course.slug ? <Pill>{pick(lang, "Actual", "Current")}</Pill> : null}
              </div>
              <Progress value={item.stats?.pct ?? 0} label={item.title} />
              <div className="mt-2 text-xs text-muted-foreground">
                {item.stats?.pct ?? 0}% · {item.lesson_count} {pick(lang, "lecciones", "lessons")}
              </div>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
