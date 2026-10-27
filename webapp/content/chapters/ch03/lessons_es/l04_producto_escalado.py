"""Lección 4 · Producto escalado y softmax."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=4,
    slug="producto-escalado",
    title="Producto escalado y softmax",
    summary=(
        "Dividir las puntuaciones por la raíz de d_k evita que softmax se sature. "
        "El escalado es la diferencia entre una distribución útil y una decisión casi binaria."
    ),
    minutes=10,
    objectives=(
        "Explicar por qué el producto escalar crece con la dimensión.",
        "Justificar la escala 1/√d_k en atención.",
        "Implementar un softmax numéricamente estable.",
        "Interpretar el efecto del escalado en los pesos y en los gradientes.",
    ),
    blocks=(
        lead(
            "La fórmula que resume la atención es <strong>softmax(QK<sup>T</sup> / √d<sub>k</sub>) "
            "· V</strong>. La división por la raíz de la dimensión de las claves parece un detalle "
            "menor, pero es lo que mantiene a softmax en una zona útil: sin ella, las puntuaciones "
            "crecen con la dimensión y los pesos se vuelven casi binarios."
        ),
        p(
            "El producto escalar de dos vectores suma d<sub>k</sub> productos. Si las componentes "
            "son independientes, con media cero y varianza uno, cada producto aporta una unidad de "
            "varianza y la suma acumula d<sub>k</sub>. Su desviación típica crece, por tanto, como "
            "√d<sub>k</sub>. En un modelo con 64 dimensiones por cabeza, una puntuación típica "
            "puede tener una magnitud de 8; en uno con 256, de 16. Esa escala no refleja una "
            "similitud mayor: es una consecuencia aritmética de sumar más términos."
        ),
        h2("Por qué dividir por la raíz de d_k"),
        p(
            "Softmax es sensible a la escala. Con puntuaciones pequeñas, la distribución resultante "
            "es suave y reparte peso entre varias opciones. Con puntuaciones grandes, la diferencia "
            "entre el máximo y el resto se amplifica y la distribución se parece a un interruptor: "
            "casi todo el peso cae en una posición. Si eso ocurre, el gradiente se vuelve muy "
            "pequeño en las demás posiciones y el aprendizaje se frena. El artículo del transformer "
            "lo describe como un problema de gradientes diminutos: cuanto más crece el producto "
            "escalar, más se aproxima softmax a una función escalón."
        ),
        p(
            "Dividir por √d<sub>k</sub> devuelve la puntuación a una escala comparable "
            "independientemente del número de dimensiones. El orden de las puntuaciones no cambia "
            "—dividir por una constante positiva es monótono—, pero la forma de la distribución sí. "
            "La atención sigue prefiriendo lo más afín, aunque deja de ignorar por completo las "
            "alternativas. Por eso el mecanismo se llama <strong>scaled dot-product "
            "attention</strong>."
        ),
        p(
            "Un ejemplo con una única puntuación dominante: si la puntuación sin escalar vale "
            "d<sub>k</sub> y las otras tres valen cero, el peso máximo después de softmax depende "
            "de la dimensión. Con d<sub>k</sub> = 4, la puntuación escalada es 2 y el peso máximo "
            "ronda 0,711. Con d<sub>k</sub> = 16, es 4 y sube a 0,948. Con d<sub>k</sub> = 64, es "
            "8 y llega a 0,999. La misma ventaja relativa se convierte en una dictadura conforme "
            "crece la dimensión si no se escala."
        ),
        table(
            ["d_k", "puntuación sin escalar", "√d_k", "puntuación escalada", "peso máximo"],
            [
                ["4", "4", "2", "2", "0,711"],
                ["16", "16", "4", "4", "0,948"],
                ["64", "64", "8", "8", "0,999"],
                ["256", "256", "16", "16", "≈1,000"],
            ],
            caption=(
                "Efecto del escalado en una fila con una puntuación dominante y tres alternativas "
                "a cero. Sin la división, la distribución se satura al crecer d_k."
            ),
            note="Cálculo propio con cuatro candidatos; ilustra el efecto, no un modelo entrenado.",
        ),
        h2("Softmax estable"),
        p(
            "Hay un segundo detalle numérico. Calcular exp(x) directamente puede desbordar si x es "
            "grande: el resultado supera el máximo representable y se convierte en infinito. La "
            "solución estándar resta el máximo de la fila antes de exponenciar. La operación es "
            "matemáticamente equivalente, porque el cociente entre exponenciales no cambia si "
            "multiplicamos numerador y denominador por el mismo factor, pero evita los extremos. "
            "En la práctica, las bibliotecas implementan esta versión estable."
        ),
        p(
            "Softmax también garantiza que los pesos sean positivos y sumen uno. Esa propiedad es "
            "la que permite interpretarlos como una distribución de importancia relativa. No son "
            "probabilidades de que ocurra un token, sino proporciones de mezcla entre valores. "
            "Confundir ambas cosas es un error frecuente al leer una matriz de atención."
        ),
        py(
            """
import math

def softmax_estable(fila):
    maximo = max(fila)
    exp = [math.exp(valor - maximo) for valor in fila]
    total = sum(exp)
    return [valor / total for valor in exp]

print("d_k | puntuación | escalada | peso máximo")
for d_k in (4, 16, 64, 256):
    puntuaciones = [float(d_k), 0.0, 0.0, 0.0]
    escaladas = [valor / math.sqrt(d_k) for valor in puntuaciones]
    pesos = softmax_estable(escaladas)
    print(f"{d_k:>3} | {puntuaciones[0]:>10.1f} | {escaladas[0]:>8.2f} | {max(pesos):.4f}")

print("\\nSin escalar, el peso máximo sería:")
for d_k in (4, 16, 64, 256):
    pesos = softmax_estable([float(d_k), 0.0, 0.0, 0.0])
    print(f"d_k={d_k:>3}: {max(pesos):.6f}")
""",
            caption=(
                "El mismo patrón de puntuaciones con cuatro dimensiones distintas. El softmax "
                "resta el máximo antes de exponenciar para no desbordar."
            ),
        ),
        callout(
            "tip",
            "Escalar no cambia quién gana",
            "La división por √d<sub>k</sub> conserva el orden de las puntuaciones: si una clave era "
            "la más afín, sigue siéndolo. Lo que cambia es el reparto del peso. Un softmax "
            "saturado aprende peor porque las alternativas reciben gradientes casi nulos; uno "
            "suave conserva señal para corregir.",
        ),
        check(
            "Una puntuación sin escalar vale 16 y d_k = 64. ¿Cuál es la puntuación escalada y por "
            "qué se usa ese divisor?",
            "La puntuación escalada es 16 / √64 = 16 / 8 = 2. Se usa √d_k porque la varianza de un "
            "producto escalar de d_k términos independientes crece con d_k; dividir por su raíz "
            "devuelve la desviación típica a una escala estable y evita que softmax se sature.",
        ),
        keypoints(
            [
                "El producto escalar acumula d_k términos y su magnitud crece con la dimensión.",
                "La escala 1/√d_k normaliza esa magnitud sin cambiar el orden de las puntuaciones.",
                "Sin escalado, softmax se satura y los gradientes se vuelven diminutos.",
                "Softmax convierte puntuaciones en pesos positivos que suman uno.",
                "Restar el máximo antes de exponenciar evita desbordamientos numéricos.",
                "Los pesos de atención son proporciones de mezcla, no probabilidades de tokens.",
            ]
        ),
    ),
    key_points=(
        "La atención escala las puntuaciones por 1/√d_k.",
        "El escalado compensa el crecimiento de la varianza con la dimensión.",
        "Softmax saturado produce gradientes pequeños y aprendizaje lento.",
        "Un softmax estable resta el máximo antes de exponenciar.",
        "Los pesos suman uno y expresan importancia relativa.",
    ),
)
