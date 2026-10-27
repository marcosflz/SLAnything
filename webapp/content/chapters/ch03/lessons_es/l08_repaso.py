"""Lección 8 · Repaso y autoevaluación."""

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
    number=8,
    slug="repaso-atencion",
    title="Repaso y autoevaluación",
    summary=(
        "Un repaso del recorrido completo —de la memoria fija a multi-head— y una "
        "autoevaluación de diez preguntas para comprobar qué has interiorizado."
    ),
    minutes=10,
    objectives=(
        "Reconstruir la cadena completa de la atención desde Q, K y V hasta el contexto.",
        "Relacionar las dimensiones de los modelos con el reparto por cabezas.",
        "Detectar confusiones frecuentes sobre pesos, máscaras y coste.",
        "Autoevaluar el capítulo con un cuestionario de diez preguntas.",
    ),
    blocks=(
        lead(
            "La atención se entiende mejor como una cadena de decisiones pequeñas. Proyectar, "
            "puntuar, escalar, enmascarar, normalizar y mezclar. Si puedes recorrer esa cadena y "
            "justificar cada paso, tienes lo esencial del capítulo 3. El cuestionario final te "
            "ayudará a comprobar qué partes necesitan otra pasada."
        ),
        h2("El mecanismo en una frase"),
        p(
            "La self-attention toma una secuencia de vectores X y calcula tres proyecciones: "
            "Q = XW<sub>q</sub>, K = XW<sub>k</sub> y V = XW<sub>v</sub>. Compara cada consulta con "
            "todas las claves mediante QK<sup>T</sup>, divide por √d<sub>k</sub>, enmascara las "
            "posiciones futuras si el modelo es causal y aplica softmax por filas. El resultado es "
            "una matriz de pesos que, multiplicada por V, produce los vectores de contexto Z. En "
            "multi-head, este proceso se repite en varias cabezas y sus salidas se concatenan."
        ),
        p(
            "Cada paso tiene una razón. Las proyecciones permiten papeles distintos para el mismo "
            "token. El producto escalar mide alineación. La escala evita la saturación de softmax. "
            "La máscara impide la fuga de futuro. Softmax convierte puntuaciones en proporciones "
            "positivas que suman uno. La suma ponderada mezcla contenidos. Si eliminas uno de estos "
            "pasos, el mecanismo cambia de comportamiento, no solo de eficiencia."
        ),
        h2("Del juguete al modelo"),
        p(
            "En los ejemplos del capítulo usamos tres tokens de cuatro dimensiones para poder "
            "seguir las cuentas. El libro usa seis tokens y vectores de tres dimensiones en la "
            "versión simple, y proyecciones de 3 a 2 en la versión con pesos. Esos números no "
            "describen un GPT real: son maquetas. GPT-2 pequeño trabaja con 768 dimensiones, 12 "
            "cabezas de 64 y una ventana de 1024 tokens. GPT-2 grande sube a 1600 dimensiones y 25 "
            "cabezas, también de 64."
        ),
        table(
            ["Idea", "Qué retener", "Dónde se vio"],
            [
                [
                    "Memoria fija",
                    "Un estado oculto único comprime toda la entrada y pierde dependencias largas.",
                    "Lección 1",
                ],
                [
                    "Pesos de atención",
                    "Se calculan para cada entrada y suman uno por fila; no son parámetros.",
                    "Lección 2",
                ],
                [
                    "Q, K y V",
                    "Tres proyecciones aprendidas con papeles distintos.",
                    "Lección 3",
                ],
                [
                    "Escalado",
                    "Dividir por √d_k controla la saturación de softmax.",
                    "Lección 4",
                ],
                [
                    "Máscara causal",
                    "−∞ antes de softmax elimina el futuro y las filas se renormalizan.",
                    "Lección 5",
                ],
                [
                    "Multi-head",
                    "Varias cabezas de d_modelo / h, concatenadas y proyectadas.",
                    "Lección 6",
                ],
                [
                    "Coste",
                    "n² puntuaciones por cabeza y capa; el contexto largo es caro.",
                    "Lección 7",
                ],
            ],
            caption=(
                "Mapa de repaso: cada fila conecta una idea con la lección donde se desarrolló. "
                "Si alguna te resulta opaca, vuelve a esa lección antes del quiz."
            ),
        ),
        h2("Errores frecuentes"),
        p(
            "El primero es confundir los pesos de atención con los pesos del modelo. Los primeros "
            "son dinámicos y suman uno por fila; los segundos son parámetros que persisten tras el "
            "entrenamiento. El segundo es creer que la máscara elimina tokens del tensor: lo que "
            "hace es asignarles peso cero, pero siguen ocupando posiciones y memoria. El tercero "
            "es pensar que un peso alto explica la predicción. La atención muestra dónde se mezcló "
            "información, no por qué el modelo eligió una palabra."
        ),
        p(
            "También es habitual olvidar el escalado o aplicarlo mal. Dividir por d<sub>k</sub> en "
            "lugar de por su raíz hace que las puntuaciones sean demasiado pequeñas y que softmax "
            "quede casi uniforme. Otro error es enmascarar después de softmax sin renormalizar: "
            "los pesos restantes ya no suman uno y la mezcla de valores queda desequilibrada. Y, "
            "por último, conviene no confundir el coste de la atención con el coste total: el "
            "término n² domina en contextos largos, pero no es la única operación del bloque."
        ),
        callout(
            "tip",
            "Cómo usar el cuestionario",
            "Responde sin mirar las notas y lee la explicación de cada pregunta, aciertes o no. Un "
            "80 % indica que tienes la base; por debajo, repasa las lecciones señaladas en la "
            "tabla. Puedes repetir el quiz tantas veces como quieras: el objetivo es entender, no "
            "acertar por suerte.",
        ),
        check(
            "Escribe de memoria la fórmula de la atención escalada y señala dónde entra la máscara "
            "causal.",
            "La fórmula es softmax(QK<sup>T</sup> / √d<sub>k</sub>) · V. En un modelo causal, antes "
            "del softmax se suman −∞ a las posiciones futuras de QK<sup>T</sup> (o se sustituyen "
            "por −∞). Así su exponencial es cero, no contribuyen a la suma y la normalización "
            "reparte el peso solo entre el pasado y el presente.",
        ),
        keypoints(
            [
                "La atención proyecta X en Q, K y V, puntúa con QKᵀ, escala, enmascara y normaliza.",
                "El contexto Z es la suma ponderada de V con los pesos de atención.",
                "Los pesos de atención son dinámicos; las proyecciones son parámetros aprendidos.",
                "La máscara causal va antes de softmax y produce ceros exactos en el futuro.",
                "Multi-head reparte d_modelo entre cabezas y concatena sus salidas.",
                "El coste es n² por cabeza y capa; el contexto largo exige compromisos.",
                "El quiz del capítulo comprueba estas ideas con diez preguntas.",
            ]
        ),
    ),
    key_points=(
        "La cadena completa es proyectar, puntuar, escalar, enmascarar, normalizar y mezclar V.",
        "Los pesos de atención no son parámetros del modelo.",
        "La máscara causal actúa antes de softmax y elimina el futuro.",
        "Multi-head concatena varias cabezas y las proyecta a d_modelo.",
        "El coste cuadrático de la atención limita el contexto largo.",
    ),
    quiz_id="quiz-capitulo-3",
)
