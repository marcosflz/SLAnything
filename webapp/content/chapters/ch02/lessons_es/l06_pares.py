"""Lección 6 · Pares entrada → objetivo."""

from webapp.content.schema import (
    Lesson,
    bullets,
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
    number=6,
    slug="pares-entrada-objetivo",
    title="Pares entrada → objetivo",
    summary=(
        "Cada ventana se convierte en dos secuencias: la entrada y el objetivo desplazado un "
        "token. El modelo aprende a predecir, en cada posición, el token que viene después."
    ),
    minutes=10,
    objectives=(
        "Construir el par x → y a partir de una secuencia de IDs.",
        "Explicar por qué el objetivo es la entrada desplazada una posición.",
        "Describir la forma de un lote y el papel de la máscara causal.",
        "Interpretar la pérdida de entropía cruzada en este contexto.",
    ),
    blocks=(
        lead(
            "Ya tenemos ventanas de IDs. Falta convertirlas en el par que necesita el "
            "entrenamiento: una entrada <code>x</code> y un objetivo <code>y</code>. La regla "
            "es tan simple que casi parece trampa: <strong>y es x desplazado un token a la "
            "izquierda</strong>. El texto proporciona la etiqueta sin anotación humana."
        ),
        p(
            "El libro lo muestra con cuatro tokens. Si la entrada es <code>[290, 4920, 2241, 287]</code>, "
            "el objetivo es <code>[4920, 2241, 287, 257]</code>. La primera posición aprende a "
            "predecir 4920 a partir de 290; la segunda, a predecir 2241 a partir de 290 y 4920; "
            "y así sucesivamente. En texto: «and» → «established»; «and established» → «himself»; "
            "«and established himself» → «in». Cada prefijo es una entrada válida y el token "
            "siguiente es su etiqueta."
        ),
        bullets(
            [
                "<strong>x</strong>: los IDs que el modelo ve en un paso.",
                "<strong>y</strong>: los IDs que debería predecir, uno por posición.",
                "<strong>Desplazamiento</strong>: y[i] = x[i + 1] dentro de la ventana.",
                "<strong>Ventana</strong>: el fragmento de contexto que se recorta del corpus.",
                "<strong>Lote</strong>: varias ventanas apiladas para procesarlas juntas.",
            ]
        ),
        h2("Una ventana, varias predicciones"),
        p(
            "Es tentador pensar que una ventana de 256 tokens produce un único ejemplo de "
            "entrenamiento. No es así: produce <strong>256 predicciones</strong>, una por "
            "posición. La entrada completa pasa por el transformer y la salida tiene la misma "
            "longitud. En cada posición hay un vector de logits sobre el vocabulario, y la "
            "pérdida compara ese vector con el token correcto. La pérdida total es la media de "
            "las pérdidas por posición."
        ),
        p(
            "Ese diseño es lo que hace eficiente el entrenamiento. En lugar de cortar el texto "
            "en 256 ejemplos de un solo token, se procesa una secuencia y se reutilizan los "
            "cálculos. La máscara causal impide que la posición <code>i</code> mire posiciones "
            "futuras: si pudiera ver <code>x[i+1]</code>, la tarea sería copiar y no predecir. "
            "La atención solo mira hacia atrás."
        ),
        table(
            ["Elemento", "Forma", "Ejemplo", "Qué contiene"],
            [
                ["IDs de entrada", "(batch, contexto)", "(8, 4)", "8 ventanas de 4 tokens"],
                ["IDs objetivo", "(batch, contexto)", "(8, 4)", "Las mismas, desplazadas"],
                ["Embeddings", "(batch, contexto, d)", "(8, 4, 256)", "Un vector por token"],
                ["Logits", "(batch, contexto, V)", "(8, 4, 50 257)", "Una puntuación por token del vocabulario"],
                ["Pérdida", "escalar", "2,31", "Media de las 32 posiciones del lote"],
            ],
            caption="Formas típicas en un lote de entrenamiento. La última dimensión es el vocabulario.",
            note=(
                "El ejemplo usa batch 8, contexto 4 y dimensión 256, como en el libro. Los "
                "50 257 y la pérdida 2,31 son ilustrativos."
            ),
        ),
        h2("El código que construye los pares"),
        p(
            "El siguiente ejemplo parte de una lista de IDs y genera ventanas con su objetivo. "
            "Después cuenta cuántas predicciones aporta cada ventana. Cambia el contexto, el "
            "stride o la secuencia y observa cómo cambian las formas."
        ),
        py(
            """
IDS = [40, 367, 2885, 1464, 1807, 3619, 402, 271, 10899]
CONTEXTO = 4
STRIDE = 2


def ventanas(ids, contexto, stride):
    pares = []
    for inicio in range(0, len(ids) - contexto + 1, stride):
        x = ids[inicio:inicio + contexto]
        y = ids[inicio + 1:inicio + contexto + 1]
        pares.append((x, y))
    return pares


pares = ventanas(IDS, CONTEXTO, STRIDE)
print(f"Secuencia de {len(IDS)} IDs, contexto {CONTEXTO}, stride {STRIDE}")
print(f"Ventanas completas: {len(pares)}")
for numero, (x, y) in enumerate(pares, start=1):
    print(f"  {numero}. x={x}  y={y}")

predicciones = sum(len(y) for _, y in pares)
print(f"Predicciones totales: {predicciones}")

# Pérdida de entropía cruzada para una predicción concreta.
import math

probabilidad = 0.8
pérdida = -math.log(probabilidad)
print(f"Si p(token correcto)=0.8, pérdida={pérdida:.3f}")
print(f"Si p(token correcto)=0.1, pérdida={-math.log(0.1):.3f}")
""",
            caption=(
                "Construcción de pares x → y y cálculo de la pérdida para una predicción. "
                "Prueba con contexto 2, 4 u 8 y con stride 1 o 2."
            ),
        ),
        lab("labels"),
        callout(
            "info",
            "La etiqueta no es un juicio humano",
            "El objetivo no dice si la frase es buena, verdadera o adecuada: dice qué token "
            "vino después en el corpus. El modelo aprende regularidades estadísticas del texto, "
            "incluidos sus sesgos. Esa es la razón por la que la calidad y el filtrado del "
            "corpus importan tanto.",
        ),
        p(
            "La función de pérdida habitual es la <strong>entropía cruzada</strong>. Para cada "
            "posición, el modelo produce una distribución de probabilidad sobre el vocabulario "
            "y la pérdida es <code>−log p(token correcto)</code>. Si asigna probabilidad 0,8 al "
            "token correcto, la pérdida es 0,223; si asigna 0,1, sube a 2,303. La media sobre "
            "todas las posiciones del lote produce un único número que se usa para actualizar "
            "los pesos. Son valores de ejemplo, no resultados de un modelo entrenado."
        ),
        h2("Lotes y estabilidad"),
        p(
            "Un lote de ocho ventanas de cuatro tokens produce una matriz de 8 × 4 de IDs y, "
            "tras los embeddings, un tensor de 8 × 4 × 256. La pérdida se calcula sobre las 32 "
            "posiciones. Con lotes mayores, el gradiente es menos ruidoso pero se necesita más "
            "memoria. El libro recuerda que el tamaño de lote es un hiperparámetro: no hay un "
            "valor universal, y lotes pequeños pueden dar actualizaciones más ruidosas."
        ),
        p(
            "También conviene descartar el último lote si no está completo. Si el corpus no se "
            "divide exactamente, un lote de tamaño menor puede producir un pico de pérdida y "
            "desestabilizar el entrenamiento. Por eso muchas implementaciones usan "
            "<code>drop_last=True</code>."
        ),
        check(
            "Si x = [10, 20, 30, 40], ¿cuál es y con contexto 4 y qué predice la última posición?",
            "y = [20, 30, 40, siguiente]. La última posición de x es 40; el modelo debe predecir "
            "el token que aparece después de 40 en la secuencia original. Ese token no está en "
            "x: está en la posición i+1 de la ventana, y por eso el objetivo se construye "
            "desplazado.",
        ),
        h2("Del par a la práctica"),
        p(
            "Con los pares ya construidos, el pipeline de datos está casi completo: texto → "
            "tokens → IDs → ventanas → pares. Solo falta convertir los IDs en vectores y añadir "
            "la posición. Esas dos operaciones son el puente hacia el transformer y ocupan las "
            "dos últimas lecciones del capítulo."
        ),
        p(
            "Antes de seguir, comprueba que puedes explicar por qué una ventana de cuatro tokens "
            "genera cuatro predicciones y no una. Si la respuesta es «porque el modelo produce "
            "una salida por posición y todas se comparan con el token siguiente», has entendido "
            "el mecanismo central del pretraining."
        ),
        keypoints(
            [
                "El objetivo y es la entrada x desplazada un token.",
                "Cada posición de la ventana genera una predicción.",
                "La máscara causal impide mirar tokens futuros.",
                "La pérdida es la media de −log p(token correcto) sobre las posiciones.",
                "Un lote apila ventanas y añade una dimensión al tensor.",
                "La etiqueta proviene del texto, no de anotación humana.",
            ]
        ),
    ),
    key_points=(
        "x e y son la misma secuencia desplazada una posición.",
        "Una ventana de L tokens produce L predicciones.",
        "La máscara causal evita que el modelo vea el futuro.",
        "La entropía cruzada mide la probabilidad asignada al token correcto.",
        "El tamaño de lote equilibra memoria y estabilidad del gradiente.",
    ),
    quiz_id=None,
)
