"""Autoevaluación del capítulo 7 (ES)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-7": Quiz(
        id="quiz-capitulo-7",
        title="Autoevaluación · Capítulo 7",
        description=(
            "Diez preguntas sobre ajuste de instrucciones, plantillas, máscaras, evaluación "
            "y preferencias. Necesitas un 80 % para superar el capítulo; puedes repetirlo."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="¿Qué distingue el ajuste supervisado de instrucciones del pretraining?",
                options=(
                    "El SFT usa texto sin etiquetas y el pretraining pares de instrucción y respuesta.",
                    "El SFT usa pares de instrucción y respuesta; el pretraining predice el siguiente token en texto general.",
                    "El SFT cambia la arquitectura del transformer.",
                    "El pretraining solo funciona con modelos pequeños.",
                ),
                correct=1,
                explanation=(
                    "Ambos optimizan la predicción del siguiente token. La diferencia está en "
                    "los datos: el SFT usa peticiones con respuestas deseadas y una máscara que "
                    "decide qué tokens contribuyen a la pérdida."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "Un registro tiene «instruction» y «output», pero «input» está vacío. "
                    "¿Qué debe hacer una plantilla Alpaca bien construida?"
                ),
                options=(
                    "Incluir «### Input:» seguido de una línea vacía.",
                    "Omitir la sección «### Input:».",
                    "Copiar la instrucción dentro de «### Input:».",
                    "Descartar el registro por incompleto.",
                ),
                correct=1,
                explanation=(
                    "La sección de entrada es opcional. Incluirla vacía añade ruido y enseña un "
                    "patrón que no aporta información; el libro la omite cuando el campo no "
                    "tiene contenido."
                ),
            ),
            Question(
                id="q3",
                prompt="¿Por qué conviene usar la misma plantilla de chat al entrenar y al inferir?",
                options=(
                    "Porque así el modelo ocupa menos memoria.",
                    "Porque la plantilla cambia los pesos automáticamente.",
                    "Porque el modelo aprende marcadores y distribución de formato; cambiarlos crea una discrepancia.",
                    "Porque las plantillas solo funcionan una vez.",
                ),
                correct=2,
                explanation=(
                    "El modelo no ve roles, ve tokens. Si en producción aparecen marcadores, "
                    "espacios o turnos distintos de los del entrenamiento, la secuencia cambia y "
                    "la respuesta puede degradarse."
                ),
            ),
            Question(
                id="q4",
                prompt="¿Qué hace exactamente el valor -100 en el tensor de objetivos?",
                options=(
                    "La entropía cruzada lo ignora por defecto, así que no contribuye a la pérdida.",
                    "Elimina el token del vocabulario del modelo.",
                    "Lo convierte automáticamente en un token de fin de secuencia.",
                    "Duplica la pérdida de la posición anterior.",
                ),
                correct=0,
                explanation=(
                    "-100 es el ignore_index predeterminado de cross_entropy en PyTorch. Las "
                    "posiciones marcadas así no entran en la media de la pérdida, lo que permite "
                    "ignorar el relleno."
                ),
            ),
            Question(
                id="q5",
                prompt=(
                    "En un lote, una respuesta termina antes que la más larga. Tras desplazar "
                    "los objetivos, ¿cómo se tratan las posiciones de relleno?"
                ),
                options=(
                    "Todas se conservan como EOS para enseñar a parar.",
                    "Todas se sustituyen por 0.",
                    "Se eliminan del lote y se acorta la secuencia.",
                    "Se conserva el primer EOS y las demás se marcan con -100.",
                ),
                correct=3,
                explanation=(
                    "El primer EOS es la señal de fin de respuesta y se conserva. Los EOS "
                    "posteriores son relleno y se sustituyen por -100 para que no contribuyan a "
                    "la pérdida."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "La pérdida de entrenamiento baja a 0,30, la de validación se queda en "
                    "0,657 y no mejora. ¿Qué lectura es más razonable?"
                ),
                options=(
                    "El modelo ha aprendido perfectamente y hay que añadir cinco épocas.",
                    "La pérdida de validación es irrelevante; solo cuenta la de entrenamiento.",
                    "Puede haber sobreajuste; conviene detener o revisar datos y respuestas.",
                    "Hay que subir la tasa de aprendizaje al doble para desbloquearla.",
                ),
                correct=2,
                explanation=(
                    "Una brecha creciente entre entrenamiento y validación es una señal de "
                    "sobreajuste. Antes de seguir entrenando, hay que leer respuestas y revisar "
                    "la representatividad de los datos."
                ),
            ),
            Question(
                id="q7",
                prompt="¿Qué aporta un LLM usado como juez en la evaluación?",
                options=(
                    "Una estimación escalable de calidad según una rúbrica, que debe calibrarse.",
                    "Una medida exacta de la verdad factual.",
                    "La garantía de que el modelo evaluado es seguro.",
                    "Una forma de evitar cualquier revisión humana.",
                ),
                correct=0,
                explanation=(
                    "El juez aproxima el juicio humano y permite puntuar muchos casos, pero "
                    "hereda sesgos, no es determinista y necesita calibración con una muestra "
                    "revisada por personas."
                ),
            ),
            Question(
                id="q8",
                prompt=(
                    "Un juez puntúa tres respuestas con 90, 60 y 30. ¿Qué conclusión es correcta?"
                ),
                options=(
                    "La media de 60 demuestra que el modelo es mediocre en cualquier tarea.",
                    "Es una señal descriptiva de esas tres respuestas; hace falta una muestra mayor y contexto.",
                    "La respuesta de 30 es necesariamente falsa y la de 90 necesariamente verdadera.",
                    "El juez ha fallado porque las puntuaciones no son idénticas.",
                ),
                correct=1,
                explanation=(
                    "Tres puntuaciones describen tres casos. Para estimar calidad general se "
                    "necesita un conjunto representativo, una rúbrica estable y, preferiblemente, "
                    "validación humana."
                ),
            ),
            Question(
                id="q9",
                prompt="¿Qué usa DPO que no requiere un modelo de recompensa separado?",
                options=(
                    "Un corpus de texto sin etiquetas.",
                    "Una búsqueda exhaustiva de respuestas correctas.",
                    "Un clasificador de spam.",
                    "Pares de respuestas preferida y rechazada para optimizar directamente.",
                ),
                correct=3,
                explanation=(
                    "DPO optimiza el modelo con comparaciones entre una respuesta preferida y "
                    "otra rechazada, manteniendo una referencia. RLHF clásico entrena un modelo "
                    "de recompensa y después optimiza la política con refuerzo."
                ),
            ),
            Question(
                id="q10",
                prompt="¿Cuál es el orden correcto del pipeline de ajuste de instrucciones?",
                options=(
                    "Formatear y tokenizar → ensamblar lotes y enmascarar → entrenar → generar y evaluar.",
                    "Entrenar → formatear → evaluar → tokenizar.",
                    "Evaluar → entrenar → tokenizar → enmascarar.",
                    "Tokenizar → evaluar → entrenar → formatear.",
                ),
                correct=0,
                explanation=(
                    "Primero se preparan los pares y la plantilla, después se construyen los "
                    "lotes con objetivos y máscara, luego se entrena y finalmente se generan "
                    "respuestas sobre el conjunto de prueba para evaluarlas."
                ),
            ),
        ),
    ),
}
