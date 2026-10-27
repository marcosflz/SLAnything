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
    slug="repaso-gpt",
    title="Repaso y autoevaluación",
    summary=(
        "Ocho ideas para consolidar la arquitectura GPT y un quiz de diez preguntas "
        "para comprobar que puedes explicar cada pieza y sus cálculos."
    ),
    minutes=10,
    objectives=(
        "Relacionar configuración, normalización, activación, FFN, bloque y salida.",
        "Reconstruir el flujo completo de un GPT pequeño sin mirar los apuntes.",
        "Comprobar el aprendizaje con la autoevaluación del capítulo.",
    ),
    blocks=(
        lead(
            "Has recorrido la arquitectura de abajo arriba: primero los números de la "
            "configuración, después las piezas del bloque y, por último, la salida hacia el "
            "vocabulario. Toca consolidar. Este repaso no añade conceptos nuevos; ordena "
            "los que ya tienes y te ayuda a detectar qué pieza necesitas volver a mirar "
            "antes de pasar al entrenamiento."
        ),
        p(
            "La pregunta que organiza el capítulo es sencilla: ¿cómo se pasa de una "
            "secuencia de identificadores a una distribución sobre el siguiente token? La "
            "respuesta es una cadena de transformaciones con formas muy concretas. Si "
            "puedes reconstruir esa cadena y justificar cada paso, has entendido la "
            "arquitectura. Si algún eslabón se rompe, el quiz te dirá dónde volver."
        ),
        h2("El mapa completo"),
        bullets(
            [
                "<strong>Configuración.</strong> 50 257 tokens de vocabulario, 1 024 posiciones, 768 dimensiones, 12 cabezas y 12 capas. El modelo con pesos atados tiene 124 412 160 parámetros.",
                "<strong>LayerNorm.</strong> Normaliza cada token sobre sus 768 componentes, con media 0 y varianza 1, y deja que scale y shift ajusten la escala.",
                "<strong>GELU.</strong> Una activación suave que sustituye el codo de ReLU y conserva una señal pequeña para entradas negativas.",
                "<strong>FFN.</strong> Expande de 768 a 3 072, aplica GELU y vuelve a 768. Aporta 4,72 M de parámetros por bloque y no mezcla tokens.",
                "<strong>Bloque transformer.</strong> LN → atención → residual → LN → FFN → residual. La forma [batch, tokens, 768] se conserva.",
                "<strong>Residuales.</strong> La suma x + f(x) abre un camino directo para el gradiente y permite apilar muchos bloques.",
                "<strong>Cabeza de salida.</strong> Proyecta 768 → 50 257, produce logits y softmax los convierte en probabilidades.",
                "<strong>Sin entrenamiento no hay lenguaje.</strong> La arquitectura define el cálculo; los pesos preentrenados aportan el conocimiento.",
            ],
            ordered=True,
        ),
        p(
            "Hay tres cálculos que conviene poder repetir sin calculadora. Primero, los "
            "embeddings de tokens: 50 257 × 768 = 38 597 376. Segundo, la FFN de un bloque: "
            "2 × 768 × 3 072 + 3 072 + 768 = 4 722 432. Tercero, el total con pesos atados: "
            "sumar embeddings, doce bloques, la normalización final y nada más, porque la "
            "cabeza reutiliza la matriz de embeddings. Si añades la cabeza separada, "
            "obtienes 163 009 536. Estos números no son decoración: explican por qué el "
            "modelo ocupa lo que ocupa y por qué atar pesos importa."
        ),
        h2("Comprueba lo que sabes"),
        p(
            "La autoevaluación del capítulo tiene <strong>diez preguntas</strong> de cuatro "
            "opciones, con explicación en cada respuesta. Cubre las ocho lecciones e "
            "incluye dos preguntas de cálculo. Necesitas un <strong>80 %</strong> —ocho "
            "aciertos— para considerar el capítulo superado. No hay límite de tiempo ni "
            "penalización por repetir: el objetivo es encontrar huecos, no acertar por "
            "suerte. Si fallas una, vuelve a la lección correspondiente y reconstruye el "
            "razonamiento antes de reintentar."
        ),
        p(
            "Antes de abrir el quiz, intenta explicar el modelo en una frase: «Un GPT "
            "convierte tokens en vectores, los pasa por bloques que mezclan contexto y "
            "transforman cada posición, normaliza el resultado y lo proyecta al vocabulario "
            "para elegir el siguiente token». Si puedes añadir qué hace cada bloque, qué "
            "forma conserva y cuántos parámetros aporta, tienes el mapa mental completo. "
            "El capítulo siguiente pone ese mapa a entrenar."
        ),
        callout(
            "success",
            "Ahora te toca a ti",
            "Abre la <strong>autoevaluación del capítulo 4</strong>: diez preguntas y una "
            "explicación por respuesta. Necesitas un 80 % para superarla. Puedes repetirla "
            "tantas veces como quieras; si fallas, la explicación te indica qué lección "
            "revisar. El quiz no sustituye la práctica, pero sí te dice si la arquitectura "
            "ya está clara.",
        ),
        check(
            "Explica en dos frases por qué el bloque transformer conserva la forma de la "
            "entrada y, sin embargo, cambia su contenido.",
            "Porque todas las subcapas —atención y FFN— proyectan de vuelta a 768 "
            "dimensiones, de modo que la suma residual y el apilado sean posibles. Lo que "
            "cambia no es el número de tokens ni la dimensión, sino la representación: cada "
            "vector incorpora información del contexto y de las transformaciones "
            "aprendidas.",
        ),
        keypoints(
            [
                "La configuración de GPT-2 small define vocabulario, contexto, dimensión, cabezas y capas.",
                "LayerNorm estabiliza cada token; GELU aporta una no linealidad suave.",
                "La FFN expande, activa y proyecta, sin mezclar posiciones.",
                "El bloque combina dos subcapas, dos LayerNorm y dos residuales.",
                "La forma [batch, tokens, 768] se conserva; el contenido se vuelve contextual.",
                "La cabeza de salida produce logits y softmax los convierte en probabilidades.",
                "El quiz del capítulo requiere un 80 % y puede repetirse sin penalización.",
            ]
        ),
    ),
    key_points=(
        "Un GPT pequeño es la misma arquitectura que uno grande, con dimensiones manejables.",
        "LayerNorm, GELU, FFN, residuales y bloque se combinan en una secuencia repetible.",
        "La forma de la secuencia se conserva; la representación se enriquece.",
        "Los cálculos de parámetros explican el tamaño y el papel de los pesos atados.",
        "La autoevaluación comprueba las ocho lecciones y exige un 80 %.",
    ),
    quiz_id="quiz-capitulo-4",
)
