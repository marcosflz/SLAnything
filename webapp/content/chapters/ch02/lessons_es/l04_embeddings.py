"""Lección 4 · Del token al vector."""

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
    number=4,
    slug="vocabulario-y-embeddings",
    title="Del token al vector",
    summary=(
        "Un identificador no tiene geometría. Para que la red pueda operar, cada token se "
        "convierte en una fila de una matriz: su embedding. Aquí calculamos cuántas filas, "
        "cuántas columnas y cuántos parámetros implica."
    ),
    minutes=11,
    objectives=(
        "Explicar por qué los IDs no bastan como entrada de una red.",
        "Describir una matriz de embeddings como tabla de consulta.",
        "Comparar one-hot con una representación densa.",
        "Calcular los parámetros de una capa de embeddings.",
    ),
    blocks=(
        lead(
            "Ya sabemos convertir texto en números enteros. Pero un entero es una etiqueta, "
            "no una posición en un espacio. La red necesita vectores densos y aprendibles. La "
            "capa que hace esa conversión es la <strong>capa de embeddings</strong>, y su "
            "tamaño condiciona la memoria y la capacidad del modelo."
        ),
        p(
            "Imagina un vocabulario de seis tokens y vectores de tres dimensiones. La capa de "
            "embeddings es una matriz de 6 × 3: una fila por token, una columna por dimensión. "
            "El token con ID 3 devuelve la cuarta fila —recordemos que Python empieza a contar "
            "en cero—. No hay una operación misteriosa: es una consulta a una tabla. Esa tabla "
            "se inicializa con valores pequeños y se optimiza durante el entrenamiento."
        ),
        p(
            "En el libro, el ejemplo mínimo usa exactamente eso: <code>vocab_size = 6</code> y "
            "<code>output_dim = 3</code>. Al pasar el ID 3 por la capa, se obtiene "
            "<code>[-0.4015, 0.9666, -1.1481]</code>, que coincide con la cuarta fila de la "
            "matriz. Pasar cuatro IDs a la vez devuelve una matriz de 4 × 3. La forma de salida "
            "añade una dimensión al lote: si entra un tensor de forma <code>(batch, contexto)</code>, "
            "sale un tensor <code>(batch, contexto, dimensión)</code>."
        ),
        h2("One-hot frente a denso"),
        p(
            "Una alternativa clásica es el <strong>one-hot</strong>: un vector de longitud igual "
            "al vocabulario, con un 1 en la posición del token y ceros en el resto. Para un "
            "vocabulario de 50 257, cada token ocuparía un vector de 50 257 números, casi todos "
            "ceros. Multiplicar ese vector por una matriz de pesos produce precisamente la fila "
            "correspondiente. La capa de embeddings hace lo mismo sin construir el vector "
            "disperso: selecciona la fila directamente. Es una optimización de implementación, "
            "no un cambio conceptual."
        ),
        p(
            "La representación densa tiene otra ventaja: cada dimensión puede especializarse en "
            "un aspecto aprendido. No hay que interpretar cada columna como «género» o "
            "«número»; en la práctica las direcciones son combinaciones y su significado se "
            "descubre a posteriori. Lo importante es que el vector completo se actualiza con "
            "gradientes y puede codificar regularidades del contexto."
        ),
        table(
            ["Modelo", "Vocabulario", "Dimensión", "Parámetros de la matriz", "Cálculo"],
            [
                ["Juguete del libro", "6", "3", "18", "6 × 3"],
                ["GPT-2 small", "50 257", "768", "38 597 376", "50 257 × 768"],
                ["GPT-3 175B", "50 257", "12 288", "617 558 016", "50 257 × 12 288"],
            ],
            caption=(
                "Parámetros de una sola matriz de tokens. Los modelos reales añaden embeddings "
                "posicionales y muchas otras capas."
            ),
            note=(
                "GPT-2 small y GPT-3 son cifras citadas en el libro para vocabulario y dimensión. "
                "Los productos son aritmética nuestra para mostrar el orden de magnitud; no "
                "incluyen sesgos ni positional embeddings."
            ),
        ),
        callout(
            "info",
            "Una matriz que se aprende",
            "Al inicializar, las filas son ruido. Después del entrenamiento, tokens que aparecen "
            "en contextos parecidos tienden a tener vectores parecidos. La semejanza no está "
            "programada: emerge de minimizar la pérdida de predicción.",
        ),
        p(
            "El número de parámetros de la matriz es <code>V × d</code>, donde <code>V</code> es "
            "el tamaño del vocabulario y <code>d</code> la dimensión. Duplicar la dimensión "
            "duplica los parámetros de esta capa; duplicar el vocabulario, también. En modelos "
            "grandes, la matriz de embeddings puede tener cientos de millones de parámetros, "
            "aunque sigue siendo una fracción del total. En GPT-3, por ejemplo, 617 millones "
            "frente a 175 000 millones de parámetros del modelo completo."
        ),
        p(
            "Hay una sutileza que conviene anticipar: la misma palabra recibe el mismo vector "
            "en cualquier posición. La capa de embeddings no sabe si «gato» es la primera o la "
            "última palabra. Esa información se añade después con embeddings posicionales, que "
            "veremos al final del capítulo. Primero necesitamos construir las secuencias de "
            "entrenamiento; de eso se ocupan las dos próximas lecciones."
        ),
        check(
            "Un vocabulario tiene 10 000 tokens y la dimensión es 128. ¿Cuántos parámetros tiene la matriz de embeddings?",
            "10 000 × 128 = 1 280 000 parámetros. Si además hay sesgos, se añaden 10 000; si hay "
            "embeddings posicionales, otra matriz aparte. La cuenta básica es siempre "
            "vocabulario × dimensión.",
        ),
        h2("Por qué esta capa importa"),
        p(
            "La matriz de embeddings es la primera representación del lenguaje dentro del "
            "modelo. Todo lo que ocurre después —atención, feed-forward, capas residuales— "
            "opera sobre estos vectores. Si el vocabulario está mal construido, la matriz "
            "dedica filas a tokens raros y deja pocos datos para los frecuentes. Si la "
            "dimensión es demasiado pequeña, el modelo no tiene espacio para distinguir "
            "matices; si es demasiado grande, paga memoria y cómputo sin garantía de mejora."
        ),
        p(
            "En los modelos GPT, la dimensión de los embeddings coincide con la dimensión oculta "
            "del transformer. GPT-2 small usa 768; GPT-3, 12 288. Esta coincidencia no es "
            "casual: permite que la salida de la capa de embeddings entre directamente en las "
            "capas de atención sin una proyección adicional. Es una decisión de arquitectura "
            "que se mantiene en la familia."
        ),
        keypoints(
            [
                "Un ID es una etiqueta; un embedding es un vector denso y aprendible.",
                "La capa de embeddings es una consulta a una matriz de V × d.",
                "One-hot más multiplicación equivale a seleccionar una fila.",
                "Los parámetros de la matriz son vocabulario × dimensión.",
                "La dimensión coincide con la dimensión oculta del transformer en GPT.",
                "Cada token recibe el mismo vector en cualquier posición; la posición se añade aparte.",
            ]
        ),
    ),
    key_points=(
        "La capa de embeddings transforma cada ID en una fila de una matriz V × d.",
        "Es equivalente a un one-hot seguido de una multiplicación, pero más eficiente.",
        "Sus parámetros se calculan como vocabulario × dimensión.",
        "Los vectores se aprenden y no contienen posición por sí mismos.",
    ),
    quiz_id=None,
)
