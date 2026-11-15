import {
  BarChart3,
  BookMarked,
  BookOpen,
  Bot,
  Building2,
  FolderOpen,
  Gauge,
  GraduationCap,
  Home,
  Layers,
  LayoutGrid,
  LineChart,
  ScrollText,
  Settings,
  ShieldCheck,
  Sparkles,
  UserPlus,
  Users,
  UsersRound,
  type LucideIcon,
} from "lucide-react";

import { pick, type Lang } from "@/lib/messages";
import type { User } from "@/lib/types";

export const NAV_ICONS = {
  home: Home,
  catalog: LayoutGrid,
  progress: LineChart,
  glossary: BookMarked,
  resources: FolderOpen,
  studio: Sparkles,
  analytics: BarChart3,
  teacher: GraduationCap,
  members: Users,
  groups: UsersRound,
  invites: UserPlus,
  audit: ScrollText,
  settings: Settings,
  workspace: Building2,
  lesson: BookOpen,
  platform: ShieldCheck,
  gauge: Gauge,
  spaces: Layers,
  ai: Bot,
} satisfies Record<string, LucideIcon>;

export interface NavItem {
  href: string;
  label: string;
  icon: keyof typeof NAV_ICONS;
}

export interface NavSection {
  label: string;
  items: NavItem[];
}

/**
 * Navegación por permisos del espacio activo (ADR-021):
 * aprender (todos) · crear (`author`) · enseñar (`teach`) ·
 * administrar la academia (`manage`) · plataforma (`platform`).
 */
export function navSections(user: User, lang: Lang, hasCourse = true): NavSection[] {
  const perms = user.permissions;
  const sections: NavSection[] = [];
  if (user.workspace) {
    sections.push({
      label: pick(lang, "Aprender", "Learn"),
      items: [
        { href: "/", label: pick(lang, "Inicio", "Home"), icon: "home" },
        { href: "/cursos", label: pick(lang, "Biblioteca", "Library"), icon: "catalog" },
        { href: "/progreso", label: pick(lang, "Mi progreso", "My progress"), icon: "progress" },
        ...(hasCourse
          ? [
              { href: "/glosario", label: pick(lang, "Glosario", "Glossary"), icon: "glossary" } as NavItem,
              { href: "/recursos", label: pick(lang, "Recursos", "Resources"), icon: "resources" } as NavItem,
            ]
          : []),
      ],
    });
  }
  const create: NavItem[] = [];
  if (perms?.author) {
    create.push({ href: "/estudio", label: pick(lang, "Estudio", "Studio"), icon: "studio" });
  }
  if (perms?.teach) {
    create.push(
      { href: "/analitica", label: pick(lang, "Analítica", "Analytics"), icon: "analytics" },
      { href: "/profesor", label: pick(lang, "Estudiantes", "Students"), icon: "teacher" }
    );
    // El profesorado invita a su alumnado (ADR-022); la administración lo hace
    // desde «Administrar academia».
    if (!perms?.manage) {
      create.push({ href: "/admin/invitaciones", label: pick(lang, "Invitar alumnos", "Invite students"), icon: "invites" });
    }
  }
  if (create.length) {
    sections.push({
      label: perms?.teach ? pick(lang, "Crear y enseñar", "Create & teach") : pick(lang, "Crear", "Create"),
      items: create,
    });
  }
  if (perms?.manage) {
    sections.push({
      label: pick(lang, "Administrar academia", "Manage academy"),
      items: [
        { href: "/admin", label: pick(lang, "Resumen", "Overview"), icon: "workspace" },
        { href: "/admin/usuarios", label: pick(lang, "Miembros", "Members"), icon: "members" },
        { href: "/admin/grupos", label: pick(lang, "Grupos", "Groups"), icon: "groups" },
        { href: "/admin/invitaciones", label: pick(lang, "Invitaciones", "Invitations"), icon: "invites" },
        { href: "/admin/ia", label: pick(lang, "IA de la academia", "Academy AI"), icon: "ai" },
        { href: "/admin/auditoria", label: pick(lang, "Auditoría", "Audit log"), icon: "audit" },
      ],
    });
  }
  if (perms?.platform) {
    sections.push({
      label: pick(lang, "Plataforma", "Platform"),
      items: [
        { href: "/plataforma", label: pick(lang, "Resumen", "Overview"), icon: "gauge" },
        { href: "/plataforma/usuarios", label: pick(lang, "Usuarios", "Users"), icon: "members" },
        { href: "/plataforma/invitaciones", label: pick(lang, "Invitaciones", "Invitations"), icon: "invites" },
        { href: "/plataforma/espacios", label: pick(lang, "Espacios", "Spaces"), icon: "spaces" },
        { href: "/plataforma/cursos", label: pick(lang, "Cursos", "Courses"), icon: "catalog" },
        { href: "/plataforma/ia", label: pick(lang, "Proveedor de IA", "AI provider"), icon: "ai" },
      ],
    });
  }
  return sections;
}
