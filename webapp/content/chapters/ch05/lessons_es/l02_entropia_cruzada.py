"""Lección 2 · Entropía cruzada y perplejidad."""

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
    slug="entropia-cruzada",
    title="Entropía cruzada y perplejidad",
    summary=(
        "La entropía cruzada convierte las probabilidades del modelo en una pérdida media; "
        "la perplejidad la devuelve a una escala más intuitiva."
    ),
    minutes=11,
    objectives=(
        "Calcular la entropía cruzada de un token y de un lote pequeño.",
        "Relacionar la pérdida media con la perplejidad mediante exp(L).",
        "Interpretar la perplejidad como número efectivo de candidatos.",
        "Explicar por qué la pérdida inicial depende del tamaño del vocabulario.",
    ),
    blocks=(
        lead(
            "La pérdida de un token es fácil de calcular, pero un modelo se entrena con "
            "millones de tokens. Necesitamos una cuenta que los resuma sin perder el "
            "significado. La <strong>entropía cruzada</strong> hace ese trabajo y la "
            "<strong>perplejidad</strong> la traduce a una unidad que se puede explicar sin "
            "logaritmos."
        ),
        h2("De una probabilidad a una pérdida"),
        p(
            "Para cada posición, el modelo produce una distribución sobre el vocabulario y el "
            "texto nos dice cuál era el token correcto. La entropía cruzada de esa posición "
            "es <code>−ln p(correcto)</code>. El signo negativo convierte un logaritmo "
            "negativo en una pérdida positiva: cuanto menor es la probabilidad asignada al "
            "token correcto, mayor es el castigo. Si el modelo está seguro y acierta, "
            "<code>p = 1</code> y la pérdida es 0. Si reparte la probabilidad entre todo el "
            "vocabulario, la pérdida se acerca a <code>ln V</code>."
        ),
        table(
            ["Probabilidad del token correcto", "Pérdida −ln p", "Lectura"],
            [
                ["1,00", "0,000", "El modelo no duda, pero esta seguridad puede ser excesiva"],
                ["0,50", "0,693", "La respuesta correcta es la más probable, sin gran margen"],
                ["0,10", "2,303", "Hay otras opciones mucho más favorecidas"],
                ["0,01", "4,605", "El token correcto está casi descartado"],
            ],
            caption="La pérdida crece de forma no lineal cuando la probabilidad se acerca a cero.",
            note="Logaritmo natural. Cambiar la base cambiaría el número, no el orden.",
        ),
        h2("Promediar un lote"),
        p(
            "Un lote de entrenamiento contiene <code>B·T</code> posiciones. La pérdida del "
            "lote es la media de las pérdidas individuales: "
            "<code>L = (1 / (B·T)) · Σ −ln p<sub>i</sub></code>. Cada token contribuye con "
            "una parte del total. Esa contribución permite detectar qué ejemplos dominan la "
            "señal: una probabilidad de 0,01 aporta 4,605, mientras que una de 0,90 aporta "
            "solo 0,105. El modelo dedica la mayor parte del gradiente a corregir los casos "
            "en los que está muy equivocado."
        ),
        p(
            "La media tiene una consecuencia importante: la pérdida no depende del número de "
            "tokens del lote de la misma forma que una suma. Dos lotes de distinto tamaño "
            "pueden compararse si ambos usan la media, pero el ruido será mayor en el lote "
            "pequeño. También conviene saber que la media se calcula sobre posiciones, así "
            "que una secuencia de 256 tokens pesa 256 veces más que una de un solo token."
        ),
        callout(
            "note",
            "Perplejidad no es porcentaje de error",
            "Una perplejidad de 10 no significa un 10 % de fallos. Significa que el modelo "
            "duda, en promedio, entre unos 10 candidatos efectivos. Una perplejidad de 1 "
            "sería una distribución perfectamente segura; una igual al tamaño del vocabulario "
            "sería una distribución uniforme. Es una escala relativa, no una nota."
        ),
        h2("La perplejidad"),
        p(
            "La perplejidad se define como <code>exp(L)</code>, la exponencial de la pérdida "
            "media. Su atractivo es que deshace el logaritmo: si el modelo asigna la misma "
            "probabilidad a <code>k</code> candidatos, su perplejidad es aproximadamente "
            "<code>k</code>. En el ejemplo del libro, una pérdida de 10,794 sobre un "
            "vocabulario de 50 257 tokens produce una perplejidad de 48 725,82. El modelo "
            "inicial está cerca de repartir la probabilidad entre todo el vocabulario. "
            "Después de entrenar, la pérdida baja y la perplejidad también."
        ),
        p(
            "La perplejidad hereda la dependencia del vocabulario. Un modelo con 1 000 tokens "
            "puede tener una perplejidad de 50 y otro con 50 000 una de 5 000; eso no dice "
            "por sí solo cuál es mejor. Para comparar modelos, usa el mismo tokenizador y el "
            "mismo conjunto de evaluación. La perplejidad es útil para seguir la evolución "
            "dentro de un experimento, no para enfrentar números de configuraciones distintas."
        ),
        table(
            ["Token", "p(correcto)", "Pérdida", "Contribución a la media"],
            [
                ["1", "0,90", "0,105", "0,026"],
                ["2", "0,50", "0,693", "0,173"],
                ["3", "0,10", "2,303", "0,576"],
                ["4", "0,25", "1,386", "0,347"],
            ],
            caption=(
                "Lote de cuatro tokens: pérdida media 1,122 y perplejidad "
                "exp(1,122) ≈ 3,07."
            ),
            note="Las contribuciones suman la pérdida media del lote.",
        ),
        py(
            """
import math

probabilidades = [0.90, 0.50, 0.10, 0.25]
perdidas = [-math.log(p) for p in probabilidades]
media = sum(perdidas) / len(perdidas)
perplejidad = math.exp(media)

for i, (p, loss) in enumerate(zip(probabilidades, perdidas), start=1):
    print(f"Token {i}: p={p:.2f}  pérdida={loss:.3f}")

print(f"Pérdida media: {media:.3f}")
print(f"Perplejidad: {perplejidad:.2f}")
""",
            caption=(
                "Entropía cruzada y perplejidad de un lote de cuatro tokens. Cambia las "
                "probabilidades para ver cómo responde la media."
            ),
        ),
        lab("loss"),
        p(
            "El laboratorio de pérdida convierte esta tabla en un control interactivo. Cada "
            "token tiene una probabilidad asignada al objetivo; al moverla cambian su pérdida, "
            "la media del lote y la perplejidad. Observa dos cosas: la curva se dispara cuando "
            "la probabilidad se acerca a cero y la media se mueve más despacio que un token "
            "individual. Esa diferencia entre el detalle y el resumen es la que se ve durante "
            "el entrenamiento."
        ),
        check(
            "Un token recibe una probabilidad de 0,50 y otro de 0,10. ¿Cuál aporta más a la "
            "pérdida del lote y cuánto vale la perplejidad si solo existieran esos dos tokens?",
            "El de 0,10 aporta 2,303 frente a 0,693 del primero. La pérdida media sería "
            "(0,693 + 2,303) / 2 = 1,498 y la perplejidad, exp(1,498) ≈ 4,47. La media se "
            "calcula sobre los dos tokens, no sobre sus probabilidades."
        ),
        keypoints(
            [
                "La entropía cruzada de un token es −ln de la probabilidad del token correcto.",
                "La pérdida de un lote es la media de las pérdidas de sus posiciones.",
                "Los tokens con probabilidad muy baja dominan la pérdida y el gradiente.",
                "La perplejidad es exp(L) y se interpreta como candidatos efectivos.",
                "Pérdida y perplejidad dependen del tamaño del vocabulario.",
                "Para comparar modelos, usa el mismo tokenizador y el mismo conjunto.",
            ]
        ),
    ),
    key_points=(
        "La pérdida media de un lote es la entropía cruzada de sus posiciones.",
        "−ln p convierte probabilidades en una escala aditiva y estable.",
        "La perplejidad es exp(L) y expresa la incertidumbre efectiva.",
        "Los errores con p muy baja contribuyen mucho más a la media.",
        "La pérdida inicial se parece a ln(V) y depende del vocabulario.",
    ),
)
