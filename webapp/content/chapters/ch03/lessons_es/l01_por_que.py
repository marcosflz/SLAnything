"""Lección 1 · El problema de la memoria fija."""

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
    slug="por-que-atencion",
    title="El problema de la memoria fija",
    summary=(
        "Antes de la atención, un encoder comprimía toda la frase en un único vector. "
        "Ese cuello de botella explica por qué nacieron los mecanismos de atención."
    ),
    minutes=10,
    objectives=(
        "Explicar por qué una traducción palabra a palabra no funciona.",
        "Describir el cuello de botella de un encoder-decoder recurrente.",
        "Entender la atención como un acceso selectivo a la entrada, no como memoria infinita.",
        "Situar la self-attention en el transformer de 2017.",
    ),
    blocks=(
        lead(
            "Traducir no es sustituir palabras. El orden de los verbos, los pronombres y las "
            "concordancias cambian de una lengua a otra, y una palabra solo se entiende dentro "
            "de la frase. Los primeros modelos neuronales de traducción intentaron resolverlo "
            "comprimiendo toda la entrada en un vector; la atención nació para romper ese "
            "cuello de botella."
        ),
        p(
            "Imagina que quieres traducir una frase alemana al inglés. En alemán, el verbo "
            "principal puede aparecer al final; en inglés, lo esperamos antes del objeto. Si "
            "traduces de izquierda a derecha palabra por palabra, cuando llegas al verbo ya has "
            "tomado decisiones que quizá debas deshacer. La solución clásica fue un "
            "<strong>encoder-decoder</strong>: una red lee la frase completa, la resume y otra "
            "red genera la traducción a partir de ese resumen. Antes de los transformers, la "
            "arquitectura habitual para hacerlo era una red recurrente (RNN)."
        ),
        p(
            "Una RNN procesa la secuencia paso a paso y actualiza un <strong>estado oculto</strong> "
            "en cada palabra. Al terminar, ese estado contiene, en teoría, el significado de toda "
            "la entrada. El decoder recibe ese único vector y empieza a generar. El problema es "
            "evidente: la frase entera cabe en un espacio de tamaño fijo. Cuanto más larga y "
            "compleja es la entrada, más información compite por el mismo puñado de números. Los "
            "detalles de las primeras palabras se diluyen y las dependencias largas se pierden."
        ),
        h2("Un estado oculto no es una memoria infinita"),
        p(
            "El cuello de botella es una consecuencia del diseño. El decoder no puede volver a "
            "diseño. El decoder no puede volver a consultar la entrada original; solo tiene el "
            "resumen que le pasa el encoder. Si la frase es «El abogado que representaba a la "
            "empresa que compró el edificio llegó tarde», la relación entre «abogado» y «tarde» "
            "atraviesa varias proposiciones. Un vector fijo puede conservar el tema general, pero "
            "no garantiza conservar cada vínculo relevante. Además, el entrenamiento de las RNN "
            "se vuelve difícil cuando las dependencias son muy largas: el gradiente tiene que "
            "atravesar muchos pasos y tiende a desvanecerse o a explotar."
        ),
        p(
            "Se probaron estados más grandes, compuertas y resúmenes intermedios, pero todos "
            "seguían obligando a comprimir. La pregunta que abrió otra vía fue: ¿y si el decoder "
            "pudiera mirar directamente la entrada? No hace falta copiar toda la frase en cada "
            "paso; basta con decidir qué partes son relevantes para la palabra que se está "
            "generando."
        ),
        h2("Atención: mirar sin comprimir"),
        p(
            "En 2014, el mecanismo de Bahdanau introdujo esa idea en la traducción neuronal. En "
            "cada paso de generación, el decoder calcula una puntuación para cada posición de la "
            "entrada y reparte su atención entre ellas. Las posiciones más útiles reciben más "
            "peso; las demás, menos. El resultado es un vector de contexto que se recalcula en "
            "cada paso y que puede combinar información de varias palabras a la vez. Esto es "
            "especialmente valioso para la <strong>alineación</strong>: al traducir, el modelo "
            "puede relacionar una palabra de salida con una o varias palabras de entrada aunque "
            "no ocupen la misma posición."
        ),
        p(
            "Conviene precisar qué significa «mirar». La atención no es una base de datos ni una "
            "memoria perfecta. Es una operación matemática: se comparan representaciones, se "
            "obtienen pesos que suman uno y se mezclan contenidos. Esa mezcla es blanda, "
            "diferenciable y se aprende con el resto de la red; no hay reglas simbólicas ni un "
            "puntero explícito."
        ),
        table(
            ["Aspecto", "Encoder-decoder recurrente", "Atención en el transformer"],
            [
                [
                    "Acceso a la entrada",
                    "El decoder recibe un estado oculto final.",
                    "Cada posición puede consultar las demás en cada capa.",
                ],
                [
                    "Dependencias largas",
                    "Deben sobrevivir comprimidas en un vector.",
                    "Se modelan con conexiones directas y pesos.",
                ],
                [
                    "Paralelización",
                    "Limitada por la recurrencia paso a paso.",
                    "Las posiciones se procesan en paralelo durante el entrenamiento.",
                ],
            ],
            caption=(
                "El cambio no fue solo de precisión: la atención elimina la necesidad de "
                "comprimir toda la entrada antes de generar."
            ),
            note="Comparación conceptual.",
        ),
        h2("Del RNN al transformer"),
        p(
            "El transformer de 2017 llevó la idea al extremo: eliminó la recurrencia y organizó "
            "el modelo alrededor de la <strong>self-attention</strong>. Cada token de una "
            "secuencia se relaciona con los demás tokens de esa misma secuencia. El transformer "
            "original mantenía un encoder y un decoder; GPT conserva solo el decoder y lo apila "
            "en muchas capas. Esa decisión encaja con la tarea generativa: predecir el siguiente "
            "token mirando únicamente el pasado."
        ),
        p(
            "La atención también tiene un precio. Comparar cada token con cada token produce una "
            "matriz de tamaño n × n, y ese coste crece con el cuadrado de la longitud. Por eso "
            "una ventana de contexto no es gratuita y por eso existen kernels eficientes y "
            "técnicas de caché. La atención resuelve el cuello de botella del resumen fijo, pero "
            "no elimina los límites del contexto: los desplaza."
        ),
        callout(
            "warning",
            "Más contexto no significa comprenderlo todo",
            "La atención permite consultar posiciones anteriores, pero el modelo sigue teniendo "
            "una ventana máxima y un coste que crece con la longitud. Además, un peso alto no es "
            "una explicación causal de la decisión: es una pista sobre dónde se mezcló "
            "información. La interpretabilidad de la atención es útil, pero no automática.",
        ),
        check(
            "¿Por qué un encoder-decoder recurrente pierde información en frases largas?",
            "Porque el decoder solo recibe el estado oculto final, un vector de tamaño fijo que "
            "debe resumir toda la entrada. Al aumentar la longitud, más información compite por "
            "el mismo espacio y las dependencias lejanas pueden quedar diluidas. La atención "
            "evita ese paso obligatorio al permitir consultar directamente las posiciones de la "
            "entrada.",
        ),
        keypoints(
            [
                "Un encoder-decoder recurrente comprime toda la entrada en un vector fijo.",
                "Ese cuello de botella pierde dependencias largas y dificulta el entrenamiento.",
                "La atención de Bahdanau permitió al decoder consultar selectivamente la entrada.",
                "La self-attention relaciona cada token con los demás de la misma secuencia.",
                "La atención reduce el problema del resumen, pero mantiene límites de contexto y coste.",
            ]
        ),
    ),
    key_points=(
        "El estado oculto fijo motivó la atención.",
        "La atención reparte pesos y construye contexto.",
        "La self-attention compara posiciones de una misma secuencia.",
        "El transformer eliminó la recurrencia y paralelizó el entrenamiento.",
        "Hay ventana de contexto y coste cuadrático.",
    ),
)
