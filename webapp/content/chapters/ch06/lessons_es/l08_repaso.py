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
)

LESSON = Lesson(
    number=8,
    slug="repaso-clasificacion",
    title="Repaso y autoevaluación",
    summary=(
        "Ocho ideas para consolidar el capítulo y una autoevaluación de diez preguntas "
        "sobre datos, cabeza, entrenamiento, métricas y umbrales."
    ),
    minutes=10,
    objectives=(
        "Repasar las ideas clave del finetuning de clasificación.",
        "Conectar datos, modelo, pérdida, métricas y decisión final.",
        "Detectar errores frecuentes antes de pasar al capítulo siguiente.",
        "Comprobar el aprendizaje con la autoevaluación del capítulo.",
    ),
    blocks=(
        lead(
            "Has recorrido el capítulo 6. El objetivo no era memorizar una lista de "
            "fórmulas, sino entender una cadena: los datos definen el problema, la cabeza "
            "convierte representaciones en clases, la pérdida guía el ajuste, las métricas "
            "revelan qué tipo de error comete el modelo y el umbral decide qué hacer con "
            "esa información. Este repaso ordena la cadena."
        ),
        p(
            "Si tuvieras que explicar el capítulo en una frase, podría ser esta: un modelo "
            "generativo se convierte en clasificador cuando se le cambia la salida por una "
            "capa de clases y se ajusta con ejemplos etiquetados, pero su valor real depende "
            "de cómo se midan los errores y de cómo se conviertan en decisiones. Las "
            "lecciones anteriores desarrollan cada eslabón."
        ),
        h2("Las ocho ideas que te llevas"),
        bullets(
            [
                "<strong>Clasificar es elegir entre etiquetas conocidas.</strong> El modelo "
                "no genera una respuesta abierta: devuelve una puntuación por clase.",
                "<strong>La cabeza sustituye al vocabulario.</strong> Una capa lineal de 768 "
                "a 2 clases reemplaza la proyección a 50 257 tokens.",
                "<strong>El último token resume la secuencia.</strong> La atención causal le "
                "permite ver todos los tokens anteriores.",
                "<strong>La entropía cruzada es el objetivo.</strong> Castiga la baja "
                "probabilidad asignada a la clase correcta y es diferenciable.",
                "<strong>El desbalance engaña.</strong> Una accuracy alta puede convivir con "
                "un recall nulo; submuestrear o ponderar clases corrige el sesgo.",
                "<strong>El finetuning se hace con cuidado.</strong> Tasa baja, capas "
                "congeladas, pocas épocas y parada temprana sobre validación.",
                "<strong>La matriz de confusión manda.</strong> Precisión, recall y F1 "
                "describen aspectos distintos del mismo recuento.",
                "<strong>El umbral es una decisión de producto.</strong> Moverlo cambia el "
                "equilibrio entre falsos positivos y falsos negativos.",
            ],
            ordered=True,
        ),
        h2("Errores que conviene evitar"),
        p(
            "El primero es confundir prompt con finetuning. Añadir ejemplos al contexto "
            "puede mejorar una respuesta, pero no cambia los pesos ni crea una cabeza de "
            "clasificación. El segundo es celebrar una accuracy alta sin mirar las clases: "
            "en un conjunto con pocos positivos, acertar siempre el negativo produce una "
            "cifra engañosa. El tercero es contaminar el test con duplicados o con "
            "decisiones tomadas sobre todo el corpus. El cuarto es elegir el umbral mirando "
            "el test: esa práctica convierte la evaluación final en otra validación y "
            "sobreestima el rendimiento."
        ),
        p(
            "También conviene recordar que el modelo del libro es pequeño: GPT-2 de 124 "
            "millones de parámetros, 120 tokens de longitud máxima y 1 494 mensajes "
            "equilibrados. Los resultados —97,21 % en entrenamiento, 97,32 % en validación y "
            "95,67 % en prueba— son excelentes para ese montaje, pero no se trasladan "
            "automáticamente a cualquier dominio. Un clasificador médico, legal o financiero "
            "necesita datos, validación y análisis de errores propios."
        ),
        p(
            "<strong>Antes de dar el capítulo por cerrado</strong>, comprueba que puedes "
            "responder a estas preguntas sin mirar los apuntes:"
        ),
        bullets(
            [
                "¿Qué capa se sustituye y cuántas salidas tiene en un problema binario?",
                "¿Por qué se usa el último token y no el primero?",
                "¿Qué diferencia hay entre validación y prueba?",
                "¿Cómo detectarías fuga de datos en un split?",
                "¿Cuándo preferirías recall alto aunque baje la precisión?",
                "¿Por qué una accuracy del 95 % puede ser peor que una del 80 %?",
            ]
        ),
        callout(
            "success",
            "Ahora te toca",
            "Abre la <strong>autoevaluación del capítulo</strong>: diez preguntas con la "
            "explicación de cada respuesta. Necesitas un <strong>80 %</strong> —ocho de "
            "diez— para considerar el capítulo superado. Puedes repetirla sin límite. Si "
            "fallas una pregunta, vuelve a la lección correspondiente y reconstruye el "
            "razonamiento antes de intentarlo de nuevo."
        ),
        check(
            "Explica en dos frases el recorrido completo, desde un mensaje nuevo hasta una "
            "decisión de spam.",
            "El mensaje se tokeniza y se rellena hasta la longitud máxima; el modelo produce "
            "logits para el último token y softmax los convierte en probabilidades. Después "
            "se compara la probabilidad de spam con un umbral elegido en validación y se "
            "decide si se marca o no, sabiendo qué coste tiene cada tipo de error.",
        ),
        keypoints(
            [
                "La clasificación sustituye la generación abierta por etiquetas prefijadas.",
                "La cabeza lineal y el último token son las piezas clave del modelo.",
                "La pérdida y el desbalance determinan qué aprende el clasificador.",
                "La matriz de confusión y el umbral conectan métricas con decisiones.",
                "El test se reserva para una evaluación final honesta.",
                "El quiz requiere un 80 % y puede repetirse sin penalización.",
            ]
        ),
    ),
    key_points=(
        "Un clasificador es un modelo generativo con una cabeza de clases.",
        "Datos, pérdida, métricas y umbral forman una cadena de decisiones.",
        "La accuracy sola no basta con clases desbalanceadas.",
        "El umbral se elige en validación según el coste del error.",
        "El quiz del capítulo exige un 80 % y puede repetirse.",
    ),
    quiz_id="quiz-capitulo-6",
)
