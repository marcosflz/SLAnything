"""Lección 2 · Self-attention paso a paso."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=2,
    slug="self-attention",
    title="Self-attention paso a paso",
    summary=(
        "Puntuar, normalizar y mezclar: las tres operaciones con las que cada token construye "
        "una representación contextual de toda la secuencia."
    ),
    minutes=12,
    objectives=(
        "Describir la self-attention como una suma ponderada de representaciones.",
        "Calcular puntuaciones de atención con productos escalares.",
        "Normalizar las puntuaciones con softmax e interpretar los pesos.",
        "Construir un vector de contexto a partir de una matriz de atención 3 × 3.",
    ),
    blocks=(
        lead(
            "La idea central de la self-attention cabe en una frase: cada token mira a los "
            "demás, decide a cuáles prestar más atención y construye con ellos una nueva "
            "representación de sí mismo. Esa representación se llama <strong>vector de "
            "contexto</strong> y sustituye al embedding aislado en las capas siguientes."
        ),
        p(
            "El prefijo <em>self</em> indica que la secuencia se compara consigo misma: no hay una "
            "frase de entrada y otra de salida. En la frase «El gato no cruzó la calle porque "
            "estaba cansado», la palabra «cansado» necesita encontrar a «gato» para resolverse; la "
            "distancia y el orden superficial no deberían impedirlo. La atención aprende a "
            "establecer ese tipo de conexión a partir de los datos."
        ),
        h2("Tres pasos: puntuar, normalizar y mezclar"),
        p(
            "La versión más simple de la self-attention no tiene pesos entrenables. Primero se "
            "calcula una <strong>puntuación de atención</strong> entre cada par de tokens con un "
            "producto escalar. El producto escalar mide cuánto se alinean dos vectores: si "
            "apuntan en direcciones parecidas, la puntuación es alta; si son ortogonales, ronda "
            "cero; si apuntan en sentidos opuestos, puede ser negativa. Segundo, las puntuaciones "
            "de cada fila se convierten en <strong>pesos de atención</strong> con softmax, de modo "
            "que sean positivos y sumen uno. Tercero, el vector de contexto de cada token es la "
            "suma ponderada de todos los vectores de entrada."
        ),
        p(
            "La matriz de pesos no es un parámetro fijo: se calcula para cada entrada. Dos frases "
            "distintas producen matrices distintas, y la misma palabra puede recibir pesos "
            "diferentes. Eso hace que la representación sea contextual y no un simple diccionario "
            "de palabras."
        ),
        h2("Un ejemplo numérico de 3 × 3"),
        p(
            "Tomemos tres tokens —«El», «gato» y «duerme»— representados por vectores de cuatro "
            "dimensiones. Los valores son inventados para que las cuentas se puedan seguir a mano; "
            "en un modelo real, los embeddings se aprenden. Con estos vectores, la matriz de "
            "puntuaciones es simétrica porque comparamos cada vector consigo mismo y con los "
            "demás:"
        ),
        table(
            ["Desde ↓ / Hacia →", "El", "gato", "duerme"],
            [
                ["El", "1,014", "0,992", "0,568"],
                ["gato", "0,992", "1,591", "1,082"],
                ["duerme", "0,568", "1,082", "1,087"],
            ],
            caption=(
                "Puntuaciones de atención de un ejemplo didáctico con vectores de cuatro "
                "dimensiones. Cada fila es el token que consulta; cada columna, el token "
                "consultado."
            ),
            note="Cálculo propio con los vectores del ejemplo; no son pesos de un modelo entrenado.",
        ),
        p(
            "Al aplicar softmax, «El» se reparte de forma casi uniforme: 0,382 / 0,374 / 0,244. "
            "«Gato» se da más peso a sí mismo (0,465), pero conserva parte de «El» (0,255) y de "
            "«duerme» (0,280). «Duerme» queda en 0,230 / 0,384 / 0,386."
        ),
        p(
            "El vector de contexto de «gato» se obtiene multiplicando cada vector de entrada por "
            "su peso y sumando: 0,255 · El + 0,465 · gato + 0,280 · duerme. El resultado es "
            "aproximadamente [0,427, 0,605, 0,626, 0,390]. Ya no es el embedding original: es una "
            "mezcla en la que «gato» domina, pero «El» y «duerme» también aportan. En una capa "
            "real, las proyecciones se aprenden para que la mezcla sea útil (lección 3)."
        ),
        lab("attention"),
        h2("Qué añade el contexto"),
        p(
            "La atención no codifica por sí sola el orden. Los embeddings indican qué palabra es; "
            "la posición, dónde está. Sin esa señal, la suma ponderada sería casi invariante al "
            "orden: «el perro muerde al gato» y «el gato muerde al perro» podrían acabar con "
            "representaciones parecidas. El transformer añade información posicional a las "
            "entradas, y la atención aprende a combinarla con el contenido."
        ),
        p(
            "Tampoco es una bolsa de palabras. Una bolsa cuenta ocurrencias y pierde el orden; la "
            "atención calcula pesos que dependen de la consulta y del contenido de cada posición. "
            "El mismo token puede mirar a sitios distintos según la frase, lo que permite resolver "
            "ambigüedades sin reglas escritas a mano."
        ),
        callout(
            "info",
            "Pesos de atención no son pesos del modelo",
            "En una red neuronal, «peso» suele designar un parámetro entrenable. En atención, "
            "«peso de atención» designa un valor calculado para una entrada concreta. Los "
            "parámetros se aprenden y persisten; los pesos de atención cambian con cada frase y "
            "cada capa. Confundirlos lleva a interpretar mal qué aprende el modelo.",
        ),
        check(
            "En el ejemplo, la fila de «gato» tiene pesos 0,255 / 0,465 / 0,280. ¿Qué significan "
            "esos tres números?",
            "Que el vector de contexto de «gato» se forma con un 25,5 % de «El», un 46,5 % de "
            "«gato» y un 28,0 % de «duerme». Son pesos relativos que suman uno, no probabilidades "
            "de que aparezca una palabra. El contexto resultante mezcla los tres vectores en esas "
            "proporciones.",
        ),
        py(
            """
import math

TOKENS = ["El", "gato", "duerme"]
X = [
    [0.43, 0.15, 0.89, 0.12],
    [0.55, 0.87, 0.66, 0.31],
    [0.22, 0.58, 0.33, 0.77],
]

def producto_escalar(a, b):
    return sum(x * y for x, y in zip(a, b))

def softmax(fila):
    maximo = max(fila)
    exp = [math.exp(valor - maximo) for valor in fila]
    total = sum(exp)
    return [valor / total for valor in exp]

puntuaciones = [[producto_escalar(a, b) for b in X] for a in X]
pesos = [softmax(fila) for fila in puntuaciones]
contextos = [
    [sum(pesos[i][j] * X[j][d] for j in range(len(X))) for d in range(len(X[0]))]
    for i in range(len(X))
]

print("Matriz de puntuaciones:")
for fila in puntuaciones:
    print([round(valor, 3) for valor in fila])

print("\\nPesos de atención (cada fila suma 1):")
for token, fila in zip(TOKENS, pesos):
    print(token, [round(valor, 3) for valor in fila], "suma:", round(sum(fila), 6))

print("\\nVector de contexto de «gato»:")
print([round(valor, 3) for valor in contextos[1]])
""",
            caption=(
                "Self-attention simplificada, sin pesos entrenables, sobre tres tokens de cuatro "
                "dimensiones. Cambia los vectores y observa cómo se mueven los pesos."
            ),
        ),
        keypoints(
            [
                "Self-attention compara una secuencia consigo misma.",
                "Las puntuaciones se obtienen con productos escalares entre representaciones.",
                "Softmax convierte cada fila de puntuaciones en pesos positivos que suman uno.",
                "El vector de contexto es la suma ponderada de los vectores de entrada.",
                "Los pesos de atención son dinámicos; los del modelo, parámetros aprendidos.",
                "La posición debe añadirse aparte: la atención por sí sola no codifica el orden.",
            ]
        ),
    ),
    key_points=(
        "Self-attention construye un contexto por token.",
        "El producto escalar mide la alineación entre dos representaciones.",
        "Softmax normaliza las puntuaciones en pesos que suman uno.",
        "El contexto es una suma ponderada de toda la secuencia.",
        "Los pesos de atención cambian con la entrada; los parámetros no.",
    ),
)
