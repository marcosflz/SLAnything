---
type: ADR
title: ADR-012 · Estudio de autoría con OpenCode y superficie web + PWA
description: Decisión de empaquetar OpenCode en el backend, generar unidades como JSON validado y servir la misma interfaz como web instalable.
tags: [adr, opencode, autoría, documentos, pwa, docker, seguridad]
status: stable
date: 2026-10-24
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T21:30:00Z }
sources:
  - id: authoring
    resource: ../../docs/AUTHORING.md
    title: Guía del Estudio
  - id: desktop
    resource: ../../docs/DESKTOP.md
    title: Decisión web, PWA y escritorio
  - id: dockerfile
    resource: ../../Dockerfile
    title: Imagen del backend con OpenCode
  - id: package
    resource: ../../webapp/authoring/package.py
    title: Contrato y validación del paquete
  - id: runner
    resource: ../../webapp/authoring/runner.py
    title: Runner aislado de OpenCode
---

# Contexto

El curso de referencia se construyó a partir de un PDF con un proceso agéntico:
leer el libro, extraer las ideas, escribir lecciones, quizzes y glosario, y
validarlo todo contra el modelo de contenido. El siguiente paso de producto es
que ese proceso se pueda repetir desde la propia web con documentos nuevos, sin
depender de una sesión de agente en el repositorio.

A la vez hay que decidir la superficie: web, aplicación de escritorio o ambas.
El Estudio necesita el sistema de ficheros, OpenCode, el sandbox de Python,
SQLite y sesiones; una app de escritorio que solo cargue la web no aporta nada, y
una app totalmente offline duplicaría el backend y el binario de OpenCode por
plataforma.

# Decisión

1. **Web primero**. El Estudio vive en `/estudio`, dentro de la app Next.js y del
   backend FastAPI. La misma interfaz se publica como **PWA instalable**.
2. **OpenCode portable dentro de la imagen Docker del backend**. Se instala el
   binario Linux x64/arm64 en `/usr/local/bin/opencode`; en local se puede usar
   `npm install -g @opencode/cli`.
3. **El agente escribe datos, no código**. OpenCode produce un único
   `course.json` bilingüe. El backend lo valida, sanea el HTML y lo convierte en
   `Course`, `Program`, `Lesson` y `Quiz`. Nunca se importa Python generado.
4. **Proveedor configurable**. OpenCode Go (`OPENCODE_API_KEY`) es la opción
   recomendada; también OpenAI, Anthropic, OpenRouter, Gemini, DeepSeek, Ollama,
   LM Studio y cualquier endpoint OpenAI-compatible. La clave se guarda fuera de
   SQLite, en `authoring/settings.json` con permisos 0600, y se inyecta al
   subproceso como variable de entorno.
5. **Aislamiento y revisión**. Un trabajo a la vez; el agente no tiene shell,
   web, subagentes ni directorios externos. El resultado queda en borrador y solo
   el profesorado puede publicarlo.
6. **Sin app nativa por ahora**. La ruta a Tauri 2 queda documentada, pero no se
   implementa hasta que exista un requisito real de offline o integración con el
   sistema de archivos.

# Consecuencias

- La imagen del backend crece con el binario de OpenCode y necesita red para
  hablar con el proveedor LLM.
- Hay dos procesos mentales distintos: el catálogo estático del curso de
  referencia y el catálogo dinámico de cursos generados. La caché de contenido
  dinámico se invalida al publicar o despublicar.
- El contenido generado puede contener HTML hostil; por eso hay lista blanca y
  pruebas de saneado.
- El límite de contexto obliga a trocear documentos largos (~300 000 caracteres)
  y a pedir capítulos o extractos para libros completos.
- La PWA no funciona offline de verdad: las páginas y `/api/` van a la red. Solo
  se cachean estáticos. Es una decisión deliberada para no servir progreso o
  sesiones obsoletas.
- Si se expone a Internet, hacen falta TLS, cuotas, backups y autenticación
  fuerte; el aislamiento del agente es defensa en profundidad, no un sandbox de
  nivel producción.

# Alternativas descartadas

- **Integrar la app de escritorio de OpenCode**: no tiene catálogo, progreso,
  quizzes ni contrato de unidades; seguiría haciendo falta SLAnything.
- **Tauri/Electron ahora**: coste de firma, actualizaciones, sidecars y binarios
  por plataforma sin un requisito de producto que lo justifique.
- **Generar módulos Python e importarlos**: ejecuta código del modelo y complica
  la validación; el JSON es auditable y reversible.
- **Ejecutar OpenCode en el navegador**: no hay acceso al sistema de ficheros ni
  al binario, y expondría la API key al cliente.
- **Un servidor OpenCode compartido con la UI de OpenCode**: añade otra
  superficie de autenticación y no encaja con el contrato de contenido.

# Referencias

- [Guía del Estudio](../../docs/AUTHORING.md)
- [Web, PWA y escritorio](../../docs/DESKTOP.md)
- [Contrato del paquete](../../webapp/authoring/package.py)
- [Runner de OpenCode](../../webapp/authoring/runner.py)
- [OpenCode V2 · SDK](https://opencode.ai/v2/docs/build/sdk)
- [OpenCode V2 · proveedores](https://opencode.ai/v2/docs/providers)
