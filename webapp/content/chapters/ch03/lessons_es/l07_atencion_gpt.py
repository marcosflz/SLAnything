"""Lección 7 · La atención dentro de GPT."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lab,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=7,
    slug="atencion-en-gpt",
    title="La atención dentro de GPT",
    summary=(
        "GPT apila bloques decoder-only con atención causal, normalización y feed-forward. "
        "Ese orden explica tanto su capacidad como su coste cuadrático."
    ),
    minutes=10,
    objectives=(
        "Situar la atención causal dentro de un bloque decoder-only.",
        "Describir el orden de normalización, atención, residual y feed-forward.",
        "Explicar por qué la atención cuesta O(n²) por capa y cabeza.",
        "Calcular el número de puntuaciones de atención para una longitud y un número de cabezas.",
    ),
    blocks=(
        lead(
            "En el capítulo anterior, la atención era un módulo aislado. En GPT es una pieza "
            "dentro de un bloque que se repite docenas de veces. Entender dónde se coloca —y qué "
            "ocurre antes y después— aclara por qué el modelo puede generar texto y por qué el "
            "contexto largo es caro."
        ),
        p(
            "GPT es <strong>decoder-only</strong>: no tiene un encoder separado ni atención "
            "cruzada sobre otra secuencia. Cada bloque procesa la misma secuencia que recibe. "
            "Primero normaliza las representaciones; después aplica multi-head attention con "
            "máscara causal; suma la entrada original mediante una conexión residual; vuelve a "
            "normalizar; pasa por una red feed-forward posición a posición; y suma otra vez. GPT-2 "
            "pequeño apila 12 de estos bloques y tiene 117 millones de parámetros."
        ),
        h2("El bloque decoder-only"),
        p(
            "El orden exacto varía entre familias. GPT-2 usa <strong>pre-normalización</strong>: "
            "LayerNorm va antes de la atención y antes del feed-forward, y la conexión residual "
            "rodea cada subcapa. El transformer original usaba post-normalización: la suma "
            "residual se hacía primero y la normalización después. La pre-normalización facilita "
            "el entrenamiento de pilas profundas porque mantiene estable la escala de las "
            "activaciones que entran en cada subcapa."
        ),
        p(
            "La atención es la única operación del bloque que mezcla información entre posiciones. "
            "El feed-forward se aplica a cada token por separado y transforma su representación, "
            "pero no la combina con las demás. Las conexiones residuales permiten que la "
            "información original llegue intacta a capas posteriores y que el gradiente encuentre "
            "un camino directo hacia atrás. Sin ellas, apilar 12 o 96 bloques sería mucho más "
            "difícil."
        ),
        lab("transformer"),
        h2("De la capa a la predicción"),
        p(
            "Tras el último bloque, una normalización final prepara las representaciones y una "
            "cabeza lineal las proyecta al tamaño del vocabulario. Esas puntuaciones son los "
            "<strong>logits</strong>; softmax las convierte en una distribución sobre el siguiente "
            "token. El modelo no elige la palabra directamente: produce una distribución y el "
            "proceso de muestreo decide cómo usarla. Durante el entrenamiento, la pérdida compara "
            "esa distribución con el token que realmente seguía en el corpus."
        ),
        p(
            "En inferencia, generar un token cada vez parece un desperdicio: si ya hemos procesado "
            "el prompt, ¿por qué recalcular todo para el siguiente token? La respuesta es la "
            "<strong>caché de claves y valores</strong>. Las representaciones K y V de las "
            "posiciones anteriores no cambian cuando añadimos un token al final, así que se "
            "guardan. El nuevo token calcula su consulta y añade su clave y valor a la caché; la "
            "atención se hace sobre lo almacenado. Eso reduce el trabajo por paso, aunque la "
            "atención sigue comparando con todas las posiciones."
        ),
        h2("El precio de mirar"),
        p(
            "Para una secuencia de n tokens, cada cabeza construye una matriz de n × n "
            "puntuaciones: cada posición se compara con cada posición. Esa matriz se normaliza y "
            "se usa para mezclar los valores. El coste de la atención crece con n², y la memoria "
            "necesaria para materializar la matriz también. En un modelo con h cabezas y L capas, "
            "el número de puntuaciones por capa es h · n²; a lo largo de todas las capas, L · h · "
            "n²."
        ),
        table(
            ["Longitud n", "Puntuaciones por cabeza", "12 cabezas, una capa", "Aprox."],
            [
                ["128", "16 384", "196 608", "0,2 M"],
                ["1024", "1 048 576", "12 582 912", "12,6 M"],
                ["4096", "16 777 216", "201 326 592", "201 M"],
                ["8192", "67 108 864", "805 306 368", "805 M"],
            ],
            caption=(
                "Puntuaciones de atención para una capa con 12 cabezas. Duplicar la longitud "
                "multiplica por cuatro el número de comparaciones."
            ),
            note="Cálculo propio: n² puntuaciones por cabeza, multiplicado por 12 cabezas.",
        ),
        p(
            "Con 1024 tokens —la ventana de GPT-2— y 12 cabezas, una sola capa genera unos 12,6 "
            "millones de puntuaciones. Con 4096 tokens, unos 201 millones. La diferencia no es "
            "lineal: duplicar la longitud multiplica por cuatro el trabajo de atención. Por eso los "
            "modelos con contextos muy largos necesitan técnicas de atención eficiente, "
            "paralelismo y memoria adicional. Algunos kernels reducen el uso de memoria sin cambiar "
            "el orden asintótico; otros métodos aproximan o reorganizan el cálculo."
        ),
        p(
            "Conviene no confundir el coste de la atención con el coste total del modelo. Las "
            "proyecciones Q, K y V, el feed-forward y la cabeza de salida también cuestan, y en "
            "secuencias cortas pueden dominar. La atención se vuelve el cuello de botella cuando n "
            "crece, porque su término cuadrático acaba imponiéndose. Esa es la razón práctica por "
            "la que la longitud del contexto es un recurso caro, no un número arbitrario."
        ),
        callout(
            "warning",
            "O(n²) es por capa y por cabeza",
            "El coste cuadrático no se refiere al modelo entero como una sola operación. Se aplica "
            "a la matriz de atención de cada cabeza en cada capa. Un modelo con 12 capas y 12 "
            "cabezas repite ese patrón 144 veces por secuencia. La notación O(n²) describe el "
            "crecimiento, no el número absoluto de operaciones.",
        ),
        check(
            "¿Cuántas puntuaciones de atención genera una capa con 12 cabezas para 1024 tokens? "
            "¿Por qué no basta con multiplicar 1024 por 12?",
            "Genera 12 × 1024² = 12 582 912 puntuaciones, es decir, unos 12,6 millones. No basta "
            "con 1024 × 12 porque cada token se compara con todos los tokens, no solo con uno: hay "
            "1024 × 1024 pares por cabeza, y luego se multiplica por las 12 cabezas.",
        ),
        keypoints(
            [
                "GPT es decoder-only: cada bloque procesa la misma secuencia con atención causal.",
                "GPT-2 pequeño apila 12 bloques, usa 12 cabezas de 64 dimensiones y tiene 117 M de parámetros.",
                "La atención mezcla posiciones; el feed-forward transforma cada token por separado.",
                "Las conexiones residuales y la normalización hacen viable apilar muchos bloques.",
                "La atención cuesta O(n²) por capa y cabeza: n tokens producen n² puntuaciones.",
                "La caché de claves y valores acelera la generación, pero no elimina el coste cuadrático del entrenamiento.",
            ]
        ),
    ),
    key_points=(
        "La atención causal vive dentro de un bloque decoder-only con residuales y feed-forward.",
        "GPT-2 pequeño: 12 capas, 12 cabezas, 768 dimensiones, 117 M de parámetros.",
        "La última representación se proyecta al vocabulario y se normaliza con softmax.",
        "La atención produce n² puntuaciones por cabeza y capa.",
        "La caché KV acelera la inferencia; el coste de entrenamiento sigue siendo cuadrático.",
    ),
)
