"""Lección 5 · La ventana deslizante."""

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
    number=5,
    slug="ventana-deslizante",
    title="La ventana deslizante",
    summary=(
        "El corpus tokenizado es una secuencia larga; el modelo entrena con fragmentos de "
        "longitud fija. La ventana deslizante decide cuánto contexto ve cada ejemplo y "
        "cuánto se solapan unos con otros."
    ),
    minutes=10,
    objectives=(
        "Explicar por qué el entrenamiento usa ventanas de longitud fija.",
        "Calcular cuántas ventanas produce una secuencia según contexto y stride.",
        "Relacionar solapamiento, cobertura y coste computacional.",
        "Elegir un stride razonable para un corpus concreto.",
    ),
    blocks=(
        lead(
            "Una novela tokenizada puede tener millones de IDs. La red no puede recibirlos "
            "todos a la vez: necesita ejemplos de tamaño manejable. La solución es recortar la "
            "secuencia en ventanas y deslizar una ventana de longitud fija a lo largo del "
            "texto. El <strong>stride</strong> o paso determina cuánto avanza entre ventanas."
        ),
        p(
            "Si la ventana mide 256 tokens y el paso es 1, cada ejemplo comparte 255 tokens con "
            "el anterior. Si el paso también es 256, las ventanas no se solapan. Entre ambos "
            "extremos hay un continuo. El libro usa por defecto <code>max_length=256</code> y "
            "<code>stride=128</code>: la mitad del contexto se repite, de modo que cada token "
            "aparece en dos ejemplos como media. Ese solapamiento ayuda a que el modelo vea "
            "cada transición desde más de un punto de vista, a cambio de más cómputo."
        ),
        figure(
            "img/ch02/ventana-deslizante.svg",
            "Tira de tokens con varias ventanas de longitud cinco y paso dos, mostrando el solapamiento.",
            "Con contexto 5 y stride 2, cada ventana comparte tres tokens con la siguiente. El "
            "solapamiento no es un error: es una decisión sobre cuánta información se reutiliza.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "La aritmética es sencilla. Si la secuencia tiene <code>N</code> tokens, la ventana "
            "mide <code>L</code> y el paso es <code>S</code>, el número de ventanas con objetivo "
            "completo es <code>floor((N − L − 1) / S) + 1</code>. Con los 5 145 tokens BPE de "
            "<em>The Verdict</em> que reporta el libro, <code>L = 256</code> y "
            "<code>S = 128</code> producen <strong>39 ventanas</strong>. Con "
            "<code>S = 256</code>, producen <strong>20</strong>. Son cálculos nuestros sobre la "
            "cifra del libro, no cifras que él enumere."
        ),
        table(
            ["Contexto", "Stride", "Solapamiento", "Ventanas con 5 145 tokens", "Uso"],
            [
                ["256", "128", "50 %", "39", "Más variedad, más cómputo"],
                ["256", "256", "0 %", "20", "Cobertura sin repetición"],
                ["128", "64", "50 %", "79", "Contexto corto, más ejemplos"],
                ["128", "128", "0 %", "40", "Alternativa ligera"],
            ],
            caption="Número de ventanas con objetivo completo: floor((N − L − 1) / S) + 1.",
            note=(
                "Los valores son ejemplos calculados. Es la misma cuenta que hace la "
                "implementación del libro con range(0, len(token_ids) - max_length, stride)."
            ),
        ),
        h2("Qué cambia el stride"),
        p(
            "Un stride pequeño aumenta el número de ejemplos y el solapamiento. Eso puede "
            "ayudar a aprender transiciones locales, pero multiplica las épocas efectivas sobre "
            "el mismo texto y el coste de entrenamiento. Un stride grande reduce el número de "
            "ejemplos y elimina la repetición; a cambio, algunas transiciones solo se ven una "
            "vez y el modelo puede ajustarse con menos diversidad. El libro observa que "
            "demasiado solapamiento puede favorecer el sobreajuste, porque el modelo ve "
            "repetidamente los mismos pasajes."
        ),
        p(
            "La elección depende del corpus y del presupuesto. Para un corpus pequeño, conviene "
            "un stride menor para generar suficientes ejemplos. Para uno enorme, un stride igual "
            "al contexto reduce el coste sin perder cobertura: cada token aparece al menos una "
            "vez. En cualquier caso, la última ventana puede ser incompleta; muchas "
            "implementaciones la descartan para mantener formas rectangulares en el lote."
        ),
        lab("window"),
        callout(
            "tip",
            "Piensa en fotogramas",
            "Una ventana es un fotograma de una película de texto. El stride es cuánto avanza "
            "la cámara entre fotogramas. Si avanza poco, ves movimiento continuo y gastas más "
            "fotogramas; si avanza mucho, cubres más rápido pero pierdes continuidad.",
        ),
        check(
            "Una secuencia tiene 1 000 tokens, el contexto es 100 y el stride es 50. ¿Cuántas ventanas con objetivo completo salen y cuánto se solapan?",
            "Salen floor((1000 − 100 − 1) / 50) + 1 = 18 ventanas. Cada una comparte 50 tokens "
            "con la siguiente, es decir, la mitad del contexto. El primer token de la ventana k "
            "aparece también en la ventana k−1, pero no en la k−2.",
        ),
        h2("La ventana no es el contexto del modelo"),
        p(
            "Conviene separar dos conceptos que se confunden con facilidad. La <strong>ventana "
            "de entrenamiento</strong> es el fragmento que se usa en un paso de optimización. La "
            "<strong>ventana de contexto</strong> del modelo es el máximo de tokens que puede "
            "procesar en inferencia. Pueden coincidir, pero no tienen por qué: un modelo puede "
            "entrenarse con ventanas de 256 y admitir 1 024 posiciones si su arquitectura y sus "
            "embeddings posicionales lo permiten."
        ),
        p(
            "Además, la ventana no se usa sola: dentro de ella se construyen los pares "
            "entrada-objetivo. Una ventana de cuatro tokens no produce un único ejemplo, sino "
            "cuatro predicciones, una por posición. Ese desplazamiento es el tema de la "
            "siguiente lección y la pieza que conecta la preparación de datos con la función de "
            "pérdida."
        ),
        keypoints(
            [
                "El corpus se divide en ventanas de longitud fija para poder entrenar por lotes.",
                "El stride es el número de tokens que avanza la ventana entre ejemplos.",
                "Stride menor implica más solapamiento, más ejemplos y más coste.",
                "El número de ventanas con objetivo completo es floor((N − L − 1) / S) + 1.",
                "Ventana de entrenamiento y ventana de contexto son conceptos distintos.",
                "Una ventana contiene varias predicciones, no una sola.",
            ]
        ),
    ),
    key_points=(
        "La ventana deslizante recorta el corpus en fragmentos de longitud fija.",
        "El stride controla el solapamiento y el número de ejemplos.",
        "Más solapamiento cuesta más cómputo y puede favorecer el sobreajuste.",
        "La ventana de entrenamiento no es necesariamente el contexto máximo del modelo.",
    ),
    quiz_id=None,
)
