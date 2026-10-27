"""Lección 6 · Multi-head attention."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=6,
    slug="multi-head-attention",
    title="Multi-head attention",
    summary=(
        "Una sola cabeza produce una única mezcla de relaciones. Varias cabezas miran la "
        "secuencia desde subespacios distintos y luego concatenan sus resultados."
    ),
    minutes=11,
    objectives=(
        "Explicar por qué se usan varias cabezas de atención.",
        "Describir el reparto de d_out en cabezas y la concatenación final.",
        "Calcular la dimensión por cabeza en GPT-2 y en el transformer original.",
        "Distinguir la implementación por apilamiento de la implementación fusionada.",
    ),
    blocks=(
        lead(
            "Una cabeza de atención produce una sola matriz de pesos y, por tanto, una sola forma "
            "de mezclar la secuencia. Si el modelo necesita relacionar un pronombre con su "
            "antecedente, un verbo con su sujeto y una palabra con la anterior a la vez, una única "
            "mezcla puede quedarse corta. La <strong>multi-head attention</strong> ejecuta varias "
            "cabezas en paralelo, cada una con sus propias proyecciones."
        ),
        p(
            "La idea no es repetir el mismo cálculo varias veces. Cada cabeza aprende sus propias "
            "matrices W<sub>q</sub>, W<sub>k</sub> y W<sub>v</sub>, de modo que puede especializarse "
            "en un tipo de relación o en un subespacio de la representación. Los resultados de "
            "todas las cabezas se concatenan y se pasan por una proyección de salida. El bloque "
            "sigue siendo uno: internamente, mira la secuencia desde varios ángulos."
        ),
        h2("Varias cabezas, un solo bloque"),
        p(
            "Si el modelo tiene d<sub>modelo</sub> dimensiones y h cabezas, cada cabeza trabaja con "
            "d<sub>cabeza</sub> = d<sub>modelo</sub> / h. En GPT-2 pequeño, 768 / 12 = 64. En el "
            "transformer original, 512 / 8 = 64. Cada cabeza calcula su propia atención sobre su "
            "proyección, produce un vector de contexto de 64 dimensiones y, al final, los 12 "
            "vectores se concatenan para volver a 768. Una última matriz W<sub>O</sub> mezcla la "
            "información de las cabezas."
        ),
        figure(
            "img/ch03/multi-cabeza.svg",
            "Diagrama de multi-head attention: la entrada se proyecta en varias cabezas, cada una calcula su atención, los resultados se concatenan y se proyectan a la salida.",
            "Cada cabeza tiene sus propias proyecciones Q, K y V. Sus salidas se concatenan y "
            "una proyección final las combina en el vector de contexto del bloque.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "El requisito aritmético es que d<sub>modelo</sub> sea divisible entre h. Si no lo es, "
            "no se pueden repartir las dimensiones en partes iguales. En el libro, el ejemplo "
            "didáctico usa d<sub>in</sub> = 3, d<sub>out</sub> = 2 y dos cabezas: cada cabeza "
            "trabaja con una dimensión y la concatenación devuelve dos. La implementación "
            "fusionada proyecta Q, K y V una vez y luego reorganiza el tensor para separar las "
            "cabezas; la implementación por apilamiento crea varias instancias de atención causal "
            "y las ejecuta una tras otra."
        ),
        table(
            ["Modelo", "d_modelo", "cabezas", "d por cabeza", "contexto"],
            [
                ["Transformer original", "512", "8", "64", "—"],
                ["GPT-2 pequeño", "768", "12", "64", "1024"],
                ["GPT-2 grande", "1600", "25", "64", "1024"],
            ],
            caption=(
                "La dimensión por cabeza se mantiene en 64 mientras crece el número de cabezas y "
                "la dimensión total. La concatenación reconstruye d_modelo."
            ),
            note="Datos de arquitectura citados en el libro; «contexto» es la longitud máxima de secuencia.",
        ),
        h2("Qué aprende cada cabeza"),
        p(
            "En modelos entrenados se observan cabezas que atienden a la posición anterior, a "
            "signos de puntuación, a verbos o a pronombres. Es tentador asignar a cada cabeza una "
            "etiqueta lingüística, pero la realidad es más difusa: muchas cabezas son redundantes, "
            "otras cambian de función según la capa y el contexto, y una misma tarea puede "
            "repartirse entre varias. Los estudios de interpretabilidad encuentran patrones "
            "recurrentes, no un organigrama limpio."
        ),
        p(
            "Esa especialización no se programa. Surge del entrenamiento: si varias cabezas ayudan "
            "a reducir la pérdida, el modelo aprende a usarlas. En las primeras capas suelen "
            "aparecer patrones locales y de posición; en las profundas, relaciones más abstractas. "
            "Pero un peso alto sigue siendo una pista, no una explicación completa de la "
            "predicción. La multi-head attention amplía la capacidad de representación, no la "
            "transparencia."
        ),
        h2("Coste y eficiencia"),
        p(
            "Con un presupuesto fijo de d<sub>modelo</sub>, repartir en más cabezas no multiplica "
            "sin más el coste de la atención: cada cabeza es más estrecha y la suma de sus "
            "productos se mantiene en el mismo orden. Lo que cambia es la expresividad y la "
            "dificultad de optimización. Si en lugar de fusionar las cabezas se apilan módulos "
            "independientes, se repiten proyecciones y se desaprovecha paralelismo; por eso la "
            "implementación habitual proyecta una vez, divide y procesa las cabezas en bloque."
        ),
        p(
            "La concatenación no es una suma. Cada cabeza ocupa un tramo distinto del vector final; "
            "la proyección W<sub>O</sub> decide después cómo combinarlos. Esa separación permite "
            "que una cabeza no borre lo que otra ha capturado. Si se sumaran directamente, las "
            "señales competirían en las mismas coordenadas desde el principio."
        ),
        callout(
            "info",
            "Más cabezas no significa más inteligencia",
            "El número de cabezas es un hiperparámetro, no una medida de calidad. Con d_modelo "
            "fijo, añadir cabezas reduce la dimensión de cada una. Un modelo con muchas cabezas "
            "puede ser mejor para ciertas tareas, pero también más difícil de entrenar y de "
            "interpretar. La comparación justa se hace con el mismo presupuesto de parámetros y "
            "cómputo.",
        ),
        check(
            "Un modelo tiene d_modelo = 768 y 12 cabezas. ¿Cuántas dimensiones tiene cada cabeza? "
            "¿Y si se usaran 16 cabezas?",
            "Con 12 cabezas, 768 / 12 = 64 dimensiones por cabeza. Con 16 cabezas, 768 / 16 = 48. "
            "En ambos casos el reparto es exacto porque 768 es divisible entre 12 y 16. Si la "
            "división no fuera entera, la arquitectura tendría que ajustar d_modelo o el número de "
            "cabezas.",
        ),
        keypoints(
            [
                "Multi-head ejecuta varias atenciones en paralelo con proyecciones distintas.",
                "Cada cabeza produce un vector de contexto de dimensión d_modelo / h.",
                "Las salidas se concatenan y se combinan con una proyección de salida.",
                "GPT-2 pequeño usa 12 cabezas de 64 dimensiones sobre un total de 768.",
                "La especialización de las cabezas emerge del entrenamiento y no es un organigrama fijo.",
                "La implementación fusionada proyecta una vez y divide el tensor; es más eficiente que apilar módulos.",
            ]
        ),
    ),
    key_points=(
        "Multi-head attention reparte d_modelo entre varias cabezas.",
        "Cada cabeza aprende sus propias proyecciones Q, K y V.",
        "Las salidas se concatenan y se proyectan con W_O.",
        "GPT-2 pequeño: 768 dimensiones, 12 cabezas, 64 por cabeza.",
        "Las cabezas pueden especializarse, pero su interpretación no es automática.",
    ),
)
