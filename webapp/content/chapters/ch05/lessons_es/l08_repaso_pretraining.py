"""Lección 8 · Repaso y autoevaluación."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=8,
    slug="repaso-pretraining",
    title="Repaso y autoevaluación",
    summary=(
        "Un mapa de las ocho lecciones, los errores más frecuentes y una lista de "
        "comprobación para saber si puedes explicar el preentrenamiento sin recitar."
    ),
    minutes=10,
    objectives=(
        "Reconectar pérdida, entrenamiento, datos, evaluación, muestreo y coste.",
        "Detectar errores conceptuales frecuentes antes de la autoevaluación.",
        "Explicar el capítulo con las fórmulas y las formas de los tensores.",
        "Usar el quiz como diagnóstico, no como nota definitiva.",
    ),
    blocks=(
        lead(
            "El capítulo 5 parece una colección de recetas: una función de pérdida, un "
            "bucle, un cargador, un optimizador, una estrategia de muestreo y una "
            "calculadora. En realidad es una sola historia: un modelo aprende a asignar "
            "probabilidad al token siguiente, y todo lo demás existe para que ese aprendizaje "
            "sea medible, estable y sostenible. Este repaso comprueba que las piezas encajan."
        ),
        h2("El mapa en una tabla"),
        table(
            ["Pregunta", "Respuesta corta", "Lección"],
            [
                ["¿Qué se optimiza?", "La entropía cruzada media del siguiente token.", "1 y 2"],
                ["¿Cómo se actualiza?", "zero_grad → forward → backward → step, por épocas.", "3 y 4"],
                ["¿Qué ve el modelo?", "Ventanas de tokens agrupadas en lotes.", "5"],
                ["¿Cómo sabemos si generaliza?", "Pérdida de validación y muestras de texto.", "6"],
                ["¿Cuánto cuesta?", "FLOPs ≈ 6 · N · D; GPU-horas y memoria.", "7"],
            ],
            caption="Las cinco preguntas que resumen el preentrenamiento.",
            note="Si puedes responderlas con un ejemplo numérico, has entendido la estructura.",
        ),
        h2("Cinco errores que conviene evitar"),
        bullets(
            [
                "<strong>Confundir pérdida con acierto.</strong> Una pérdida baja no garantiza "
                "texto verdadero ni útil; mide probabilidad asignada, no corrección factual.",
                "<strong>Comparar pérdidas entre tokenizadores.</strong> La escala de referencia "
                "depende de ln(V). Cambia el vocabulario y cambia el punto de partida.",
                "<strong>Olvidar zero_grad.</strong> Los gradientes se acumulan y el paso efectivo "
                "se vuelve impredecible.",
                "<strong>Evaluar con dropout activo.</strong> Sin model.eval(), la métrica de "
                "validación es inestable y difícil de comparar.",
                "<strong>Creer que una muestra es una evaluación.</strong> Una generación "
                "afortunada no compensa una curva de validación que empeora.",
            ]
        ),
        p(
            "Hay un sexto error, más sutil: mirar solo el número final. La pérdida de "
            "entrenamiento puede bajar hasta casi cero mientras la de validación sube. Sin "
            "las dos curvas, el resultado parece un éxito. Con las dos, se ve el sobreajuste. "
            "Lo mismo ocurre con la perplejidad: es útil para seguir un experimento, pero no "
            "resume por sí sola la calidad del texto. La evaluación combina métricas, "
            "conjuntos reservados y lectura crítica de las muestras."
        ),
        h2("Lista de comprobación"),
        bullets(
            [
                "Puedo escribir la forma de los logits, los objetivos y la pérdida de un lote.",
                "Sé calcular −ln p y exp(L) para un ejemplo pequeño.",
                "Puedo ordenar las cinco operaciones de un paso de entrenamiento.",
                "Explico la diferencia entre Adam y AdamW sin mirar apuntes.",
                "Sé por qué el split 90/10 y por qué drop_last se usa solo en entrenamiento.",
                "Distingo greedy decoding de muestreo con temperatura y top-k.",
                "Estimo 6 · N · D y lo convierto en GPU-horas con un rendimiento efectivo.",
                "Recuerdo que los datos, no solo el modelo, limitan la calidad.",
            ],
            ordered=True,
        ),
        callout(
            "tip",
            "Cómo usar la autoevaluación",
            "Haz el quiz sin mirar las notas. Si fallas una pregunta, vuelve a la lección "
            "correspondiente y explica el error en voz alta. Un 80 % no significa que hayas "
            "memorizado todo: significa que puedes avanzar sin arrastrar una confusión "
            "básica. Repite el intento después de un día; la memoria a corto plazo infla el "
            "resultado."
        ),
        p(
            "El capítulo termina con el modelo base entrenado y con la posibilidad de cargar "
            "los pesos de GPT-2. Esa carga no es un truco para saltarse el aprendizaje: es "
            "una forma de comprobar que la arquitectura implementada coincide con la de un "
            "modelo real. Si los pesos encajan y el texto generado es coherente, las piezas "
            "están bien conectadas. El finetuning de los capítulos siguientes parte de ahí."
        ),
        check(
            "Explica en tres frases por qué la pérdida de validación es más informativa que "
            "la de entrenamiento para decidir si el modelo ha aprendido algo general.",
            "La pérdida de entrenamiento se calcula con los mismos ejemplos que actualizan "
            "los pesos, así que siempre puede bajar por memorización. La de validación usa "
            "texto no visto y estima si el modelo generaliza. Cuando ambas bajan, hay "
            "aprendizaje útil; cuando solo baja la de entrenamiento, hay sobreajuste."
        ),
        keypoints(
            [
                "La pérdida mide la probabilidad del token correcto, no la verdad del texto.",
                "El bucle de entrenamiento aplica gradientes en un orden concreto.",
                "Los data loaders convierten texto en ventanas y lotes reproducibles.",
                "La validación detecta sobreajuste; las muestras detectan problemas cualitativos.",
                "Temperatura y top-k controlan la variedad de la generación.",
                "6 · N · D y 16 bytes por parámetro permiten estimar cómputo y memoria.",
                "El quiz es un diagnóstico; si falla, vuelve a la lección, no al azar.",
            ]
        ),
    ),
    key_points=(
        "Pérdida, perplejidad, entrenamiento, datos, evaluación y coste forman un sistema.",
        "La validación es la brújula de la generalización.",
        "El orden del bucle y el modo de evaluación cambian el resultado.",
        "La decodificación controla la variedad, no la calidad aprendida.",
        "Las estimaciones de coste son cotas de orden de magnitud.",
        "La autoevaluación sirve para localizar la lección que hay que repasar.",
    ),
    quiz_id="quiz-capitulo-5",
)
