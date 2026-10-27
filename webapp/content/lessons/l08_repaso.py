"""Lección 8 · Repaso y autoevaluación."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
)

LESSON = Lesson(
    number=8,
    slug="repaso",
    title="Repaso y autoevaluación",
    summary=(
        "Ocho ideas para llevarte y un quiz de diez preguntas para comprobar lo aprendido "
        "antes de pasar al capítulo 2."
    ),
    minutes=10,
    objectives=(
        "Repasar las ocho ideas clave del capítulo.",
        "Conectar los conceptos de las siete lecciones anteriores.",
        "Comprobar el aprendizaje con una autoevaluación.",
    ),
    blocks=(
        lead(
            "Has recorrido el capítulo 1. Es momento de consolidar: menos definiciones "
            "sueltas y más conexiones entre ellas. Si puedes explicar estas ocho ideas con "
            "tus propias palabras, tienes el mapa mental que necesitas para construir. No es "
            "un examen: es una oportunidad de detectar qué idea necesita una segunda visita."
        ),
        p(
            "El capítulo empezó con una frase incompleta y termina con un pipeline completo. "
            "Entre medias aparecieron los parámetros, el corpus, el transformer, la atención, "
            "la generación autorregresiva y los prompts. Este repaso los ordena. No intentes "
            "memorizar la lista: úsala como una red de comprobación."
        ),
        h2("Las ocho ideas que te llevas"),
        bullets(
            [
                "<strong>Un LLM predice el siguiente token.</strong> Esa tarea, sostenida por "
                "la escala de parámetros y datos, produce capacidades generales.",
                "<strong>“Grande” significa dos cosas:</strong> muchos parámetros y un corpus "
                "enorme y diverso. Ninguna de las dos basta por separado.",
                "<strong>El pretraining es autosupervisado:</strong> la etiqueta es el propio "
                "texto, concretamente el token que sigue. No hacen falta anotadores humanos.",
                "<strong>El finetuning especializa</strong> el modelo base con datos "
                "etiquetados, ya sea para seguir instrucciones o para clasificar.",
                "<strong>El transformer original tiene encoder y decoder.</strong> BERT usa el "
                "encoder; GPT usa el decoder. Son formas distintas de resolver tareas.",
                "<strong>La self-attention pondera la relevancia</strong> de los demás tokens "
                "y permite conectar información distante.",
                "<strong>GPT genera de forma autorregresiva:</strong> su salida anterior se "
                "convierte en entrada del siguiente paso.",
                "<strong>Zero-shot y few-shot no cambian los pesos:</strong> colocan "
                "instrucciones y ejemplos en el contexto. El finetuning sí cambia los pesos.",
            ],
            ordered=True,
        ),
        p(
            "Si tuvieras que quedarte con una sola frase, sería esta: un LLM es una red "
            "entrenada para predecir el siguiente token, y casi todo lo demás —traducir, "
            "resumir, programar, conversar— emerge de esa tarea cuando el modelo y los datos "
            "son suficientemente grandes. La temperatura y el top-k no cambian lo que el "
            "modelo sabe; solo cambian cómo elige entre sus candidatos. Del mismo modo, un "
            "prompt no cambia sus pesos: cambia el contexto desde el que predice."
        ),
        p(
            "Tres pares que conviene no confundir: parámetros frente a tokens (capacidad de la "
            "red frente a unidades de texto); pretraining frente a finetuning (aprender el "
            "idioma frente a especializarse en una tarea); y few-shot frente a finetuning "
            "(contexto frente a pesos). La atención, por su parte, no es un almacén de "
            "hechos: pondera la relevancia de los tokens presentes en el contexto. Si puedes "
            "explicar cada par en una frase, has entendido la estructura del capítulo."
        ),
        p(
            "Antes de seguir, intenta dibujar el pipeline de memoria: texto → tokens → "
            "embeddings → transformer → probabilidades → siguiente token → repetir. Si te "
            "atascas en un paso, vuelve a la lección correspondiente. El dibujo cabe en una "
            "servilleta y resume el capítulo entero. No hace falta memorizar cada fórmula: "
            "basta con saber qué entra y qué sale en cada etapa."
        ),
        h2("Comprobar lo aprendido"),
        p(
            "La autoevaluación del capítulo tiene <strong>diez preguntas</strong> de opción "
            "múltiple. Cada respuesta viene con una explicación y, al terminar, puedes "
            "revisar en qué lección se trabaja cada idea. No hay límite de tiempo ni "
            "penalización por repetir: el objetivo es detectar huecos, no aprobar por suerte. "
            "Si dudas entre dos opciones, pregúntate qué cambia y qué no: casi todas las "
            "preguntas del capítulo giran alrededor de esa distinción."
        ),
        check(
            "Explica en dos frases por qué few-shot no es lo mismo que finetuning.",
            "Few-shot añade ejemplos al prompt y condiciona la predicción sin tocar los "
            "pesos; el efecto desaparece al cerrar la conversación. El finetuning entrena "
            "con datos etiquetados y modifica los pesos de forma permanente.",
        ),
        callout(
            "success",
            "Ahora te toca",
            "Abre la <strong>autoevaluación del capítulo</strong>: diez preguntas y la "
            "explicación de cada respuesta. Necesitas un <strong>80 %</strong> —ocho de "
            "diez— para considerar el capítulo superado. Puedes repetirla tantas veces como "
            "quieras; si fallas alguna, vuelve a la lección correspondiente y prueba de "
            "nuevo.",
        ),
        keypoints(
            [
                "Predecir el siguiente token es la tarea que sostiene a un LLM.",
                "Parámetros y datos son las dos dimensiones de la escala.",
                "Transformer, atención y generación autorregresiva forman el núcleo técnico.",
                "Few-shot condiciona el contexto; el finetuning cambia los pesos.",
                "El quiz requiere un 80 % y puede repetirse sin penalización.",
            ]
        ),
    ),
    key_points=(
        "Un LLM predice el siguiente token; la escala y los datos explican sus capacidades.",
        "El pretraining aprende el idioma; el finetuning especializa el modelo.",
        "GPT usa el decoder y genera de forma autorregresiva.",
        "Few-shot no entrena: condiciona el contexto sin tocar los pesos.",
    ),
    quiz_id="quiz-capitulo-1",
)
