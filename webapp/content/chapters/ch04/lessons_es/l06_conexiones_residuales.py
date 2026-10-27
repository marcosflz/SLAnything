"""Lección 6 · Conexiones residuales."""

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
)

LESSON = Lesson(
    number=6,
    slug="conexiones-residuales",
    title="Conexiones residuales",
    summary=(
        "La suma x + f(x) que da al gradiente un camino directo, comparada con una red "
        "profunda sin atajos y con una simulación numérica del efecto."
    ),
    minutes=10,
    objectives=(
        "Explicar el problema del gradiente que se desvanece en redes profundas.",
        "Describir qué suma una conexión residual y qué exige.",
        "Interpretar el experimento de gradientes del libro.",
        "Relacionar los residuales con la profundidad de GPT-2.",
    ),
    blocks=(
        lead(
            "Una conexión residual es una de las operaciones más simples de todo el "
            "modelo: sumar la entrada de una capa a su salida. No tiene parámetros, no "
            "ocupa memoria y se escribe en una línea. Sin embargo, es lo que permite que "
            "GPT-2 apile doce bloques sin que el gradiente se desvanezca por el camino. "
            "Entender por qué exige mirar hacia atrás, hacia la propagación del error."
        ),
        h2("El problema del gradiente"),
        p(
            "Durante el entrenamiento, la red calcula una pérdida y propaga su derivada "
            "hacia atrás, capa por capa, para actualizar los pesos. Cada capa multiplica el "
            "gradiente por sus derivadas locales. Si esos factores son pequeños, el "
            "gradiente llega a las primeras capas casi a cero: es el "
            "<strong>problema del gradiente que se desvanece</strong>. Si son grandes, "
            "explota. En una red de cinco capas el efecto puede ser moderado; en una pila "
            "de doce o de noventa y seis, se acumula."
        ),
        p(
            "El libro lo ilustra con una red de cinco capas y una pérdida cuadrática. Sin "
            "atajos, la media absoluta del gradiente cae desde 0,00505 en la última capa "
            "hasta 0,00020 en la primera. Con conexiones residuales, la última capa sigue "
            "teniendo el gradiente mayor, pero la primera conserva 0,22170 y las "
            "intermedias se mantienen en un rango mucho más estable. Son cifras de un "
            "experimento ilustrativo con una semilla concreta, no una ley universal; lo "
            "que muestran es el mecanismo, no un valor que haya que memorizar."
        ),
        figure(
            "img/ch04/conexiones-residuales.svg",
            "Comparación de una red profunda sin conexiones residuales, con gradientes que se desvanecen, y otra con atajos que conservan un camino directo.",
            "Sin residual, el gradiente se hace diminuto al alejarse de la salida. Con "
            "residual, la identidad ofrece un camino directo y el gradiente llega a las "
            "primeras capas con un orden de magnitud mucho mayor.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("Una identidad que atraviesa el bloque"),
        p(
            "La conexión residual crea un camino alternativo. En lugar de calcular "
            "<code>x = f(x)</code>, el bloque calcula <code>x = x + f(x)</code>. Al derivar, "
            "aparece un término constante: la derivada de la identidad es uno. Ese uno "
            "significa que, aunque la derivada de <code>f</code> sea pequeña, el gradiente "
            "siempre tiene una vía para retroceder sin multiplicarse por todas las capas. "
            "La subcapa puede aprender una transformación pequeña —incluso cercana a "
            "cero— sin bloquear el flujo de información."
        ),
        p(
            "En el bloque transformer hay dos residuales: uno alrededor de la atención y "
            "otro alrededor de la FFN. Ambos suman sobre el mismo vector de 768 "
            "dimensiones. Esa acumulación se suele llamar <strong>corriente "
            "residual</strong>: un camino principal que atraviesa todos los bloques y va "
            "recibiendo las aportaciones de cada subcapa. La atención y la FFN no "
            "sustituyen ese camino; escriben sobre él. Esa arquitectura facilita el "
            "entrenamiento y permite que la información de la entrada llegue lejos sin "
            "degradarse por completo."
        ),
        py(
            """
# Simulación escalar propia: no reproduce el experimento de PyTorch del libro.
# Cada capa multiplica el gradiente por 0,5; el residual añade un camino de identidad.
derivada_capa = 0.5
capas = 5

sin_residual = derivada_capa ** capas
con_residual = (1 + derivada_capa) ** capas

print(f"Gradiente relativo sin residual: {sin_residual:.6f}")
print(f"Gradiente relativo con residual: {con_residual:.6f}")
print(f"Mejora de escala: x{con_residual / sin_residual:.1f}")

print()
gradiente = 1.0
for capa in range(capas, 0, -1):
    gradiente *= derivada_capa
    print(f"Capa {capa} sin residual: {gradiente:.6f}")

gradiente = 1.0
for capa in range(capas, 0, -1):
    gradiente *= (1 + derivada_capa)
    print(f"Capa {capa} con residual: {gradiente:.6f}")
""",
            caption=(
                "Ejemplo didáctico con derivadas constantes. El residual no elimina la "
                "multiplicación, pero añade un factor (1 + f') que evita la caída "
                "exponencial del gradiente."
            ),
        ),
        p(
            "La simulación exagera el efecto para que se vea: con cinco capas y una "
            "derivada de 0,5, el gradiente sin residual se reduce a 0,03125; con el atajo, "
            "asciende a 7,59375. En una red real las derivadas no son constantes ni el "
            "residual garantiza que todo entrene bien, pero el mecanismo es el mismo. La "
            "identidad no impide que la subcapa aprenda; le da un suelo desde el que "
            "hacerlo. Por eso los residuales aparecen en prácticamente todos los "
            "transformers modernos."
        ),
        callout(
            "tip",
            "Sumar no es concatenar",
            "Una conexión residual suma dos tensores de la misma forma; no los pega uno al "
            "lado del otro. Esa es la razón por la que la atención y la FFN deben devolver "
            "768 dimensiones. Si devolvieran otra forma, habría que proyectar antes de "
            "sumar o cambiar el diseño del bloque.",
        ),
        check(
            "Si una subcapa aprendiera la función cero, ¿qué haría el bloque con una "
            "conexión residual?",
            "Devolver la entrada sin cambios: <code>x + 0 = x</code>. Esa es la propiedad "
            "clave del camino de identidad. Sin residual, la salida sería cero y la "
            "información se perdería. Con residual, la subcapa puede no aportar nada en un "
            "momento dado sin destruir lo que ya había.",
        ),
        keypoints(
            [
                "El gradiente se desvanece cuando se multiplica por derivadas pequeñas capa tras capa.",
                "Una conexión residual suma la entrada de la subcapa a su salida.",
                "La identidad aporta un término constante que mantiene un camino para el gradiente.",
                "El libro compara gradientes sin y con atajos en una red de cinco capas.",
                "GPT-2 tiene dos residuales por bloque: uno para atención y otro para FFN.",
                "La corriente residual atraviesa todos los bloques y acumula sus aportaciones.",
            ]
        ),
    ),
    key_points=(
        "Las conexiones residuales mitigan el gradiente que se desvanece.",
        "La suma x + f(x) exige que entrada y salida tengan la misma forma.",
        "La identidad ofrece un camino directo para el gradiente y la información.",
        "El experimento del libro muestra gradientes mucho más estables con atajos.",
        "Cada bloque transformer tiene un residual para la atención y otro para la FFN.",
        "La corriente residual es el camino principal que atraviesa la pila.",
    ),
)
