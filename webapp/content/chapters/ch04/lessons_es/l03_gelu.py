"""Lección 3 · GELU y activaciones."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=3,
    slug="gelu",
    title="GELU y activaciones",
    summary=(
        "Por qué la red feed-forward de GPT no usa ReLU sin más: la curva suave de "
        "GELU, su aproximación con tangente hiperbólica y su efecto en el entrenamiento."
    ),
    minutes=9,
    objectives=(
        "Comparar ReLU y GELU por forma y por comportamiento en valores negativos.",
        "Escribir la aproximación de GELU que usa GPT-2.",
        "Explicar por qué una activación suave puede facilitar la optimización.",
        "Situar GELU dentro de la red feed-forward del bloque transformer.",
    ),
    blocks=(
        lead(
            "Una activación decide qué parte de la señal deja pasar una neurona. ReLU "
            "resuelve la pregunta con un codo: si la entrada es positiva, pasa; si es "
            "negativa, se convierte en cero. GELU responde con una curva. Esa diferencia, "
            "pequeña en apariencia, cambia el paisaje de optimización de una red profunda "
            "y es la que GPT-2 adopta en su red feed-forward."
        ),
        h2("ReLU y sus límites"),
        p(
            "ReLU es popular porque es barata y funciona: <code>max(0, x)</code>. Su "
            "derivada vale uno para valores positivos y cero para negativos. Esa "
            "simplicidad tiene un precio. En el punto cero hay un codo que la función no "
            "puede suavizar, y una neurona que cae siempre en la zona negativa deja de "
            "recibir gradiente: se apaga. En redes muy profundas, esa acumulación de "
            "neuronas inactivas puede dificultar el aprendizaje. No significa que ReLU sea "
            "mala —se usa en muchísimos modelos—, pero deja margen para alternativas."
        ),
        h2("La curva GELU"),
        p(
            "GELU, Gaussian Error Linear Unit, se define como "
            "<code>x · Φ(x)</code>, donde <code>Φ</code> es la función de distribución "
            "acumulada de una gaussiana estándar. La idea es ponderar cada entrada por la "
            "probabilidad de que una normal estándar sea menor que ella: los valores muy "
            "negativos se atenúan casi hasta cero, los positivos pasan casi intactos y la "
            "transición es suave. Calcular <code>Φ</code> de forma exacta es caro, así que "
            "GPT-2 usa la aproximación "
            "<code>0,5 · x · (1 + tanh(√(2/π) · (x + 0,044715 · x³)))</code>. Es la misma "
            "que implementa el libro y la que se usa al cargar los pesos preentrenados."
        ),
        py(
            """
import math

def gelu(x):
    return 0.5 * x * (1 + math.tanh(
        math.sqrt(2 / math.pi) * (x + 0.044715 * x ** 3)
    ))

def relu(x):
    return max(0.0, x)

print(f"{'x':>5} {'ReLU':>9} {'GELU':>9}")
for x in (-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0):
    print(f"{x:>5.1f} {relu(x):>9.4f} {gelu(x):>9.4f}")
""",
            caption=(
                "Comparación numérica de ReLU y GELU con la aproximación de GPT-2. "
                "Observa que GELU no llega a cero en los valores negativos."
            ),
        ),
        p(
            "La curva de GELU se parece a ReLU en la zona positiva y se acerca a cero en "
            "la negativa, pero sin cortar. Esa suavidad tiene dos consecuencias. Primero, "
            "la derivada cambia de forma continua, lo que da al optimizador información más "
            "fina cerca del cero. Segundo, una neurona con entrada negativa puede conservar "
            "una salida y un gradiente pequeños, en lugar de apagarse por completo. El "
            "libro lo resume así: GELU permite ajustes más matizados de los parámetros y "
            "suele comportarse mejor en arquitecturas profundas y complejas. No es una "
            "garantía universal, sino una elección empírica que funcionó en GPT-2."
        ),
        p(
            "Dentro del bloque, GELU no actúa sola: vive entre las dos proyecciones de la "
            "red feed-forward. La primera proyección expande cada token de 768 a 3 072 "
            "dimensiones; GELU introduce la no linealidad; la segunda proyección devuelve "
            "el vector a 768. Sin una activación no lineal, las dos matrices colapsarían en "
            "una sola transformación lineal y la red perdería capacidad. GELU es, por "
            "tanto, una pieza pequeña pero imprescindible del bloque que se repite doce "
            "veces en GPT-2 small. Modelos más recientes usan variantes como SwiGLU, pero "
            "la lógica es la misma: una no linealidad suave entre proyecciones."
        ),
        callout(
            "warning",
            "Suave no significa mágica",
            "Que GELU sea derivable en todo su dominio no garantiza que un modelo entrene "
            "mejor en todos los casos. La elección de activación interactúa con la "
            "inicialización, la normalización, la profundidad y los datos. En el libro, "
            "GELU es la pieza que acompaña a la FFN de GPT-2; la comparación con ReLU "
            "sirve para entender el diseño, no para declarar un ganador absoluto.",
        ),
        check(
            "¿Qué gana una neurona con GELU frente a ReLU cuando recibe una entrada "
            "negativa?",
            "GELU le deja una salida pequeña, no nula, y por tanto un gradiente distinto de "
            "cero. Esa neurona puede seguir contribuyendo al aprendizaje, aunque sea en "
            "menor medida. Con ReLU, una entrada negativa produce cero y bloquea el "
            "gradiente en esa unidad.",
        ),
        keypoints(
            [
                "ReLU es lineal a trozos, barata y anula todos los valores negativos.",
                "GELU pondera la entrada por la distribución acumulada gaussiana.",
                "GPT-2 usa una aproximación con tanh y el término 0,044715 · x³.",
                "La suavidad de GELU ofrece gradientes más finos cerca de cero.",
                "GELU permite que las entradas negativas conserven una señal pequeña.",
                "En la FFN, GELU aporta la no linealidad entre las dos proyecciones.",
            ]
        ),
    ),
    key_points=(
        "ReLU tiene un codo en cero y apaga por completo los valores negativos.",
        "GELU es una curva suave basada en la distribución normal.",
        "La aproximación con tanh es la que usa GPT-2 y la que implementa el libro.",
        "La suavidad mejora la información disponible para el optimizador.",
        "Las neuronas con entrada negativa no se apagan del todo con GELU.",
        "GELU ocupa el centro de la red feed-forward, entre sus dos proyecciones.",
    ),
)
