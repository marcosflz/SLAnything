"""Lección 7 · Embeddings y significado."""

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
    table,
)

LESSON = Lesson(
    number=7,
    slug="embeddings-y-significado",
    title="Embeddings y significado",
    summary=(
        "Los vectores permiten comparar tokens con geometría: dirección, distancia y "
        "similitud coseno. Esa geometría captura regularidades útiles, pero también límites "
        "y sesgos que conviene conocer."
    ),
    minutes=11,
    objectives=(
        "Calcular la similitud coseno entre dos vectores.",
        "Interpretar los vecinos más cercanos de un token.",
        "Distinguir proximidad geométrica de sinonimia.",
        "Reconocer los sesgos y límites de los embeddings estáticos.",
    ),
    blocks=(
        lead(
            "Dos tokens parecidos deberían tener vectores parecidos. Esa intuición convierte "
            "la matriz de embeddings en un mapa: palabras que aparecen en contextos similares "
            "quedan cerca, y la distancia entre vectores se puede medir. La herramienta básica "
            "es la <strong>similitud coseno</strong>."
        ),
        p(
            "La similitud coseno compara la dirección de dos vectores, no su longitud. Se "
            "calcula como el producto escalar dividido por el producto de sus normas: "
            "<code>cos(a, b) = (a · b) / (||a|| ||b||)</code>. El resultado va de −1 a 1. Un "
            "valor cercano a 1 indica direcciones parecidas; cercano a 0, direcciones "
            "ortogonales; cercano a −1, direcciones opuestas. Al ignorar la magnitud, dos "
            "vectores pueden ser muy similares aunque uno sea mucho más largo que el otro."
        ),
        figure(
            "img/ch02/espacio-embeddings.svg",
            "Mapa bidimensional con grupos de vectores para animales, vehículos y comida.",
            "Una proyección de dos dimensiones permite ver agrupaciones, pero no demuestra que "
            "el modelo «entienda» los conceptos. Es una visualización, no una prueba.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "El ejemplo siguiente usa seis vectores de tres dimensiones inventados para que el "
            "cálculo sea transparente. Los valores están elegidos a mano para que los animales "
            "queden cerca entre sí, los vehículos también y la comida forme su propio grupo. "
            "En un modelo real las coordenadas se aprenden y no se interpretan una a una; lo "
            "que se conserva es la operación matemática."
        ),
        py(
            """
import math

VECTORES = {
    "gato":    [0.90, 0.30, 0.10],
    "perro":   [0.85, 0.35, 0.15],
    "coche":   [0.10, 0.90, 0.20],
    "autobús": [0.15, 0.85, 0.25],
    "pizza":   [0.70, 0.20, 0.60],
    "paella":  [0.65, 0.25, 0.65],
}


def coseno(a, b):
    producto = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    return producto / (norma_a * norma_b)


def vecinos(consulta, vectores, limite=3):
    puntuaciones = []
    for palabra, vector in vectores.items():
        if palabra != consulta:
            puntuaciones.append((coseno(vectores[consulta], vector), palabra))
    return sorted(puntuaciones, reverse=True)[:limite]


for palabra in ("gato", "coche", "pizza"):
    print(f"Vecinos de «{palabra}»:")
    for puntuación, vecino in vecinos(palabra, VECTORES):
        print(f"  {vecino:8} coseno={puntuación:.3f}")

print()
print(f"coseno(gato, perro) = {coseno(VECTORES['gato'], VECTORES['perro']):.3f}")
print(f"coseno(gato, coche) = {coseno(VECTORES['gato'], VECTORES['coche']):.3f}")
""",
            caption=(
                "Similitud coseno y vecinos más cercanos con vectores didácticos. Cambia las "
                "coordenadas y observa cómo se reordenan los vecinos."
            ),
        ),
        lab("embedding"),
        h2("Qué significan los vecinos"),
        p(
            "En un embedding entrenado, los vecinos de «gato» suelen incluir «perro», «felino» "
            "o «mascota». Eso no significa que el vector contenga una definición: significa que "
            "esos tokens aparecen en contextos parecidos y el modelo los ha acercado para "
            "reducir la pérdida. La proximidad es una regularidad estadística, no una relación "
            "lógica garantizada."
        ),
        p(
            "Por eso la similitud coseno es útil para explorar y para construir sistemas de "
            "recuperación, pero no es un oráculo. Dos antónimos pueden aparecer en contextos "
            "muy similares («alto» y «bajo» junto a «edificio») y quedar cerca. Dos palabras "
            "relacionadas pueden quedar lejos si el corpus las usa en registros distintos. La "
            "geometría resume el uso, no el diccionario."
        ),
        table(
            ["Fenómeno", "Qué se observa", "Por qué ocurre", "Consecuencia"],
            [
                [
                    "Sinonimia",
                    "Vecinos cercanos",
                    "Contextos intercambiables",
                    "Útil para recuperación y agrupación",
                ],
                [
                    "Antonimia",
                    "También pueden ser cercanos",
                    "Aparecen en los mismos contextos",
                    "La distancia no distingue oposición",
                ],
                [
                    "Polisemia",
                    "Un vector mezcla sentidos",
                    "El embedding estático no depende del contexto",
                    "«Banco» no distingue asiento y entidad",
                ],
                [
                    "Sesgo",
                    "Asociaciones del corpus",
                    "El modelo aprende frecuencias sociales",
                    "Puede reproducir estereotipos",
                ],
            ],
            caption="Límites habituales de los embeddings de token. Los modelos contextuales matizan algunos, no todos.",
        ),
        callout(
            "warning",
            "Cerca no significa correcto",
            "Que dos vectores tengan un coseno de 0,95 no demuestra que sus tokens sean "
            "sinónimos ni que la asociación sea deseable. Antes de usar embeddings para tomar "
            "decisiones —filtrar candidatos, recomendar, moderar— conviene medir y revisar "
            "ejemplos reales, no confiar solo en la puntuación.",
        ),
        h2("Estático frente a contextual"),
        p(
            "La matriz de embeddings del capítulo asigna un vector fijo a cada token. Es una "
            "representación <strong>estática</strong>: «banco» tiene el mismo vector en «banco "
            "del parque» y en «banco central». Los transformers modernos producen además "
            "representaciones <strong>contextuales</strong>: la salida de una capa depende de "
            "los tokens vecinos, de modo que el vector de «banco» cambia según la frase. El "
            "embedding de entrada sigue siendo estático; lo que se contextualiza es la "
            "representación que circula por la red."
        ),
        p(
            "Esta distinción explica por qué comparar embeddings de la primera capa tiene "
            "límites. Es útil para analizar el vocabulario y para tareas de recuperación, pero "
            "no sustituye a una representación contextual cuando el sentido depende de la "
            "frase. También explica por qué los modelos de recuperación modernos entrenan "
            "embeddings de frases o documentos completos, no solo de tokens."
        ),
        check(
            "Dos vectores tienen coseno 0,98 pero uno mide el doble que el otro. ¿Son muy similares según la similitud coseno?",
            "Sí. La similitud coseno normaliza por las normas, así que la longitud no afecta. "
            "Solo importa la dirección. Si lo que quieres medir es distancia absoluta, necesitas "
            "otra métrica, como la distancia euclídea.",
        ),
        h2("Cómo usarlos con criterio"),
        p(
            "Para explorar un vocabulario, calcula vecinos y revisa casos extremos. Para "
            "comparar modelos, usa el mismo conjunto de consultas y mide con métricas de la "
            "tarea, no solo la cohesión de los grupos. Para detectar sesgos, busca asociaciones "
            "sistemáticas entre atributos y grupos, y complementa la métrica con revisión "
            "cualitativa. La geometría es una herramienta potente, pero no se interpreta sola."
        ),
        p(
            "Con esto cierras el recorrido conceptual del capítulo: texto, tokens, IDs, "
            "ventanas, pares y vectores. La última lección ordena el mapa y te propone una "
            "autoevaluación. Si puedes explicar cada transición y calcular un par de cifras, "
            "tienes la base que el capítulo 3 necesita para entrar en la atención."
        ),
        keypoints(
            [
                "La similitud coseno compara direcciones y va de −1 a 1.",
                "Los vecinos cercanos reflejan contextos parecidos, no definiciones.",
                "Antónimos y palabras polisémicas pueden quedar cerca.",
                "Los embeddings estáticos no distinguen sentidos según la frase.",
                "Los sesgos del corpus se reflejan en la geometría.",
                "La métrica se interpreta junto a la tarea y a la revisión cualitativa.",
            ]
        ),
    ),
    key_points=(
        "El coseno mide el ángulo entre vectores, no su longitud.",
        "Vecinos cercanos indican contextos similares, no sinonimia garantizada.",
        "Los embeddings estáticos mezclan sentidos de palabras polisémicas.",
        "La geometría hereda sesgos del corpus.",
    ),
    quiz_id=None,
)
