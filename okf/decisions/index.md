# Decisiones de arquitectura

Registro de decisiones que conviene no reabrir sin contexto.

* [ADR-001 · FastAPI + Jinja](/decisions/adr-001-fastapi-jinja.md) - Backend y primera interfaz.
* [ADR-002 · SQLite](/decisions/adr-002-sqlite.md) - Cero infraestructura para el MVP.
* [ADR-003 · Contenido en Python](/decisions/adr-003-content-python.md) - Contenido versionado y validable.
* [ADR-004 · Labs en JS vanilla](/decisions/adr-004-vanilla-js-labs.md) - Interactividad sin build.
* [ADR-005 · OKF como memoria](/decisions/adr-005-okf-memory.md) - Contexto persistente entre sesiones.
* [ADR-006 · Ejecución Python](/decisions/adr-006-server-python.md) - Runner aislado con límites.
* [ADR-007 · Contenido bilingüe](/decisions/adr-007-bilingual-content.md) - Curso e interfaz ES/EN.
* [ADR-008 · Frontend Next.js](/decisions/adr-008-nextjs-frontend.md) - Interfaz principal sobre la API.
* [ADR-009 · Docker](/decisions/adr-009-docker.md) - Backend y frontend en imágenes separadas con Compose.
* [ADR-010 · Programa multi-capítulo](/decisions/adr-010-multi-chapter.md) - Paquetes autocontenidos, slugs globales y `Program`.
* [ADR-011 · Catálogo multi-curso](/decisions/adr-011-multi-course.md) - `Course`, catálogo público y progreso aislado por curso.
* [ADR-012 · Estudio de autoría con OpenCode](/decisions/adr-012-authoring-opencode.md) - Documentos → JSON validado, OpenCode en Docker y PWA. *Sustituido por ADR-023.*
* [ADR-013 · Retirar la interfaz Jinja](/decisions/adr-013-retire-jinja.md) - Next.js pasa a ser la única interfaz; FastAPI solo expone la API JSON, la ejecución y los estáticos.
* [ADR-014 · Sistema de diseño Tailwind + componentes estilo shadcn](/decisions/adr-014-design-system.md) - Tailwind v4 con componentes propios sobre Radix, Recharts, cmdk y lucide; el CSS heredado vive en una capa legacy.
* [ADR-015 · Migraciones versionadas (PostgreSQL pendiente)](/decisions/adr-015-versioned-migrations.md) - Migraciones numeradas con PRAGMA user_version sobre SQLite; el paso a SQLAlchemy/PostgreSQL queda como siguiente fase.
* [ADR-016 · Espacios de trabajo (tenancy)](/decisions/adr-016-workspaces.md) - Cada usuario tiene un espacio personal y las academias son espacios de organización con roles owner/admin/teacher/student.
* [ADR-017 · Generación por etapas con salida JSON](/decisions/adr-017-staged-generation.md) - Ingesta estructurada, temario editable, lecciones en paralelo con citas, banco de preguntas y verificación. *Matizado por ADR-023.*
* [ADR-018 · Eventos de aprendizaje como fuente de los KPIs](/decisions/adr-018-learning-events.md) - Tabla learning_events al estilo xAPI; los KPIs de alumno, profesor y admin se calculan a partir de ella.
* [ADR-019 · Cola de generación persistente y reanudable](/decisions/adr-019-generation-queue.md) - Estado en authoring_jobs y artefactos en disco; pool en proceso con reanudación al arrancar y worker opcional aparte.
* [ADR-020 · Plataforma genérica y curso LLM como ejemplo opcional](/decisions/adr-020-generic-platform.md) - La app funciona con la biblioteca vacía; el curso LLM solo aparece con AULA_SAMPLE_COURSES=1; curso activo, glosario y recursos por curso.
* [ADR-021 · Perfiles de cuenta - individual, academia y superadmin](/decisions/adr-021-account-profiles.md) - Alta individual o academia, matriz learn/author/teach/manage/platform, alumnado sin Estudio y panel /plataforma.
* [ADR-022 · Registro solo por invitación](/decisions/adr-022-invite-only-signup.md) - Sin registro abierto; la superadministración invita a cuentas individuales y profesorado y el profesorado invita a su alumnado.
* [ADR-023 · Agentes propios con nas-adk](/decisions/adr-023-nas-adk-agents.md) - Un único motor por etapas con agentes nas-adk y herramientas propias; se retiran OpenCode y el cliente HTTP propio.
* [ADR-024 · Credenciales de IA por usuario](/decisions/adr-024-user-ai-credentials.md) - API key o suscripción de Claude propias, resueltas siempre con quien lanza la acción y nunca compartidas.
