"""Lección 3 · Consultas, claves y valores."""

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
    table,
)

LESSON = Lesson(
    number=3,
    slug="consultas-claves-valores",
    title="Consultas, claves y valores",
    summary=(
        "Q, K y V son tres proyecciones aprendidas del mismo token: lo que busca, lo que "
        "ofrece y lo que aporta. La atención es una búsqueda blanda entre ellas."
    ),
    minutes=12,
    objectives=(
        "Distinguir los papeles de query, key y value.",
        "Explicar cómo las proyecciones Wq, Wk y Wv transforman los embeddings.",
        "Seguir el cálculo de puntuaciones y pesos con dimensiones concretas.",
        "Relacionar las dimensiones de GPT-2 con el reparto por cabezas.",
    ),
    blocks=(
        lead(
            "Los nombres <strong>query</strong>, <strong>key</strong> y <strong>value</strong> "
            "vienen de las bases de datos y de los sistemas de recuperación de información. "
            "Imagina una biblioteca: formulas una consulta, buscas claves que encajen con ella y "
            "te llevas los valores asociados. La atención hace algo parecido, pero en lugar de "
            "elegir una ficha, mezcla todas con un peso."
        ),
        p(
            "Cada token de la entrada se proyecta en tres vectores distintos mediante tres "
            "matrices aprendidas. La consulta (<em>query</em>, q) representa lo que ese token "
            "busca; la clave (<em>key</em>, k), lo que ofrece a los demás; el valor "
            "(<em>value</em>, v), el contenido que aporta si se le presta atención. Las tres "
            "proyecciones salen del mismo embedding, pero no son intercambiables: cumplen "
            "funciones distintas y se entrenan por separado."
        ),
        h2("Tres proyecciones, tres papeles"),
        p(
            "Si la entrada es una matriz X con una fila por token, las proyecciones se escriben "
            "Q = X · W<sub>q</sub>, K = X · W<sub>k</sub> y V = X · W<sub>v</sub>. Cada matriz "
            "tiene forma d<sub>entrada</sub> × d<sub>salida</sub>. En los transformers modernos, "
            "la dimensión de entrada y la de salida suelen coincidir —GPT-2 pequeño usa 768—, "
            "aunque en los ejemplos didácticos se reducen para poder seguir las cuentas. La "
            "dimensión de las claves, d<sub>k</sub>, será la que aparezca en el escalado de la "
            "lección 4."
        ),
        figure(
            "img/ch03/qkv.svg",
            "Diagrama de las proyecciones Q, K y V a partir de un token, seguidas del cálculo de puntuaciones, softmax y suma ponderada de valores.",
            "Un mismo token se proyecta en consulta, clave y valor. La consulta se compara con "
            "todas las claves; los pesos resultantes mezclan los valores.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        lab("qkv"),
        h2("Una búsqueda blanda"),
        p(
            "Con Q y K se calculan las puntuaciones: cada consulta se compara con todas las "
            "claves mediante un producto escalar. Esas puntuaciones se normalizan con softmax y "
            "producen los pesos de atención. Finalmente, el vector de contexto es la suma "
            "ponderada de los valores V. La diferencia con una base de datos es que no hay una "
            "coincidencia exacta: todos los valores contribuyen, unos más que otros. Esa "
            "suavidad es lo que permite entrenar el mecanismo con descenso de gradiente."
        ),
        p(
            "Un ejemplo con una consulta de cuatro dimensiones: q = [0,8, 0,2, −0,4, 0,6]. "
            "Frente a tres claves, los productos escalares son 0,50, 0,16 y 0,28. Al dividir por "
            "√4 = 2 quedan 0,25, 0,08 y 0,14; tras softmax, los pesos son aproximadamente 0,365, "
            "0,308 y 0,327. La primera clave es la más afín, pero las otras dos conservan un peso "
            "considerable. Si los valores asociados fueran v<sub>1</sub>, v<sub>2</sub> y "
            "v<sub>3</sub>, el contexto sería 0,365 v<sub>1</sub> + 0,308 v<sub>2</sub> + 0,327 "
            "v<sub>3</sub>. Los valores son un ejemplo propio para seguir la aritmética."
        ),
        p(
            "¿Por qué no usar directamente los embeddings como consultas y claves? Porque el "
            "modelo necesita aprender una relación asimétrica. Lo que un token busca no tiene por "
            "qué coincidir con lo que ofrece. Al proyectar en subespacios distintos, la red puede "
            "especializar una dirección para «busco un sujeto» y otra para «ofrezco un sujeto», "
            "aunque el embedding original sea el mismo. Las matrices W<sub>q</sub>, "
            "W<sub>k</sub> y W<sub>v</sub> son parámetros: se ajustan durante el entrenamiento y "
            "no se escriben a mano."
        ),
        h2("Dimensiones que importan"),
        p(
            "En el transformer original, el modelo base tenía 512 dimensiones y 8 cabezas; cada "
            "cabeza trabajaba con 64 dimensiones. GPT-2 pequeño tiene 768 dimensiones, 12 cabezas "
            "y una ventana de 1024 tokens; GPT-2 grande, 1600 dimensiones y 25 cabezas. En todos "
            "estos casos, la dimensión por cabeza es 64. Esa coincidencia no es casual: el diseño "
            "reparte un presupuesto fijo de dimensiones entre varias cabezas para que cada una "
            "pueda especializarse sin multiplicar el coste por el número de cabezas."
        ),
        table(
            ["Modelo", "dimensión del modelo", "cabezas", "dimensión por cabeza"],
            [
                ["Juguete del libro", "3 → 2", "1", "2"],
                ["Transformer original", "512", "8", "64"],
                ["GPT-2 pequeño", "768", "12", "64"],
                ["GPT-2 grande", "1600", "25", "64"],
            ],
            caption=(
                "El presupuesto de dimensiones se reparte entre las cabezas. En GPT-2, la "
                "dimensión total es mucho mayor que en el transformer original, pero la dimensión "
                "por cabeza se mantiene en 64."
            ),
            note="Datos de arquitectura citados en el libro; el ejemplo del juguete usa d_in = 3 y d_out = 2.",
        ),
        callout(
            "info",
            "Las proyecciones no son diccionarios",
            "W<sub>q</sub>, W<sub>k</sub> y W<sub>v</sub> no contienen definiciones ni reglas "
            "simbólicas. Son matrices de números que se ajustan para minimizar la pérdida de la "
            "tarea. Que una dirección acabe correlacionando con una función lingüística es un "
            "efecto emergente del entrenamiento, no una instrucción que hayamos escrito.",
        ),
        check(
            "¿Por qué la atención usa tres matrices distintas en lugar de comparar los embeddings "
            "originales entre sí?",
            "Porque consulta, clave y valor cumplen papeles diferentes. La consulta expresa qué "
            "busca el token actual; la clave, qué ofrece cada token candidato; el valor, qué "
            "contenido se mezcla. Con tres proyecciones aprendidas, el modelo puede especializar "
            "cada papel en un subespacio y romper la simetría de comparar un vector consigo mismo.",
        ),
        keypoints(
            [
                "Cada token se proyecta en una consulta, una clave y un valor.",
                "La consulta se compara con todas las claves para obtener puntuaciones.",
                "Softmax convierte las puntuaciones en pesos que suman uno.",
                "El contexto es la suma ponderada de los valores.",
                "Las proyecciones son parámetros aprendidos; los pesos de atención son dinámicos.",
                "GPT-2 pequeño usa 768 dimensiones, 12 cabezas y 64 dimensiones por cabeza.",
            ]
        ),
    ),
    key_points=(
        "Query, key y value son tres proyecciones aprendidas del mismo token.",
        "La consulta busca, la clave ofrece y el valor aporta contenido.",
        "La atención es una búsqueda blanda: todos los valores contribuyen con algún peso.",
        "Las dimensiones por cabeza reparten el presupuesto del modelo.",
        "GPT-2 pequeño: 768 dimensiones, 12 cabezas, 64 por cabeza.",
    ),
)
