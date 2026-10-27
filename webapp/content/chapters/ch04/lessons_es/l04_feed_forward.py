"""Lección 4 · La red feed-forward."""

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
    slug="feed-forward",
    title="La red feed-forward",
    summary=(
        "La subred que expande cada token a 3 072 dimensiones, aplica GELU y vuelve a "
        "768: dónde está su capacidad y por qué no mezcla tokens entre sí."
    ),
    minutes=10,
    objectives=(
        "Describir la estructura y las dimensiones de la FFN de GPT-2 small.",
        "Calcular sus parámetros y compararlos con los del resto del bloque.",
        "Explicar por qué la FFN no sustituye a la atención.",
        "Entender por qué se mantiene la dimensión de entrada y salida.",
    ),
    blocks=(
        lead(
            "La atención se lleva buena parte de la fama, pero en GPT-2 small la red "
            "feed-forward es la subred más grande del bloque: casi el doble de parámetros "
            "que la atención. Su trabajo no es mezclar tokens, sino transformar cada uno "
            "por separado, darle espacio para combinaciones no lineales y devolverlo a la "
            "misma dimensión para que el siguiente bloque pueda seguir apilándose."
        ),
        p(
            "La FFN del libro tiene dos capas lineales y una GELU en medio: "
            "<code>Linear(768, 3072) → GELU → Linear(3072, 768)</code>. La primera "
            "proyección expande el vector cuatro veces; la segunda lo comprime de nuevo. "
            "La figura 4.9 del libro resume ese recorrido. La dimensión intermedia no es "
            "un capricho: da a la red un espacio más ancho donde combinar las 768 "
            "componentes antes de volver a la representación compartida por todos los "
            "bloques. El factor 4 es una convención frecuente, no una ley física."
        ),
        table(
            ["Pieza", "Forma", "Parámetros"],
            [
                ["Primera proyección", "768 → 3 072", "768 × 3 072 + 3 072 = 2 362 368"],
                ["Segunda proyección", "3 072 → 768", "3 072 × 768 + 768 = 2 360 064"],
                ["Total FFN", "768 → 3 072 → 768", "4 722 432"],
                ["Atención del bloque", "Q, K, V y salida", "2 360 064"],
                ["LayerNorm (dos)", "768", "3 072"],
                ["Bloque completo", "—", "7 085 568"],
            ],
            caption="Parámetros de la FFN comparados con el resto del bloque de GPT-2 small.",
            note=(
                "Cálculo propio a partir de las dimensiones del libro. Los sesgos de las "
                "proyecciones lineales están incluidos; qkv_bias se mantiene desactivado."
            ),
        ),
        p(
            "La comparación es reveladora. La FFN aporta 4 722 432 parámetros por bloque; "
            "la atención, 2 360 064. Multiplicando por doce, la FFN suma unos 56,67 "
            "millones y la atención unos 28,32 millones. En el modelo con pesos atados, "
            "eso significa que la FFN concentra aproximadamente el 45,5 % de los "
            "parámetros, frente al 22,8 % de la atención. Son porcentajes calculados aquí "
            "para orientar la intuición: la mayor parte de la capacidad del bloque no está "
            "en decidir a qué mirar, sino en transformar lo que ya se ha mirado."
        ),
        h2("Expandir, activar, proyectar"),
        p(
            "Piensa en la FFN como una máquina de tres pasos que se aplica a cada posición "
            "de la secuencia. Primero, una proyección lineal lleva el vector de 768 a 3 072 "
            "dimensiones: más espacio para representar combinaciones de rasgos. Después, "
            "GELU decide qué componentes pasan y con qué intensidad. Por último, la segunda "
            "proyección vuelve a 768. El resultado conserva la forma "
            "<code>[batch, tokens, 768]</code>, así que puede sumarse al residual y entrar "
            "en el bloque siguiente sin ajustar dimensiones."
        ),
        p(
            "Esa constancia de forma es una decisión de diseño, no un detalle. Si la FFN "
            "devolviera otro tamaño, habría que añadir una proyección adicional en cada "
            "bloque y la conexión residual dejaría de ser una suma directa. Mantener la "
            "forma permite apilar doce bloques idénticos en interfaz, cambiar solo los "
            "pesos y reutilizar la misma lógica. También permite que la atención y la FFN "
            "se alternen sin fricción: una mezcla información entre tokens; la otra "
            "procesa cada token con una red más ancha."
        ),
        h2("Capacidad sin mezclar tokens"),
        p(
            "La atención y la FFN hacen trabajos complementarios. La atención calcula pesos "
            "entre posiciones y construye representaciones contextuales; la FFN no mira a "
            "los demás tokens, aplica la misma transformación a cada uno. Esa división "
            "evita que la red tenga que resolver dos problemas a la vez en la misma "
            "operación. La FFN aporta profundidad y no linealidad por token; la atención "
            "aporta comunicación entre tokens. Juntas forman el bloque, y el bloque "
            "repetido forma el modelo."
        ),
        p(
            "Hay una consecuencia práctica: la FFN es computacionalmente costosa porque "
            "trabaja con una dimensión intermedia cuatro veces mayor. En GPT-2 small, "
            "3 072 columnas por token y por bloque suponen una parte importante de las "
            "operaciones. Modelos posteriores han explorado variantes como SwiGLU o "
            "distintos factores de expansión para equilibrar capacidad y coste. El "
            "principio sigue siendo el mismo: expandir, aplicar una no linealidad y "
            "proyectar de vuelta."
        ),
        callout(
            "tip",
            "Una forma de recordar el bloque",
            "Atención = comunicar entre tokens. FFN = transformar cada token. "
            "LayerNorm = mantener la escala bajo control. Residual = conservar el camino "
            "directo. Si puedes decir estas cuatro frases, puedes reconstruir el bloque "
            "sin memorizar el diagrama.",
        ),
        check(
            "¿Por qué la FFN no puede sustituir a la atención?",
            "Porque la FFN aplica la misma transformación a cada posición y no compara unos "
            "tokens con otros. No puede decidir que «gato» debe influir en «cansado» ni "
            "mover información entre posiciones. La atención sí construye esa mezcla "
            "contextual; la FFN se limita a transformar cada vector de forma independiente.",
        ),
        keypoints(
            [
                "La FFN tiene dos proyecciones lineales y una GELU entre ellas.",
                "Expande de 768 a 3 072 dimensiones y vuelve a 768.",
                "Aporta 4 722 432 parámetros por bloque, más que la atención.",
                "No mezcla tokens: aplica la misma red a cada posición.",
                "Conserva la forma [batch, tokens, 768] para permitir el residual y el apilado.",
                "La atención comunica; la FFN transforma y añade capacidad no lineal.",
            ]
        ),
    ),
    key_points=(
        "La FFN expande cuatro veces la dimensión, aplica GELU y proyecta de vuelta.",
        "Es la subred con más parámetros del bloque: 4,72 M frente a 2,36 M de atención.",
        "No mezcla información entre tokens; eso lo hace la atención.",
        "Mantener la forma de entrada y salida permite apilar bloques y sumar residuales.",
        "El factor de expansión es una convención de diseño, no una obligación.",
        "La capacidad del bloque depende tanto de comunicar como de transformar.",
    ),
)
