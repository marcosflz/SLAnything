import {
  BarChart3,
  BookMarked,
  BookOpen,
  Building2,
  FolderOpen,
  GraduationCap,
  Home,
  LayoutGrid,
  LineChart,
  ScrollText,
  Settings,
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

/** Navegación por rol en el espacio activo: aprender, enseñar y administrar. */
export function navSections(user: User, lang: Lang): NavSection[] {
  const perms = user.permissions;
  const sections: NavSection[] = [
    {
      label: pick(lang, "Aprender", "Learn"),
      items: [
        { href: "/", label: pick(lang, "Inicio", "Home"), icon: "home" },
        { href: "/cursos", label: pick(lang, "Biblioteca", "Library"), icon: "catalog" },
        { href: "/progreso", label: pick(lang, "Mi progreso", "My progress"), icon: "progress" },
        { href: "/glosario", label: pick(lang, "Glosario", "Glossary"), icon: "glossary" },
        { href: "/recursos", label: pick(lang, "Recursos", "Resources"), icon: "resources" },
      ],
    },
  ];
  if (perms?.author || perms?.teach) {
    const isOrg = user.workspace?.kind === "organization";
    sections.push({
      label: pick(lang, "Crear y enseñar", "Create & teach"),
      items: [
        { href: "/estudio", label: pick(lang, "Estudio", "Studio"), icon: "studio" },
        ...(isOrg
          ? [
              { href: "/analitica", label: pick(lang, "Analítica", "Analytics"), icon: "analytics" } as NavItem,
              { href: "/profesor", label: pick(lang, "Estudiantes", "Students"), icon: "teacher" } as NavItem,
            ]
          : []),
      ],
    });
  }
  if (perms?.admin && user.workspace?.kind === "organization") {
    sections.push({
      label: pick(lang, "Administrar", "Manage"),
      items: [
        { href: "/admin", label: pick(lang, "Resumen", "Overview"), icon: "workspace" },
        { href: "/admin/usuarios", label: pick(lang, "Miembros", "Members"), icon: "members" },
        { href: "/admin/grupos", label: pick(lang, "Grupos", "Groups"), icon: "groups" },
        { href: "/admin/invitaciones", label: pick(lang, "Invitaciones", "Invitations"), icon: "invites" },
        { href: "/admin/auditoria", label: pick(lang, "Auditoría", "Audit log"), icon: "audit" },
      ],
    });
  }
  return sections;
}
