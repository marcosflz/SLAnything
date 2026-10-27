"""Lección 7 · De vectores a tokens."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
)

LESSON = Lesson(
    number=7,
    slug="cabeza-de-salida",
    title="De vectores a tokens",
    summary=(
        "Cómo la cabeza de salida convierte 768 dimensiones en 50 257 logits, cómo "
        "softmax los transforma en probabilidades y cuánta memoria ahorran los pesos atados."
    ),
    minutes=10,
    objectives=(
        "Seguir el paso de un vector contextual a un vector de logits.",
        "Explicar qué hace softmax y por qué se puede elegir con argmax.",
        "Calcular el coste de la cabeza de salida y el efecto de atar pesos.",
        "Relacionar la arquitectura con la memoria de inferencia y entrenamiento.",
    ),
    blocks=(
        lead(
            "El último bloque devuelve un vector contextual por cada posición, pero el "
            "modelo todavía no ha dicho qué token viene después. Para eso necesita una "
            "cabeza de salida: una capa lineal que proyecta 768 dimensiones al tamaño del "
            "vocabulario y produce una puntuación por cada token posible. Es el paso que "
            "convierte geometría en lenguaje."
        ),
        h2("Logits y softmax"),
        p(
            "La cabeza de salida es una matriz de 768 × 50 257, sin sesgo en GPT-2. Si la "
            "entrada es un lote de dos secuencias de cuatro tokens, la salida tiene forma "
            "<code>[2, 4, 50 257]</code>: una puntuación por posición y por token del "
            "vocabulario. Esas puntuaciones se llaman <strong>logits</strong> y no son "
            "probabilidades; pueden ser negativas, positivas y no suman nada. Para generar "
            "el siguiente token solo se usa la última posición de la secuencia."
        ),
        figure(
            "img/ch04/cabeza-de-salida.svg",
            "Recorrido desde un vector contextual de 768 dimensiones hasta los logits de 50 257, el softmax y el token elegido.",
            "La proyección final comparte su matriz con los embeddings de tokens cuando "
            "se atan los pesos; softmax convierte los logits en una distribución.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "Softmax convierte el vector de logits en una distribución de probabilidad "
            "positiva que suma 1. Lo hace calculando la exponencial de cada logit y "
            "dividiéndola por la suma de todas. Es una función monótona: conserva el orden, "
            "así que el token con el logit más alto sigue siendo el más probable después "
            "del softmax. Por eso la generación voraz —elegir siempre el máximo— puede "
            "aplicar <code>argmax</code> directamente a los logits y obtener el mismo "
            "resultado. El softmax sigue siendo útil para ver la confianza y para técnicas "
            "de muestreo como la temperatura o el top-k."
        ),
        h2("Pesos atados y memoria"),
        p(
            "La cabeza de salida tiene 50 257 × 768 = 38 597 376 parámetros, exactamente la "
            "misma forma que la tabla de embeddings de tokens. Atar los pesos significa "
            "usar una sola matriz para ambas funciones. El modelo pasa de 163 009 536 "
            "parámetros a 124 412 160, y ahorra 38,6 M de pesos. La idea tiene sentido: "
            "cada fila de la matriz representa un token, y esa representación puede servir "
            "tanto para leerlo como para puntuarlo. El libro implementa primero la cabeza "
            "separada y deja la compartición para el capítulo 6, cuando carga los pesos de "
            "GPT-2."
        ),
        p(
            "La memoria no termina en los pesos. En inferencia hay que sumar la caché de "
            "claves y valores, que crece con la longitud del contexto y con el número de "
            "capas. En entrenamiento hay que sumar gradientes y estados del optimizador; "
            "con Adam en fp32, una regla habitual es reservar unos 16 bytes por parámetro, "
            "además de las activaciones. El laboratorio de memoria permite cambiar de "
            "modelo, precisión y ventana de contexto para ver cómo cambian las cifras. Son "
            "estimaciones de orden de magnitud, no un presupuesto de hardware."
        ),
        lab("memory"),
        p(
            "El libro calcula que los 163 009 536 parámetros del modelo sin atar ocupan "
            "621,83 MB en coma flotante de 32 bits. Es una cantidad manejable para un "
            "portátil moderno, pero ya muestra que incluso un GPT pequeño es un objeto "
            "grande. La arquitectura es compacta; el tamaño viene de repetir bloques y de "
            "multiplicar por un vocabulario de 50 257. Esa relación entre forma, parámetros "
            "y memoria es la que permite comparar modelos de 124 M, 345 M, 762 M o 1 542 M "
            "sin cambiar la estructura del código."
        ),
        callout(
            "warning",
            "La arquitectura no es el entrenamiento",
            "Un GPT con pesos aleatorios produce logits, probabilidades y tokens, pero no "
            "texto coherente. El libro lo muestra con «Hello, I am»: la salida es una "
            "secuencia sin sentido porque el modelo aún no ha aprendido nada. La cabeza de "
            "salida completa el circuito; el pretraining es lo que llena los pesos de "
            "información útil.",
        ),
        check(
            "¿Por qué se puede usar argmax sobre los logits sin calcular softmax primero?",
            "Porque softmax es una función monótona: si un logit es mayor que otro, su "
            "exponencial también lo es, y la normalización divide a todos por la misma "
            "suma. El orden no cambia. Para elegir el token más probable, argmax sobre los "
            "logits da el mismo índice; softmax se usa cuando se necesita una "
            "distribución, no solo el ganador.",
        ),
        keypoints(
            [
                "La cabeza de salida proyecta cada vector de 768 dimensiones al vocabulario.",
                "La salida tiene forma [batch, tokens, 50 257] y contiene logits sin normalizar.",
                "Softmax convierte los logits en probabilidades que suman 1.",
                "La generación voraz elige el logit máximo; el orden se conserva.",
                "Atar pesos reutiliza la matriz de embeddings y ahorra 38,6 M de parámetros.",
                "La memoria real incluye pesos, caché KV y, al entrenar, gradientes y optimizador.",
            ]
        ),
    ),
    key_points=(
        "La cabeza de salida es una proyección lineal de 768 a 50 257.",
        "Los logits son puntuaciones sin normalizar, una por token del vocabulario.",
        "Softmax los convierte en una distribución de probabilidad.",
        "El token más probable se puede elegir con argmax sobre los logits.",
        "Los pesos atados reducen el modelo de 163 M a 124 M de parámetros.",
        "Inferencia y entrenamiento añaden memoria más allá de los pesos.",
    ),
)
