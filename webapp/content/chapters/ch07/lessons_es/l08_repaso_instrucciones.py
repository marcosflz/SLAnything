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
    slug="repaso-instrucciones",
    title="Repaso y autoevaluación",
    summary=(
        "Ocho pasos para ordenar el capítulo, tres confusiones que conviene deshacer y un "
        "quiz de diez preguntas para comprobar lo aprendido."
    ),
    minutes=10,
    objectives=(
        "Reconstruir el pipeline de ajuste de instrucciones de principio a fin.",
        "Distinguir SFT, máscara, plantilla y evaluación sin confundirlos.",
        "Detectar lagunas con una autoevaluación de diez preguntas.",
        "Relacionar el capítulo con el siguiente paso: las preferencias.",
    ),
    blocks=(
        lead(
            "Has recorrido el camino que va de un modelo que completa texto a un modelo que "
            "responde a peticiones. No es un cambio de arquitectura: es un cambio de datos, "
            "formato y señal. Este repaso ordena las piezas y te ayuda a detectar qué idea "
            "necesita una segunda visita antes de seguir."
        ),
        p(
            "El capítulo empieza con una distinción y termina con una medición. Entre medias "
            "aparecen un dataset, una plantilla, un lote enmascarado, un bucle de "
            "entrenamiento y un juez. Si puedes explicar qué entra y qué sale en cada etapa, "
            "tienes el mapa. Si alguna te suena pero no sabrías dibujarla, vuelve a la "
            "lección correspondiente: el quiz no premia la memorización, sino la comprensión."
        ),
        h2("El pipeline en ocho pasos"),
        bullets(
            [
                "<strong>1. Definir el objetivo.</strong> Un modelo preentrenado no sigue "
                "instrucciones de forma fiable; el SFT lo especializa con ejemplos.",
                "<strong>2. Reunir pares.</strong> Instrucción, entrada opcional y respuesta. "
                "Calidad, diversidad, licencia y privacidad se revisan antes de entrenar.",
                "<strong>3. Formatear.</strong> Alpaca o ChatML convierten roles en texto y "
                "marcadores. La misma plantilla debe usarse al entrenar y al inferir.",
                "<strong>4. Tokenizar y agrupar.</strong> El lote se rellena hasta la "
                "secuencia más larga; los objetivos se desplazan una posición.",
                "<strong>5. Enmascarar.</strong> El relleno se marca con -100; se conserva un "
                "EOS. Enmascarar la instrucción es opcional y se decide midiendo.",
                "<strong>6. Entrenar.</strong> Pocas épocas, tasa baja y validación. La "
                "pérdida baja no demuestra buenas respuestas.",
                "<strong>7. Generar y evaluar.</strong> Se reserva un conjunto de prueba, se "
                "leen respuestas y se combinan métricas con juicio humano.",
                "<strong>8. Iterar.</strong> Ajustar datos, formato, hiperparámetros o tamaño "
                "del modelo según los errores observados, no según la intuición.",
            ],
            ordered=True,
        ),
        p(
            "Tres confusiones frecuentes. Primera: creer que el SFT «instala» conocimiento. "
            "El conocimiento viene en gran parte del pretraining; el SFT moldea cómo se "
            "usa. Segunda: confundir la máscara de relleno con la de instrucción. La primera "
            "es obligatoria para no entrenar sobre posiciones vacías; la segunda es una "
            "decisión experimental sobre qué parte de la secuencia recibe señal. Tercera: "
            "tomar la puntuación de un juez como verdad. Es una medida aproximada, útil para "
            "comparar configuraciones, pero necesita calibración y contexto."
        ),
        table(
            ["Pregunta", "Respuesta corta"],
            [
                ["¿Qué cambia el SFT?", "Los datos y la máscara; no la arquitectura."],
                ["¿Qué ignora la pérdida?", "Las posiciones marcadas con -100."],
                ["¿Qué comparte train e inferencia?", "La plantilla, el tokenizador y el formato."],
                ["¿Qué mide un juez LLM?", "Calidad aproximada según una rúbrica, no verdad absoluta."],
            ],
            caption="Cuatro comprobaciones rápidas antes de cerrar el capítulo.",
        ),
        h2("Comprobar lo aprendido"),
        p(
            "La autoevaluación del capítulo tiene <strong>diez preguntas</strong> de opción "
            "múltiple, con explicación en cada respuesta. Necesitas un <strong>80 %</strong> "
            "—ocho de diez— para considerar el capítulo superado. Puedes repetirla sin "
            "penalización. Si fallas una, no te quedes con la opción correcta: vuelve a la "
            "lección, reconstruye el razonamiento y prueba a explicarlo en voz alta. Ese "
            "esfuerzo de explicación es el que consolida."
        ),
        callout(
            "success",
            "Ahora te toca",
            "Abre la <strong>autoevaluación del capítulo 7</strong>. Cubre las ocho lecciones "
            "y combina definiciones con casos de aplicación. Si aciertas las diez, perfecto; "
            "si fallas alguna, ya sabes dónde mirar. El objetivo no es la nota, sino llegar "
            "al capítulo siguiente con las ideas conectadas.",
        ),
        check(
            "Explica en dos frases por qué una pérdida de validación excelente no garantiza un buen asistente.",
            "La pérdida mide la probabilidad de los tokens de referencia, no si la respuesta "
            "es útil, verdadera o segura. Un modelo puede ajustarse muy bien al estilo del "
            "dataset y fallar en peticiones nuevas o producir respuestas plausibles pero "
            "incorrectas.",
        ),
        keypoints(
            [
                "El SFT especializa un modelo preentrenado con pares de instrucción y respuesta.",
                "La plantilla, el tokenizador y el formato deben coincidir en train e inferencia.",
                "El relleno se enmascara con -100; el primer EOS se conserva.",
                "La pérdida de validación y la lectura de respuestas se interpretan juntas.",
                "La evaluación combina métricas, jueces y revisión humana.",
                "Las preferencias y DPO son el siguiente paso, no un requisito del SFT.",
                "El quiz requiere un 80 % y puede repetirse sin penalización.",
            ]
        ),
    ),
    key_points=(
        "El pipeline va del par formateado al lote enmascarado, el entrenamiento y la evaluación.",
        "Máscara de relleno, máscara de instrucción y truncado son controles distintos.",
        "Una puntuación de juez es una aproximación que se calibra con personas.",
        "El capítulo cierra con una autoevaluación de diez preguntas.",
    ),
    quiz_id="quiz-capitulo-7",
)
