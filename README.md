# SLAnything · Biblioteca de cursos interactivos

Plataforma web bilingüe (español e inglés), tipo aula virtual, con un **catálogo
de cursos** basados en libros técnicos y un **Estudio de autoría** que convierte
documentos en unidades didácticas. El primer curso convierte *Build a Large
Language Model (From Scratch)* de Sebastian Raschka (Manning, 2024) en siete
capítulos interactivos. La idea no es resumir el libro, sino **reconstruir las
ideas con código ejecutable, visualizaciones y experimentos**. La interfaz es
**Next.js 16 + React 19**; el backend es **FastAPI + SQLite** y la generación
asistida corre sobre **OpenCode**.

El proyecto incluye tres formas de aprender o enseñar:

1. **Aula web** (recomendada): catálogo de cursos, siete capítulos, laboratorios
   en el navegador, ejemplos de Python ejecutables en servidor, progreso aislado
   por curso, apuntes, quizzes y panel del profesor.
2. **Estudio de autoría** (`/estudio`, solo profesorado): sube PDF, DOCX, EPUB,
   ODT, Markdown, HTML o TXT; OpenCode genera una unidad bilingüe que se valida,
   se sanea y se publica en el catálogo.
3. **Cuaderno de Jupyter**: material complementario del capítulo 1, con celdas y
   widgets de `ipywidgets`.

La web se puede instalar como **PWA** y funciona igual en navegador, escritorio
y móvil. La decisión y la ruta a un wrapper nativo están en
[`docs/DESKTOP.md`](docs/DESKTOP.md). Los identificadores internos (`aula.db`,
cookies, volumen `aula-llm-data`) se mantienen por compatibilidad; el nombre del
producto es SLAnything.

![Portada de SLAnything con el programa del curso](docs/capturas/00b_landing_programa.png)

---

## Contexto para agentes

El repositorio mantiene una memoria persistente en formato **Open Knowledge
Format (OKF) v0.2**. Cualquier agente debe empezar por [`AGENTS.md`](AGENTS.md),
que enlaza el bundle [`okf/`](okf/index.md), y actualizarlo al terminar.

```powershell
uv run python tools/check_okf.py
```

---

## Aula web

### Arrancar

Requisitos: [uv](https://docs.astral.sh/uv/), Python 3.10 o superior, Node.js 20+ y npm.
No hace falta GPU.

```powershell
# Terminal 1 · backend FastAPI
uv sync
uv run python aula.py

# Terminal 2 · frontend Next.js
cd frontend
npm install
npm run dev
```

Abre <http://127.0.0.1:3000>. La interfaz Jinja anterior sigue disponible en
<http://127.0.0.1:8000> como fallback durante la migración.

### Docker

El proyecto incluye `Dockerfile` para FastAPI, `frontend/Dockerfile` para Next y
`compose.yaml` para levantar ambos servicios:

```powershell
Copy-Item .env.example .env
# Cambia AULA_SECRET en .env
docker compose up -d --build
docker compose ps
```

Abrir <http://127.0.0.1:3000>. La base SQLite vive en el volumen
`aula-llm-data`; `docker compose down` la conserva y `down -v` la borra. Guía
completa: [`docs/DOCKER.md`](docs/DOCKER.md).

Cuentas sembradas:

| Perfil | Correo | Contraseña |
|---|---|---|
| Estudiante | `demo@aulallm.local` | `demo1234` |
| Profesora | `profe@aulallm.local` | `profe1234` |

También puedes crear una cuenta nueva desde `/registro`.

### Estudio de autoría

Entra con `profe@aulallm.local / profe1234` y abre
<http://127.0.0.1:3000/estudio>.

1. Configura **OpenCode Go** (o OpenAI, Anthropic, OpenRouter, Gemini, DeepSeek,
   Ollama/LM Studio o un endpoint OpenAI-compatible) y guarda la API key.
2. Sube uno o varios documentos, elige ES/EN y pulsa **Generar unidad**.
3. Revisa el log y la unidad en borrador; publícala cuando esté lista.

La imagen Docker del backend incluye OpenCode. La key se guarda en
`/data/authoring/settings.json` (0600), nunca se devuelve al navegador y se
inyecta al subproceso como variable de entorno. El agente no tiene shell, web ni
acceso a directorios externos; el HTML generado se sanea y el contenido se valida
antes de entrar en el catálogo.

Guía completa: [`docs/AUTHORING.md`](docs/AUTHORING.md).

### Qué incluye

- **Catálogo multi-curso** (`/cursos` y `/cursos/{slug}`) con libro, nivel,
  duración, progreso y acceso al curso. El curso de referencia es
  `llm-desde-cero`; `/curso` sigue disponible como alias autenticado.
- **7 capítulos · 56 lecciones** (584 minutos) con objetivos, figuras y diagramas,
  tablas, código y autochequeos, en **español e inglés** (selector ES/EN en la cabecera).
  El recorrido va de entender los LLM a tokenizar texto, atención, arquitectura GPT,
  pretraining, clasificación y ajuste por instrucciones.
- **26 ejemplos de Python ejecutables** desde las lecciones: edita, ejecuta en un
  proceso aislado del servidor, ve stdout/tablas/gráficos y descarga el `.py` para
  ejecutarlo en local.
- **15 laboratorios interactivos** en JavaScript: memoria, etiquetas, transformer,
  atención, n-gramas, prompts, coste, tokenizador BPE, ventana deslizante, embeddings,
  Q/K/V, bloque GPT, pérdida, clasificador y plantilla de chat.
- **Progreso persistente por curso** en SQLite: lecciones completadas, actividad,
  racha, notas, marcadores e intentos. Cambiar de curso no mezcla el avance.
- **7 quizzes de 10 preguntas** corregidos en servidor, con revisión razonada e intentos
  ilimitados (80 % para aprobar).
- **Apuntes privados** y marcadores por lección.
- **Glosario** de 113 términos, buscador de lecciones y recursos descargables.
- **Panel del profesor** con progreso, actividad y mejores notas.
- **Catálogo de cursos** en `/cursos`, con un curso publicado y espacio para nuevos
  libros; el progreso, las notas y los intentos se guardan por curso.
- **Tema claro por defecto** y oscuro opcional, diseño responsive y navegación por teclado.

### Capturas

Todas las imágenes están tomadas de la app en local: 1440 × 1000 px en
escritorio y 390 × 844 px en móvil. La galería completa está en
[`docs/capturas/`](docs/capturas/README.md), con una descripción por archivo.

**Portada y catálogo**

| Portada completa | Programa del curso |
|---|---|
| ![Portada](docs/capturas/00_landing_full.png) | ![Programa del curso](docs/capturas/02_curso.png) |

**Aula**

| Dashboard del estudiante | Lección |
|---|---|
| ![Dashboard](docs/capturas/01_dashboard.png) | ![Lección](docs/capturas/03_leccion.png) |

| Progreso | Panel del profesorado |
|---|---|
| ![Progreso](docs/capturas/15_progreso.png) | ![Panel del profesorado](docs/capturas/20_profesor.png) |

**Evaluación y apoyo**

| Quiz | Glosario |
|---|---|
| ![Quiz](docs/capturas/05_quiz.png) | ![Glosario](docs/capturas/06_glosario.png) |

| Recursos descargables | Inicio de sesión | Registro |
|---|---|---|
| ![Recursos](docs/capturas/07_recursos.png) | ![Inicio de sesión](docs/capturas/16_login.png) | ![Registro](docs/capturas/17_registro.png) |

**Laboratorios interactivos**

| N-gramas | Memoria | Transformer |
|---|---|---|
| ![N-gramas](docs/capturas/04_lab_ngram.png) | ![Memoria](docs/capturas/09_lab_memoria.png) | ![Transformer](docs/capturas/10_lab_transformer.png) |

| Atención | Constructor de prompts | Calculadora de coste |
|---|---|---|
| ![Atención](docs/capturas/11_lab_attention.png) | ![Prompts](docs/capturas/12_lab_prompt.png) | ![Coste](docs/capturas/13_lab_cost.png) |

**Móvil**

| Lección | Menú lateral |
|---|---|
| ![Lección en móvil](docs/capturas/08_movil.png) | ![Menú en móvil](docs/capturas/14_movil_menu.png) |

**Tema oscuro**

![Dashboard en tema oscuro](docs/capturas/19_dark.png)

### Estructura

```text
frontend/                 # interfaz Next.js 16 (App Router, React, TypeScript)
  src/app/                # rutas (incluye /estudio y manifest PWA)
  src/components/         # shell, bloques, laboratorios, quiz, Studio y UI
  src/lib/                # API, tipos, mensajes y cliente HTTP
  next.config.ts          # rewrites a FastAPI y cabeceras
  Dockerfile              # imagen standalone del frontend
Dockerfile                # imagen del backend FastAPI
compose.yaml              # backend + frontend + volumen SQLite
.env.example              # variables de Docker Compose
docs/DOCKER.md            # guía de imágenes, datos y despliegue
AGENTS.md                 # arranque de sesión y mantenimiento del OKF
okf/                      # bundle OKF: memoria persistente del proyecto
  index.md                # catálogo de conceptos
  log.md                  # historial newest-first
  context/                # playbook, glosario, problemas, siguientes pasos
  project/                # visión, estado y roadmap
  product/                # curso, lecciones, labs, quiz y UX
  architecture/           # backend, frontend, datos, seguridad y contenido
  operations/             # arranque, tests, despliegue y mapa
  decisions/              # ADRs
  references/             # fuentes y comandos
tools/
  check_okf.py            # validador de conformidad y enlaces
webapp/
  main.py                 # app FastAPI, middleware de idioma, errores
  db.py                   # SQLite, esquema y cuentas demo
  security.py             # scrypt, sesiones, CSRF, rate limit
  deps.py                 # autenticación y permisos
  repositories.py         # consultas SQL
  i18n.py                 # traducciones ES→EN de interfaz
  execution.py            # límites, rate limit y subproceso de ejecución
  sandbox_runner.py       # runner Python aislado (`python -I`)
  routers/                # api JSON, auth, curso, autoría, ejecución, idioma, quiz, progreso, glosario, recursos, búsqueda, profesor
  authoring/              # Estudio: ajustes, extracción, contrato JSON, runner de OpenCode y agente
  content/                # lecciones, quiz y glosario (ES/EN) como módulos Python
  templates/              # Jinja2 (base, componentes y páginas)
  static/
    css/app.css           # sistema de diseño
    js/app.js             # tema, navegación, runner Python, laboratorios, quiz
    js/i18n.js            # textos de interfaz generados desde JS
    js/labs/              # 15 laboratorios + utilidades
    img/ch01..ch07/       # figuras del libro y diagramas propios
    data/                 # corpus de El Quijote
  tests/                  # suite pytest
docs/
  PLAN_PLATAFORMA_WEB.md  # plan de acción e implementación
  CONTRATO_AGENTES.md     # contratos del agent swarm
  AUTHORING.md            # documentos → unidades con OpenCode
  DESKTOP.md              # web + PWA y ruta a escritorio
  QA.md                   # estrategia y resultados de pruebas
notebooks/
  capitulo_01_entender_los_llms.ipynb
```

### Tests

```powershell
uv run pytest -q
uv run python tools/check_okf.py

cd frontend
npm run typecheck
npm run build

# Con ambos servidores arrancados
uv run python tools/smoke_next.py

# Smoke E2E de navegador (la primera vez instala Chromium)
npx playwright install chromium
npm run e2e
npm run e2e:labs   # monta los 15 laboratorios
```

La suite (111 tests) cubre contenido, catálogo de cursos, autenticación, CSRF,
progreso, notas, quiz, permisos de profesor, buscador, glosario, recursos,
errores, ejecución Python, descargas de código, contenido en inglés, la API JSON
que consume Next.js y el Estudio de autoría (contrato, saneado, extracción,
ajustes, publicación, reparación y runner simulado). El validador OKF comprueba
frontmatter, enlaces, índices y el historial.

### Producción mínima

```powershell
$env:AULA_ENV="production"
$env:AULA_SECRET="cambia-esto-por-un-secreto-largo"
$env:AULA_SECURE_COOKIES="1"
$env:AULA_DB="C:\datos\aula.db"
$env:AULA_EXEC_ENABLED="0"   # o mantén 1 con aislamiento adicional
uv run uvicorn webapp.main:app --host 127.0.0.1 --port 8000

# Frontend
cd frontend
$env:API_INTERNAL_URL="http://127.0.0.1:8000"
npm ci
npm run build
npm start
```

Pon un proxy inverso con TLS (Caddy o Nginx) delante de Next (puerto 3000),
limita el acceso al panel del profesor y haz copias de seguridad de `aula.db`.
FastAPI puede quedar escuchando solo en loopback porque el navegador habla con
Next; los rewrites se encargan del resto.

La ejecución de Python corre en un subproceso con validación AST, hook de auditoría y
límites de tiempo, memoria, salida y concurrencia. Es defensa en profundidad, **no un
sandbox de nivel producción**: para exponer la app a Internet, ejecuta el runner en un
contenedor sin red y sin privilegios o desactívalo con `AULA_EXEC_ENABLED=0`. Variables
útiles: `AULA_EXEC_TIMEOUT`, `AULA_EXEC_MEMORY_MB`, `AULA_EXEC_CONCURRENT`,
`AULA_EXEC_RUNS_PER_MINUTE`.

---

## Cuaderno de Jupyter

```powershell
uv sync
uv run jupyter lab notebooks/capitulo_01_entender_los_llms.ipynb
```

El cuaderno contiene 44 celdas, 17 de código, las figuras 1.1–1.9 y 8 demos con
`ipywidgets`. Duración estimada: 75–90 minutos. No hace falta GPU.

---

## Estado del proyecto

| Capítulo | Cuaderno | Aula web |
|---|---|---|
| 1 · Entender los LLM | listo | **listo** |
| 2 · Trabajar con texto | pendiente | pendiente |
| 3 · Atención | pendiente | pendiente |
| 4 · Arquitectura GPT | pendiente | pendiente |
| 5 · Pretraining | pendiente | pendiente |
| 6 · Clasificación | pendiente | pendiente |
| 7 · Instrucciones | pendiente | pendiente |

El motor web está preparado para añadir capítulos: cada lección es un módulo en
`webapp/content/lessons/` y el curso se ensambla en `webapp/content/course.py`.

---

## Créditos y licencias

Este material es de **uso educativo personal**. Las figuras 1.1–1.9 provienen de
*Build a Large Language Model (From Scratch)* de Sebastian Raschka (Manning, 2024); todos
los derechos pertenecen a Manning Publications y al autor. No redistribuyas esas figuras
fuera de este contexto de estudio. Los diagramas `fig_es_*.png` son elaboración propia.

El fragmento de *Don Quijote* procede de [Project Gutenberg](https://www.gutenberg.org/ebooks/2000)
y es de dominio público. Se usa únicamente como corpus didáctico para el laboratorio de
n-gramas.

Las estimaciones de tokens, memoria y coste son aproximadas y de orden de magnitud; no
sustituyen una medición sobre hardware real.

El Estudio usa [OpenCode](https://opencode.ai/) como motor de autoría. El binario
se instala desde el paquete oficial `@opencode/cli`; su licencia y la del
proveedor LLM elegido son independientes de SLAnything.
