"""Lección 6 · Evaluar respuestas."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=6,
    slug="evaluar-instrucciones",
    title="Evaluar respuestas",
    summary=(
        "La exactitud de clasificación no sirve para respuestas abiertas. Se evalúan "
        "utilidad, fidelidad y formato con referencias, personas y modelos jueces."
    ),
    minutes=10,
    objectives=(
        "Explicar por qué la evaluación de texto abierto es multidimensional.",
        "Comparar benchmarks, evaluación humana y evaluación automática con LLM.",
        "Interpretar una puntuación media y sus límites.",
        "Calcular exactitud y F1 de tokens en un conjunto pequeño.",
    ),
    blocks=(
        lead(
            "En el capítulo anterior, una respuesta era spam o no lo era, y la exactitud "
            "resolvía la pregunta. Aquí una respuesta puede ser correcta pero larga, útil "
            "pero mal formateada, o fluida pero falsa. Evaluar instrucciones exige decidir "
            "qué significa «buena» y aceptar que ninguna métrica sola responde a esa pregunta."
        ),
        p(
            "El libro reserva 110 ejemplos para prueba. Para cada uno genera hasta 256 "
            "tokens, recorta el texto de la instrucción y guarda la respuesta del modelo "
            "junto a la referencia. En los primeros tres casos, la inspección manual muestra "
            "un acierto claro, una respuesta parcialmente correcta y otro acierto. Esa "
            "lectura es valiosa, pero no escala: revisar cientos de respuestas una por una "
            "consume tiempo y es difícil de repetir con el mismo criterio."
        ),
        h2("Tres familias de evaluación"),
        bullets(
            [
                "<strong>Benchmarks de respuesta corta o elección múltiple:</strong> miden "
                "conocimiento y razonamiento con una respuesta verificable, como MMLU. Son "
                "fáciles de puntuar, pero no capturan una conversación abierta.",
                "<strong>Comparación humana:</strong> personas leen respuestas y las puntúan "
                "o las prefieren frente a otro modelo. Es el patrón de referencia, aunque "
                "caro, lento y sujeto a variabilidad entre anotadores.",
                "<strong>Evaluación automática con otro LLM:</strong> un modelo mayor actúa "
                "como juez con una rúbrica. Es barato y repetible, pero aproxima el juicio "
                "humano y hereda sesgos.",
            ]
        ),
        p(
            "El libro opta por la tercera vía para cuantificar el conjunto completo. Usa "
            "Llama 3 de 8 mil millones de parámetros, ejecutado localmente con Ollama, y le "
            "pide una puntuación de 0 a 100 para cada respuesta, comparándola con la "
            "referencia. El resultado del modelo ajustado es una media de "
            "<strong>54,16</strong>. Como contexto, el Llama 3 base sin ajuste obtiene 58,51 "
            "con la misma metodología, y el Llama 3 instruct, ajustado con un dataset general, "
            "alcanza 82,6. Son cifras del libro y sirven para comparar configuraciones, no "
            "para declarar que un modelo es «bueno» en abstracto. La puntuación es una señal, "
            "no una certificación."
        ),
        h2("Utilidad, fidelidad, formato y límites"),
        p(
            "Una rúbrica útil separa dimensiones. La <strong>utilidad</strong> pregunta si la "
            "respuesta resuelve la tarea. La <strong>fidelidad</strong> comprueba si lo que "
            "afirma está respaldado por la entrada o por una fuente fiable. El "
            "<strong>formato</strong> verifica que se respeta la estructura pedida y que la "
            "generación termina. La <strong>seguridad</strong> añade una capa: rechazar lo "
            "que debe rechazarse sin caer en rechazos excesivos. Un juez único que devuelve "
            "un número comprime todas esas dimensiones y puede premiar la verbosidad o el "
            "estilo aunque la respuesta sea incorrecta."
        ),
        p(
            "Las métricas automáticas clásicas siguen siendo útiles. La exactitud compara la "
            "respuesta normalizada con la referencia; el F1 de tokens mide el solapamiento "
            "parcial y perdona pequeñas diferencias de forma. Ninguna entiende de sinónimos "
            "ni de corrección factual. Además, un juez LLM no es determinista, puede variar "
            "entre ejecuciones y tiende a preferir respuestas largas o al propio modelo que "
            "lo generó. Por eso se calibra con una muestra humana, se fija la rúbrica y se "
            "repiten las medidas cuando la decisión es importante."
        ),
        py(
            """
from collections import Counter

def normalizar(texto):
    tabla = str.maketrans("áéíóúüñ", "aeiouun", ".,;:!?¿¡\\"'()")
    return " ".join(texto.lower().translate(tabla).split())

def exactitud(prediccion, referencia):
    return float(normalizar(prediccion) == normalizar(referencia))

def f1_tokens(prediccion, referencia):
    p = normalizar(prediccion).split()
    r = normalizar(referencia).split()
    if not p or not r:
        return 0.0
    aciertos = sum((Counter(p) & Counter(r)).values())
    if aciertos == 0:
        return 0.0
    precision = aciertos / len(p)
    recall = aciertos / len(r)
    return 2 * precision * recall / (precision + recall)

ejemplos = [
    ("La cena es cocinada cada día por el chef.",
     "La cena es cocinada cada día por el chef."),
    ("Cumulus.", "Cumulonimbus."),
    ("La autora es Jane Austen.", "Jane Austen."),
]

for i, (prediccion, referencia) in enumerate(ejemplos, start=1):
    em = exactitud(prediccion, referencia)
    f1 = f1_tokens(prediccion, referencia)
    print(f"Ejemplo {i}: exactitud={em:.2f}  f1={f1:.4f}")

media_em = sum(exactitud(p, r) for p, r in ejemplos) / len(ejemplos)
media_f1 = sum(f1_tokens(p, r) for p, r in ejemplos) / len(ejemplos)
print(f"Media: exactitud={media_em:.4f}  f1={media_f1:.4f}")
""",
            caption=(
                "Normalización, exactitud y F1 de tokens. El segundo ejemplo no comparte "
                "ningún token con la referencia; el tercero obtiene un F1 parcial."
            ),
        ),
        callout(
            "warning",
            "El juez no es el tribunal",
            "Una media de 54 sobre 100 no significa que el modelo sea «medio» en términos "
            "absolutos: significa que ese juez, con esa rúbrica y ese conjunto, puntuó así. "
            "Cambiar el prompt del juez, el orden de las respuestas o el modelo evaluador "
            "puede mover el resultado. Documenta la configuración y valida con personas.",
        ),
        check(
            "¿Qué dos comprobaciones harías antes de confiar en una evaluación automática?",
            "Calibrarla con una muestra puntuada por personas y comprobar su estabilidad "
            "repitiendo la evaluación o cambiando el orden de las respuestas. También "
            "revisaría que la rúbrica mida utilidad, fidelidad y formato, no solo estilo.",
        ),
        keypoints(
            [
                "La evaluación de texto abierto no se reduce a exactitud.",
                "Utilidad, fidelidad, formato y seguridad son dimensiones distintas.",
                "El libro usa 110 ejemplos de prueba y un juez Llama 3 de 8B.",
                "La media del modelo ajustado es 54,16; la referencia instruct, 82,6.",
                "Exactitud y F1 de tokens miden solapamiento, no comprensión.",
                "Todo juez LLM necesita calibración humana y control de sesgos.",
            ]
        ),
    ),
    key_points=(
        "Las respuestas abiertas se evalúan con varias dimensiones y varias fuentes.",
        "Benchmarks, personas y jueces automáticos responden a preguntas distintas.",
        "Una puntuación media es descriptiva de un conjunto y una rúbrica concretos.",
        "La evaluación automática se calibra con revisión humana.",
    ),
)
