"""Lección 5 · La máscara causal."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=5,
    slug="mascara-causal",
    title="La máscara causal",
    summary=(
        "En un modelo generativo, cada posición solo puede mirar su pasado. La máscara causal "
        "convierte esa restricción en ceros exactos antes de softmax."
    ),
    minutes=10,
    objectives=(
        "Explicar por qué la generación autorregresiva necesita una máscara.",
        "Construir una máscara triangular inferior.",
        "Aplicar −∞ antes de softmax y comprobar que las filas suman uno.",
        "Distinguir el enmascaramiento causal del dropout.",
    ),
    blocks=(
        lead(
            "GPT se entrena para predecir el siguiente token. Si al calcular la representación de "
            "la posición 3 el modelo pudiera leer la posición 4, la tarea sería trampa: la "
            "respuesta estaría en la entrada. La <strong>máscara causal</strong> impide esa fuga y "
            "obliga a cada posición a construirse solo con lo que ya ha visto."
        ),
        p(
            "Sin máscara, la self-attention es bidireccional: cada token puede consultar los de la "
            "izquierda y los de la derecha. Eso es útil para tareas de comprensión, como clasificar "
            "una frase completa, pero incompatible con la generación de izquierda a derecha. "
            "Durante el entrenamiento procesamos todas las posiciones a la vez para aprovechar la "
            "GPU; la máscara permite hacerlo sin que las posiciones futuras se filtren en las "
            "representaciones pasadas."
        ),
        h2("Una matriz triangular inferior"),
        p(
            "Para una secuencia de tres tokens, la máscara permite la posición 1 mirar a la 1; la "
            "2, a la 1 y a la 2; la 3, a las tres. La matriz de permisos es triangular inferior: "
            "unos en la diagonal y por debajo, ceros por encima. Si las puntuaciones son "
            "S = [[2,0, 1,0, 0,5], [1,5, 2,5, 0,8], [0,7, 1,2, 3,0]], la máscara deja intactas las "
            "entradas permitidas y sustituye las futuras por −∞."
        ),
        table(
            ["Desde ↓ / Hacia →", "t1", "t2", "t3"],
            [
                ["t1", "2,0", "−∞", "−∞"],
                ["t2", "1,5", "2,5", "−∞"],
                ["t3", "0,7", "1,2", "3,0"],
            ],
            caption=(
                "Puntuaciones después de aplicar la máscara causal. Las posiciones futuras se "
                "marcan con −∞ antes de softmax; las pasadas y la actual se conservan."
            ),
            note="Ejemplo didáctico de tres tokens; los valores no proceden de un modelo entrenado.",
        ),
        p(
            "Al aplicar softmax, exp(−∞) tiende a cero, así que las posiciones enmascaradas "
            "reciben exactamente peso cero. La normalización se recalcula sobre las posiciones "
            "restantes y cada fila vuelve a sumar uno. Con las puntuaciones del ejemplo, la "
            "primera fila queda en [1,000, 0, 0]; la segunda, en [0,269, 0,731, 0]; la tercera, en "
            "[0,079, 0,131, 0,790]. El token 1 solo se mira a sí mismo; el token 2 reparte entre el "
            "1 y el 2; el token 3 puede usar los tres."
        ),
        figure(
            "img/ch03/mascara-causal.svg",
            "Matriz de puntuaciones con la parte superior derecha sustituida por menos infinito y, a la derecha, la matriz de pesos normalizada con ceros en las posiciones futuras.",
            "La máscara se aplica antes de softmax: las posiciones futuras pasan a −∞ y su "
            "contribución desaparece. Cada fila resultante suma uno.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("Qué se filtra y qué no"),
        p(
            "La máscara no oculta el token actual ni el pasado: la diagonal y la parte inferior "
            "quedan visibles. Tampoco cambia los valores V; solo decide qué valores se mezclan. Si "
            "se aplica después de softmax en lugar de antes, hay que volver a normalizar la fila, "
            "porque los pesos restantes ya no suman uno. Hacerlo mal es una fuente clásica de "
            "fugas de información: el modelo puede acabar usando, a través de la normalización, "
            "algo que creía haber enmascarado."
        ),
        p(
            "El enmascaramiento causal se combina a menudo con <strong>dropout</strong>, que apaga "
            "aleatoriamente una parte de los pesos durante el entrenamiento para reducir el "
            "sobreajuste. Son mecanismos distintos: la máscara es estructural y determinista; el "
            "dropout es aleatorio y solo se activa mientras se entrena. En el libro se usa una "
            "tasa de dropout del 50 % para ilustrar el efecto, aunque al entrenar GPT se emplean "
            "tasas menores, como 0,1 o 0,2."
        ),
        h2("Generación y contexto"),
        p(
            "En inferencia, un modelo decoder-only suele generar un token cada vez. La máscara "
            "sigue presente cuando se procesa el prompt completo, porque el modelo calcula las "
            "representaciones de todas las posiciones en paralelo. Después, cada nuevo token se "
            "añade a la secuencia y vuelve a pasar por el bloque. La máscara garantiza que la "
            "representación de una posición nunca dependa de tokens que aún no existían cuando se "
            "calculó."
        ),
        p(
            "La máscara tampoco convierte al modelo en un buscador del pasado perfecto. Solo "
            "restringe el acceso; la calidad de lo que se recupera depende de las proyecciones y "
            "del entrenamiento. Un token puede mirar una posición y no extraer nada útil de ella. "
            "La atención causal es una condición necesaria para generar, no una garantía de "
            "coherencia."
        ),
        callout(
            "warning",
            "Enmascarar no es explicar",
            "Que una posición no pueda mirar al futuro no significa que el modelo haya aprendido "
            "una noción humana de causalidad. La máscara es una restricción del cálculo. Las "
            "relaciones que aprende dentro del pasado pueden seguir siendo correlaciones "
            "superficiales o atajos del corpus.",
        ),
        check(
            "¿Por qué se usa −∞ antes de softmax en lugar de poner un cero directamente en las "
            "puntuaciones futuras?",
            "Porque exp(0) = 1: un cero en las puntuaciones seguiría contribuyendo a la suma de "
            "softmax y daría un peso no nulo a la posición futura. Con −∞, la exponencial es "
            "exactamente cero, así que la posición enmascarada no participa y la fila se "
            "renormaliza solo con las posiciones permitidas.",
        ),
        py(
            """
import math

TOKENS = ["t1", "t2", "t3"]
PUNTUACIONES = [
    [2.0, 1.0, 0.5],
    [1.5, 2.5, 0.8],
    [0.7, 1.2, 3.0],
]

def softmax(fila):
    maximo = max(fila)
    exp = [math.exp(valor - maximo) if valor != float("-inf") else 0.0 for valor in fila]
    total = sum(exp)
    return [valor / total for valor in exp]

print("Máscara causal: -inf en el futuro")
masked = []
for i, fila in enumerate(PUNTUACIONES):
    nueva = [valor if j <= i else float("-inf") for j, valor in enumerate(fila)]
    masked.append(nueva)
    print(TOKENS[i], nueva)

print("\\nPesos después de softmax:")
for token, fila in zip(TOKENS, masked):
    pesos = softmax(fila)
    print(token, [round(valor, 4) for valor in pesos], "suma:", round(sum(pesos), 6))
""",
            caption=(
                "Máscara causal sobre una matriz 3 × 3. La parte superior se marca con −∞ y "
                "softmax la convierte en ceros exactos."
            ),
        ),
        keypoints(
            [
                "La máscara causal impide que una posición vea tokens futuros.",
                "Se implementa como una matriz triangular inferior de permisos.",
                "Las posiciones futuras se sustituyen por −∞ antes de softmax.",
                "Exp(−∞) es cero: la fila se normaliza solo con pasado y presente.",
                "La máscara es estructural; el dropout es aleatorio y solo actúa al entrenar.",
                "La generación autorregresiva necesita esta restricción.",
            ]
        ),
    ),
    key_points=(
        "La máscara causal restringe cada posición a su pasado y a sí misma.",
        "Se aplica antes de softmax con −∞ en las posiciones futuras.",
        "Los pesos enmascarados quedan exactamente en cero y las filas suman uno.",
        "Enmascarar después de softmax exige renormalizar y es propenso a errores.",
        "La máscara es una restricción de cálculo, no una explicación de causalidad.",
    ),
)
