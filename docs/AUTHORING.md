# Estudio de autoría · documentos → unidades con agentes nas-adk

El **Estudio** convierte un documento de cualquier materia en una unidad
didáctica publicable en la biblioteca. Lo usan las **cuentas individuales** y el
**profesorado** de una academia. El alumnado no crea unidades ni configura
proveedores de IA.

Funciona así: subes un PDF, DOCX, EPUB, ODT, Markdown, HTML o TXT, eliges qué
partes convertir y revisas el temario. Después, unos agentes propios construidos
con [nas-adk](https://github.com/marcosflz/nas-adk) escriben las lecciones, la
autoevaluación y el glosario. El backend valida, sanea y verifica las citas antes
de dejar la unidad en borrador.

Decisiones de diseño:

- [ADR-023](../okf/decisions/adr-023-nas-adk-agents.md): los agentes. Sustituye
  al motor OpenCode.
- [ADR-017](../okf/decisions/adr-017-staged-generation.md): las etapas.
- [ADR-024](../okf/decisions/adr-024-user-ai-credentials.md): las credenciales.

## Flujo

```text
/estudio
  ├─ subir 1..5 documentos            → jobs/<id>/uploads/
  ├─ analizar estructura               → document.json (secciones + fragmentos citables)
  ├─ elegir alcance (capítulos, nivel, tipos de pregunta)
  ├─ agente outline + agente course    → outline.json (temario editable)
  ├─ revisar el temario
  ├─ agentes lesson (en paralelo)      → lessons/cN-lM.json
  ├─ agente assessment por capítulo    → assess/cN.json
  ├─ ensamblar, validar y verificar    → course.json + report.json
  └─ revisar, editar y publicar        → /cursos y /api/v1/catalog
```

Cada agente recibe su tarea, con los fragmentos del documento que le
corresponden. Dispone de varias herramientas Python:

| Herramienta | Qué hace |
|---|---|
| `read_fragment(chunk_id)` | Lee un fragmento completo del documento. |
| `search_document(query)` | Busca los fragmentos más parecidos dentro de su parte del documento. |
| `check_lesson(data)` | Comprueba un borrador de lección: formato y citas dudosas. |
| `submit_<tarea>(data)` | Entrega el resultado. Se valida con las reglas reales de la plataforma; si falla, el agente recibe el error y lo corrige. |

Los agentes no tienen shell, web ni acceso a archivos, y los documentos se tratan
como datos no confiables. La página del trabajo enseña su actividad en directo,
por ejemplo «Consultando un fragmento…».

## Proveedor de IA

Hay dos niveles:

1. **Plataforma.** Lo configura la superadministración en `/plataforma/ia` y lo
   usa quien no tenga uno propio. Puede ser OpenCode Go, OpenCode Zen gratuitos,
   Anthropic (API), OpenRouter, OpenAI, Gemini, DeepSeek, un endpoint compatible
   con OpenAI, Ollama o LM Studio.
2. **Propio.** Cualquier persona que crea unidades puede configurarlo en
   **Mi cuenta → Proveedor de IA**. Puede ser una API key o **su suscripción de
   Claude**. Los endpoints con URL propia (Ollama, LM Studio, gateway) solo los
   puede configurar la plataforma.

El Estudio indica con qué proveedor vas a generar («Generarás con…»).

Cada etapa se genera siempre con las credenciales de **quien la lanza**. Si otra
persona regenera una lección de tu unidad, por ejemplo un admin de la academia,
se usan sus credenciales o las de la plataforma, nunca las tuyas.

### Suscripción de Claude (personal)

1. Instala [Claude Code](https://claude.com/claude-code) en tu equipo e inicia
   sesión con tu plan Pro o Max.
2. Ejecuta `claude setup-token` y copia el token.
3. En **Mi cuenta → Proveedor de IA**, elige **Claude · mi suscripción
   personal**, pega el token y marca la casilla de uso personal. Después pulsa
   **Probar**.

Cómo se protege el token:

- Se guarda cifrado.
- Solo se usa en las unidades que generas tú.
- Solo llega al proceso del CLI `claude` del servidor, con una configuración
  propia en `/data/authoring/claude/<tu-id>`.
- La plataforma no puede usar una suscripción como proveedor general.

Ten en cuenta que cumplir las condiciones de Anthropic es responsabilidad tuya.
Además, con la suscripción no hay streaming y las lecciones se generan de una en
una.

La imagen Docker ya incluye el CLI con una versión fija. Para quitarlo, constrúyela
con `--build-arg INSTALL_CLAUDE_CODE=0`. También puedes desactivar la suscripción
con `AULA_SUBSCRIPTION_PROVIDER=0`, o todos los proveedores propios con
`AULA_USER_PROVIDERS=0`.

## Arranque

### Docker (recomendado)

```bash
cp .env.example .env
docker compose up -d --build
```

Para entrar en <http://127.0.0.1:3000/estudio>, usa una de estas cuentas:
`autodidacta@slanything.local / auto1234` o `profe@slanything.local / profe1234`.
Para probar sin proveedor ni red, arranca el backend con `AULA_LLM_FAKE=1`: un
modelo determinista llama a las mismas herramientas a través del `Runner` real.

Los datos del Estudio se guardan en `/data/authoring`, dentro del volumen:

```text
/data/authoring/
  settings.json          # proveedor de la plataforma (0600)
  claude/<user_id>/      # configuración del CLI de cada suscripción (0700)
  jobs/<id>/
    uploads/  document.json  outline.json  lessons/  assess/
    course.json  report.json  events.jsonl  meta.json
```

Las credenciales propias de cada usuario no van en este directorio: se guardan
cifradas en la base de datos (`user_ai_settings`).

### Local

```bash
uv sync                     # incluye nas-adk
uv run python aula.py       # backend
cd frontend && npm run dev  # frontend
```

## Formatos y límites

- PDF con capa de texto. Los escaneos no funcionan porque no hay OCR.
- También DOCX, EPUB, ODT, Markdown, HTML y TXT.
- Hasta 5 documentos de 25 MB cada uno, y hasta 3 trabajos activos por persona.
- Cuota mensual por espacio (`AULA_GEN_MONTHLY_*` o la fijada por la plataforma).
- Cada agente tiene un límite de llamadas al modelo y de contexto
  (`AULA_GEN_CONTEXT_TOKENS`), y cada ejecución tiene un tiempo máximo
  (`AULA_AUTHORING_TIMEOUT`).

## Contrato y calidad

La forma de las lecciones y de los bloques está en
`webapp/generation/prompts.py`. El backend comprueba lo siguiente con
`webapp/authoring/package.py`:

- Las lecciones empiezan por `lead`, terminan en `keypoints` y tienen al menos un
  `callout` y un `check`.
- Cada lección tiene un mínimo de 220 palabras.
- Cada capítulo tiene un quiz de 4 a 20 preguntas y un glosario de 6 a 24
  términos.
- El HTML se sanea con una lista blanca.
- El código Python solo lo ejecuta el sandbox.
- Si se pide ES+EN, los dos idiomas tienen la misma estructura y las mismas
  respuestas correctas.

En `report.json` está el porcentaje de bloques con cita y los bloques sin
respaldo, que la pantalla de revisión resalta.

## Problemas típicos

| Síntoma | Causa y solución |
|---|---|
| «La plataforma todavía no tiene configurado un proveedor» | Configúralo en `/plataforma/ia` o usa el tuyo en «Mi cuenta». |
| «El proveedor rechazó la credencial» | API key o token incorrectos o caducados. Vuelve a pegarlos y pulsa **Probar**. |
| «Se agotó la cuota del proveedor» | Espera a que se renueve. No se cambia de proveedor automáticamente. |
| «No se pudo ejecutar Claude Code» | El servidor no tiene el CLI `claude`. Reconstruye la imagen o define `AULA_CLAUDE_CODE_BIN`. |
| «El agente terminó sin entregar el resultado» | El modelo no llamó a `submit_*`, cosa habitual en modelos locales sin *tool calling*. Usa otro modelo. |
| «La lección es demasiado corta» | Añade indicaciones o sube un documento más rico. |
| Tus credenciales dejan de funcionar tras rotar `AULA_SECRET` | Vuelve a pegarlas en «Mi cuenta». |

## Verificación

```bash
uv run python -m pytest -q
uv run python tools/check_okf.py
cd frontend && npm run typecheck && npm run build
```

Los tests de autoría están en `test_authoring.py`, `test_generation.py`,
`test_adk_agents.py` y `test_ai_credentials.py`.
