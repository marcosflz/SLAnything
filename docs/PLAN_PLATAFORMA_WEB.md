# Plan de acción · SLAnything

> Convertir los cuadernos de *Build a Large Language Model (From Scratch)* en una
> plataforma web de aprendizaje tipo Moodle, empezando por el capítulo 1.
>
> Versión 1.0 · Octubre 2026

> **Actualización (24 oct 2026):** este documento describe el MVP inicial con
> FastAPI + Jinja2. La evolución posterior añadió Next.js 16 + React 19, API JSON
> `/api/v1`, contenido ES/EN, ejecución de Python en servidor, los **7 capítulos
> completos** (56 lecciones, 15 labs, 7 quizzes) y el **catálogo multi-curso**. El estado vigente está en
> `README.md`, `AGENTS.md` y `okf/project/status.md`; este plan se conserva como
> registro histórico de las fases F0-F7 y del alcance del capítulo 1.

## Estado de ejecución · 24 de octubre de 2026

| Fase | Estado | Evidencia |
|---|---|---|
| F0 · Plan | Completada | Este documento y `docs/CONTRATO_AGENTES.md` |
| F1 · Cimientos | Completada | FastAPI, SQLite, auth, CSRF, diseño base |
| F2 · Contenido | Completada | 8 lecciones, 10 preguntas, 39 términos |
| F3 · Laboratorios | Completada | 7 módulos JS probados en Chrome |
| F4 · Vistas | Completada | 14 plantillas, responsive y modo oscuro |
| F5 · Integración | Completada | Flujo estudiante y panel del profesor |
| F6 · QA | Completada | 77 tests en verde + revisión visual |
| F7 · Entrega | Completada | `uv run python aula.py`, README, capturas y OKF |

**Resultado:** el capítulo 1 está disponible en `http://127.0.0.1:8000` con las 8 lecciones,
los 7 laboratorios, el quiz, el progreso persistente y el panel del profesor.

---

## 1. Resumen ejecutivo

El cuaderno del capítulo 1 ya funciona, pero vive en Jupyter: exige instalar Python,
saber ejecutar celdas y entender widgets. El objetivo es **trasladar la experiencia a una
web autocontenida**, con la estructura de un aula virtual:

- curso con módulos y lecciones;
- cuenta de estudiante y progreso persistente;
- lecciones con texto, figuras, código y laboratorios interactivos;
- quizzes corregidos en servidor y con retroalimentación;
- apuntes, marcadores, glosario, buscador y panel de progreso;
- un panel de profesor con estadísticas básicas.

La web se construye con **FastAPI + Jinja2 + SQLite + JavaScript sin framework**. Es una
decisión deliberada: el proyecto ya usa Python y `uv`, no añade una cadena Node, arranca
con un comando y se puede desplegar en cualquier servidor pequeño. La interactividad
—modelo de n-gramas, calculadoras, atención, prompts— se reimplementa en JavaScript
moderno, sin depender de Jupyter ni de un kernel Python en el navegador.

**Resultado esperado:** `uv run python aula.py` abre una plataforma en `http://127.0.0.1:8000`
con el capítulo 1 completo, navegable, evaluable y visualmente cuidada.

---

## 2. Objetivos

### 2.1 Objetivo general

Ofrecer una experiencia de aprendizaje guiada, interactiva y medible para el capítulo 1,
equivalente funcional a un curso Moodle, pero con la calidad editorial de los cuadernos.

### 2.2 Objetivos específicos

1. **Aula navegable:** portada, curso, 8 lecciones, quiz final, glosario y recursos.
2. **Progreso real:** cada usuario ve qué ha completado, su nota media y su racha.
3. **Interactividad nativa:** 7 laboratorios en JavaScript, sin instalar nada.
4. **Contenido didáctico:** mismo nivel que el cuaderno, adaptado a lectura web.
5. **Evaluación:** quiz de 10 preguntas, corrección en servidor, intentos y revisión.
6. **Extensibilidad:** añadir capítulos 2-7 sin tocar el motor de la aplicación.
7. **Reproducibilidad:** un solo comando para arrancar; tests automáticos.

### 2.3 No objetivos (v1)

- No es un LMS multi-curso ni multi-institución.
- No hay vídeo, foros, mensajería ni matrículas con pago.
- No se ejecuta Python real en el navegador (Pyodide/JupyterLite queda para v2). La
  v1 añade ejemplos Python ejecutables en un subproceso aislado del servidor y
  descargables para local.
- No hay integración con Google/Microsoft ni LTI.
- No se persiguen notas oficiales ni certificados verificables.

---

## 3. Usuarios y casos de uso

| Perfil | Necesidad | Recorrido principal |
|---|---|---|
| **Estudiante** | Aprender sin configurar un entorno | Registro → portada del curso → lecciones → laboratorios → quiz |
| **Autodidacta curioso** | Probar antes de registrarse | Landing pública → vista previa del programa → registro |
| **Profesor** | Ver avance y detectar bloqueos | Panel de profesor → progreso por estudiante → resultados de quiz |
| **Autor de contenido** | Añadir capítulos | Editar módulos de contenido → tests → recarga en caliente |

### 3.1 Historias de usuario prioritarias

- Como estudiante, quiero **continuar donde lo dejé** en un clic.
- Como estudiante, quiero **marcar una lección como completada** y ver mi avance.
- Como estudiante, quiero **experimentar con la temperatura** de un modelo de lenguaje.
- Como estudiante, quiero **hacer el quiz y entender mis fallos**.
- Como estudiante, quiero **guardar apuntes** asociados a cada lección.
- Como profesor, quiero **ver quién avanza y quién se queda atascado**.
- Como autor, quiero **añadir una lección escribiendo un módulo Python**.

---

## 4. Alcance del MVP (capítulo 1)

### 4.1 Mapa de lecciones

| # | Slug | Título | Min | Labs | Quiz |
|---|---|---|---|---|---|
| 1 | `que-es-un-llm` | ¿Qué es un LLM? | 10 | `memory` | — |
| 2 | `pretraining-y-finetuning` | Las dos etapas | 10 | `labels` | — |
| 3 | `transformer-y-atencion` | Transformer y atención | 12 | `transformer`, `attention` | — |
| 4 | `escala-de-datos` | La escala de los datos | 8 | — | — |
| 5 | `predecir-la-siguiente-palabra` | Predecir la siguiente palabra | 15 | `ngram` | — |
| 6 | `zero-shot-y-few-shot` | Zero-shot y few-shot | 10 | `prompt` | — |
| 7 | `como-se-construye` | Cómo se construye un LLM | 8 | `cost` | — |
| 8 | `repaso` | Repaso y autoevaluación | 10 | — | `quiz-capitulo-1` |

Duración total estimada: **83 minutos**.

### 4.2 Funcionalidades incluidas

- [x] Landing pública con propuesta de valor y programa.
- [x] Registro, inicio y cierre de sesión con contraseña hasheada.
- [x] Cuenta demo y cuenta de profesor precargadas.
- [x] Dashboard con progreso, siguiente lección, racha y nota media.
- [x] Curso con módulos, estados y tiempo estimado.
- [x] Lección con objetivos, contenido, figuras, callouts, código y labs.
- [x] Navegación anterior/siguiente y marca de completada.
- [x] Notas privadas por lección y marcadores.
- [x] Quiz de 10 preguntas, 80 % para aprobar, intentos ilimitados.
- [x] Revisión detallada de cada intento.
- [x] Glosario con búsqueda.
- [x] Buscador de lecciones.
- [x] Recursos descargables (cuaderno, corpus, figuras).
- [x] Panel de profesor con métricas agregadas.
- [x] Tema claro/oscuro y diseño responsive.
- [x] Tests de humo, auth, progreso, quiz y contenido.

### 4.3 Fuera del MVP

- Foros, comentarios, mensajería.
- Editor visual de contenido.
- Subida de archivos por el usuario.
- Notificaciones por correo.
- Analítica avanzada.
- Ejecución de Python en el navegador.

---

## 5. Arquitectura

### 5.1 Vista general

```text
┌──────────────────────────────────────────────────────────────────┐
│  Navegador                                                       │
│  HTML + CSS + JS (labs, quiz, tema, navegación)                  │
└───────────────┬──────────────────────────────────────────────────┘
                │ HTTP (formularios + fetch)
┌───────────────▼──────────────────────────────────────────────────┐
│  FastAPI                                                         │
│  ├─ Routers: auth, curso, lecciones, quiz, progreso, profesor    │
│  ├─ Plantillas Jinja2                                            │
│  ├─ Contenido Python (lecciones, quiz, glosario)                 │
│  └─ Estáticos: CSS, JS, imágenes, corpus                         │
└───────────────┬──────────────────────────────────────────────────┘
                │ sqlite3 (stdlib)
┌───────────────▼──────────────────────────────────────────────────┐
│  SQLite  aula.db                                                 │
│  usuarios · sesiones · progreso · intentos · notas · actividad   │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Decisiones técnicas

| Decisión | Alternativa descartada | Motivo |
|---|---|---|
| FastAPI + Jinja2 | Next.js / React | Un solo runtime (Python), arranque simple, SEO y formularios sin complejidad |
| SQLite | PostgreSQL | Cero infraestructura; migrable después |
| JS vanilla con módulos ES | React/Vue | Labs pequeños y aislados; evita build y dependencias |
| Contenido en Python | CMS / base de datos | Versionado en git, tipado, tests y edición sencilla |
| Sesiones en BD + cookie | JWT en localStorage | Revocación, CSRF explícito y menos superficie de ataque |
| CSS propio con variables | Tailwind | Sin build; control total del diseño y del modo oscuro |
| `scrypt` de stdlib | bcrypt/argon2 | Sin dependencia extra; parámetros ajustables |

### 5.3 Estructura de carpetas

```text
webapp/
  __init__.py
  main.py                  # app factory, lifespan, montaje de estáticos
  config.py                # rutas, secreto, entorno
  db.py                    # conexión, esquema y migraciones idempotentes
  security.py              # hash de contraseñas, tokens, CSRF
  deps.py                  # usuario actual, require_user
  repositories.py          # consultas SQL reutilizables
  routers/
    auth.py                # /entrar, /registro, /salir
    course.py              # portada, curso, lección, completar, notas
    quiz.py                # quiz, envío, resultado
    progress.py            # panel de progreso
    glossary.py            # glosario
    resources.py           # recursos
    search.py              # buscador
    teacher.py             # panel del profesor
  content/
    schema.py              # dataclasses y helpers de bloques
    course.py              # ensambla el curso
    lessons/               # una lección por archivo
    quizzes.py             # preguntas y metadatos
    glossary.py            # términos
  templates/
    base.html
    components/            # macros: callout, figure, code, lab, progress…
    pages/                 # una plantilla por vista
  static/
    css/app.css
    js/app.js
    js/quiz.js
    js/labs/               # un módulo por laboratorio
    img/ch01/              # figuras
    data/                  # corpus de El Quijote
  tests/
    conftest.py
    test_auth.py
    test_content.py
    test_course.py
    test_quiz.py
    test_progress.py
```

### 5.4 Modelo de datos

```sql
users (
  id INTEGER PK,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'student',  -- student | teacher
  created_at TEXT NOT NULL
)

sessions (
  id TEXT PK,              -- hash del token de cookie
  user_id INTEGER NOT NULL REFERENCES users(id),
  csrf_token TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL
)

lesson_progress (
  user_id INTEGER NOT NULL,
  lesson_slug TEXT NOT NULL,
  completed INTEGER NOT NULL DEFAULT 0,
  first_seen_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  completed_at TEXT,
  views INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, lesson_slug)
)

quiz_attempts (
  id INTEGER PK,
  user_id INTEGER NOT NULL,
  quiz_id TEXT NOT NULL,
  score INTEGER NOT NULL,
  total INTEGER NOT NULL,
  answers_json TEXT NOT NULL,
  created_at TEXT NOT NULL
)

notes (
  user_id INTEGER NOT NULL,
  lesson_slug TEXT NOT NULL,
  body TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (user_id, lesson_slug)
)

bookmarks (
  user_id INTEGER NOT NULL,
  lesson_slug TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (user_id, lesson_slug)
)

activity (
  user_id INTEGER NOT NULL,
  day TEXT NOT NULL,       -- YYYY-MM-DD
  kind TEXT NOT NULL,      -- login | lesson | quiz
  count INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (user_id, day, kind)
)
```

### 5.5 Modelo de contenido

Una lección es un objeto inmutable:

```python
Lesson(
    number=1,
    slug="que-es-un-llm",
    title="¿Qué es un LLM?",
    summary="...",
    minutes=10,
    objectives=["...", "..."],
    blocks=[p("..."), figure(...), callout(...), lab("memory")],
    key_points=["...", "..."],
    quiz_id=None,
)
```

Bloques disponibles:

| Helper | Render |
|---|---|
| `p(html)` | Párrafo con HTML seguro de autor |
| `h2(text)` / `h3(text)` | Encabezados con ancla |
| `callout(tone, title, html)` | Aviso info/tip/warning/danger/success |
| `figure(src, alt, caption, credit)` | Figura con pie y lightbox |
| `code(lang, code, caption)` | Bloque de código con botón copiar |
| `table(headers, rows, caption)` | Tabla responsive |
| `quote(text, source)` | Cita destacada |
| `lab(lab_id)` | Monta un laboratorio interactivo |
| `keypoints(items)` | Caja de ideas clave |
| `check(question, answer)` | Autochequeo desplegable |

El contenido se valida al arrancar: slugs únicos, labs existentes, quizzes existentes,
imágenes presentes y números consecutivos.

### 5.6 Rutas

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/` | pública | Landing o dashboard si hay sesión |
| GET/POST | `/entrar` | pública | Inicio de sesión |
| GET/POST | `/registro` | pública | Alta de estudiante |
| POST | `/salir` | usuario | Cierre de sesión |
| GET | `/curso` | usuario | Programa y progreso |
| GET | `/leccion/{slug}` | usuario | Lección |
| POST | `/leccion/{slug}/completar` | usuario | Alternar completada |
| POST | `/leccion/{slug}/nota` | usuario | Guardar apuntes |
| POST | `/leccion/{slug}/marcador` | usuario | Alternar marcador |
| GET | `/quiz/{quiz_id}` | usuario | Cuestionario |
| POST | `/quiz/{quiz_id}` | usuario | Enviar y corregir |
| GET | `/quiz/intento/{id}` | usuario | Revisión del intento |
| GET | `/progreso` | usuario | Panel personal |
| GET | `/glosario` | usuario | Glosario buscable |
| GET | `/recursos` | usuario | Descargas y créditos |
| GET | `/buscar?q=` | usuario | Búsqueda en lecciones |
| GET | `/profesor` | teacher | Métricas del curso |
| GET | `/salud` | pública | Health check |

### 5.7 Seguridad

- Contraseñas con `scrypt` (N=2¹⁴, r=8, p=1) y sal aleatoria de 16 bytes.
- Cookie de sesión `HttpOnly`, `SameSite=Lax`, `Secure` en producción.
- Token de sesión de 32 bytes; en BD solo se guarda su SHA-256.
- Caducidad de sesión: 14 días; renovación al usar.
- CSRF: token por sesión en campo oculto y cabecera `X-CSRF-Token` para `fetch`.
- Validación de entrada y límites de longitud (notas ≤ 20 000 caracteres).
- Rate limit simple en login (5 intentos fallidos por email/IP cada 15 min) en memoria.
- Sin HTML de usuario: los apuntes se escapan siempre en plantilla.
- Cabeceras: `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`.
- El contenido de autor es de confianza (se renderiza con `|safe`), no la entrada de usuario.

### 5.8 Accesibilidad y rendimiento

- HTML semántico, landmarks, `skip-link`, foco visible.
- Contraste AA en ambos temas; navegación completa por teclado.
- `prefers-reduced-motion` respetado.
- Imágenes con `alt`, `loading="lazy"` y dimensiones para evitar saltos.
- CSS y JS propios; sin fuentes externas; objetivo < 250 KB de JS.
- Labs cargados bajo demanda con `IntersectionObserver`.
- Corpus de 400 KB cacheado; modelo de n-gramas construido una vez.

---

## 6. Diseño de producto

### 6.1 Identidad

- **Nombre:** SLAnything.
- **Lema:** “Construye un LLM desde cero, una idea a la vez.”
- **Tono:** cercano, riguroso, sin hype. Español de España.
- **Paleta:** azul tinta (`#0f172a`), azul académico (`#2563eb`), ámbar (`#f59e0b`),
  verde (`#059669`), rojo (`#dc2626`) y neutros cálidos.
- **Tipografía:** pila del sistema (`Inter`, `Segoe UI`, `system-ui`) + monoespaciada
  para código.
- **Modo oscuro:** variables CSS con `data-theme="dark"`, preferencia persistida.

### 6.2 Pantallas

1. **Landing:** hero con promesa, programa resumido, cifras del curso, CTA y créditos.
2. **Dashboard:** saludo, anillo de progreso, “continuar”, racha, nota media, próximos hitos.
3. **Curso:** lista de módulos con estado, duración, labs y botón de entrada.
4. **Lección:** barra de progreso de lectura, objetivos, contenido, labs, ideas clave,
   navegación y panel lateral con notas/marcador.
5. **Quiz:** una pregunta por tarjeta, barra de respuesta, envío único, resultado.
6. **Revisión:** nota, mensaje, desglose pregunta a pregunta y explicación.
7. **Progreso:** historial, lecciones completadas, intentos y racha.
8. **Glosario:** buscador instantáneo y términos agrupados por letra.
9. **Profesor:** tabla de estudiantes, progreso, último acceso y mejores notas.
10. **Recursos:** descargas, figuras, créditos y licencias.

### 6.3 Componentes reutilizables

- `progress-ring` (SVG), `progress-bar`, `badge`, `stat-card`, `lesson-row`,
  `callout`, `figure`, `code-block`, `lab-shell`, `quiz-card`, `empty-state`,
  `toast`, `modal` (lightbox), `tabs`, `sidebar`, `topbar`.

### 6.4 Laboratorios interactivos

| ID | Qué hace | Técnica |
|---|---|---|
| `memory` | Memoria por parámetro y precisión, comparación de modelos | Cálculo + barras |
| `labels` | Fabrica pares entrada→objetivo señalando tokens | Interacción DOM |
| `transformer` | Recorre encoder/decoder y sus pasos | Stepper visual |
| `attention` | Heatmap y pesos de atención por palabra | Matriz + SVG/CSS |
| `ngram` | Entrena n-gramas con El Quijote y genera texto | JS + corpus |
| `prompt` | Construye prompts zero/few-shot y los copia | Plantillas |
| `cost` | Estima coste y tiempo de entrenamiento | Fórmulas + barras |

Todos comparten el contrato:

```js
export default {
  id: "ngram",
  mount(root) { /* renderiza y devuelve cleanup opcional */ }
}
```

`app.js` detecta `[data-lab]`, carga el módulo con `import()` y lo monta una sola vez.

---

## 7. Plan de implementación

### 7.1 Fases

| Fase | Entregable | Depende de | Criterio de salida |
|---|---|---|---|
| **F0. Plan** | Este documento | — | Revisado y versionado |
| **F1. Cimientos** | pyproject, config, BD, auth, esquema de contenido, base visual | F0 | `pytest` de auth en verde; app arranca |
| **F2. Contenido** | 8 lecciones, quiz, glosario | F1 | Validación de contenido sin errores |
| **F3. Labs** | 7 módulos JS | F1 | Cada lab se monta y responde a interacción |
| **F4. Vistas** | Plantillas y CSS de todas las pantallas | F1-F3 | Navegación completa sin errores 500 |
| **F5. Integración** | Rutas, formularios, progreso, quiz, profesor | F2-F4 | Flujo completo de estudiante y profesor |
| **F6. QA** | Tests, revisión visual, accesibilidad, textos | F5 | Suite en verde y checklist visual |
| **F7. Entrega** | README, script de arranque, datos demo | F6 | `uv run python aula.py` funciona en limpio |

### 7.2 Desglose de tareas

#### F1 · Cimientos

- [x] T1.1 Añadir dependencias (`fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `pytest`, `httpx`).
- [x] T1.2 Crear `webapp/config.py` con rutas y secreto persistente.
- [x] T1.3 Crear `webapp/db.py` con esquema idempotente y conexión por petición.
- [x] T1.4 Implementar `security.py` (scrypt, tokens, CSRF, rate limit).
- [x] T1.5 Implementar `deps.py` (usuario actual, `require_user`, `require_teacher`).
- [x] T1.6 Implementar `repositories.py` (usuarios, sesiones, progreso, quiz, notas).
- [x] T1.7 Definir `content/schema.py` y helpers de bloques.
- [x] T1.8 Crear `main.py`, montaje de estáticos, handlers 401/404/500.
- [x] T1.9 Sembrar demo/profesor y datos de ejemplo.
- [x] T1.10 Crear `base.html`, sistema de diseño CSS y JS global.

#### F2 · Contenido

- [x] T2.1 Lección 1 · ¿Qué es un LLM?
- [x] T2.2 Lección 2 · Pretraining y finetuning.
- [x] T2.3 Lección 3 · Transformer y atención.
- [x] T2.4 Lección 4 · Escala de datos.
- [x] T2.5 Lección 5 · Predecir la siguiente palabra.
- [x] T2.6 Lección 6 · Zero-shot y few-shot.
- [x] T2.7 Lección 7 · Cómo se construye.
- [x] T2.8 Lección 8 · Repaso.
- [x] T2.9 Quiz de 10 preguntas con explicaciones.
- [x] T2.10 Glosario de 30-40 términos.
- [x] T2.11 Copiar figuras y corpus a `static/` con créditos.

#### F3 · Laboratorios

- [x] T3.1 `memory` y `cost`.
- [x] T3.2 `labels` y `prompt`.
- [x] T3.3 `transformer` y `attention`.
- [x] T3.4 `ngram` con corpus real, temperatura, top-k y generación.
- [x] T3.5 Registro de labs y carga diferida.

#### F4 · Vistas

- [x] T4.1 Landing y auth.
- [x] T4.2 Dashboard y curso.
- [x] T4.3 Lección y componentes.
- [x] T4.4 Quiz y revisión.
- [x] T4.5 Progreso, glosario, recursos y búsqueda.
- [x] T4.6 Panel de profesor y errores.
- [x] T4.7 Responsive, modo oscuro y estados vacíos.

#### F5 · Integración

- [x] T5.1 Routers de auth y curso.
- [x] T5.2 Router de quiz y cálculo de nota.
- [x] T5.3 Progreso, notas, marcadores y actividad.
- [x] T5.4 Búsqueda y glosario.
- [x] T5.5 Panel de profesor.
- [x] T5.6 Navegación anterior/siguiente y “continuar”.

#### F6 · QA

- [x] T6.1 Tests de auth, contenido, progreso y quiz.
- [x] T6.2 Revisión visual en escritorio y móvil.
- [x] T6.3 Checklist de accesibilidad.
- [x] T6.4 Prueba de flujo completo con cuenta demo.
- [x] T6.5 Corrección de textos y erratas.

#### F7 · Entrega

- [x] T7.1 README con arranque, cuentas y estructura.
- [x] T7.2 `.gitignore` para `aula.db`, `.venv`, capturas temporales.
- [x] T7.3 Script `uv run python aula.py` y variables de entorno documentadas.
- [x] T7.4 Capturas de referencia en `docs/capturas/`.

### 7.3 Orquestación del agent swarm

| Agente | Responsabilidad | Archivos propios | Depende de |
|---|---|---|---|
| **Lead** | Plan, contratos, integración, QA final | `docs/`, `webapp/config.py`, `db.py`, `security.py`, `deps.py`, `repositories.py`, `main.py`, `static/css/`, `templates/base.html` | — |
| **Backend** | Routers y formularios | `webapp/routers/*.py` | F1 |
| **Contenido A** | Lecciones 1-4 | `webapp/content/lessons/l01…l04.py` | schema |
| **Contenido B** | Lecciones 5-8, quiz, glosario | `webapp/content/lessons/l05…l08.py`, `quizzes.py`, `glossary.py` | schema |
| **Labs A** | `ngram`, `memory`, `cost` | `static/js/labs/{ngram,memory,cost}.js` | contrato de labs |
| **Labs B** | `labels`, `transformer`, `attention`, `prompt` | `static/js/labs/{labels,transformer,attention,prompt}.js` | contrato de labs |
| **Vistas** | Plantillas de páginas | `webapp/templates/pages/`, `components/` | F1-F3 |
| **QA** | Tests, enlaces, accesibilidad, revisión visual | `webapp/tests/`, `docs/QA.md` | F5 |

Reglas del swarm:

1. Cada agente escribe **solo** en sus archivos; nadie toca contratos compartidos.
2. Los contratos (`schema.py`, rutas, nombres de labs, clases CSS) se congelan antes.
3. Cada agente entrega código ejecutable, no pseudocódigo, y ejecuta su propia comprobación.
4. El lead integra, corrige interfaces y ejecuta la suite completa.
5. Ninguna tarea se considera hecha sin prueba manual o automática.

### 7.4 Hitos

| Hito | Fecha objetivo | Contenido |
|---|---|---|
| M1 | Día 1 | Plan aprobado + cimientos |
| M2 | Día 1-2 | Contenido y labs en paralelo |
| M3 | Día 2 | Vistas e integración |
| M4 | Día 3 | QA y entrega |

---

## 8. Estrategia de pruebas

### 8.1 Automáticas

- **Unitarias:** hash/verificación de contraseña, tokens, validación de contenido.
- **Integración:** registro, login, CSRF, acceso a lección, completar, nota, quiz.
- **Contenido:** slugs únicos, labs declarados existentes, quizzes referenciados,
  imágenes existentes, longitudes razonables.
- **Humo:** todas las rutas principales responden 200/302 con sesión.

Comando: `uv run pytest -q`.

### 8.2 Manuales

- Flujo completo: registro → lección → completar → quiz → revisión → progreso.
- Flujo profesor: login → panel → tabla.
- Responsive: 360, 768, 1280 px.
- Tema claro/oscuro.
- Navegación solo con teclado.
- Labs: cada control produce un cambio visible.
- Sin errores en consola del navegador.

### 8.3 Criterios de aceptación

1. `uv sync && uv run python aula.py` arranca sin pasos manuales.
2. Las 8 lecciones se leen completas y las figuras cargan.
3. Un usuario nuevo puede registrarse, completar una lección y hacer el quiz.
4. El progreso persiste tras reiniciar el servidor.
5. El quiz calcula bien la nota y guarda el intento.
6. El panel del profesor muestra datos reales.
7. No hay errores 500 en el recorrido principal.
8. La web es usable a 360 px y con teclado.
9. La suite de tests pasa.
10. README y créditos están actualizados.

---

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Contenido demasiado largo para web | Fatiga | Lecciones de 8-15 min, bloques escaneables, ideas clave |
| Labs lentos en móvil | Mala experiencia | Carga diferida, corpus cacheado, límites de tokens |
| Deriva de diseño entre agentes | Inconsistencia | Design system y contratos congelados; revisión del lead |
| Conflictos de archivos en el swarm | Bloqueo | Propiedad estricta de archivos y contratos previos |
| Seguridad casera defectuosa | Riesgo | scrypt, sesiones en BD, CSRF, escape automático, tests |
| Contenido con derechos | Legal | Figuras solo uso educativo, atribución y aviso |
| SQLite con concurrencia | Bloqueos | WAL, transacciones cortas, una conexión por petición |
| Cambios de alcance | Retraso | MVP cerrado; ideas a `docs/BACKLOG.md` |

---

## 10. Despliegue

### 10.1 Local

```powershell
uv sync
uv run python aula.py
# http://127.0.0.1:8000
```

Cuentas sembradas:

- Estudiante: `demo@aulallm.local` / `demo1234`
- Profesor: `profe@aulallm.local` / `profe1234`

### 10.2 Producción mínima

- `uv run uvicorn webapp.main:app --host 0.0.0.0 --port 8000`
- Variables: `AULA_SECRET`, `AULA_DB`, `AULA_ENV=production`, `AULA_SECURE_COOKIES=1`.
- Reverse proxy Caddy/Nginx con TLS.
- Copia de seguridad diaria de `aula.db`.
- Un solo worker mientras se use SQLite.

### 10.3 Evolución

- v1.1: capítulos 2-7 con el mismo motor.
- v1.2: traducción al inglés y ejemplos Python ejecutables en servidor (hecho).
- v1.3: Pyodide/kernel persistente para ejecutar snippets del libro en el navegador.
- v1.4: exportación de progreso, certificado y modo offline.
- v2: PostgreSQL, OAuth, múltiples cursos, foros.

---

## 11. Backlog inmediato post-MVP

- [ ] Capítulo 2 · Trabajar con texto (tokenización, BPE, embeddings).
- [ ] Capítulo 3 · Atención (QKV, máscara causal, multi-head).
- [x] Ejemplos Python ejecutables en servidor y descarga local.
- [x] Traducción a inglés.
- [ ] Modo “laboratorio Python” con Pyodide.
- [ ] Exportar apuntes y progreso a Markdown/PDF.
- [ ] Preguntas de repaso espaciado.
- [ ] Tests E2E con Playwright.
- [ ] Dockerfile y despliegue de demostración.

---

## 12. Definición de terminado (Definition of Done)

Una tarea está terminada cuando:

1. El código está implementado y formateado de forma coherente.
2. Existe al menos una prueba o comprobación manual registrada.
3. No rompe rutas existentes.
4. Respeta el diseño y los contratos.
5. Está documentado si introduce una decisión nueva.
6. El flujo de estudiante funciona de principio a fin.

El MVP está terminado cuando un visitante puede, sin ayuda:

> registrarse → entender el programa → estudiar las 8 lecciones → experimentar con los
> 7 laboratorios → aprobar el quiz → ver su progreso → consultar el glosario.

---

## 13. Registro de decisiones

| ID | Decisión | Fecha | Estado |
|---|---|---|---|
| D1 | FastAPI + Jinja2 en lugar de SPA | 2026-10-23 | Aceptada |
| D2 | SQLite en lugar de PostgreSQL | 2026-10-23 | Aceptada |
| D3 | Contenido en módulos Python versionados | 2026-10-23 | Aceptada |
| D4 | Labs en JS vanilla con carga diferida | 2026-10-23 | Aceptada |
| D5 | 8 lecciones para el capítulo 1 | 2026-10-23 | Aceptada |
| D6 | Cuentas demo y profesor sembradas | 2026-10-23 | Aceptada |
| D7 | OKF v0.2 + `AGENTS.md` como memoria persistente | 2026-10-24 | Aceptada |

---

*Este plan vive en el repositorio y se actualiza con cada fase. Las tareas se marcan al
completarse; las decisiones nuevas se añaden al registro.*
