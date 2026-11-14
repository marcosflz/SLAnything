/**
 * Etiquetas de roles, perfiles e invitaciones. Módulo sin "use client": lo usan
 * tanto componentes de servidor (registro, invitación) como de cliente.
 */
import { pick, type Lang } from "@/lib/messages";
import type { InvitationInfo, User } from "@/lib/types";

export function roleLabel(role: string | null | undefined, lang: Lang): string {
  const labels: Record<string, [string, string]> = {
    owner: ["Propietario", "Owner"],
    admin: ["Administración", "Admin"],
    teacher: ["Profesorado", "Teacher"],
    student: ["Estudiante", "Student"],
  };
  const pair = labels[role ?? "student"] ?? labels.student;
  return lang === "en" ? pair[1] : pair[0];
}

/** Perfil visible del usuario en el espacio activo (ADR-021). */
export function profileLabel(user: Pick<User, "profile" | "ws_role" | "is_platform_admin">, lang: Lang): string {
  const labels: Record<string, [string, string]> = {
    self_learner: ["Cuenta individual", "Individual account"],
    student: ["Estudiante", "Student"],
    teacher: ["Profesorado", "Teacher"],
    academy_admin: [
      user.ws_role === "owner" ? "Propietario de la academia" : "Administración de la academia",
      user.ws_role === "owner" ? "Academy owner" : "Academy admin",
    ],
  };
  const pair = user.profile ? labels[user.profile] : null;
  if (!pair) return user.is_platform_admin ? pick(lang, "Superadmin", "Superadmin") : pick(lang, "Sin espacio", "No space");
  return lang === "en" ? pair[1] : pair[0];
}

/** Qué se obtiene al aceptar una invitación (ADR-022). */
export function invitationLabel(info: InvitationInfo, lang: Lang): string {
  if (info.kind === "individual") {
    return pick(
      lang,
      "Abrirás tu cuenta individual: aprenderás y crearás tus propias unidades.",
      "You will open your individual account: learn and create your own units."
    );
  }
  if (info.kind === "academy_owner") {
    return info.academy_name
      ? pick(lang, "Serás el profesor propietario de la academia {a}.", "You will be the teacher who owns the academy {a}.").replace(
          "{a}",
          info.academy_name
        )
      : pick(
          lang,
          "Serás el profesor propietario de una academia nueva. Ponle nombre abajo.",
          "You will be the teacher who owns a new academy. Name it below."
        );
  }
  return pick(lang, "Te unirás a {w} como {r}.", "You will join {w} as {r}.")
    .replace("{w}", info.workspace ?? "")
    .replace("{r}", roleLabel(info.role, lang).toLowerCase());
}
