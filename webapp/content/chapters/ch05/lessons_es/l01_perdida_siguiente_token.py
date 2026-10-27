"""Lección 1 · La pérdida del siguiente token."""

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
    number=1,
    slug="perdida-siguiente-token",
    title="La pérdida del siguiente token",
    summary=(
        "Un GPT produce un vector de logits por posición. La pérdida mide cuánta "
        "probabilidad recibe el token correcto y resume esa cuenta en un solo número."
    ),
    minutes=11,
    objectives=(
        "Describir la forma de los logits y de los objetivos en un lote.",
        "Explicar cómo se obtiene la probabilidad del token correcto con softmax.",
        "Interpretar la pérdida de una posición y la media de un lote.",
        "Evitar comparaciones de pérdida entre vocabularios distintos.",
    ),
    blocks=(
        lead(
            "Entrenar un GPT consiste, en el fondo, en subir la probabilidad del token que "
            "realmente aparece en el texto. Para saber si el modelo mejora necesitamos una "
            "medida numérica de cuánto se acerca a esa respuesta. Esa medida es la "
            "<strong>pérdida del siguiente token</strong>, la brújula de todo el capítulo."
        ),
        h2("Qué sale del modelo"),
        p(
            "Cada posición de la secuencia produce un vector de <strong>logits</strong>, uno "
            "por token del vocabulario. Si el vocabulario tiene 50 257 entradas, el vector "
            "tiene 50 257 números sin normalizar. Un logit alto significa que el modelo "
            "favorece ese token, pero no es una probabilidad: los valores pueden ser negativos "
            "y no suman 1. La función <strong>softmax</strong> los convierte en una "
            "distribución, elevando cada logit a la exponencial y dividiendo por la suma de "
            "todas las exponenciales. El resultado es un vector de probabilidades positivas "
            "que suma 1."
        ),
        figure(
            "img/ch05/perdida.svg",
            "Distribución de probabilidad del siguiente token con el token correcto resaltado y la fórmula de la pérdida.",
            "La pérdida no mira todo el vector por igual: selecciona la probabilidad del token "
            "correcto, le aplica −ln y promedia las posiciones del lote.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "El objetivo del entrenamiento es que esa probabilidad se acerque a 1. Si el token "
            "correcto es «cielo» y el modelo le asigna 0,60, la pérdida de esa posición es "
            "−ln(0,60) ≈ 0,511. Si le asigna 0,05, la pérdida sube a −ln(0,05) ≈ 3,00. La "
            "cuenta castiga con fuerza las probabilidades pequeñas: pasar de 0,60 a 0,90 "
            "reduce la pérdida de 0,511 a 0,105, mientras que pasar de 0,05 a 0,10 solo la "
            "baja de 3,00 a 2,30. Esa asimetría es útil: el modelo aprende sobre todo de los "
            "casos en los que está muy equivocado."
        ),
        h2("La forma del batch"),
        p(
            "En la práctica no se entrena con una frase y una posición cada vez. Un lote "
            "contiene varias secuencias y cada secuencia aporta varias posiciones. Los logits "
            "tienen forma <code>[B, T, V]</code>: tamaño de lote, longitud de la secuencia y "
            "tamaño del vocabulario. Los objetivos tienen forma <code>[B, T]</code>, porque "
            "para cada posición solo guardamos el identificador del token correcto. La "
            "pérdida se calcula sobre todas las posiciones del lote, no sobre una media de "
            "frases independientes."
        ),
        table(
            ["Tensor", "Forma", "Qué contiene"],
            [
                ["Logits", "<code>[B, T, V]</code>", "Una puntuación por token del vocabulario y posición"],
                ["Objetivos", "<code>[B, T]</code>", "El token que sigue en cada posición"],
                ["Logits aplanados", "<code>[B·T, V]</code>", "Las posiciones del lote como filas independientes"],
                ["Pérdida", "Escalar", "Media de −ln p en las B·T posiciones"],
            ],
            caption="Formas habituales durante el cálculo de la pérdida.",
            note=(
                "La pérdida se promedia sobre posiciones, no sobre secuencias. Una secuencia "
                "larga aporta más posiciones que una corta."
            ),
        ),
        p(
            "Los objetivos se construyen desplazando la entrada una posición. Si la secuencia "
            "es «El cielo está nublado», las entradas son «El cielo está» y los objetivos "
            "«cielo está nublado». El modelo ve el mismo texto en ambos lados: la etiqueta ya "
            "estaba allí. Esta es la razón por la que el pretraining no necesita anotadores. "
            "La pérdida de un lote es la media de las pérdidas de todas las posiciones, así "
            "que un lote con secuencias de 256 tokens aporta 256 veces más señal que una "
            "predicción aislada."
        ),
        p(
            "El modelo del libro, con 124 millones de parámetros y un vocabulario de 50 257 "
            "tokens, empieza con una pérdida cercana a 10,99 sobre el cuento <em>The "
            "Verdict</em>. Ese valor está próximo al de una distribución uniforme: "
            "ln(50 257) ≈ 10,825. No es casualidad. Antes de entrenar, los pesos son "
            "aleatorios y el modelo reparte la probabilidad entre casi todo el vocabulario. "
            "La pérdida alta no significa que «no sepa nada»: significa que todavía no "
            "concentra la probabilidad en el token correcto."
        ),
        callout(
            "warning",
            "La pérdida no es una nota porcentual",
            "Una pérdida de 2,0 no equivale a un 2 % de acierto. Es el negativo del logaritmo "
            "medio de la probabilidad del token correcto. Tampoco se puede comparar sin más "
            "entre modelos con vocabularios distintos: un vocabulario de 50 000 tokens parte "
            "de una pérdida base mucho mayor que uno de 1 000. Para comparar, usa la misma "
            "tokenización o mira la perplejidad y las métricas de la tarea."
        ),
        check(
            "¿Por qué la pérdida se calcula posición a posición y luego se promedia, en lugar "
            "de comparar solo la última palabra de cada frase?",
            "Porque durante el pretraining el modelo aprende de todas las posiciones: cada "
            "token de la secuencia es un objetivo potencial. Promediar todas las posiciones "
            "aprovecha mucho más el texto y produce una señal más estable que fijarse solo en "
            "el final de cada frase."
        ),
        keypoints(
            [
                "Los logits son puntuaciones sin normalizar; softmax las convierte en probabilidades.",
                "La pérdida de una posición es −ln de la probabilidad asignada al token correcto.",
                "Los objetivos son la entrada desplazada una posición, no anotaciones humanas.",
                "En un lote, los logits tienen forma [B, T, V] y los objetivos [B, T].",
                "La pérdida del lote promedia todas las posiciones, no solo la última.",
                "Una pérdida cercana a ln(V) indica un modelo casi uniforme, como el inicial.",
            ]
        ),
    ),
    key_points=(
        "La pérdida mide la probabilidad del token correcto con −ln y la promedia.",
        "Softmax transforma logits en una distribución que suma 1.",
        "Los objetivos son la secuencia de entrada desplazada una posición.",
        "La pérdida de un lote es la media de todas las posiciones.",
        "La escala de la pérdida depende del tamaño del vocabulario.",
    ),
)
