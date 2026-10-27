# Estudio de autoría · documentos → unidades con OpenCode

El **Estudio** convierte un documento en una unidad didáctica publicable en el
catálogo. Está pensado para el profesorado: sube un PDF, DOCX, EPUB, ODT,
Markdown, HTML o TXT, elige idioma y proveedor, y OpenCode genera un
`course.json` que el backend valida, sanea y deja en borrador.

## Flujo

```text
/estudio
  ├─ subir 1..5 documentos
  ├─ extraer texto (pypdf / python-docx / zipfile)
  ├─ trocear en source/source-NN.md
  ├─ opencode run --agent slanything-author --auto
  ├─ leer course.json y validar el contrato
  ├─ guardar en generated_courses (draft)
  └─ publicar → aparece en /cursos y /api/v1/catalog
```

El agente solo puede leer y escribir dentro del directorio del trabajo. No tiene
shell, web, tareas ni acceso a directorios externos. Los documentos se tratan
como datos no confiables: si contienen instrucciones, se ignoran.

## Arranque

### Docker (recomendado)

La imagen del backend ya incluye el binario portable de OpenCode:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Abre <http://127.0.0.1:3000/estudio> con la cuenta de profesora:

```text
profe@aulallm.local / profe1234
```

El Estudio escribe en `/data/authoring` dentro del volumen `aula-llm-data`:

```text
/data/authoring/
  settings.json          # proveedor, modelo y API key (0600)
  opencode-home/         # HOME/XDG aislados para OpenCode
  jobs/<id>/
    uploads/             # documentos originales
    source/              # texto extraído y troceado
    meta.json
    opencode.json
    AGENTS.md
    course.json
    run.log
```

### Local

```powershell
npm install -g @opencode/cli
uv sync
uv run python aula.py
```

Si `opencode` no está en el `PATH`, define
`AULA_AUTHORING_OPENCODE_BIN=C:\ruta\a\opencode.exe`.

## Configuración del proveedor

En `/estudio` ▸ **Proveedor y modelo**:

| Proveedor | Variable interna | Notas |
|---|---|---|
| OpenCode Go | `OPENCODE_API_KEY` | Recomendado. Pega la key del Console. |
| OpenCode · gratuitos | — | Modelos `*-free` para probar sin clave; límites variables. |
| OpenAI | `OPENAI_API_KEY` | Modelos GPT; admite base URL de gateway. |
| Anthropic | `ANTHROPIC_API_KEY` | Claude. |
| OpenRouter | `OPENROUTER_API_KEY` | ID completo del modelo. |
| Google Gemini | `GOOGLE_GENERATIVE_AI_API_KEY` | Google AI Studio. |
| DeepSeek | `DEEPSEEK_API_KEY` | API directa. |
| OpenAI-compatible | `SLANYTHING_LLM_KEY` | vLLM, LM Studio, gateways; base URL obligatoria. |
| Ollama / LM Studio | — | Servidor local; por defecto `host.docker.internal`. |

La API key **no se escribe en `opencode.json`**: se inyecta al subproceso como
variable de entorno. El navegador solo recibe `key_configured` y los cuatro
últimos caracteres. El archivo de ajustes se guarda con permisos `0600`.

### OpenCode Go

1. Entra en <https://opencode.ai/console> y copia la API key de Go.
2. En `/estudio`, elige **OpenCode Go**, modelo `deepseek-v4.1-flash` (o el que
   prefieras) y pega la key.
3. Guarda. El indicador debe pasar a **OpenCode listo para generar unidades**.
4. Sube un documento y pulsa **Generar unidad**.

La generación consume tu cuota de Go. El Estudio no envía la clave al
navegador ni la incluye en los logs.

### Endpoint propio

Para vLLM, LM Studio, Ollama o un gateway:

- Elige **OpenAI-compatible**.
- Base URL terminada en `/v1`, por ejemplo
  `http://host.docker.internal:11434/v1`.
- Modelo tal como lo sirve el endpoint.
- API key solo si el endpoint la exige.

En Linux, `host.docker.internal` funciona con el `extra_hosts` que ya incluye
`compose.yaml`. Si el endpoint está en otra máquina, usa su IP o DNS.

## Formatos y límites

- PDF con capa de texto (no escaneos; no hay OCR).
- DOCX, EPUB, ODT, Markdown, HTML y TXT.
- Hasta 5 documentos y 25 MB por archivo (configurable).
- Hasta ~300 000 caracteres de texto extraído; si se supera, se recorta y el
  agente recibe un aviso. Para libros largos, sube un capítulo o un extracto.
- Una generación produce por defecto **1 capítulo y 4 lecciones**, un quiz de
  8–10 preguntas y 8–12 términos de glosario. Si el documento lo justifica,
  puede llegar a 2 capítulos y 5 lecciones.
- Los idiomas se eligen en el formulario. Si marcas ES y EN, el paquete debe
  tener la misma estructura en ambos; si no, la validación falla.

## Contrato `course.json`

El contrato completo, con ejemplo y reglas editoriales, vive en
[`webapp/authoring/agent/AGENTS.md`](../webapp/authoring/agent/AGENTS.md). El
backend aplica además:

- `schema_version: 1`, 1–4 capítulos, 3–8 lecciones por capítulo.
- Primer bloque `lead`, último `keypoints`, al menos un `callout` y un `check`.
- Slugs globales con prefijo `gen-`; quiz vinculado a la última lección.
- HTML saneado con lista blanca (`strong`, `em`, `code`, `a`, listas…).
- Nada de `figure` ni `lab` en contenido generado.
- Código Python compilado antes de guardarse y ejecutado después por el sandbox
  existente, nunca por OpenCode.
- Menos de 30 lecciones y 3 MB de JSON.
- Si el primer `course.json` no valida, se pide **una reparación automática** con
  el error exacto. Si tampoco pasa, el trabajo falla y muestra el motivo.
- Si OpenCode cierra con código 1 pero dejó un `course.json` completo (por un
  corte transitorio del proveedor), se valida y se acepta.

## Seguridad

- Solo el rol `teacher` puede entrar en `/estudio` y en `/api/v1/authoring`.
- Todas las escrituras exigen CSRF.
- Los documentos no se sirven por HTTP; viven en el volumen privado.
- El agente no puede usar shell, web, subagentes ni directorios externos.
- El HTML generado se sanea antes de renderizarse en Next o Jinja.
- El binario de OpenCode se ejecuta como el usuario `aula` (no root) y con un
  `HOME`/`XDG` propios.
- El límite de tiempo por trabajo es de 30 minutos por defecto.

Esto es defensa en profundidad para una instalación autoalojada. Si expones el
Estudio a Internet, añade autenticación fuerte, TLS, cuotas por usuario y un
volumen de backups; el agente sigue siendo un proceso con acceso de escritura a
su directorio de trabajo.

## Operación

- Un trabajo a la vez (`ThreadPoolExecutor(max_workers=1)`), hasta 3 activos por
  profesor.
- Si el backend se reinicia, los trabajos en curso se marcan como fallidos para
  que no queden bloqueados.
- Cancelar termina el proceso de OpenCode y conserva el log.
- El log se recorta a 2 MB y se muestra en `/estudio`; se redactan las claves.
- Los borradores se pueden publicar, despublicar o eliminar. Hoy no hay una
  vista previa navegable del borrador: se publica para revisarlo y se puede
  despublicar; el editor de revisión es la siguiente mejora.
- Publicar invalida la caché de contenido dinámico; el curso aparece en el
  catálogo y en la API sin reiniciar.

## Problemas típicos

| Síntoma | Causa y solución |
|---|---|
| «No se encontró OpenCode» | En local instala `@opencode/cli` o define `AULA_AUTHORING_OPENCODE_BIN`. En Docker reconstruye la imagen. |
| «Falta la API key» | Guarda la key en `/estudio`; el indicador debe estar en verde. |
| «El PDF no contiene texto extraíble» | Es un escaneo. Aplica OCR o sube un DOCX/TXT. |
| «OpenCode terminó sin crear course.json» | El modelo no completó el archivo. Revisa el log, reduce el alcance o usa un modelo con más contexto. |
| «course.json no es JSON válido» | El agente dejó comas o marcadores. Reintenta; el log indica la línea. |
| «La lección es demasiado corta» | El modelo resumió demasiado. Añade notas de alcance o sube un documento más rico. |
| Timeout | Sube un documento más corto o aumenta `AULA_AUTHORING_TIMEOUT`. |
| El endpoint local no responde | En Docker usa `host.docker.internal`; comprueba que el servidor escucha en `0.0.0.0`. |

## Verificación

```powershell
uv run pytest -q
uv run python tools/validate_all_chapters.py
uv run python tools/check_okf.py

cd frontend
npm run typecheck
npm run build
```

La suite de autoría cubre el saneado, el contrato, la extracción, los ajustes,
la API, la publicación en el catálogo y el flujo del runner con OpenCode
simulado. La prueba manual con el modelo gratuito de OpenCode genera una unidad
de 4 lecciones y pasa `parse_package`.
