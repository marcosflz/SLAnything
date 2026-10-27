# QA · SLAnything

Documento de calidad de la plataforma web. Recoge la suite automática, su
cobertura, el resultado de la última ejecución y las comprobaciones que siguen
siendo manuales.

> **Nota (24 oct 2026):** este informe conserva las cifras del MVP del capítulo 1.
> El estado actual tiene 7 capítulos, 56 lecciones, 15 labs, 7 quizzes, catálogo
> de cursos, Estudio de autoría y 111 tests; el estado vigente está en
> `okf/project/status.md` y `okf/operations/testing.md`.

## Cómo ejecutar la suite

Requisitos: `uv` y las dependencias de desarrollo del proyecto (`pytest`).

```powershell
uv sync
uv run pytest -q
uv run python tools/check_okf.py
```

`pyproject.toml` ya fija `testpaths = ["webapp/tests"]`, por lo que no hace falta
pasar rutas. Para ver el resumen final con tiempos (recomendado en local):

```powershell
uv run pytest
```

### Aislamiento de las pruebas

- Cada test usa una base SQLite nueva en `tmp_path`; la fixture `db_path`
  parchea `webapp.config.DB_PATH` antes de arrancar la app.
- El `TestClient` se usa como context manager para ejecutar el `lifespan`
  (`init_db` + `validate_content`).
- El limitador de login en memoria (`login_limiter`) se vacía antes y después de
  cada test para evitar contaminación entre casos.
- No se realizan peticiones de red ni se usan servicios externos.
- `webapp/tests/conftest.py` añade la raíz del repositorio a `sys.path` porque
  `uv run pytest` no la incluye automáticamente al no instalarse el proyecto
  como paquete.

## Estructura de la suite

| Archivo | Tests | Qué cubre |
|---|---:|---|
| `test_content.py` | 8 | 8 lecciones, slugs/números, 83 min, quiz, glosario, labs, figuras y validador. |
| `test_public.py` | 6 | Landing, formularios públicos, redirección de zonas privadas, estáticos y cabeceras. |
| `test_auth.py` | 16 | Login demo, errores, registro, duplicados, logout, `next` seguro, rate limit, caducidad y hash. |
| `test_lessons.py` | 11 | Lectura, completar, apuntes, escape XSS, marcadores, CSRF, persistencia y límite de notas. |
| `test_quiz.py` | 5 | No filtración, 100 %, 0 %, revisión, privacidad de intentos y CSRF. |
| `test_flow.py` | 1 | Flujo completo: registro → lección → completar → quiz → revisión → progreso. |
| `test_teacher.py` | 3 | Acceso anónimo, 403 de estudiante y tabla del profesor. |
| `test_pages.py` | 4 | Buscador, glosario, recursos y descarga del cuaderno. |
| `test_errors.py` | 4 | 404 de lección, quiz, intento y ruta inexistente. |
| `test_security.py` | 4 | scrypt, tokens, comparación CSRF y limitador de login. |
| `test_execution.py` | 9 | Runner Python, stdout, tablas, gráficos, imports bloqueados, CSRF, timeout, descargas y ejemplos ingleses. |
| `test_i18n.py` | 6 | Validación ES/EN, landing, lecciones, quiz, glosario, cambio de idioma y ejecución en inglés. |
| `test_api.py` | 8 | API JSON: sesión, curso, lección, notas, marcadores, quiz, privacidad, profesor, registro y logout. |
| **Total** | **85** | |

## Docker

```powershell
docker compose build
docker compose up -d
docker compose ps
```

Comprobado con Docker Desktop (Linux containers): ambas imágenes construyen,
los healthchecks pasan, `/salud` responde a través de Next, login y flujo de
quiz funcionan, el runner Python ejecuta dentro del backend, las descargas
responden y `aula.db` persiste al recrear el contenedor backend.

## Frontend Next.js

```powershell
cd frontend
npm run typecheck
npm run build

# Con backend y frontend arrancados
uv run python tools/smoke_next.py
```

El smoke test comprueba el login a través del rewrite, la cookie de sesión, las
rutas principales, el cambio de idioma y el panel del profesor. La interfaz Jinja
del puerto 8000 se mantiene cubierta por la suite pytest durante la transición.

Smoke E2E de navegador:

```powershell
cd frontend
npx playwright install chromium
npm run e2e
```

Verifica login, montaje del laboratorio `memory`, ejecución de un ejemplo Python,
cambio de tema, selector ES/EN en ambos sentidos (landing y curso), colapso y
persistencia de la barra lateral, geometría del anillo de progreso, envío del quiz
y ausencia de errores de consola. Es un smoke manual, no una suite E2E completa.

## Cobertura por área

### 1. Contenido

- Exactamente 8 lecciones, números consecutivos y slugs únicos.
- Duraciones esperadas y total de 83 minutos.
- Quiz `quiz-capitulo-1` con 10 preguntas, `pass_score = 80`, ids únicos,
  explicaciones y todos los índices `correct` dentro de rango.
- Glosario con al menos 30 términos, sin duplicados y con enlaces a lecciones
  existentes.
- `validate_content` no lanza; todas las figuras referenciadas existen en
  `webapp/static/`.
- Cada lección empieza por `lead`, termina en `keypoints`, incluye `check`,
  objetivos e ideas clave; todos los labs son conocidos y tienen módulo JS.
- El validador detecta una figura inexistente (prueba negativa).

### 2. Público

- `GET /` responde 200 con el mensaje «Entiende cómo funciona ChatGPT» y el
  programa completo (8 items, 83 minutos).
- `GET /entrar` y `GET /registro` responden 200 con sus formularios.
- `GET /curso` y `GET /progreso` sin sesión redirigen con 303 a
  `/entrar?next=...`.
- `/salud` responde 200 y las cabeceras de seguridad están presentes.
- CSS y una figura real se sirven desde `/static/`.

### 3. Autenticación y sesión

- Login de la cuenta demo: 303, cookie de sesión y acceso a `/curso`.
- Login incorrecto y email desconocido: error visible, sin cookie y sin sesión.
- Registro válido: 303, sesión creada, dashboard y curso accesibles.
- Email duplicado (incluida otra capitalización), contraseña corta y
  contraseñas que no coinciden: error y sin alta.
- Logout con CSRF: 303, cookie eliminada, sesión borrada de la BD y `/curso`
  vuelve a redirigir al login.
- `next` externo (`https://evil.example`, `//evil.example`,
  `http://evil.example/phishing`) cae al fallback interno; `next` interno se
  conserva.
- Rate limit: tras 5 fallos, incluso la contraseña correcta recibe 429.
- Cookie de sesión `HttpOnly`, `SameSite=Lax` y `Path=/`.
- Contraseñas guardadas como `scrypt$...` con sal; el token de sesión se guarda
  como SHA-256 y nunca en claro.
- Una sesión caducada se rechaza y redirige al login.

### 4. Lecciones, progreso, notas y marcadores

- La lección responde 200 con título, objetivos, bloques y laboratorio.
- Completar con CSRF: 303, estado «Completada» en lección y `/progreso`, y
  contador `1 / 8`.
- Completar sin CSRF: 403.
- Nota sin CSRF o con token inválido: 403.
- La cabecera `X-CSRF-Token` también se acepta para peticiones tipo `fetch`.
- Un token CSRF de una sesión anterior se rechaza.
- Nota guardada y recuperada; el HTML de usuario se escapa (`<script>` no se
  renderiza literalmente).
- Las notas son privadas por usuario.
- El cuerpo de la nota se trunca al límite documentado de 20 000 caracteres.
- El marcador alterna el texto del botón (`Guardar en marcadores` ↔
  `Quitar marcador`).
- El progreso persiste al arrancar un segundo `TestClient` (nuevo `lifespan`)
  sobre la misma base de datos.
- Un estudiante nuevo completa el recorrido entero: registro, curso, lección,
  completar, quiz y revisión con 10/10.

### 5. Quiz

- El GET del quiz no incluye explicaciones ni la clase de revisión; no filtra
  respuestas.
- Todas las respuestas correctas: 303 a `/quiz/intento/{id}`, revisión con 100 %,
  «Capítulo superado» y explicaciones.
- Todas las respuestas incorrectas: 0 %, mensaje de fallo y «A repasar» en el
  panel de progreso.
- El intento de otro usuario devuelve 404.
- Enviar sin CSRF devuelve 403 y no crea intento.

### 6. Profesorado

- Anónimo: 303 al login con `next=/profesor`.
- Estudiante: 403 con mensaje de acceso restringido.
- Profesor: 200, tabla `teacher-table` y datos reales del estudiante demo.

### 7. Buscador, glosario y recursos

- `/buscar?q=atención` devuelve al menos la lección
  `transformer-y-atencion`.
- Una búsqueda sin coincidencias muestra el estado vacío.
- `/glosario` incluye `self-attention` y enlaces «Ver en la lección».
- `/recursos` lista el cuaderno; `/recursos/cuaderno` responde 200 con
  `application/x-ipynb+json` y JSON válido con celdas.

### 8. Errores

- `/leccion/no-existe`, `/quiz/no-existe`, `/quiz/intento/999999` y una ruta
  arbitraria devuelven 404 con la página de error.

### 9. Ejecución de Python

- Las lecciones incluyen `data-python-runner` y el código editable.
- `print(6 * 7)` devuelve `stdout = "42\n"`.
- pandas devuelve una tabla escapada; matplotlib devuelve una imagen PNG.
- `import os`, `open`, `getattr`, `eval` y `__class__` se bloquean con error de
  seguridad, no con una excepción no controlada.
- Sin CSRF, `/api/ejecutar` responde 403 JSON.
- `while True` se corta con el mensaje de tiempo máximo.
- La descarga individual y la descarga conjunta devuelven `.py` con el código.
- La tasa de ejecución se reinicia entre tests y no contamina la suite.

### 10. Idiomas

- Ambas variantes (`COURSES`, `GLOSSARIES`, `QUIZZES_BY_LANG`) pasan
  `validate_content`.
- `?lang=en` y `/idioma/en` activan inglés; la landing, curso, lecciones, quiz,
  glosario y progreso no contienen textos de interfaz en español.
- La revisión de un intento en inglés usa las preguntas inglesas con el mismo
  `quiz_id`.
- `/idioma/es` vuelve al español y la cookie `aula_lang` persiste.
- Los ejemplos Python tienen versión inglesa (variables y mensajes propios).

## Resultado de la última ejecución

- **Fecha:** 2026-10-24
- **Comando requerido:** `uv run pytest -q` (código de salida 0).
- **Resultado:** **85 tests, 85 passed, 0 failed**. Como `pyproject.toml` ya
  añade `-q`, el doble `-q` oculta la línea de resumen y solo imprime los
  puntos. Para ver el resumen con tiempos se ejecutó también `uv run pytest`:
  **85 passed, 1 warning in ~35s**.
- **Tests:** 85.
- **Warning:** `StarletteDeprecationWarning` emitido por
  `fastapi/testclient.py:1` al importar el cliente de pruebas
  («Using `httpx` with `starlette.testclient` is deprecated; install `httpx2`
  instead»). Es un aviso de dependencia, no un fallo de la aplicación ni de la
  suite.

Salida resumida de `uv run pytest`:

```text
..............................................................           [100%]
85 passed, 1 warning in 35.00s
```

## Incidencias y observaciones

No hay ningún test en rojo ni un fallo funcional que impida el flujo principal.
Las tres observaciones de la primera revisión se resolvieron antes de cerrar la
entrega:

1. **Lección 3 sin `callout`.** Se añadió el aviso «No todo transformer es un
   LLM» en `l03_transformer.py`.
2. **Lección 1 con 19 bloques.** Se amplió la lección con aplicaciones y la
   figura 1.2; tiene 25 bloques y 918 palabras. El contrato se ajustó a un rango
   de 6-25 bloques porque una lección puede combinar párrafos, tablas y figuras.
3. **Sesión sin renovación deslizante.** `webapp/deps.py` amplía ahora la
   sesión cuando quedan menos de 7 días, según el plan §5.7. Verificado con un
   script que sitúa la caducidad a 2 días y comprueba que se extiende a 14.

`validate_content` no comprueba las reglas editoriales 1-2 (número de bloques y
presencia de `callout`), pero la suite de contenido sí verifica `callout` y la
estructura pedagógica básica.

## Comprobaciones manuales pendientes

Las siguientes áreas no se pueden validar de forma fiable con `TestClient` y
requieren navegador, lector de pantalla o revisión humana:

### Visual y responsive

- Landing, dashboard, curso, lección, quiz, revisión, progreso, glosario,
  profesorado y recursos a 360, 768 y 1280 px. (Revisado en Chrome headless a
  1440 px y 390 px; pendiente una pasada final con lector de pantalla.)
- Menú lateral móvil, tabla de progreso/profesor y tarjetas del quiz sin
  desbordamientos.
- Modo claro y oscuro (incluida la persistencia en `localStorage` y
  `prefers-color-scheme`).
- Estados vacíos, mensajes flash `?ok=`/`?error=`, foco y hover.
- Figuras, lightbox y créditos; que las 9 figuras del capítulo cargan.

### Teclado y accesibilidad

- Recorrido completo con Tab/Shift+Tab, `skip-link`, foco visible y orden lógico.
- Formularios de login, registro, nota, completar, marcador y logout.
- Radios del quiz, `details` de autoevaluación, menú de usuario, selector de
  tema y lightbox.
- Contraste AA en ambos temas, textos alternativos, landmarks, etiquetas
  `aria-*` y lectura con lector de pantalla.
- `prefers-reduced-motion` y ausencia de animaciones molestas.

### Laboratorios

- Los 7 labs (`memory`, `labels`, `transformer`, `attention`, `ngram`, `prompt`,
  `cost`) montan sin errores de consola.
- Cada control produce un cambio visible e inmediato.
- Carga diferida con `IntersectionObserver`, limpieza al desmontar y
  comportamiento a 360 px.
- `ngram` carga `/static/data/quijote_fragmento.txt`, genera texto y responde a
  temperatura/top-k.
- `attention` dibuja el heatmap y permite cambiar la palabra objetivo.
- Copiar prompts/código funciona en navegadores reales (permisos de
  portapapeles).

### Persistencia y despliegue

- Reiniciar el servidor y comprobar que progreso, notas, marcadores, intentos y
  sesiones persisten en `AULA_DB`.
- Arranque limpio con `uv sync && uv run python aula.py` y con una BD vacía.
- Descarga del cuaderno y apertura en Jupyter.
- Cookies `Secure` con `AULA_SECURE_COOKIES=1` detrás de HTTPS.
- Rate limit detrás de un proxy real (la IP de `request.client` puede ser la del
  proxy; revisar cabeceras de confianza).
- Cabeceras de seguridad en producción y ausencia de `debug`.
- Consola del navegador sin errores y sin peticiones a dominios externos.

### Contenido y datos

- Lectura completa de las 8 lecciones y revisión de erratas.
- Enlaces internos, anclas, créditos y licencias de las figuras.
- Panel del profesor con varios estudiantes, intentos y actividad real.
- Búsqueda y filtro instantáneo del glosario en cliente.
