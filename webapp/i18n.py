"""Internacionalización mínima de la interfaz.

Las claves son el texto en español; el diccionario traduce al inglés. Así el
código sigue siendo legible y una cadena nueva en español nunca rompe la web:
si falta la traducción, se muestra el original.

Los textos didácticos no viven aquí: cada idioma tiene su propio módulo de
contenido en `webapp/content/`.
"""

from __future__ import annotations

from fastapi import Request

SUPPORTED_LANGS = ("es", "en")
DEFAULT_LANG = "es"
LANG_COOKIE = "aula_lang"
LANG_NAMES = {"es": "Español", "en": "English"}


EN: dict[str, str] = {
    # ------------------------------------------------------------------ base
    "Saltar al contenido": "Skip to content",
    "Navegación del curso": "Course navigation",
    "Navegación principal": "Main navigation",
    "Cerrar": "Close",
    "material didáctico basado en": "teaching material based on",
    "de Sebastian Raschka.": "by Sebastian Raschka.",
    "Uso educativo": "Educational use",
    "Créditos": "Credits",
    "Basado en": "Based on",
    "de Sebastian Raschka (Manning, 2024). Figuras con fines educativos; todos los derechos pertenecen a Manning y al autor.": (
        "by Sebastian Raschka (Manning, 2024). Figures are used for educational purposes; all rights belong to Manning and the author."
    ),
    "Cerrar menú": "Close menu",
    "Abrir menú": "Open menu",
    "Colapsar barra lateral": "Collapse sidebar",
    "Expandir barra lateral": "Expand sidebar",
    "De cero a GPT": "From zero to GPT",
    "Capítulo 1": "Chapter 1",
    "Capítulo {n}": "Chapter {n}",
    "{n} lecciones": "{n} lessons",
    "{n} lección": "{n} lesson",
    "{n} capítulos": "{n} chapters",
    "{n} capítulos · {m} lecciones": "{n} chapters · {m} lessons",
    "Curso completo": "Full course",
    "Programa completo": "Full syllabus",
    "Capítulos y lecciones": "Chapters and lessons",
    "Ver capítulo": "View chapter",
    "Curso completado": "Course completed",
    "Continuar lección": "Continue lesson",
    "Has llegado al final del curso.": "You have reached the end of the course.",
    "Repasa las ideas clave o vuelve a intentar los quizzes para consolidar.": (
        "Review the key ideas or retake the quizzes to consolidate."
    ),
    "de este curso": "in this course",
    "interactivos en el curso": "interactive labs in the course",
    "La ruta del curso": "The course route",
    "Progreso del curso": "Course progress",
    "Glosario del curso": "Course glossary",
    "Repaso y quizzes": "Review and quizzes",
    "Curso interactivo · {n} capítulos disponibles": (
        "Interactive course · {n} chapters available"
    ),
    "Empezar el curso": "Start the course",
    "El libro, en {n} capítulos": "The book, in {n} chapters",
    "Del texto tokenizado a la atención, el pretraining y las instrucciones. Cada capítulo termina con su propio quiz.": (
        "From tokenized text to attention, pretraining, and instructions. "
        "Each chapter ends with its own quiz."
    ),
    "Siete capítulos y {n} lecciones breves que construyen intuición: del texto tokenizado a la atención, el pretraining y las instrucciones.": (
        "Seven chapters and {n} short lessons that build intuition: from tokenized "
        "text to attention, pretraining, and instructions."
    ),
    "Lecciones del curso": "Course lessons",
    "del curso": "of the course",
    "Vocabulario del curso": "Course vocabulary",
    "{completed} de {total} lecciones del curso": "{completed} of {total} course lessons",
    "Fin del curso": "End of course",
    "Puedes seguir con el siguiente capítulo del programa.": (
        "You can move on to the next chapter in the syllabus."
    ),
    "Puedes pasar al capítulo 2 cuando esté disponible.": (
        "You can move on to chapter 2 when it is available."
    ),
    "Inicio": "Home",
    "Curso": "Course",
    "Mi progreso": "My progress",
    "Glosario": "Glossary",
    "Recursos": "Resources",
    "Profesorado": "Teacher",
    "Estudiante": "Student",
    "Lecciones": "Lessons",
    "Cerrar sesión": "Sign out",
    "Cambiar tema": "Change theme",
    "Cambiar a tema claro": "Switch to light theme",
    "Cambiar a tema oscuro": "Switch to dark theme",
    "Buscar en el curso": "Search the course",
    "Buscar lecciones…": "Search lessons…",
    "Aula LLM · curso interactivo para construir un modelo de lenguaje desde cero.": (
        "Aula LLM: an interactive course on building a language model from scratch."
    ),
    "Construye un LLM desde cero, una idea a la vez.": (
        "Build an LLM from scratch, one idea at a time."
    ),
    "Construye un LLM desde cero": "Build an LLM from Scratch",
    "Capítulo 1 · Entender los LLM": "Chapter 1 · Understanding LLMs",
    "Capítulo 1 · {title}": "Chapter 1 · {title}",
    "Curso interactivo en español para entender y construir un modelo de lenguaje desde cero.": (
        "Interactive course to understand and build a language model from scratch."
    ),
    "Entrar": "Sign in",
    "Crear cuenta": "Create account",
    "Empezar gratis": "Start for free",
    "Estado": "Status",
    "Idioma": "Language",
    "Español": "Español",
    "English": "English",
    "Volver al inicio": "Back to home",
    "Ir al curso": "Go to the course",

    # ------------------------------------------------------------- componentes
    "Completada": "Completed",
    "En curso": "In progress",
    "Pendiente": "Not started",
    "Copiar": "Copy",
    "Copiado": "Copied",
    "No disponible": "Not available",
    "Limpiar": "Clear",
    "Salida": "Output",
    "Ejecutar": "Run",
    "Restablecer": "Reset",
    "Descargar": "Download",
    "Python · ejecutable": "Python · runnable",
    "Código Python editable": "Editable Python code",
    "Se ejecuta en el servidor, en un proceso aislado y con límite de tiempo y memoria.": (
        "Runs on the server in an isolated process with time and memory limits."
    ),
    "También puedes descargarlo y ejecutarlo en tu equipo.": (
        "You can also download it and run it on your machine."
    ),
    "Ejecutando…": "Running…",
    "Sin salida.": "No output.",
    "Gráfico generado por el ejemplo": "Chart generated by the example",
    "No se pudo ejecutar el código.": "The code could not be run.",
    "No se pudo cargar este laboratorio.": "This lab could not be loaded.",
    "Recarga la página o revisa la consola del navegador.": (
        "Reload the page or check the browser console."
    ),
    "Has respondido {answered} de {total} preguntas. ¿Enviar de todos modos?": (
        "You have answered {answered} of {total} questions. Submit anyway?"
    ),
    "El servidor no respondió. Inténtalo de nuevo.": (
        "The server did not respond. Please try again."
    ),
    "La ejecución remota está desactivada en este servidor.": (
        "Remote execution is disabled on this server."
    ),
    "Demasiadas ejecuciones seguidas. Espera {seconds} segundos.": (
        "Too many runs in a row. Wait {seconds} seconds."
    ),
    "El servidor está ejecutando otros ejemplos. Prueba en unos segundos.": (
        "The server is running other examples. Try again in a few seconds."
    ),
    "El código supera el límite de {chars} caracteres.": (
        "The code exceeds the {chars}-character limit."
    ),
    "Escribe algo de código antes de ejecutar.": "Write some code before running it.",
    "Error de seguridad": "Security error",
    "El código se ejecutó correctamente.": "Code ran successfully.",
    "El código devolvió un error.": "The code returned an error.",
    "Descargar los ejemplos de esta lección (.py)": (
        "Download this lesson's examples (.py)"
    ),
    "Descargar este ejemplo (.py)": "Download this example (.py)",
    "Laboratorio interactivo": "Interactive lab",
    "Cargando laboratorio…": "Loading lab…",
    "Ideas clave": "Key ideas",
    "Ampliar imagen: {alt}": "Enlarge image: {alt}",
    "Vista ampliada de la figura": "Enlarged figure view",
    "Figura ampliada": "Enlarged figure",

    # -------------------------------------------------------------- navegación
    "Tu aula": "Your classroom",
    "Tu recorrido": "Your journey",
    "Vocabulario del capítulo": "Chapter vocabulary",
    "Material de apoyo": "Support material",
    "Buscador": "Search",
    "Autoevaluación": "Self-assessment",
    "Revisión del intento": "Attempt review",
    "Panel del profesorado": "Teacher dashboard",
    "Error {code}": "Error {code}",
    "Lección {n} de {total}": "Lesson {n} of {total}",

    # ---------------------------------------------------------------- portada
    "Curso interactivo · Capítulo 1 disponible": (
        "Interactive course · Chapter 1 available"
    ),
    "Entiende cómo funciona ChatGPT. Luego constrúyelo.": (
        "Understand how ChatGPT works. Then build it."
    ),
    "Entiende cómo funciona ChatGPT. Luego": "Understand how ChatGPT works. Then",
    "Un aula online en español para estudiar Build a Large Language Model (From Scratch) sin instalar nada. Lecciones guiadas, laboratorios que se ejecutan en tu navegador y un quiz que comprueba lo que has aprendido.": (
        "An online classroom to study Build a Large Language Model (From Scratch) "
        "without installing anything. Guided lessons, labs that run in your browser, "
        "and a quiz that checks what you have learned."
    ),
    "constrúyelo": "build it",
    "Un aula online en español para estudiar": "An online classroom to study",
    "sin instalar nada. Lecciones guiadas, laboratorios que se ejecutan en tu navegador y un quiz que comprueba lo que has aprendido.": (
        "without installing anything. Guided lessons, labs that run in your browser, "
        "and a quiz that checks what you have learned."
    ),
    "Empezar el capítulo 1": "Start chapter 1",
    "Ya tengo cuenta": "I already have an account",
    "{n} minutos": "{n} minutes",
    "Sin GPU": "No GPU needed",
    "100 % en el navegador": "100% in the browser",
    "Aula LLM · predicción en vivo": "Aula LLM · live prediction",
    "Progreso guardado": "Progress saved",
    "Continúa donde lo dejaste": "Pick up where you left off",
    "Cómo funciona": "How it works",
    "Menos vídeos. Más entender haciendo.": "Fewer videos. More learning by doing.",
    "Cada lección combina una idea, una imagen o una demo, y una comprobación. Si algo no queda claro, vuelves al laboratorio y cambias un parámetro.": (
        "Each lesson combines an idea, a figure or a demo, and a quick check. "
        "If something is unclear, you go back to the lab and change a parameter."
    ),
    "Lecciones con hilo": "Lessons with a thread",
    "Ocho lecciones breves que construyen intuición: qué es un LLM, cómo se entrena, qué hace la atención y cómo se genera texto.": (
        "Eight short lessons that build intuition: what an LLM is, how it is trained, "
        "what attention does, and how text is generated."
    ),
    "Laboratorios reales": "Real labs",
    "Entrena un modelo de n-gramas con El Quijote, ajusta la temperatura, explora la atención y calcula el coste de entrenar a escala.": (
        "Train an n-gram model on Don Quixote, adjust the temperature, explore "
        "attention, and estimate the cost of training at scale."
    ),
    "Progreso y quiz": "Progress and quiz",
    "Marca lecciones, guarda apuntes y comprueba tu comprensión con diez preguntas corregidas en el servidor.": (
        "Mark lessons, save notes, and check your understanding with ten questions "
        "graded on the server."
    ),
    "Programa": "Syllabus",
    "El capítulo 1, en ocho paradas": "Chapter 1, in eight stops",
    'Del "juego de la siguiente palabra" al mapa completo de lo que construirás en el resto del libro.': (
        'From the "next-word game" to the full map of what you will build in the rest of the book.'
    ),
    "Crea tu cuenta": "Create your account",
    "Treinta segundos. Tu progreso, apuntes y notas quedan guardados en el aula.": (
        "Thirty seconds. Your progress, notes, and bookmarks are saved in the classroom."
    ),
    "Estudia y experimenta": "Study and experiment",
    "Lee, mueve los controles de los laboratorios y marca cada lección al terminarla.": (
        "Read, move the lab controls, and mark each lesson when you finish it."
    ),
    "Demuéstralo": "Prove it",
    "Haz el quiz final. Con un 80 % superas el capítulo y desbloqueas el siguiente.": (
        "Take the final quiz. With 80% you pass the chapter and unlock the next one."
    ),
    "Tu primer LLM empieza por entender el primero.": (
        "Your first LLM starts by understanding the first one."
    ),
    "Sin GPU, sin instalar Python y sin perderte en terminología. Solo tú, el texto y un navegador.": (
        "No GPU, no Python install, no getting lost in terminology. Just you, text, and a browser."
    ),
    "Entrar al aula": "Enter the classroom",

    # ---------------------------------------------------------------- acceso
    "Aula LLM · Capítulo 1": "Aula LLM · Chapter 1",
    "Aula LLM · Curso completo": "Aula LLM · Full course",
    "Vuelve a donde lo dejaste.": "Return to where you left off.",
    "Tu progreso, tus apuntes y tus intentos de quiz te esperan. Entra y continúa construyendo intuición sobre los LLM.": (
        "Your progress, notes, and quiz attempts are waiting. Sign in and keep "
        "building intuition about LLMs."
    ),
    "“Un LLM no devuelve una única palabra: devuelve una probabilidad para cada token posible y elige una.”": (
        "“An LLM does not return a single word: it returns a probability for every "
        "possible token and picks one.”"
    ),
    "Accede con tu correo y contraseña.": "Sign in with your email and password.",
    "Correo electrónico": "Email",
    "Contraseña": "Password",
    "Entrar al aula": "Enter the classroom",
    "¿No tienes cuenta?": "Don't have an account?",
    "Crear una cuenta gratis": "Create a free account",
    "Cuenta de demostración": "Demo account",
    "Correo": "Email",
    "Empieza por entender. Termina construyendo.": "Start by understanding. Finish by building.",
    "Ocho lecciones, siete laboratorios y un quiz. Sin instalar nada y sin GPU. Tu progreso se guarda automáticamente.": (
        "Eight lessons, seven labs, and a quiz. No installs, no GPU. Your progress is saved automatically."
    ),
    "“Predecir la siguiente palabra parece simple. De esa tarea emergen la gramática, el estilo y buena parte del razonamiento.”": (
        "“Predicting the next word sounds simple. Grammar, style, and much of "
        "reasoning emerge from that task.”"
    ),
    "Gratis, sin tarjeta. Solo necesitas un correo y una contraseña.": (
        "Free, no card. All you need is an email and a password."
    ),
    "Nombre": "Name",
    "Cómo quieres que te llamemos": "What should we call you?",
    "Repite la contraseña": "Repeat the password",
    "Al menos 8 caracteres": "At least 8 characters",
    "Otra vez, para evitar erratas": "Again, to avoid typos",
    "Crear mi cuenta": "Create my account",
    "¿Ya tienes cuenta?": "Already have an account?",

    # --------------------------------------------------------------- dashboard
    "Hola": "Hello",
    "Actividad de los últimos 14 días": "Activity over the last 14 days",
    "{n} acciones": "{n} actions",
    "Has terminado el capítulo. Puedes repasar o repetir el quiz.": (
        "You have finished the chapter. You can review it or retake the quiz."
    ),
    "Tu siguiente paso está a un clic. Sin prisa, pero sin pausa.": (
        "Your next step is one click away. No rush, but no pause either."
    ),
    "Ver el programa": "View the syllabus",
    "Siguiente paso": "Next step",
    "Capítulo completado": "Chapter completed",
    "Continuar lección {n}": "Continue lesson {n}",
    "{n} objetivos": "{n} objectives",
    "{n} laboratorio": "{n} lab",
    "{n} laboratorios": "{n} labs",
    "Has llegado al final del capítulo 1.": "You have reached the end of chapter 1.",
    "Repasa las ideas clave o vuelve a intentar el quiz para consolidar.": (
        "Review the key ideas or retake the quiz to consolidate."
    ),
    "Ir al repaso": "Go to the review",
    "Lecciones completadas": "Lessons completed",
    "de este capítulo": "in this chapter",
    "Racha actual": "Current streak",
    "{n} día": "{n} day",
    "{n} días": "{n} days",
    "actividad consecutiva": "consecutive activity",
    "Nota media": "Average score",
    "en los intentos de quiz": "across quiz attempts",
    "Laboratorios": "Labs",
    "7 laboratorios": "7 labs",
    "Quiz": "Quiz",
    "interactivos en el capítulo": "interactive labs in the chapter",
    "Tu actividad reciente": "Your recent activity",
    "Últimos 14 días": "Last 14 days",
    "Acciones": "Actions",
    "La ruta del capítulo": "The chapter route",
    "Ver detalle": "View details",
    "Progreso del capítulo": "Chapter progress",
    "completado": "completed",
    "{completed} de {total} lecciones completadas": "{completed} of {total} lessons completed",
    "Ver mi progreso": "View my progress",
    "Últimos intentos": "Recent attempts",
    "Todavía no has hecho el quiz. Cuando lo hagas, tus resultados aparecerán aquí.": (
        "You haven't taken the quiz yet. Your results will appear here when you do."
    ),
    "Accesos rápidos": "Quick links",
    "Glosario del capítulo": "Chapter glossary",
    "Recursos y descargas": "Resources and downloads",
    "Repaso y quiz": "Review and quiz",
    "Tu progreso": "Your progress",
    "Lección completada": "Lesson completed",
    "Aún en curso": "Still in progress",
    "Progreso del capítulo": "Chapter progress",
    "Marcar como pendiente": "Mark as not done",
    "Marcar como completada": "Mark as completed",
    "Tus apuntes": "Your notes",
    "Apuntes de la lección": "Lesson notes",
    "Escribe una idea, una duda o un ejemplo…": "Write an idea, a question, or an example…",
    "{n} caracteres": "{n} characters",
    "Guardar": "Save",
    "Marcador": "Bookmark",
    "Guarda esta lección para volver más tarde.": "Save this lesson to come back later.",
    "Quitar marcador": "Remove bookmark",
    "Guardar en marcadores": "Add bookmark",
    "Quiz del capítulo": "Chapter quiz",
    "Mejor resultado: {pct} % ({score}/{total}).": "Best result: {pct}% ({score}/{total}).",
    "Repetir quiz": "Retake quiz",
    "Diez preguntas para comprobar las ideas del capítulo.": (
        "Ten questions to check the chapter's main ideas."
    ),
    "Hacer el quiz": "Take the quiz",
    "Consejo de estudio": "Study tip",
    "Si una idea no queda clara, vuelve al laboratorio y cambia un parámetro. Aprender LLMs es construir intuición, no memorizar siglas.": (
        "If an idea is unclear, go back to the lab and change a parameter. Learning "
        "LLMs is about building intuition, not memorizing acronyms."
    ),
    "Al terminar sabrás…": "By the end you will be able to…",
    "Objetivos de la lección": "Lesson objectives",
    "Comprueba lo aprendido": "Check what you learned",
    "mejor intento": "best attempt",
    "Empezar quiz": "Start quiz",
    "{n} preguntas · necesitas {pct} % para aprobar": "{n} questions · you need {pct}% to pass",
    "Navegación entre lecciones": "Lesson navigation",
    "← Anterior": "← Previous",
    "Siguiente →": "Next →",
    "Fin del capítulo": "End of chapter",
    "Volver al programa": "Back to the syllabus",

    # ------------------------------------------------------------------ curso
    "Programa del curso": "Course syllabus",
    "{n} laboratorios": "{n} labs",
    "Continuar": "Continue",
    "Empezar": "Start",
    "{completed} / {total}": "{completed} / {total}",
    "lecciones completadas": "lessons completed",
    "Ver mi progreso →": "View my progress →",
    "Marca cada lección al terminarla para avanzar": (
        "Mark each lesson when you finish it to move forward"
    ),
    "Repasar": "Review",
    "Entrar a la lección": "Open lesson",
    "Cómo aprovechar el capítulo": "How to make the most of the chapter",
    "Cómo aprovechar el curso": "How to make the most of the course",
    "1 · Lee y predice": "1 · Read and predict",
    "Antes de seguir, intenta anticipar la respuesta. El cerebro aprende más cuando se equivoca y corrige.": (
        "Before moving on, try to anticipate the answer. The brain learns more when it errs and corrects."
    ),
    "2 · Toca los laboratorios": "2 · Play with the labs",
    "Mueve la temperatura, cambia el contexto, prueba otra precisión. Cada control enseña algo.": (
        "Move the temperature, change the context, try another precision. Every control teaches something."
    ),
    "3 · Cierra con el quiz": "3 · Finish with the quiz",
    "El quiz no es un examen: es una forma de detectar qué idea necesita otra pasada.": (
        "The quiz is not an exam: it is a way to spot which idea needs another pass."
    ),

    # ------------------------------------------------------------------- quiz
    "{n} preguntas": "{n} questions",
    "{pct} % para aprobar": "{pct}% to pass",
    "Intentos ilimitados": "Unlimited attempts",
    "Tu mejor resultado hasta ahora: {pct} %": "Your best result so far: {pct}%",
    "{score} de {total} correctas.": "{score} of {total} correct.",
    "Ya has superado el quiz; puedes repetirlo para consolidar.": (
        "You have already passed the quiz; you can retake it to consolidate."
    ),
    "Sigue practicando: cada intento te muestra qué repasar.": (
        "Keep practising: each attempt shows you what to review."
    ),
    "{score} de {total} correctas. Ya has superado el quiz; puedes repetirlo para consolidar.": (
        "{score} of {total} correct. You have already passed the quiz; you can retake it to consolidate."
    ),
    "{score} de {total} correctas. Sigue practicando: cada intento te muestra qué repasar.": (
        "{score} of {total} correct. Keep practising: each attempt shows you what to review."
    ),
    "{answered} de {total} respondidas": "{answered} of {total} answered",
    "Sin límite de tiempo": "No time limit",
    "Progreso del quiz": "Quiz progress",
    "Enviar respuestas": "Submit answers",
    "Puedes cambiar tus respuestas antes de enviar.": "You can change your answers before submitting.",
    "Intentos anteriores": "Previous attempts",
    "{n} intento": "{n} attempt",
    "{n} intentos": "{n} attempts",
    "Revisar →": "Review →",
    "¡Capítulo superado!": "Chapter passed!",
    "Todavía no, pero vas por buen camino": "Not yet, but you're on the right track",
    "{score} de {total} respuestas correctas": "{score} of {total} correct answers",
    "Puedes pasar al capítulo 2 cuando esté disponible.": (
        "You can move on to chapter 2 when it is available."
    ),
    "Repasa las explicaciones y vuelve a intentarlo: no hay límite de intentos.": (
        "Review the explanations and try again: there is no attempt limit."
    ),
    "{score} de {total} respuestas correctas · {date}. Puedes pasar al capítulo 2 cuando esté disponible.": (
        "{score} of {total} correct answers · {date}. You can move on to chapter 2 when it is available."
    ),
    "{score} de {total} respuestas correctas · {date}. Repasa las explicaciones y vuelve a intentarlo: no hay límite de intentos.": (
        "{score} of {total} correct answers · {date}. Review the explanations and try again: there is no attempt limit."
    ),
    "Volver al curso": "Back to the course",
    "Revisión pregunta a pregunta": "Question-by-question review",
    "Cada explicación te dice por qué la respuesta correcta lo es. Úsala para volver a la lección correspondiente.": (
        "Each explanation tells you why the correct answer is correct. Use it to return to the relevant lesson."
    ),
    "Sin responder.": "Not answered.",
    "Tu respuesta:": "Your answer:",
    "Respuesta correcta:": "Correct answer:",
    "Intentar de nuevo": "Try again",
    "Volver al repaso": "Back to the review",
    "Ver evolución": "View progress",
    "Resultado del quiz": "Quiz result",

    # --------------------------------------------------------------- progreso
    "Así va tu aprendizaje": "How your learning is going",
    "Todo tu progreso se guarda en el aula: lecciones completadas, apuntes, intentos de quiz y actividad diaria.": (
        "All your progress is saved in the classroom: completed lessons, notes, quiz attempts, and daily activity."
    ),
    "Progreso": "Progress",
    "del capítulo": "of the chapter",
    "en los quizzes": "across quizzes",
    "completadas": "completed",
    "Actividad · 28 días": "Activity · 28 days",
    "Racha": "Streak",
    "consecutivos": "in a row",
    "Lecciones del capítulo": "Chapter lessons",
    "{n} completada": "{n} completed",
    "{n} completadas": "{n} completed",
    "Lección": "Lesson",
    "Lección {n}": "Lesson {n}",
    "Estado": "Status",
    "Última visita": "Last visit",
    "Abrir →": "Open →",
    "Progreso total": "Total progress",
    "Actividad · 28 días": "Activity · 28 days",
    "Intentos de quiz": "Quiz attempts",
    "Hacer el quiz →": "Take the quiz →",
    "Aprobado": "Passed",
    "A repasar": "Needs review",
    "Aún no hay intentos. Cuando termines el capítulo, el quiz te dará una medida de lo aprendido.": (
        "No attempts yet. When you finish the chapter, the quiz will give you a measure of what you learned."
    ),

    # --------------------------------------------------------------- glosario
    "Las palabras que necesitas": "The words you need",
    "Una definición breve para cada término. Si una te resulta opaca, abre la lección enlazada: ahí está el contexto y el ejemplo.": (
        "A brief definition for each term. If one is unclear, open the linked lesson: "
        "the context and the example are there."
    ),
    "Buscar término": "Search term",
    "Buscar un término o una definición…": "Search for a term or definition…",
    "Ver en la lección →": "See it in the lesson →",
    "No hay términos que coincidan con tu búsqueda.": "No terms match your search.",

    # --------------------------------------------------------------- recursos
    "Para seguir explorando": "Keep exploring",
    "Descargas, datos y material complementario. Todo lo que necesitas para reproducir las demos o profundizar.": (
        "Downloads, data, and supplementary material. Everything you need to reproduce the demos or go deeper."
    ),
    "Abrir": "Open",
    "Créditos y licencias": "Credits and licenses",
    "Este material es de": "This material is for",
    "uso educativo personal": "personal educational use",
    "y está basado en": "and is based on",
    "de Sebastian Raschka (Manning, 2024). Las figuras 1.1–1.9 pertenecen a Manning Publications y al autor; se incluyen únicamente como apoyo al estudio. No las redistribuyas fuera de este contexto.": (
        "by Sebastian Raschka (Manning, 2024). Figures 1.1–1.9 belong to Manning "
        "Publications and the author; they are included only as study support. Do not "
        "redistribute them outside this context."
    ),
    "Los diagramas": "The",
    "son elaboración propia. El fragmento de": "diagrams are our own work. The excerpt from",
    "procede de Project Gutenberg y es de dominio público; se usa como corpus didáctico para el laboratorio de n-gramas.": (
        "comes from Project Gutenberg and is in the public domain; it is used as a teaching "
        "corpus for the n-gram lab."
    ),
    "Las estimaciones de tokens, memoria y coste son aproximadas y de orden de magnitud. No sustituyen una medición sobre hardware real.": (
        "Token, memory, and cost estimates are approximate and order-of-magnitude. They do "
        "not replace a measurement on real hardware."
    ),
    "Cuaderno interactivo": "Interactive notebook",
    "El capítulo completo en Jupyter, con las celdas y experimentos originales del libro.": (
        "The full chapter in Jupyter, with the book's original cells and experiments."
    ),
    "Corpus de El Quijote": "Don Quixote corpus",
    "Fragmento de texto en dominio público para entrenar el generador de n-gramas del laboratorio.": (
        "Public-domain text excerpt for training the lab's n-gram generator."
    ),
    "Figuras del capítulo": "Chapter figures",
    "Diagramas de la jerarquía de la IA, el transformer y las dos etapas del entrenamiento.": (
        "Diagrams of the AI hierarchy, the transformer, and the two training stages."
    ),
    "Plan de la plataforma": "Platform plan",
    "Documento de diseño con el alcance, la arquitectura, las fases y las decisiones técnicas del proyecto.": (
        "Design document with the scope, architecture, phases, and technical decisions of the project."
    ),
    "Guía de créditos": "Credits guide",
    "Fuentes, atribuciones y licencias del material didáctico y de las figuras utilizadas.": (
        "Sources, attributions, and licenses for the teaching material and figures."
    ),
    "Licencias y atribución": "Licenses and attribution",
    "Ejemplo Python ejecutable": "Runnable Python example",

    # --------------------------------------------------------------- buscador
    "Buscar: {query}": "Search: {query}",
    "Buscar": "Search",
    "Resultados para “{query}”": "Results for “{query}”",
    "¿Qué quieres encontrar?": "What do you want to find?",
    "Busca una idea, una sigla o un concepto. El buscador recorre títulos, resúmenes y el texto completo de las lecciones.": (
        "Search for an idea, an acronym, or a concept. The search covers lesson titles, summaries, and full text."
    ),
    "Por ejemplo: atención, temperatura, pretraining…": (
        "For example: attention, temperature, pretraining…"
    ),
    "{n} resultado": "{n} result",
    "{n} resultados": "{n} results",
    "Abrir": "Open",
    "Sin resultados": "No results",
    "desde cualquier página.": "from any page.",
    "Prueba con una palabra más general, por ejemplo “token”, “atención” o “datos”.": (
        "Try a more general word, for example “token”, “attention”, or “data”."
    ),
    "Empieza a escribir": "Start typing",
    "El buscador está disponible también con la tecla": (
        "The search box is also available with the"
    ),

    # -------------------------------------------------------------- profesor
    "Seguimiento del curso": "Course tracking",
    "¿Cómo va la clase?": "How is the class doing?",
    "Una vista agregada del avance del estudiantado. Los datos se actualizan con cada lección visitada y cada intento de quiz.": (
        "An aggregate view of student progress. Data updates with every lesson visit and quiz attempt."
    ),
    "Estudiantes": "Students",
    "cuentas registradas": "registered accounts",
    "Activos (7 días)": "Active (7 days)",
    "con actividad reciente": "with recent activity",
    "Intentos de quiz": "Quiz attempts",
    "en total": "in total",
    "de todos los intentos": "across all attempts",
    "Mejor quiz": "Best quiz",
    "Intentos": "Attempts",
    "Última actividad": "Last activity",
    "Todavía no hay estudiantes registrados.": "No students registered yet.",
    "Nota sobre privacidad": "Privacy note",
    "Este panel muestra datos de progreso con fines didácticos. En una instalación real, limita el acceso, informa al estudiantado y aplica una política de retención.": (
        "This dashboard shows progress data for teaching purposes. In a real "
        "deployment, restrict access, inform students, and apply a retention policy."
    ),

    # ---------------------------------------------------------------- errores
    "Acceso restringido": "Access restricted",
    "No tienes permiso para ver esta página.": "You do not have permission to view this page.",
    "Página no encontrada": "Page not found",
    "La dirección no existe o el contenido se ha movido.": (
        "The address does not exist or the content has moved."
    ),
    "Algo se ha roto": "Something broke",
    "Ha ocurrido un error interno. Vuelve a intentarlo en unos segundos.": (
        "An internal error occurred. Try again in a few seconds."
    ),
    "Inicia sesión para continuar.": "Sign in to continue.",
    "Esta sección es solo para el profesorado.": "This section is for teachers only.",
    "Token de seguridad inválido o caducado.": "Invalid or expired security token.",
    "Lección no encontrada.": "Lesson not found.",
    "Cuestionario no encontrado.": "Quiz not found.",
    "Intento no encontrado.": "Attempt not found.",
    "Cuaderno no disponible.": "Notebook not available.",
    "Plan no disponible.": "Plan not available.",
    "Demasiados intentos de inicio de sesión. Espera {minutes} minutos antes de volver a intentarlo.": (
        "Too many sign-in attempts. Wait {minutes} minutes before trying again."
    ),
    "Correo o contraseña incorrectos.": "Incorrect email or password.",
    "El nombre debe tener entre 2 y 80 caracteres.": "The name must be between 2 and 80 characters.",
    "Introduce un correo electrónico válido.": "Enter a valid email address.",
    "La contraseña debe tener al menos 8 caracteres.": "The password must be at least 8 characters.",
    "Las contraseñas no coinciden.": "The passwords do not match.",
    "Ya existe una cuenta con ese correo. Prueba a iniciar sesión.": (
        "An account with that email already exists. Try signing in."
    ),
    "Lección marcada como completada.": "Lesson marked as completed.",
    "Lección marcada como pendiente.": "Lesson marked as not done.",
    "Apuntes guardados.": "Notes saved.",
    "Marcador actualizado.": "Bookmark updated.",
    "No autenticado": "Not authenticated",
    "Recurso no disponible.": "Resource not available.",

    # ------------------------------------------------------- catálogo de cursos
    "Biblioteca de cursos": "Course library",
    "Aprende IA desde los libros que": "Learn AI from the books that",
    "la explican": "explain it",
    "Un aula online con cursos guiados, laboratorios que se ejecutan en el navegador y evaluación integrada. Empieza por el libro que quieras y continúa donde lo dejaste.": (
        "An online classroom with guided courses, browser-based labs, and integrated "
        "assessment. Start with any book and pick up where you left off."
    ),
    "Explorar cursos": "Explore courses",
    "1 curso": "1 course",
    "1 curso disponible": "1 course available",
    "Biblioteca de cursos · 1 curso disponible": "Course library · 1 course available",
    "Biblioteca de cursos · {n} cursos disponibles": (
        "Course library · {n} courses available"
    ),
    "{n} cursos": "{n} courses",
    "Elige tu próximo libro": "Choose your next book",
    "Cada curso es un recorrido completo con lecciones, laboratorios y quizzes. La biblioteca crecerá con nuevos libros.": (
        "Each course is a complete path with lessons, labs, and quizzes. The library "
        "will grow with new books."
    ),
    "Disponible": "Available",
    "Ver el curso": "View course",
    "En preparación": "Coming soon",
    "Nuevos cursos": "New courses",
    "El próximo libro": "The next book",
    "Estamos preparando nuevos recorridos. La plataforma ya está lista para incorporarlos sin cambiar la experiencia.": (
        "We are preparing new paths. The platform is ready to add them without "
        "changing the experience."
    ),
    "Mismo formato modular": "Same modular format",
    "Capítulos breves que construyen intuición: del texto tokenizado a la atención, el pretraining y las instrucciones.": (
        "Short chapters that build intuition: from tokenized text to attention, "
        "pretraining, and instructions."
    ),
    "Dentro del curso": "Inside the course",
    "Entiende cómo funciona ChatGPT. Luego constrúyelo.": (
        "Understand how ChatGPT works. Then build it."
    ),
    "El curso de referencia recorre el libro en {n} capítulos. Del texto tokenizado a la atención, el pretraining y las instrucciones.": (
        "The flagship course follows the book across {n} chapters. From tokenized "
        "text to attention, pretraining, and instructions."
    ),
    "Elige un curso": "Choose a course",
    "Explora la biblioteca y abre el libro que quieras estudiar. Cada curso tiene su propio temario y progreso.": (
        "Explore the library and open the book you want to study. Each course has its "
        "own syllabus and progress."
    ),
    "Haz el quiz final. Con un 80 % superas el capítulo y consolidas lo aprendido.": (
        "Take the final quiz. With 80% you pass the chapter and consolidate what you "
        "learned."
    ),
    "Tu próximo tema empieza por el libro adecuado.": (
        "Your next topic starts with the right book."
    ),
    "Curso actual": "Current course",
    "Cambiar de curso": "Switch course",
    "Ver todos": "View all",
    "Buscar en la biblioteca": "Search the library",
    "Buscar en la biblioteca…": "Search the library…",
    "Todos los cursos": "All courses",
    "Tus cursos": "Your courses",
    "Ver catálogo →": "View catalog →",
    "Catálogo de cursos": "Course catalog",
    "{completed} de {total} lecciones": "{completed} of {total} lessons",
    "Continuar curso": "Continue course",
    "Empezar curso": "Start course",
    "Cursos": "Courses",
    "Curso no encontrado.": "Course not found.",
    "Migas de pan": "Breadcrumbs",
    "Biblioteca de cursos interactivos para aprender IA construyendo.": (
        "A library of interactive courses for learning AI by building."
    ),
    "Material didáctico con fines educativos. Cada curso acredita el libro en el que se basa.": (
        "Educational material. Each course credits the book it is based on."
    ),
    "Cursos interactivos para entender y construir inteligencia artificial desde los libros que la explican.": (
        "Interactive courses to understand and build artificial intelligence from "
        "the books that explain it."
    ),
    "Acceso abierto": "Open access",
    "Crea una cuenta para guardar tu progreso, apuntes y resultados.": (
        "Create an account to save your progress, notes, and results."
    ),
    "Inicia sesión para empezar": "Sign in to start",
    "Otros cursos": "Other courses",
    "Cómo se organiza la biblioteca": "How the library is organised",
    "Un curso, un libro": "One course, one book",
    "Cada curso parte de un libro y mantiene su propio temario, figuras, laboratorios y quizzes.": (
        "Each course starts from a book and keeps its own syllabus, figures, labs, "
        "and quizzes."
    ),
    "Progreso independiente": "Independent progress",
    "Tus lecciones, apuntes, marcadores e intentos se guardan por curso. Cambiar de libro no mezcla tu avance.": (
        "Your lessons, notes, bookmarks, and attempts are stored per course. "
        "Switching books does not mix your progress."
    ),
    "Misma experiencia": "Same experience",
    "Todos los cursos comparten navegación, buscador, glosario y panel de progreso.": (
        "All courses share navigation, search, glossary, and the progress dashboard."
    ),
    "{n} cursos disponibles": "{n} courses available",
    "Elige qué quieres aprender": "Choose what you want to learn",
    "Cada curso es un recorrido modular con su propio temario, laboratorios, quizzes y progreso. Puedes entrar en cualquier momento y cambiar de curso sin perder lo avanzado.": (
        "Each course is a modular path with its own syllabus, labs, quizzes, and "
        "progress. You can join at any time and switch courses without losing your work."
    ),
    "Las figuras y marcas pertenecen a sus autores y editoriales; se incluyen únicamente como apoyo al estudio. No las redistribuyas fuera de este contexto.": (
        "Figures and trademarks belong to their authors and publishers; they are "
        "included only as study support. Do not redistribute them outside this context."
    ),
    "Volver al curso": "Back to the course",
    "Sin respuesta": "No answer",
    # --------------------------------------------------------------- estudio
    "Estudio": "Studio",
    "Estudio de autoría": "Authoring studio",
    "Convierte documentos en unidades": "Turn documents into units",
    "Sube un PDF, DOCX, EPUB, Markdown o TXT y OpenCode lo convierte en una unidad didáctica revisable antes de publicarla.": (
        "Upload a PDF, DOCX, EPUB, Markdown, or TXT file and OpenCode turns it into a "
        "teaching unit you can review before publishing."
    ),
    "Proveedor y modelo": "Provider and model",
    "Proveedor": "Provider",
    "Modelo": "Model",
    "Base URL": "Base URL",
    "API key": "API key",
    "Guardar configuración": "Save settings",
    "Borrar la clave guardada": "Delete the saved key",
    "La clave se guarda en el servidor y nunca se devuelve al navegador.": (
        "The key is stored on the server and never returned to the browser."
    ),
    "Proveedor configurado": "Provider configured",
    "Falta la API key": "API key missing",
    "OpenCode": "OpenCode",
    "Motor de generación": "Generation engine",
    "Nueva unidad a partir de documentos": "New unit from documents",
    "Título de trabajo": "Working title",
    "Slug (opcional)": "Slug (optional)",
    "Idiomas": "Languages",
    "Notas para el agente (opcional)": "Notes for the agent (optional)",
    "Documentos": "Documents",
    "Generar unidad": "Generate unit",
    "Formatos: PDF, DOCX, EPUB, ODT, Markdown, HTML o TXT. Varios archivos se combinan en una sola unidad.": (
        "Formats: PDF, DOCX, EPUB, ODT, Markdown, HTML, or TXT. Multiple files are "
        "combined into a single unit."
    ),
    "Trabajos recientes": "Recent jobs",
    "Todavía no hay trabajos.": "No jobs yet.",
    "Ver registro": "View log",
    "Cancelar": "Cancel",
    "Unidades generadas": "Generated units",
    "Todavía no hay unidades generadas.": "No generated units yet.",
    "Publicar": "Publish",
    "Despublicar": "Unpublish",
    "Eliminar": "Delete",
    "Borrador": "Draft",
    "Publicada": "Published",
    "En cola": "Queued",
    "Extrayendo texto": "Extracting text",
    "Generando unidad": "Generating unit",
    "Validando": "Validating",
    "Lista para revisar": "Ready to review",
    "Error": "Error",
    "Cancelada": "Cancelled",
    "Revisar unidad": "Review unit",
    "Abrir en el catálogo": "Open in catalog",
    "Configuración guardada.": "Settings saved.",
    "Trabajo creado. La unidad se generará en segundo plano.": (
        "Job created. The unit will be generated in the background."
    ),
    "Generación cancelada.": "Generation cancelled.",
    "Unidad publicada en el catálogo.": "Unit published in the catalog.",
    "Unidad retirada del catálogo.": "Unit removed from the catalog.",
    "Unidad eliminada.": "Unit deleted.",
    "Actualizar": "Refresh",
    "Se generará una unidad de 1 capítulo y 4 lecciones por defecto. Si el documento es largo, sube un capítulo o un extracto para obtener más detalle.": (
        "By default one chapter with four lessons is generated. For long documents, "
        "upload one chapter or an excerpt to get more detail."
    ),
    "El resultado se valida y se sanea antes de entrar en el catálogo. Nada del documento se ejecuta.": (
        "The result is validated and sanitized before entering the catalog. Nothing "
        "from the document is executed."
    ),
    "SLAnything · aprende IA desde los libros que la explican.": (
        "SLAnything: learn AI from the books that explain it."
    ),
    "OpenCode · autoría asistida": "OpenCode · assisted authoring",
    "Del documento a una unidad publicable": "From document to a publishable unit",
    "Qué ocurre al generar": "What happens when you generate",
    "El resultado se valida y se sanea antes de entrar en el catálogo. Nada del documento se ejecuta. La unidad queda en borrador hasta que la publiques.": (
        "The result is validated and sanitized before entering the catalog. Nothing "
        "from the document is executed. The unit stays as a draft until you publish it."
    ),
    "Redes neuronales en 4 lecciones": "Neural networks in 4 lessons",
    "Enfoca la unidad en el capítulo 3; nivel intermedio.": (
        "Focus the unit on chapter 3; intermediate level."
    ),
    "Máximo {n} MB por archivo y {m} archivos. El texto se recorta si supera el límite de contexto.": (
        "Up to {n} MB per file and {m} files. Text is truncated if it exceeds the "
        "context limit."
    ),
    "Selecciona al menos un idioma.": "Select at least one language.",
    "deja en blanco para conservarla": "leave blank to keep it",
    "lecciones": "lessons",
    "¿Eliminar esta unidad generada?": "Delete this generated unit?",
    "¿Cancelar este trabajo?": "Cancel this job?",
    "Si marcas los dos, el agente genera el mismo temario en ambos idiomas y la navegación no pierde el progreso.": (
        "If you select both, the agent generates the same syllabus in both languages "
        "and navigation keeps your progress."
    ),
    "Máximo {n} MB por archivo y {m} archivos.": "Up to {n} MB per file and {m} files.",
}


def normalize_lang(value: str | None) -> str:
    value = (value or "").lower().split("-")[0]
    return value if value in SUPPORTED_LANGS else DEFAULT_LANG


def translate(text: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Traduce una cadena de interfaz; si falta, mantiene el español."""
    value = EN.get(text, text) if lang == "en" else text
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError):
            return value
    return value


def request_lang(request: Request) -> str:
    return normalize_lang(getattr(request.state, "lang", DEFAULT_LANG))


def t(request: Request, text: str, **kwargs) -> str:
    return translate(text, request_lang(request), **kwargs)
