"""Lección 1 · Del modelo base al clasificador."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=1,
    slug="finetuning-clasificacion",
    title="Del modelo base al clasificador",
    summary=(
        "El finetuning de clasificación reutiliza un modelo generativo y lo "
        "especializa en un conjunto cerrado de etiquetas."
    ),
    minutes=10,
    objectives=(
        "Distinguir el finetuning de clasificación del finetuning de instrucciones.",
        "Explicar por qué un modelo base no resuelve bien una tarea solo con un prompt.",
        "Describir qué capas se congelan y cuáles se ajustan al añadir una cabeza de clasificación.",
        "Situar la clasificación dentro de las tres etapas de construcción de un LLM.",
    ),
    blocks=(
        lead(
            "Un modelo base sabe continuar un texto, pero no sabe tomar una decisión. "
            "Puede escribir «spam» después de una frase si el contexto lo invita, aunque "
            "también puede seguir la instrucción al pie de la letra y repetirla. Convertirlo "
            "en un clasificador exige algo más que un buen prompt: hay que cambiar la salida "
            "del modelo y ajustar parte de sus pesos con ejemplos etiquetados."
        ),
        h2("Especializar no es lo mismo que preguntar"),
        p(
            "El <strong>finetuning de clasificación</strong> entrena un modelo para asignar "
            "una de varias etiquetas prefijadas. En el ejemplo del capítulo, cada mensaje de "
            "texto se clasifica como <em>spam</em> o <em>no spam</em>. El modelo no elige "
            "libremente entre todas las palabras de su vocabulario: su última capa produce "
            "una puntuación por clase y la predicción es la clase con mayor puntuación. Esa "
            "restricción es una virtud y un límite. Es una virtud porque hace la tarea "
            "predecible y fácil de evaluar; es un límite porque el modelo solo puede "
            "responder con las etiquetas que ha visto durante el entrenamiento."
        ),
        p(
            "El libro sitúa esta técnica junto al <strong>finetuning de instrucciones</strong>, "
            "que se estudia en el capítulo siguiente. El segundo enseña al modelo a seguir "
            "órdenes variadas y conserva una gran flexibilidad; el primero lo convierte en un "
            "especialista. Desarrollar un especialista suele ser más sencillo y más barato que "
            "construir un generalista que rinda bien en todo. La contrapartida es clara: un "
            "clasificador de spam no sirve para traducir ni para resumir, aunque el modelo del "
            "que parta sepa hacerlo."
        ),
        table(
            ["Enfoque", "Qué añade", "Qué obtienes"],
            [
                [
                    "Prompt sobre el modelo base",
                    "Instrucciones y ejemplos en el contexto",
                    "Una respuesta condicionada, sin pesos nuevos",
                ],
                [
                    "Finetuning de clasificación",
                    "Una cabeza de clases y pesos ajustados",
                    "Una etiqueta fija para cada entrada",
                ],
                [
                    "Finetuning de instrucciones",
                    "Pares de instrucción y respuesta",
                    "Un modelo versátil que sigue órdenes",
                ],
            ],
            caption="Tres formas de adaptar un modelo. Solo las dos últimas modifican los pesos.",
        ),
        h2("Qué se congela y qué se ajusta"),
        p(
            "El punto de partida es un GPT-2 pequeño de 124 millones de parámetros, la misma "
            "arquitectura que el libro construyó en los capítulos anteriores y cuyos pesos "
            "carga ahora desde OpenAI. El procedimiento tiene "
            "tres gestos. Primero se <strong>congelan</strong> todos los parámetros: se marca "
            "que no requieren gradiente y dejan de actualizarse. Después se sustituye la capa "
            "de salida, que proyectaba 768 dimensiones al vocabulario de 50 257 tokens, por una "
            "capa lineal de 768 a 2 clases. Por último se <strong>descongelan</strong> la nueva "
            "cabeza, la última capa del transformer y la normalización final. El resto del "
            "modelo permanece intacto."
        ),
        p(
            "La razón es que las capas bajas capturan estructuras lingüísticas generales "
            "—morfología, sintaxis, asociaciones frecuentes— que sirven para muchas tareas. "
            "Las capas altas son más específicas y están más cerca de la decisión. Ajustar "
            "solo una parte reduce el coste y el riesgo de destruir lo aprendido. El libro "
            "comenta que entrenar únicamente la cabeza ya funciona, pero que añadir la última "
            "capa del transformer y su normalización mejora de forma apreciable el resultado. "
            "No es una receta universal: es un compromiso razonable entre adaptación y coste."
        ),
        callout(
            "warning",
            "El prompt no es entrenamiento",
            "Al pedirle al GPT-2 base «¿Es spam este texto? Responde sí o no», el libro obtiene "
            "una repetición de la instrucción, no una respuesta. El modelo no está roto: le "
            "falta el entrenamiento que le enseña a obedecer. El finetuning no consiste en "
            "escribir un prompt más largo, sino en modificar pesos y la forma de la salida."
        ),
        check(
            "¿Por qué un clasificador de spam solo puede responder «spam» o «no spam»?",
            "Porque su última capa tiene una salida por clase y se entrenó con esas dos "
            "etiquetas. La predicción es el índice con mayor puntuación, no una secuencia "
            "libre de tokens. Para responder cualquier otra cosa haría falta otro conjunto de "
            "clases u otro tipo de finetuning.",
        ),
        keypoints(
            [
                "El finetuning de clasificación especializa un modelo generativo en etiquetas prefijadas.",
                "El modelo solo puede predecir clases vistas durante el entrenamiento.",
                "Se congela el modelo, se sustituye la cabeza y se descongelan las últimas capas.",
                "Las capas bajas contienen lenguaje general; las altas se adaptan a la tarea.",
                "El finetuning de instrucciones es más flexible y requiere más datos y cómputo.",
                "Un prompt condiciona la generación, pero no sustituye al entrenamiento.",
            ]
        ),
    ),
    key_points=(
        "Clasificar es elegir entre etiquetas conocidas, no generar texto libre.",
        "La cabeza de clasificación sustituye la proyección al vocabulario.",
        "Congelar capas preserva el conocimiento general y reduce el coste.",
        "El finetuning de instrucciones y el de clasificación persiguen objetivos distintos.",
        "El modelo base necesita entrenamiento, no solo instrucciones, para clasificar.",
    ),
)
