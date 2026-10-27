"""Lección 3 · La cabeza de clasificación."""

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
    py,
)

LESSON = Lesson(
    number=3,
    slug="cabeza-clasificacion",
    title="La cabeza de clasificación",
    summary=(
        "Una capa lineal nueva traduce las 768 dimensiones del modelo en una puntuación "
        "por clase; el último token resume la secuencia."
    ),
    minutes=11,
    objectives=(
        "Explicar cómo se sustituye la capa de salida del vocabulario por una cabeza de clases.",
        "Interpretar la forma del tensor de salida y los logits de cada clase.",
        "Justificar el uso del último token en un modelo con atención causal.",
        "Convertir logits en probabilidades con softmax y obtener la clase predicha.",
    ),
    blocks=(
        lead(
            "Clasificar no requiere un transformer distinto. Requiere cambiar la última "
            "proyección: en lugar de repartir probabilidad entre 50 257 tokens, la red debe "
            "repartirla entre un puñado de clases. Esa capa nueva es la cabeza de "
            "clasificación, y su diseño explica por qué el modelo sigue siendo el mismo "
            "GPT-2 que generaba texto."
        ),
        h2("Del vocabulario a las clases"),
        p(
            "En el GPT-2 pequeño, la capa <code>out_head</code> transforma un vector de 768 "
            "dimensiones en 50 257 puntuaciones, una por token del vocabulario. Para "
            "clasificación se reemplaza por una capa lineal de <strong>768 → 2</strong>: dos "
            "salidas, una para «no spam» y otra para «spam». Si la tarea tuviera tres clases "
            "—por ejemplo, tecnología, deportes y política—, la capa tendría tres salidas. "
            "El número de nodos coincide con el número de clases, no con el tamaño del "
            "vocabulario."
        ),
        p(
            "La entrada sigue siendo una secuencia de identificadores de token. La salida "
            "pasa a tener forma <code>[lote, tokens, clases]</code>. Con un lote de 8 "
            "mensajes de 120 tokens y dos clases, el tensor resultante es "
            "<code>[8, 120, 2]</code>. Cada posición de la secuencia produce una predicción, "
            "pero no todas son igual de útiles. Para clasificar el mensaje completo se elige "
            "una sola posición y se ignoran las demás."
        ),
        figure(
            "img/ch06/cabeza-clasificacion.svg",
            "Esquema de un GPT-2 con doce bloques; la última capa y la normalización final se ajustan, y la cabeza de vocabulario se sustituye por una proyección a dos clases.",
            "La cabeza de clasificación sustituye la proyección al vocabulario por una capa "
            "lineal de 768 a 2 clases. Solo se ajustan la última capa del transformer, la "
            "normalización final y la cabeza nueva.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("Por qué el último token"),
        p(
            "GPT usa atención causal: cada token solo puede mirar los tokens anteriores y a "
            "sí mismo. El primero no ve nada del futuro; el último, en cambio, ha podido "
            "atender a toda la secuencia. Por eso el libro concentra la clasificación en la "
            "última fila del tensor de salida, <code>outputs[:, -1, :]</code>. Es la posición "
            "que acumula más información del mensaje y la que se usa para calcular la pérdida "
            "y la predicción."
        ),
        p(
            "Los dos valores de esa fila son <strong>logits</strong>: puntuaciones sin "
            "normalizar. En el ejemplo del libro, el último token produce "
            "<code>[-3.5983, 3.9902]</code>. Como la segunda puntuación es mayor, la clase "
            "predicha es 1, «spam». Aplicar softmax es opcional para decidir, porque la "
            "transformación conserva el orden; es imprescindible, en cambio, si queremos "
            "interpretar el resultado como probabilidad o elegir un umbral distinto de 0,5."
        ),
        py(
            """
import math

logits = [-3.5983, 3.9902]
etiquetas = ["no spam", "spam"]

# Softmax estable: restamos el máximo antes de exponenciar.
maximo = max(logits)
exponenciales = [math.exp(valor - maximo) for valor in logits]
total = sum(exponenciales)
probabilidades = [valor / total for valor in exponenciales]

for etiqueta, logit, probabilidad in zip(etiquetas, logits, probabilidades):
    print(f"{etiqueta:8s} logit={logit:6.2f}  probabilidad={probabilidad:.4f}")

prediccion = 0
for indice in range(1, len(probabilidades)):
    if probabilidades[indice] > probabilidades[prediccion]:
        prediccion = indice

print("Clase predicha:", etiquetas[prediccion])
""",
            caption=(
                "Softmax de los logits del último token. La clase con mayor probabilidad "
                "coincide con la de mayor logit."
            ),
        ),
        p(
            "El laboratorio «Clasificador interactivo» convierte estas puntuaciones en "
            "decisiones. Con una lista de mensajes de ejemplo puedes mover el umbral y ver "
            "cómo cambian la matriz de confusión, la precisión, el recall y el F1. Es la "
            "mejor forma de comprobar que la cabeza no decide sola: produce puntuaciones, y "
            "el sistema que la rodea fija la regla."
        ),
        lab("classifier"),
        callout(
            "tip",
            "Una cabeza, muchas arquitecturas",
            "El mismo patrón aparece en BERT y en otros modelos: una representación "
            "contextual y una capa lineal por clase. La diferencia está en qué token o "
            "vector se usa como resumen. En GPT se usa el último por la máscara causal; en "
            "un encoder bidireccional suele usarse el token <code>[CLS]</code> o un pooling "
            "sobre la secuencia."
        ),
        check(
            "Si el tensor de salida es [8, 120, 2], ¿qué representa cada dimensión y por qué "
            "se elige la posición 119?",
            "Ocho es el tamaño del lote, 120 la longitud de la secuencia y 2 el número de "
            "clases. La posición 119 es el último token; gracias a la atención causal ha "
            "podido mirar los 119 anteriores y resume mejor el mensaje completo.",
        ),
        keypoints(
            [
                "La cabeza de clasificación sustituye la proyección al vocabulario.",
                "Una capa lineal de 768 a 2 produce un logit por clase.",
                "La salida tiene forma [lote, tokens, clases].",
                "El último token resume la secuencia porque ve todos los anteriores.",
                "Softmax convierte logits en probabilidades, pero no cambia el argmax.",
                "La cabeza produce puntuaciones; el umbral y las métricas deciden.",
            ]
        ),
    ),
    key_points=(
        "La cabeza de clasificación es una capa lineal con una salida por clase.",
        "El tensor de salida conserva la dimensión de tokens y añade la de clases.",
        "El último token es el resumen natural de una secuencia con atención causal.",
        "Los logits se ordenan igual antes y después de softmax.",
        "La predicción es argmax; el umbral es una decisión posterior.",
    ),
)
