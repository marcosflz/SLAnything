"""Lección 2 · Datos, etiquetas y splits."""

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
    number=2,
    slug="datos-etiquetados",
    title="Datos, etiquetas y splits",
    summary=(
        "La calidad del clasificador empieza en el dataset: etiquetas claras, clases "
        "equilibradas y una separación honesta entre entrenamiento, validación y prueba."
    ),
    minutes=10,
    objectives=(
        "Describir la composición del conjunto SMS Spam Collection usado en el libro.",
        "Explicar la función de los conjuntos de entrenamiento, validación y prueba.",
        "Detectar fuga de datos antes de entrenar.",
        "Justificar el equilibrio de clases y el formato de las secuencias.",
    ),
    blocks=(
        lead(
            "Un clasificador no aprende de la nada: aprende de ejemplos y de etiquetas. Si "
            "las etiquetas son ambiguas, si el test se contamina con el entrenamiento o si "
            "una clase aparece casi siempre, el modelo puede obtener una puntuación "
            "excelente en el papel y fallar justo donde importa. Preparar el dataset es la "
            "primera decisión de diseño del capítulo, no un trámite previo."
        ),
        h2("Un conjunto real: SMS Spam Collection"),
        p(
            "El libro trabaja con mensajes de texto etiquetados como <em>ham</em> (no spam) "
            "o <em>spam</em>. El conjunto original tiene <strong>5 572</strong> mensajes: "
            "<strong>4 825</strong> ham y <strong>747</strong> spam. Es decir, el 86,6 % es "
            "ham y solo el 13,4 % es spam. Esa proporción refleja la vida real —recibimos "
            "muchos más mensajes legítimos que fraudulentos— y a la vez crea un problema: "
            "un modelo que siempre diga «ham» acertaría casi nueve de cada diez veces."
        ),
        p(
            "Para que el entrenamiento sea manejable y didáctico, el libro reduce la clase "
            "mayoritaria. Conserva los 747 spam y muestrea al azar 747 ham. El resultado son "
            "<strong>1 494</strong> mensajes equilibrados, 747 de cada clase. Después traduce "
            "las etiquetas de texto a números: <code>ham → 0</code> y <code>spam → 1</code>. "
            "El cambio es parecido a convertir palabras en identificadores, pero aquí el "
            "vocabulario de etiquetas tiene solo dos símbolos. Existen otras técnicas para "
            "tratar el desbalance —pesos de clase, remuestreo, datos sintéticos—; el libro "
            "elige el submuestreo por simplicidad."
        ),
        h2("Entrenar, validar y probar"),
        p(
            "El conjunto equilibrado se baraja y se divide en tres partes: <strong>70 % para "
            "entrenamiento, 10 % para validación y 20 % para prueba</strong>. Con 1 494 "
            "ejemplos, el reparto del código produce aproximadamente 1 045, 149 y 300 "
            "mensajes. Cada parte tiene una misión distinta. El entrenamiento actualiza los "
            "pesos; la validación se usa para tomar decisiones —número de épocas, umbral, "
            "arquitectura—; el test se reserva para una estimación final y no debe guiar "
            "ajustes sucesivos."
        ),
        table(
            ["Split", "Proporción", "Ejemplos aprox.", "Para qué sirve"],
            [
                ["Entrenamiento", "70 %", "1 045", "Actualizar los pesos"],
                ["Validación", "10 %", "149", "Elegir épocas, umbral y ajustes"],
                ["Prueba", "20 %", "300", "Estimar el rendimiento final una sola vez"],
            ],
            caption="Reparto del conjunto equilibrado de 1 494 mensajes.",
            note="Los números exactos dependen del redondeo del código; el libro usa 70/10/20.",
        ),
        h2("Fuga de datos y otras trampas"),
        p(
            "La <strong>fuga de datos</strong> (<em>leakage</em>) ocurre cuando información del "
            "test se cuela en el entrenamiento. Un caso típico es dividir al azar sin quitar "
            "duplicados: el mismo mensaje, o una variante casi idéntica, aparece en train y "
            "en test, y el modelo parece memorizar mejor de lo que generaliza. También hay "
            "fuga si se normaliza o se seleccionan características usando todo el dataset "
            "antes de separar, o si los mensajes de un mismo remitente se reparten entre "
            "partes. La regla es simple: el test debe ser, en la medida de lo posible, "
            "información que el modelo nunca vio."
        ),
        p(
            "El desbalance merece una comprobación por split, no solo global. Tras el "
            "submuestreo las clases están equilibradas, pero un reparto mal hecho podría "
            "dejar la validación con pocos spam. Conviene estratificar o, como mínimo, "
            "verificar las proporciones. También conviene mirar la longitud de los textos: "
            "el mensaje más largo del conjunto de entrenamiento tiene <strong>120 tokens</strong>, muy por "
            "debajo de la ventana de 1 024 del modelo. Por eso el libro rellena las "
            "secuencias más cortas con el token <code>&lt;|endoftext|&gt;</code>, cuyo id es "
            "<strong>50256</strong>, hasta la longitud máxima del entrenamiento."
        ),
        callout(
            "warning",
            "Divide antes de mirar",
            "Si calculas estadísticas, ajustas el tokenizador o eliminas duplicados usando "
            "todo el corpus y después divides, ya has contaminado el test. La separación "
            "debe ocurrir antes de cualquier decisión que dependa de los datos. En este "
            "capítulo el tokenizador es fijo, pero el principio sigue siendo válido."
        ),
        check(
            "Tienes 10 000 mensajes y el 90 % son ham. ¿Por qué no basta con reportar una "
            "accuracy del 90 %?",
            "Porque un clasificador trivial que siempre prediga «ham» obtendría esa misma "
            "cifra sin detectar ni un solo spam. La accuracy global oculta el rendimiento "
            "sobre la clase minoritaria; hacen falta precisión, recall o una matriz de "
            "confusión que separe los tipos de acierto y error.",
        ),
        keypoints(
            [
                "El conjunto original tiene 5 572 mensajes: 4 825 ham y 747 spam.",
                "El libro submuestrea ham hasta 747 para equilibrar las clases.",
                "Las etiquetas se codifican como 0 (ham) y 1 (spam).",
                "El reparto es 70 % entrenamiento, 10 % validación y 20 % prueba.",
                "La fuga de datos infla las métricas y se evita separando antes de procesar.",
                "Las secuencias se rellenan hasta 120 tokens con el id 50256.",
            ]
        ),
    ),
    key_points=(
        "Las etiquetas convierten una tarea abierta en un problema de clasificación.",
        "El desbalance exige mirar más allá de la accuracy global.",
        "Entrenamiento, validación y prueba tienen funciones distintas.",
        "La fuga de datos se combate separando antes de procesar y eliminando duplicados.",
        "El padding permite agrupar secuencias de longitud variable en lotes.",
    ),
)
