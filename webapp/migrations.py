"""Migraciones versionadas del esquema SQLite.

``db.SCHEMA`` es la línea base (v3). Cada migración posterior es una función
idempotente que recibe la conexión y se aplica una sola vez, en orden, según
``PRAGMA user_version``. Para añadir un cambio de esquema:

1. Escribe ``def _mNNNN_descripcion(conn)`` con SQL idempotente.
2. Añádela al final de ``MIGRATIONS`` con el siguiente número.
3. Añade un test en ``webapp/tests/test_migrations.py``.

Las migraciones no se reescriben una vez publicadas: si algo cambia, se añade
una nueva.
"""

from __future__ import annotations

import re
import secrets
import sqlite3
from collections.abc import Callable

BASELINE_VERSION = 3


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if column not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def slugify_name(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:48] or "espacio"


def new_join_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(8))


# ---------------------------------------------------------------------------
# v4 · Espacios de trabajo, grupos, invitaciones, auditoría y eventos
# ---------------------------------------------------------------------------

_V4_SCHEMA = """
CREATE TABLE IF NOT EXISTS workspaces (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    kind          TEXT NOT NULL CHECK (kind IN ('personal', 'organization')),
    name          TEXT NOT NULL,
    slug          TEXT NOT NULL UNIQUE,
    owner_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    plan          TEXT NOT NULL DEFAULT 'free',
    seat_limit    INTEGER,
    join_code     TEXT UNIQUE,
    settings_json TEXT NOT NULL DEFAULT '{}',
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memberships (
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role         TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'teacher', 'student')),
    created_at   TEXT NOT NULL,
    PRIMARY KEY (workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_memberships_user ON memberships(user_id);

CREATE TABLE IF NOT EXISTS groups (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_groups_workspace ON groups(workspace_id);

CREATE TABLE IF NOT EXISTS group_members (
    group_id   INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    PRIMARY KEY (group_id, user_id)
);

CREATE TABLE IF NOT EXISTS enrollments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    course_slug  TEXT NOT NULL,
    group_id     INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    user_id      INTEGER REFERENCES users(id) ON DELETE CASCADE,
    due_at       TEXT,
    created_by   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at   TEXT NOT NULL,
    CHECK (group_id IS NOT NULL OR user_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_ws ON enrollments(workspace_id, course_slug);

CREATE TABLE IF NOT EXISTS invitations (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email        TEXT,
    role         TEXT NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
    group_id     INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    token_hash   TEXT NOT NULL UNIQUE,
    created_by   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at   TEXT NOT NULL,
    expires_at   TEXT NOT NULL,
    accepted_at  TEXT,
    accepted_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    revoked_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_invitations_ws ON invitations(workspace_id, created_at DESC);

CREATE TABLE IF NOT EXISTS audit_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT NOT NULL,
    actor_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    action       TEXT NOT NULL,
    target       TEXT NOT NULL DEFAULT '',
    ip           TEXT NOT NULL DEFAULT '',
    meta_json    TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_audit_ws ON audit_log(workspace_id, ts DESC);

CREATE TABLE IF NOT EXISTS learning_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT NOT NULL,
    day          TEXT NOT NULL,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_slug  TEXT NOT NULL DEFAULT '',
    lesson_slug  TEXT NOT NULL DEFAULT '',
    verb         TEXT NOT NULL,
    object_id    TEXT NOT NULL DEFAULT '',
    score        REAL,
    success      INTEGER,
    duration_ms  INTEGER NOT NULL DEFAULT 0,
    meta_json    TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_events_user_day ON learning_events(user_id, day);
CREATE INDEX IF NOT EXISTS idx_events_course ON learning_events(course_slug, verb, day);
"""


def _m0004_workspaces_and_events(conn: sqlite3.Connection) -> None:
    conn.executescript(_V4_SCHEMA)
    _add_column(conn, "users", "is_platform_admin", "INTEGER NOT NULL DEFAULT 0")
    _add_column(conn, "users", "last_login_at", "TEXT")
    _add_column(conn, "users", "disabled_at", "TEXT")
    _add_column(conn, "users", "locale", "TEXT")
    _add_column(conn, "authoring_jobs", "workspace_id", "INTEGER")
    _add_column(conn, "generated_courses", "workspace_id", "INTEGER")
    _add_column(
        conn, "generated_courses", "visibility", "TEXT NOT NULL DEFAULT 'workspace'"
    )


# ---------------------------------------------------------------------------
# v5 · Generación por etapas: estados nuevos, motor, progreso y consumo
# ---------------------------------------------------------------------------

JOB_STATUSES = (
    "queued",
    "extracting",
    "awaiting_scope",
    "outlining",
    "awaiting_outline",
    "generating",
    "validating",
    "ready",
    "failed",
    "cancelled",
)


def _m0005_staged_generation(conn: sqlite3.Connection) -> None:
    """Reconstruye ``authoring_jobs`` sin el CHECK cerrado de estados.

    SQLite no permite cambiar un CHECK, así que se copia a una tabla nueva. El
    estado se valida en código (``migrations.JOB_STATUSES``).
    """
    columns = _columns(conn, "authoring_jobs")
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.executescript(
        """
        CREATE TABLE authoring_jobs_v5 (
            id           TEXT PRIMARY KEY,
            owner_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            workspace_id INTEGER,
            title        TEXT NOT NULL,
            source_names TEXT NOT NULL,
            status       TEXT NOT NULL DEFAULT 'queued',
            engine       TEXT NOT NULL DEFAULT 'opencode',
            stage        TEXT NOT NULL DEFAULT '',
            progress_json TEXT NOT NULL DEFAULT '{}',
            config_json  TEXT NOT NULL DEFAULT '{}',
            tokens_in    INTEGER NOT NULL DEFAULT 0,
            tokens_out   INTEGER NOT NULL DEFAULT 0,
            provider     TEXT NOT NULL,
            model        TEXT NOT NULL,
            languages    TEXT NOT NULL,
            course_slug  TEXT,
            error        TEXT,
            created_at   TEXT NOT NULL,
            started_at   TEXT,
            finished_at  TEXT
        );
        """
    )
    shared = [
        name
        for name in (
            "id", "owner_id", "workspace_id", "title", "source_names", "status",
            "provider", "model", "languages", "course_slug", "error",
            "created_at", "started_at", "finished_at",
        )
        if name in columns
    ]
    names = ", ".join(shared)
    conn.execute(f"INSERT INTO authoring_jobs_v5 ({names}) SELECT {names} FROM authoring_jobs")
    conn.executescript(
        """
        DROP TABLE authoring_jobs;
        ALTER TABLE authoring_jobs_v5 RENAME TO authoring_jobs;
        CREATE INDEX IF NOT EXISTS idx_authoring_jobs_owner
            ON authoring_jobs(owner_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_authoring_jobs_ws
            ON authoring_jobs(workspace_id, created_at DESC);
        """
    )
    _add_column(conn, "generated_courses", "report_json", "TEXT NOT NULL DEFAULT '{}'")
    conn.execute("PRAGMA foreign_keys = ON")


# ---------------------------------------------------------------------------
# v6 · Perfiles de cuenta (ADR-021) y curso activo
# ---------------------------------------------------------------------------

# Cuentas demo de la etapa «Aula LLM». Se renombran a las de SLAnything para
# que una base local antigua no conserve una profesora superadministradora.
_LEGACY_DEMO_ACCOUNTS = (
    ("demo@aulallm.local", "alumno@slanything.local", "alumno1234"),
    ("profe@aulallm.local", "profe@slanything.local", "profe1234"),
)


def _m0006_account_profiles(conn: sqlite3.Connection) -> None:
    """Separa la cuenta individual del alumnado de academia.

    - ``users.last_course_slug`` guarda el último curso abierto.
    - Los alumnos que solo pertenecen a academias pierden su espacio personal
      si está vacío (sin trabajos ni cursos generados): el alumno solo consume.
    - Los usuarios sin ningún espacio (bases v3) reciben su cuenta individual,
      como hacía hasta ahora el arranque.
    - Las cuentas demo antiguas se renombran y dejan de ser superadmin.
    """
    from webapp.security import hash_password

    _add_column(conn, "users", "last_course_slug", "TEXT")

    conn.execute(
        """DELETE FROM workspaces
           WHERE kind = 'personal'
             AND owner_id IN (
                 SELECT m.user_id FROM memberships m
                 JOIN workspaces w ON w.id = m.workspace_id
                 WHERE w.kind = 'organization'
                 GROUP BY m.user_id
                 HAVING SUM(CASE WHEN m.role != 'student' THEN 1 ELSE 0 END) = 0
             )
             AND NOT EXISTS (SELECT 1 FROM generated_courses g WHERE g.workspace_id = workspaces.id)
             AND NOT EXISTS (SELECT 1 FROM authoring_jobs j WHERE j.workspace_id = workspaces.id)"""
    )

    orphans = conn.execute(
        """SELECT u.id FROM users u
           WHERE NOT EXISTS (SELECT 1 FROM memberships m WHERE m.user_id = u.id)"""
    ).fetchall()
    for (user_id,) in orphans:
        slug = f"personal-{user_id}"
        candidate, n = slug, 2
        while conn.execute("SELECT 1 FROM workspaces WHERE slug = ?", (candidate,)).fetchone():
            candidate = f"{slug}-{n}"
            n += 1
        cursor = conn.execute(
            """INSERT INTO workspaces (kind, name, slug, owner_id, created_at)
               VALUES ('personal', 'Mi espacio', ?, ?, datetime('now'))""",
            (candidate, user_id),
        )
        conn.execute(
            """INSERT INTO memberships (workspace_id, user_id, role, created_at)
               VALUES (?, ?, 'owner', datetime('now'))""",
            (cursor.lastrowid, user_id),
        )

    for old, new, password in _LEGACY_DEMO_ACCOUNTS:
        taken = conn.execute("SELECT 1 FROM users WHERE email = ?", (new,)).fetchone()
        if taken:
            continue
        conn.execute(
            """UPDATE users SET email = ?, password_hash = ?, is_platform_admin = 0
               WHERE email = ?""",
            (new, hash_password(password), old),
        )


# ---------------------------------------------------------------------------
# v7 · Invitaciones de plataforma (ADR-022)
# ---------------------------------------------------------------------------

def _m0007_platform_invitations(conn: sqlite3.Connection) -> None:
    """Invitaciones que emite la superadministración.

    ``individual`` abre una cuenta individual; ``teacher`` incorpora a un
    profesor a una academia existente (``workspace_id``) o le crea una academia
    nueva de la que será propietario (``academy_name`` opcional, se puede
    escribir al aceptar).
    """
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS platform_invitations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            kind         TEXT NOT NULL CHECK (kind IN ('individual', 'teacher')),
            email        TEXT,
            workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
            academy_name TEXT,
            token_hash   TEXT NOT NULL UNIQUE,
            created_by   INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at   TEXT NOT NULL,
            expires_at   TEXT NOT NULL,
            accepted_at  TEXT,
            accepted_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
            revoked_at   TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_platform_invitations_created
            ON platform_invitations(created_at DESC);
        """
    )


def _m0008_adk_engine(conn: sqlite3.Connection) -> None:
    """Motor único nas-adk (ADR-023) y credenciales de IA por usuario (ADR-024).

    - ``user_ai_settings``: proveedor, modelo y secreto cifrado de cada persona.
    - ``authoring_jobs.actor_id``: quién lanzó la última acción del trabajo; sus
      credenciales son las que se usan al reanudar.
    - Los trabajos del motor por etapas pasan a ``adk``; los de OpenCode que
      quedaron a medias se cierran (su motor ya no existe).
    """
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS user_ai_settings (
            user_id              INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            provider             TEXT NOT NULL,
            model                TEXT NOT NULL DEFAULT '',
            secret_enc           TEXT,
            secret_hint          TEXT,
            accepted_personal_at TEXT,
            updated_at           TEXT NOT NULL
        );
        """
    )
    _add_column(conn, "authoring_jobs", "actor_id", "INTEGER")
    conn.execute("UPDATE authoring_jobs SET actor_id = owner_id WHERE actor_id IS NULL")
    conn.execute("UPDATE authoring_jobs SET engine = 'adk' WHERE engine = 'direct'")
    conn.execute(
        """UPDATE authoring_jobs
           SET status = 'failed',
               error = 'El motor OpenCode se ha retirado; vuelve a generar la unidad.',
               finished_at = COALESCE(finished_at, created_at)
           WHERE engine = 'opencode'
             AND status IN ('queued', 'extracting', 'outlining', 'generating', 'validating')"""
    )


MIGRATIONS: list[tuple[int, Callable[[sqlite3.Connection], None]]] = [
    (4, _m0004_workspaces_and_events),
    (5, _m0005_staged_generation),
    (6, _m0006_account_profiles),
    (7, _m0007_platform_invitations),
    (8, _m0008_adk_engine),
]

LATEST_VERSION = MIGRATIONS[-1][0]


def current_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


def migrate(conn: sqlite3.Connection) -> list[int]:
    """Aplica en orden las migraciones pendientes. Devuelve las aplicadas."""
    version = current_version(conn)
    if version < BASELINE_VERSION:
        conn.execute(f"PRAGMA user_version = {BASELINE_VERSION}")
        version = BASELINE_VERSION
    applied: list[int] = []
    for number, func in MIGRATIONS:
        if number <= version:
            continue
        func(conn)
        conn.execute(f"PRAGMA user_version = {number}")
        conn.commit()
        applied.append(number)
    return applied
