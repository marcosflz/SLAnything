export type Lang = "es" | "en";

export interface User {
  id: number;
  email: string;
  name: string;
  role: "student" | "teacher";
  initials: string;
  csrf_token: string;
}

export interface Site {
  name: string;
  tagline: string;
  course_title: string;
  course_chapter: string;
  catalog_count: number;
  year: number;
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
  total_minutes: number;
  lesson_count: number;
  chapter_count: number;
  lab_count: number;
  stats: Stats;
  next_lesson: LessonSummary | null;
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
  course: Course;
  catalog: CourseSummary[];
  site: Site;
  lab_meta: LabMap;
  lang: Lang;
}

export interface CatalogPayload {
  courses: CourseSummary[];
  featured: Course;
  site: Site;
  lang: Lang;
}

export interface ShellPayload {
  user: User;
  course: Course;
  courses: CourseSummary[];
  default_course_slug: string;
  progress: ProgressMap;
  stats: Stats;
  next_lesson: LessonSummary | null;
  lab_meta: LabMap;
  site: Site;
  lang: Lang;
}

export interface DashboardPayload {
  course: Course;
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
  course: Course;
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
  course: Course;
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
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface SearchPayload {
  query: string;
  results: Array<{ lesson: LessonSummary; snippet: string }>;
  course: Course;
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
  course: Course;
  courses: CourseSummary[];
  progress: ProgressMap;
}

export interface AuthoringProvider {
  id: string;
  label: string;
  requires_key: boolean;
  default_base_url: string | null;
  models: string[];
  notes: string;
}

export interface AuthoringEngine {
  enabled: boolean;
  available: boolean;
  version: string | null;
  binary: string;
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

export interface AuthoringJob {
  id: string;
  title: string;
  source_names: string[];
  status:
    | "queued"
    | "extracting"
    | "generating"
    | "validating"
    | "ready"
    | "failed"
    | "cancelled";
  status_label: string;
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

export interface AuthoringCourse {
  slug: string;
  title: string;
  status: "draft" | "published";
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

export interface AuthoringPayload {
  settings: AuthoringSettings;
  jobs: AuthoringJob[];
  courses: AuthoringCourse[];
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
