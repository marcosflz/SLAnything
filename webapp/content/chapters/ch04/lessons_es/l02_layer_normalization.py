"""Lección 2 · Layer normalization."""

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
    number=2,
    slug="layer-normalization",
    title="Layer normalization",
    summary=(
        "Cómo LayerNorm centra y escala las activaciones de cada token, por qué "
        "estabiliza el entrenamiento y qué cambia al colocarla antes de cada subcapa."
    ),
    minutes=10,
    objectives=(
        "Explicar qué calcula LayerNorm y sobre qué dimensión lo hace.",
        "Interpretar el papel de epsilon, scale y shift.",
        "Comparar LayerNorm con BatchNorm en el contexto de un LLM.",
        "Situar la normalización Pre-LN dentro del bloque transformer.",
    ),
    blocks=(
        lead(
            "LayerNorm no cambia qué información contiene un vector: cambia su escala. "
            "Es una operación pequeña —una media, una varianza y dos parámetros por "
            "dimensión—, pero sin ella apilar doce bloques se vuelve frágil. Entenderla "
            "es entender por qué un transformer profundo puede entrenarse sin que las "
            "activaciones se disparen o se apaguen."
        ),
        h2("Media, varianza y dos parámetros"),
        p(
            "Para cada token, LayerNorm recorre sus 768 componentes, calcula la media y la "
            "varianza, resta la media y divide por la desviación típica. El resultado tiene "
            "media cero y varianza uno. Después aplica una escala y un desplazamiento "
            "aprendibles, uno por componente: la red puede recuperar una escala distinta "
            "si le conviene. La fórmula es "
            "<code>(x − μ) / sqrt(σ² + ε) · γ + β</code>, donde <code>ε</code> evita dividir "
            "por cero cuando la varianza es diminuta."
        ),
        p(
            "El libro usa <code>eps = 1e-5</code> y calcula la varianza dividiendo entre "
            "<em>n</em>, no entre <em>n − 1</em>. Es la llamada varianza sesgada, la misma "
            "convención que TensorFlow y los pesos originales de GPT-2. Con 768 componentes, "
            "la diferencia entre ambos denominadores es despreciable; lo importante es que "
            "el resultado sea reproducible y compatible con los pesos que se cargarán más "
            "adelante. Los parámetros <code>scale</code> y <code>shift</code> se inicializan "
            "a unos y ceros, y el entrenamiento los ajusta si mejora la pérdida."
        ),
        h2("Por qué estabiliza y por qué Pre-LN"),
        p(
            "En una red profunda, los gradientes se multiplican capa tras capa. Si los "
            "factores son algo menores que uno, el gradiente se desvanece; si son algo "
            "mayores, explota. Normalizar las activaciones mantiene su escala bajo control "
            "y hace que la pérdida se comporte de forma más predecible. En un transformer, "
            "LayerNorm se aplica antes de la atención y antes de la red feed-forward; "
            "después de cada subcapa se suma la conexión residual. Esa disposición se llama "
            "<strong>Pre-LN</strong> y es la que usa GPT-2. El transformer original aplicaba "
            "Post-LN, con la normalización después de la subcapa, y solía necesitar más "
            "cuidado para entrenar."
        ),
        p(
            "La diferencia con BatchNorm es importante. BatchNorm calcula estadísticas a "
            "través del lote para cada característica; su resultado depende de qué ejemplos "
            "hayan caído juntos y del tamaño del lote. LayerNorm calcula estadísticas "
            "dentro de cada token, con independencia del resto del lote. Eso encaja con "
            "LLMs, que a menudo se entrenan con lotes variables o se despliegan en "
            "entornos con recursos limitados. También encaja con la forma "
            "<code>[batch, tokens, 768]</code>: la normalización se aplica sobre la última "
            "dimensión y cada posición se trata por separado."
        ),
        py(
            """
import math

def layer_norm(row, eps=1e-5):
    mean = sum(row) / len(row)
    var = sum((x - mean) ** 2 for x in row) / len(row)
    norm = [(x - mean) / math.sqrt(var + eps) for x in row]
    return mean, var, norm

filas = [
    [0.9, -0.4, 0.2, 1.1, -0.8],
    [2.0, 2.1, 1.9, 2.2, 1.8],
]

for i, fila in enumerate(filas, start=1):
    media, varianza, salida = layer_norm(fila)
    media_out = sum(salida) / len(salida)
    var_out = sum((x - media_out) ** 2 for x in salida) / len(salida)
    print(f"Fila {i}: media={media:.3f}, varianza={varianza:.3f}")
    print("  normalizada:", [round(x, 3) for x in salida])
    print(f"  media de salida={media_out:.6f}, varianza de salida={var_out:.6f}")
""",
            caption=(
                "LayerNorm calculada a mano sobre dos vectores. El ejemplo es propio; "
                "sirve para comprobar que la salida queda con media 0 y varianza 1."
            ),
        ),
        callout(
            "info",
            "Normalizar no es perder información",
            "LayerNorm no borra la dirección del vector: la conserva y reescala sus "
            "componentes. La escala y el desplazamiento aprendibles permiten que la red "
            "recupere amplitudes útiles. Lo que se elimina es la deriva global de magnitud, "
            "no el contenido relativo de cada dimensión.",
        ),
        check(
            "¿Por qué LayerNorm funciona aunque el lote tenga un tamaño distinto en cada "
            "paso?",
            "Porque calcula media y varianza dentro de cada token, no a través del lote. "
            "Cada vector se normaliza con sus propias estadísticas, así que no depende de "
            "qué otros ejemplos lo acompañen. BatchNorm, en cambio, mezcla información del "
            "lote y necesita tamaños y distribuciones más estables.",
        ),
        keypoints(
            [
                "LayerNorm normaliza cada token a lo largo de la dimensión de embedding.",
                "La media y la varianza se calculan por vector, no por lote.",
                "Epsilon evita divisiones por cero; scale y shift son parámetros aprendibles.",
                "GPT-2 usa Pre-LN: normaliza antes de la atención y antes de la FFN.",
                "BatchNorm depende del lote; LayerNorm es más flexible para LLMs.",
                "La normalización estabiliza activaciones y gradientes en pilas profundas.",
            ]
        ),
    ),
    key_points=(
        "LayerNorm centra y escala cada token sobre sus 768 componentes.",
        "Usa media y varianza por vector, con epsilon para estabilidad numérica.",
        "Scale y shift permiten recuperar una escala útil durante el entrenamiento.",
        "Pre-LN normaliza antes de cada subcapa; es la opción de GPT-2.",
        "A diferencia de BatchNorm, no depende del tamaño ni de la composición del lote.",
        "Su función es mantener estables las activaciones y los gradientes.",
    ),
)
