export type Lang = "es" | "en";

export type WorkspaceRole = "owner" | "admin" | "teacher" | "student";

export interface WorkspaceRef {
  id: number;
  kind: "personal" | "organization";
  name: string;
  slug: string;
  plan?: string;
  role: WorkspaceRole;
}

/** Matriz de permisos del espacio activo (ADR-021). */
export interface Permissions {
  /** Aprender: biblioteca, progreso y cuenta. */
  learn: boolean;
  /** Estudio: cuenta individual o profesorado de una academia. */
  author: boolean;
  /** Analítica de curso y panel de estudiantes (solo academias). */
  teach: boolean;
  /** Miembros, grupos, invitaciones y auditoría de una academia. */
  manage: boolean;
  /** Alias histórico de `manage`. */
  admin: boolean;
  owner: boolean;
  /** Superadministración de toda la plataforma. */
  platform: boolean;
}

/** Perfil de presentación en el espacio activo. */
export type Profile = "self_learner" | "student" | "teacher" | "academy_admin";

export interface User {
  id: number;
  email: string;
  name: string;
  initials: string;
  csrf_token: string;
  workspace?: WorkspaceRef | null;
  workspaces?: WorkspaceRef[];
  ws_role?: WorkspaceRole | null;
  profile?: Profile | null;
  is_platform_admin?: boolean;
  permissions?: Permissions;
}

export interface Site {
  name: string;
  tagline: string;
  course_title: string | null;
  course_chapter: string | null;
  catalog_count: number;
  /** Registro abierto. Si es false, solo se entra por invitación (ADR-022). */
  signup_open: boolean;
  year: number;
}

/** Invitación pendiente (de academia o de plataforma). */
export interface InvitationInfo {
  source: "academy" | "platform";
  /** member: entra en una academia; individual: cuenta individual; academy_owner: crea su academia. */
  kind: "member" | "individual" | "academy_owner";
  workspace: string | null;
  role: string;
  email: string | null;
  expires_at: string;
  academy_name: string | null;
  needs_academy_name: boolean;
}

export interface DemoAccount {
  profile: Profile | "platform";
  email: string;
  password: string;
}

export interface Book {
  title: string;
  author: string;
  year: number | null;
  url: string | null;
}

export interface LessonSummary {
  number: number;
  slug: string;
  title: string;
  summary: string;
  minutes: number;
  objectives: string[];
  labs: string[];
  quiz_id: string | null;
  chapter_number?: number;
  chapter_title?: string;
  course_slug?: string;
  course_title?: string;
}

export interface Chapter {
  number: number;
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  level: string;
  total_minutes: number;
  lesson_count: number;
  lessons: LessonSummary[];
}

export interface Course {
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  level: string;
  status: "published" | "coming_soon";
  accent: string;
  cover: string | null;
  book: Book | null;
  tags: string[];
  is_sample?: boolean;
  total_minutes: number;
  lesson_count: number;
  chapter_count: number;
  lab_count: number;
  chapters: Chapter[];
  lessons: LessonSummary[];
}

export interface CourseSummary {
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  level: string;
  status: "published" | "coming_soon";
  accent: string;
  cover: string | null;
  book: Book | null;
  tags: string[];
  is_sample?: boolean;
  total_minutes: number;
  lesson_count: number;
  chapter_count: number;
  lab_count: number;
  stats: Stats;
  next_lesson: LessonSummary | null;
  /** Asignado al usuario por su academia (grupo o matrícula directa). */
  assigned?: boolean;
  due_at?: string | null;
}

export type Block = {
  type: string;
  [key: string]: unknown;
};

export interface LessonFull extends LessonSummary {
  key_points: string[];
  blocks: Block[];
  python_blocks: number[];
  word_count: number;
}

export interface ProgressRow {
  completed: boolean;
  first_seen_at: string | null;
  last_seen_at: string | null;
  completed_at: string | null;
  views: number;
}

export type ProgressMap = Record<string, ProgressRow>;

export interface Stats {
  completed: number;
  total: number;
  pct: number;
}

export interface Attempt {
  id: number;
  course_slug: string;
  quiz_id: string;
  score: number;
  total: number;
  percent: number;
  passed: boolean;
  created_at: string;
}

export interface ActivityDay {
  day: string;
  label: string;
  count: number;
  is_today: boolean;
}

export interface QuizMeta {
  id: string;
  title: string;
  description: string;
  pass_score: number;
  total: number;
}

export interface QuizQuestion {
  id: string;
  prompt: string;
  options: string[];
  kind?: "single" | "multiple" | "true_false";
}

export interface QuizFull extends QuizMeta {
  questions: QuizQuestion[];
}

export interface LabMeta {
  title: string;
  description: string;
  icon: string;
  accent: string;
}

export type LabMap = Record<string, LabMeta>;

export interface SessionPayload {
  user: User | null;
  csrf_token: string;
  lang: Lang;
}

export interface PublicPayload {
  course: Course | null;
  catalog: CourseSummary[];
  site: Site;
  lab_meta: LabMap;
  demo_accounts: DemoAccount[];
  formats: string[];
  lang: Lang;
}

export interface CatalogPayload {
  courses: CourseSummary[];
  featured: Course | null;
  site: Site;
  lang: Lang;
}

export interface ShellPayload {
  user: User;
  course: Course | null;
  courses: CourseSummary[];
  default_course_slug: string | null;
  progress: ProgressMap;
  stats: Stats;
  next_lesson: LessonSummary | null;
  lab_meta: LabMap;
  site: Site;
  lang: Lang;
}

export interface DashboardPayload {
  course: Course | null;
  courses: CourseSummary[];
  progress: ProgressMap;
  stats: Stats;
  next_lesson: LessonSummary | null;
  next_progress: ProgressRow | null;
  avg_score: number | null;
  streak: number;
  activity: ActivityDay[];
  attempts: Attempt[];
}

export interface CoursePayload {
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
  stats: Stats;
  next_lesson: LessonSummary | null;
}

export interface CourseDetailPayload extends CoursePayload {
  site: Site;
  lang: Lang;
}

export interface LessonPayload {
  lesson: LessonFull;
  chapter: Chapter;
  progress: ProgressRow | null;
  note: string;
  bookmarked: boolean;
  prev_lesson: LessonSummary | null;
  next_lesson: LessonSummary | null;
  quiz: QuizMeta | null;
  best_attempt: Attempt | null;
  course: Course;
  courses: CourseSummary[];
  all_progress: ProgressMap;
  stats: Stats;
  lab_meta: LabMap;
}

export interface QuizPayload {
  quiz: QuizFull;
  chapter: Chapter;
  attempts: Attempt[];
  best_attempt: Attempt | null;
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface AttemptReviewPayload {
  quiz: QuizMeta;
  chapter: Chapter;
  attempt: Attempt;
  review: Array<{
    number: number;
    question: string;
    selected: number | null;
    selected_text: string;
    correct_text: string;
    is_correct: boolean;
    explanation: string;
  }>;
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface ProgressPayload {
  course: Course | null;
  courses: CourseSummary[];
  progress: ProgressMap;
  stats: Stats;
  rows: Array<{ lesson: LessonSummary; progress: ProgressRow | null }>;
  attempts: Attempt[];
  activity: ActivityDay[];
  avg_score: number | null;
  streak: number;
}

export interface GlossaryTerm {
  term: string;
  definition: string;
  lesson: string | null;
}

export interface GlossaryPayload {
  groups: Array<{ letter: string; terms: GlossaryTerm[] }>;
  course: Course | null;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface ResourceItem {
  title: string;
  description: string;
  href: string;
  icon: string;
  meta: string;
  download: boolean;
}

export interface ResourcesPayload {
  resources: ResourceItem[];
  source: Book | null;
  course: Course | null;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface SearchPayload {
  query: string;
  results: Array<{ lesson: LessonSummary; snippet: string }>;
  course: Course | null;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface TeacherStudent {
  id: number;
  name: string;
  email: string;
  created_at: string;
  completed: number;
  last_seen: string | null;
  best_score: number | null;
  attempts: number;
}

export interface TeacherPayload {
  students: TeacherStudent[];
  stats: {
    students: number;
    attempts: number;
    avg_score: number | null;
    active_week: number;
    total_lessons: number;
  };
  course: Course | null;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface AuthoringProvider {
  id: string;
  label: string;
  requires_key: boolean;
  default_base_url: string | null;
  base_url_editable: boolean;
  models: string[];
  model_optional: boolean;
  notes: string;
  /** Suscripción personal: solo la configura su titular (ADR-024). */
  personal: boolean;
  /** `api`: claves de pago por uso. `subscription`: planes personales (ADR-025). */
  kind?: "api" | "subscription";
  /** Cómo se conecta: clave pegada o vinculación (Claude, ChatGPT). */
  link?: "key" | "claude" | "chatgpt";
  /** Se pueden consultar sus modelos. */
  can_list?: boolean;
}

/** Un modelo activo de un proveedor (ADR-025). */
export interface AiModelEntry {
  id: string;
  label: string;
  /** Aviso del catálogo (p. ej. versión conocida no anunciada por la cuenta). */
  hint?: string;
}

/** Configuración de un proveedor en un ámbito (cuenta o academia). */
export interface AiProviderConfig {
  enabled: boolean;
  key_configured: boolean;
  key_readable: boolean;
  key_hint: string;
  model: string;
  models: AiModelEntry[];
  accepted_personal_at: string | null;
  account: string | null;
  ready: boolean;
  updated_at: string | null;
}

export interface AiProviderView extends AuthoringProvider {
  config: AiProviderConfig | null;
}

/** Elección de modelo: de quién es la credencial, proveedor y modelo. */
export interface AiChoice {
  source: "user" | "workspace" | "platform";
  provider: string;
  model: string;
}

/** `/api/v1/account/ai` (cuenta) o `/api/v1/admin/ai` (academia). */
export interface AiProvidersData {
  enabled: boolean;
  subscription_enabled?: boolean;
  providers: AiProviderView[];
  default?: AiChoice | null;
  claude_cli?: ClaudeCliStatus | null;
}

/** `/api/v1/ai/models`: modelos activos agrupados para el selector del Estudio. */
export interface AiModelGroups {
  groups: {
    source: AiChoice["source"];
    provider: string;
    label: string;
    kind: "api" | "subscription";
    models: AiModelEntry[];
  }[];
  default: AiChoice | null;
}

/** Estado del motor de agentes nas-adk (ADR-023). */
export interface AuthoringEngine {
  enabled: boolean;
  available: boolean;
  version: string | null;
  message: string;
}

/** Con qué proveedor generará la persona actual (sin secretos). */
export interface AuthoringAi {
  source: "user" | "workspace" | "platform";
  provider: string;
  provider_label: string;
  model: string;
  personal: boolean;
}

export interface ClaudeCliStatus {
  available: boolean;
  version: string | null;
  message: string;
}

export interface AuthoringSettings {
  provider: string;
  model: string;
  base_url: string;
  key_configured: boolean;
  key_hint: string;
  requires_key: boolean;
  updated_at: string | null;
  providers: AuthoringProvider[];
  engine: AuthoringEngine;
}

export type JobStatus =
  | "queued"
  | "extracting"
  | "awaiting_scope"
  | "outlining"
  | "awaiting_outline"
  | "generating"
  | "validating"
  | "ready"
  | "failed"
  | "cancelled";

export interface AuthoringJob {
  id: string;
  title: string;
  source_names: string[];
  status: JobStatus;
  status_label: string;
  owner_id?: number;
  workspace_id?: number | null;
  /** "adk" = agentes nas-adk; "direct" y "opencode" son trabajos anteriores. */
  engine: "adk" | "direct" | "opencode";
  stage: string;
  progress: {
    sections?: number;
    chunks?: number;
    pages?: number | null;
    chapters?: number;
    lessons_total?: number;
    lessons_done?: number;
  };
  config: Record<string, unknown>;
  tokens_in: number;
  tokens_out: number;
  provider: string;
  model: string;
  languages: string[];
  course_slug: string | null;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  active: boolean;
  log: string;
}

export interface QualityReport {
  lessons?: number;
  content_blocks?: number;
  cited_blocks?: number;
  cited_pct?: number;
  unsupported?: { lesson: string; block: number; score: number; excerpt: string }[];
  invalid_refs?: { lesson: string; lang: string; block: number; refs: string[] }[];
  warnings?: string[];
  repaired_lessons?: string[];
  questions?: number;
  generated_at?: string;
}

export interface AuthoringCourse {
  slug: string;
  title: string;
  status: "draft" | "published";
  visibility?: "workspace" | "public";
  owner_id?: number;
  workspace_id?: number | null;
  report?: QualityReport;
  package?: CoursePackage;
  job_id: string | null;
  created_at: string;
  updated_at: string;
  summary: {
    slug: string;
    languages: string[];
    titles: Record<string, string>;
    chapter_count: number;
    lesson_count: number;
    quiz_count: number;
    glossary_count: number;
    tags: string[];
    book: Book | null;
  };
}

export type Localized<T = string> = Record<string, T>;

export interface PackageBlock {
  type: string;
  sources?: string[];
  unsupported?: boolean;
  [key: string]: unknown;
}

export interface PackageQuestion {
  id: string;
  kind?: "single" | "multiple" | "true_false";
  prompt: Localized;
  options: Localized<string[]>;
  correct: number | number[];
  explanation: Localized;
  difficulty?: string;
  source?: string;
}

export interface PackageLesson {
  number: number;
  slug: string;
  title: Localized;
  summary: Localized;
  minutes: number;
  objectives: Localized<string[]>;
  key_points: Localized<string[]>;
  blocks: Localized<PackageBlock[]>;
}

export interface PackageChapter {
  number: number;
  slug: string;
  title: Localized;
  subtitle: Localized;
  description: Localized;
  lessons: PackageLesson[];
  quiz: { id: string; title: Localized; description: Localized; pass_score: number; questions: PackageQuestion[] };
  glossary: { term: Localized; definition: Localized; lesson: string | null }[];
}

export interface CoursePackage {
  schema_version: number;
  languages: string[];
  course: { title: Localized; subtitle: Localized; description: Localized; [key: string]: unknown };
  chapters: PackageChapter[];
  [key: string]: unknown;
}

export interface DocumentSection {
  id: string;
  title: string;
  level: number;
  parent: string | null;
  source: string;
  page_start: number | null;
  page_end: number | null;
  chars: number;
  words: number;
  chunks: number;
}

export interface DocumentOutline {
  sources: { key: string; name: string; pages: number | null }[];
  sections: DocumentSection[];
  stats: { chars: number; chunks: number; sections: number; pages: number | null; truncated: boolean };
  warnings: string[];
}

export interface OutlineLesson {
  slug: string;
  title: Localized;
  summary: Localized;
  objectives: string[];
  chunk_ids: string[];
}

export interface OutlineChapter {
  number: number;
  section_id: string;
  slug: string;
  title: Localized;
  subtitle: Localized;
  description: Localized;
  objectives: { id: string; text: Localized }[];
  lessons: OutlineLesson[];
}

export interface CourseOutline {
  course: { title?: Localized; subtitle?: Localized; description?: Localized; [key: string]: unknown };
  chapters: OutlineChapter[];
}

export interface JobEvent {
  ts: string;
  type: "stage" | "progress" | "done" | "warning" | "error" | "ready" | "cancelled" | "tool";
  message: string;
  stage?: string;
  done?: number;
  total?: number;
  course_slug?: string;
}

export interface AuthoringPayload {
  settings: AuthoringSettings;
  jobs: AuthoringJob[];
  courses: AuthoringCourse[];
  can_configure: boolean;
  ai: AuthoringAi;
  quota: { limit: number; used: number; remaining: number };
  limits: {
    max_upload_mb: number;
    max_files: number;
    max_chars: number;
    timeout_seconds: number;
    max_active_jobs: number;
  };
}

export interface QuizSubmitResult {
  ok: boolean;
  attempt_id: number;
  score: number;
  total: number;
  percent: number;
  passed: boolean;
}

export interface MutationResult {
  ok: boolean;
  message?: string;
  completed?: boolean;
  bookmarked?: boolean;
  stats?: Stats;
  progress?: ProgressMap;
}

// ---------------------------------------------------------------------------
// Analítica (KPIs)
// ---------------------------------------------------------------------------

export interface StudentKpis {
  course: { slug: string; title: string } | null;
  study: {
    week_minutes: number;
    prev_week_minutes: number;
    goal_minutes: number;
    goal_pct: number;
    daily: { day: string; minutes: number }[];
  };
  streak: number;
  completion: { done: number; total: number; pct: number; eta: string | null; pace_per_week: number };
  chapters: { number: number; title: string; completion: number; quiz_score: number | null; mastery: number }[];
  score_trend: { id: number; quiz_id: string; date: string; percent: number }[];
  avg_score: number | null;
  review: { quiz_id: string; question_id: string; prompt: string; answer: string; explanation: string }[];
  review_count: number;
  practice: { code_runs: number; lab_interactions: number; checks: number };
  continue_lesson: string | null;
}

export interface ItemStat {
  number: number;
  question_id: string;
  prompt: string;
  p_value: number;
  discrimination: number | null;
  responses: number;
  top_distractor: string | null;
  top_distractor_rate: number | null;
  flag: "hard" | "easy" | "low_discrimination" | null;
}

export interface StudentRow {
  user_id: number;
  name: string;
  completion: number;
  avg_score: number | null;
  minutes: number;
  last_seen: string | null;
  inactive_days: number | null;
  risk: ("never_started" | "inactive" | "low_score")[];
}

export interface CourseAnalytics {
  course: { slug: string; title: string } | null;
  courses: { slug: string; title: string }[];
  groups: { id: number; name: string }[];
  group: number | null;
  days: number;
  kpis: {
    students: number;
    active_week: number;
    active_days_week: number;
    avg_completion: number;
    avg_score: number | null;
    pass_rate: number | null;
    study_hours: number;
    at_risk: number;
  };
  funnel: { slug: string; title: string; chapter: number; started: number; completed: number }[];
  drop_off: { slug: string; title: string; loss: number } | null;
  heatmap: { chapters: number[]; rows: { user_id: number; name: string; chapters: number[] }[] };
  daily_active: { day: string; active: number }[];
  time_distribution: { label: string; students: number }[];
  quizzes: { quiz_id: string; title: string; chapter: number; attempts: number; items: ItemStat[] }[];
  students: StudentRow[];
  at_risk: StudentRow[];
}

export interface WorkspaceMetrics {
  workspace: WorkspaceRef;
  members: number;
  roles: Record<string, number>;
  seat_limit: number | null;
  plan: string;
  dau: number;
  wau: number;
  daily_active: { day: string; active: number }[];
  courses: Record<string, number>;
  jobs: { by_status: Record<string, number>; success_rate: number | null; avg_minutes: number | null };
}

// ---------------------------------------------------------------------------
// Superadministración de la plataforma
// ---------------------------------------------------------------------------

export interface PlatformOverview {
  users: { total: number; disabled: number; platform_admins: number; wau: number; dau: number };
  workspaces: { personal: number; organization: number };
  courses: { published: number; draft: number; public: number };
  jobs: { month: number; failed_month: number };
}

export interface PlatformUser {
  id: number;
  name: string;
  email: string;
  created_at: string;
  last_login_at: string | null;
  disabled_at: string | null;
  is_platform_admin: boolean;
  workspaces: WorkspaceRef[];
}

export interface PlatformWorkspace {
  id: number;
  kind: "personal" | "organization";
  name: string;
  slug: string;
  owner_email: string | null;
  plan: string;
  seat_limit: number | null;
  settings: { gen_monthly?: number };
  members: number;
  courses: number;
  jobs_month: number;
  created_at: string;
}

export interface PlatformInvitation {
  id: number;
  kind: "individual" | "teacher";
  email: string | null;
  workspace_id: number | null;
  workspace_name: string | null;
  academy_name: string | null;
  accepted_email: string | null;
  state: "pending" | "accepted" | "expired" | "revoked";
  created_at: string;
  expires_at: string;
}
