---
type: Assessment
title: Quizzes del curso
description: Siete evaluaciones de 10 preguntas, corrección en servidor, revisión y política de intentos.
tags: [quiz, evaluacion, correccion, progreso, capitulos]
status: stable
generated: { by: opencode/deepseek-v4.1-flash, at: 2026-10-24T20:00:00Z }
sources:
  - id: quizzes
    resource: ../../webapp/content/quizzes.py
    title: Quiz del capítulo 1
  - id: chapters
    resource: ../../webapp/content/chapters/
    title: Quizzes de los capítulos 2-7
  - id: router
    resource: ../../webapp/routers/quiz.py
    title: Corrección y revisión
---

# Catálogo

| ID | Capítulo | Preguntas | Aprobado |
|---|---|---|---|
| `quiz-capitulo-1` | Entender los LLM | 10 | 80 % |
| `quiz-capitulo-2` | Trabajar con texto | 10 | 80 % |
| `quiz-capitulo-3` | Atención | 10 | 80 % |
| `quiz-capitulo-4` | Arquitectura GPT | 10 | 80 % |
| `quiz-capitulo-5` | Pretraining | 10 | 80 % |
| `quiz-capitulo-6` | Clasificación | 10 | 80 % |
| `quiz-capitulo-7` | Instrucciones | 10 | 80 % |

# Contrato

- Los IDs son estables y se comparten entre español e inglés.
- 10 preguntas, 3-4 opciones cada una, con explicación.
- 80 % para aprobar (8/10).
- Intentos ilimitados y sin tiempo.
- Corrección en servidor: el GET nunca revela la respuesta.
- Cada intento guarda `score`, `total`, `answers_json` y `created_at`.
- La revisión muestra respuesta elegida, correcta y explicación.
- El quiz se enlaza desde la lección 8 de cada capítulo.

# Flujo

1. `GET /quiz/{id}` muestra preguntas y mejores intentos.
2. `POST` con `csrf_token` y campos `q_q1`…`q_q10` (índice de opción).
3. El servidor puntúa, crea el intento y registra actividad.
4. Redirige a `/quiz/intento/{id}`.
5. La revisión es privada del usuario: un intento ajeno devuelve 404.

# Persistencia

`quiz_attempts` (SQLite) guarda el intento. `best_attempt` ordena por porcentaje y
fecha. `attempts_for_quiz` alimenta el historial. La media se calcula sobre todos
los intentos del usuario, independientemente del capítulo.

# Mensajes

- ≥ 80 %: «Capítulo superado».
- < 80 %: «Todavía no…» y invitación a repasar.
- Sin responder: se permite enviar con confirmación en JS; las no respondidas
  cuentan como fallo.

# Quizzes generados

El Estudio añade un quiz por capítulo generado, con 4–10 preguntas y 80 % para
aprobar. Se prefija con el slug del curso (`gen-…-quiz`), se valida igual que los
estáticos y comparte corrección, intentos y revisión. Las respuestas correctas
deben coincidir entre ES y EN.

# Añadir o cambiar un quiz

Los quizzes del capítulo 1 viven en `webapp/content/quizzes.py` y
`quizzes_en.py`. Los de los capítulos 2-7 viven en
`webapp/content/chapters/chNN/quiz_es.py` y `quiz_en.py`. Mantén 10 preguntas,
`pass_score=80`, ids `q1`-`q10` y el `quiz_id` en la lección 8. Después ejecuta
`uv run pytest -q`, `tools/check_chapter.py chNN`,
`tools/validate_all_chapters.py` y el validador OKF. Actualiza este concepto,
[lessons](/product/lessons.md), [status](/project/status.md) y [log](/log.md).
Los intentos guardan el `quiz_id`, no el idioma: al cambiar de lengua se revisan
con las preguntas del bundle activo.
